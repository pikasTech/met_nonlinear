#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN][GRU_INPUT_DIM];
static port_float debug_gru_hidden[VALIDATION_SEQ_LEN][GRU_UNITS];
static port_float debug_dense_output[VALIDATION_SEQ_LEN][DENSE_UNITS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static port_float tanh_approx(port_float value)
{
    port_float squared;

    if (value > 3.0f) {
        return 0.99505478f;
    }
    if (value < -3.0f) {
        return -0.99505478f;
    }

    squared = value * value;
    return value * (27.0f + squared) / (27.0f + 9.0f * squared);
}

static port_float sigmoid_approx(port_float value)
{
    if (value > 8.0f) {
        return 0.99966466f;
    }
    if (value < -8.0f) {
        return 0.00033535f;
    }
    return 0.5f * (tanh_approx(value * 0.5f) + 1.0f);
}

static port_float relu(port_float value)
{
    return value > 0.0f ? value : 0.0f;
}

static port_float silu_approx(port_float value)
{
    return value * sigmoid_approx(value);
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

static void dense_forward_silu(const port_float input[GRU_UNITS],
                               port_float output[DENSE_UNITS])
{
    uint32_t out_index;
    for (out_index = 0u; out_index < DENSE_UNITS; ++out_index) {
        uint32_t input_index;
        port_float sum = dense_bias[out_index];
        for (input_index = 0u; input_index < GRU_UNITS; ++input_index) {
            sum += input[input_index] * dense_kernel[input_index][out_index];
        }
        output[out_index] = silu_approx(sum);
    }
}

static port_float output_forward_linear(const port_float input[DENSE_UNITS])
{
    uint32_t input_index;
    port_float sum = output_bias[0u];
    for (input_index = 0u; input_index < DENSE_UNITS; ++input_index) {
        sum += input[input_index] * output_kernel[input_index][0u];
    }
    return sum;
}

static void gru_forward_step(const port_float input_step[GRU_INPUT_DIM],
                             port_float hidden_state[GRU_UNITS],
                             port_float *output_scaled_value,
                             port_float debug_scaled_input_step[GRU_INPUT_DIM],
                             port_float debug_hidden_step[GRU_UNITS],
                             port_float debug_dense_step[DENSE_UNITS],
                             port_float *output_value)
{
    uint32_t unit;
    uint32_t input_index;
    port_float previous_hidden[GRU_UNITS];
    port_float dense_output[DENSE_UNITS];
    port_float scaled_input_step[GRU_INPUT_DIM];

    for (input_index = 0u; input_index < GRU_INPUT_DIM; ++input_index) {
        scaled_input_step[input_index] = scale_input(input_step[input_index]);
        if (debug_scaled_input_step != 0) {
            debug_scaled_input_step[input_index] = scaled_input_step[input_index];
        }
    }

    for (unit = 0u; unit < GRU_UNITS; ++unit) {
        previous_hidden[unit] = hidden_state[unit];
    }

    for (unit = 0u; unit < GRU_UNITS; ++unit) {
        uint32_t hidden_index;
        port_float update_gate_input = gru_input_bias[unit + GRU_UNITS * 0u];
        port_float reset_gate_input = gru_input_bias[unit + GRU_UNITS * 1u];
        port_float candidate_input = gru_input_bias[unit + GRU_UNITS * 2u];
        port_float update_gate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 0u];
        port_float reset_gate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 1u];
        port_float candidate_recurrent = gru_recurrent_bias[unit + GRU_UNITS * 2u];
        port_float update_gate;
        port_float reset_gate;
        port_float candidate;
        port_float hidden_value;

        for (input_index = 0u; input_index < GRU_INPUT_DIM; ++input_index) {
            port_float input_value = scaled_input_step[input_index];
            update_gate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 0u];
            reset_gate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 1u];
            candidate_input += input_value * gru_kernel[input_index][unit + GRU_UNITS * 2u];
        }

        for (hidden_index = 0u; hidden_index < GRU_UNITS; ++hidden_index) {
            port_float prev_value = previous_hidden[hidden_index];
            update_gate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 0u];
            reset_gate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 1u];
            candidate_recurrent += prev_value * gru_recurrent_kernel[hidden_index][unit + GRU_UNITS * 2u];
        }

        update_gate = sigmoid_approx(update_gate_input + update_gate_recurrent);
        reset_gate = sigmoid_approx(reset_gate_input + reset_gate_recurrent);
        candidate = tanh_approx(candidate_input + reset_gate * candidate_recurrent);
        hidden_value = update_gate * previous_hidden[unit] + (1.0f - update_gate) * candidate;

        hidden_state[unit] = hidden_value;
        if (debug_hidden_step != 0) {
            debug_hidden_step[unit] = hidden_value;
        }
    }

    dense_forward_silu(hidden_state, dense_output);
    for (unit = 0u; unit < DENSE_UNITS; ++unit) {
        if (debug_dense_step != 0) {
            debug_dense_step[unit] = dense_output[unit];
        }
    }

    {
        port_float output_scaled = output_forward_linear(dense_output);
        if (output_scaled_value != 0) {
            *output_scaled_value = output_scaled;
        }
        *output_value = inverse_scale_output(output_scaled);
    }
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][GRU_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[GRU_UNITS],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][GRU_INPUT_DIM],
                                  port_float debug_gru_hidden_buffer[VALIDATION_SEQ_LEN][GRU_UNITS],
                                  port_float debug_dense_output_buffer[VALIDATION_SEQ_LEN][DENSE_UNITS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;
    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, GRU_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float *step_scaled_input = 0;
        port_float *step_hidden = 0;
        port_float *step_dense = 0;
        port_float *step_output_scaled = 0;

        if (debug_scaled_input_buffer != 0) {
            step_scaled_input = debug_scaled_input_buffer[step];
        }
        if (debug_gru_hidden_buffer != 0) {
            step_hidden = debug_gru_hidden_buffer[step];
        }
        if (debug_dense_output_buffer != 0) {
            step_dense = debug_dense_output_buffer[step];
        }
        if (debug_output_scaled_buffer != 0) {
            step_output_scaled = &debug_output_scaled_buffer[step];
        }

        gru_forward_step(
            sequence[step],
            hidden_state,
            step_output_scaled,
            step_scaled_input,
            step_hidden,
            step_dense,
            &output_sequence[step]
        );
    }
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t dwt_supported;
    port_float hidden_state[GRU_UNITS];
    port_float output_value = 0.0f;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;

    uart_init();
    dwt_supported = dwt_is_counting();
    zero_buffer(hidden_state, GRU_UNITS);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_validation_record(
                validation_input[record_index],
                validation_output[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                hidden_state,
                0,
                0,
                0,
                0
            );
            output_value = validation_output[record_index][VALIDATION_SEQ_LEN - 1u];
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("GRN_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\ninput_dim=");
    uart_put_u32(GRU_INPUT_DIM);
    uart_puts("\ngru_units=");
    uart_put_u32(GRU_UNITS);
    uart_puts("\ndense_units=");
    uart_put_u32(DENSE_UNITS);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        zero_buffer(hidden_state, GRU_UNITS);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            hidden_state,
            debug_scaled_input,
            debug_gru_hidden,
            debug_dense_output,
            debug_output_scaled
        );
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u][0u], VALIDATION_SEQ_LEN, GRU_INPUT_DIM);
        uart_puts("\n");

        uart_puts("validation_gru_hidden_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_gru_hidden[0u][0u], VALIDATION_SEQ_LEN, GRU_UNITS);
        uart_puts("\n");

        uart_puts("validation_dense_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_dense_output[0u][0u], VALIDATION_SEQ_LEN, DENSE_UNITS);
        uart_puts("\n");

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
    }
    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
