#include <stdint.h>

#include "model_data.h"

#if defined(BENCHMARK_PLATFORM_KEIL)
#include "benchmark_keil_port.h"
#endif

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
static port_float debug_input_scaled[VALIDATION_SEQ_LEN][1u];
static port_float debug_initial_conv[VALIDATION_SEQ_LEN][4u];
static port_float debug_conv_block_0[VALIDATION_SEQ_LEN][8u];
static port_float debug_post_dense_1[VALIDATION_SEQ_LEN][8u];
static port_float debug_post_dense_2[VALIDATION_SEQ_LEN][8u];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN][1u];

static void uart_init(void)
{
#if defined(BENCHMARK_PLATFORM_KEIL)
    benchmark_keil_uart_init();
#else
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
#endif
}

static __attribute__((noinline)) void uart_putc(char ch)
{
#if defined(BENCHMARK_PLATFORM_KEIL)
    benchmark_keil_uart_putc(ch);
#else
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
#endif
}

static __attribute__((noinline)) void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }
        uart_putc(*message++);
    }
}

static __attribute__((noinline)) void uart_put_u32(uint32_t value)
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

static __attribute__((noinline)) void uart_put_ms_from_us(uint64_t value_us)
{
    uint32_t whole_ms = (uint32_t)(value_us / 1000u);
    uint32_t frac_us = (uint32_t)(value_us % 1000u);

    uart_put_u32(whole_ms);
    uart_putc('.');
    uart_putc((char)('0' + (frac_us / 100u)));
    uart_putc((char)('0' + ((frac_us / 10u) % 10u)));
    uart_putc((char)('0' + (frac_us % 10u)));
    uart_puts("000");
}

static __attribute__((noinline)) void uart_put_fixed6(port_float value)
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

static __attribute__((noinline)) void uart_put_matrix_rows(const port_float *values,
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

static port_float silu_approx(port_float value)
{
    return value * sigmoid_approx(value);
}

static port_float relu(port_float value)
{
    return value > 0.0f ? value : 0.0f;
}

static port_float apply_activation_code(port_float value, uint32_t activation_code)
{
    if (activation_code == ACT_RELU) {
        return relu(value);
    }
    if (activation_code == ACT_TANH) {
        return tanh_approx(value);
    }
    if (activation_code == ACT_SIGMOID) {
        return sigmoid_approx(value);
    }
    if (activation_code == ACT_SILU) {
        return silu_approx(value);
    }
    return value;
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

static port_float conv1d_causal_step(const port_float *history, uint32_t step_index, uint32_t history_channels, uint32_t kernel_size, uint32_t dilation, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t output_channel)
{
    port_float sum = bias_values[output_channel];
    uint32_t kernel_index;
    for (kernel_index = 0u; kernel_index < kernel_size; ++kernel_index) {
        int32_t sample_index = (int32_t)step_index - (int32_t)((kernel_size - 1u - kernel_index) * dilation);
        uint32_t input_channel;
        if (sample_index < 0) {
            continue;
        }
        for (input_channel = 0u; input_channel < history_channels; ++input_channel) {
            uint32_t history_offset = ((uint32_t)sample_index * history_channels) + input_channel;
            uint32_t kernel_offset = ((kernel_index * history_channels) + input_channel) * output_channels + output_channel;
            sum += history[history_offset] * kernel_values[kernel_offset];
        }
    }
    return sum;
}

static void dense_pointwise_forward(const port_float *input_values, uint32_t input_channels, uint32_t output_channels, const port_float *kernel_values, const port_float *bias_values, uint32_t activation_code, port_float *output_values)
{
    uint32_t output_index;
    for (output_index = 0u; output_index < output_channels; ++output_index) {
        uint32_t input_index;
        port_float sum = bias_values[output_index];
        for (input_index = 0u; input_index < input_channels; ++input_index) {
            sum += input_values[input_index] * kernel_values[(input_index * output_channels) + output_index];
        }
        output_values[output_index] = apply_activation_code(sum, activation_code);
    }
}

static void clear_debug_buffers(void)
{
    zero_buffer(&debug_input_scaled[0u][0u], VALIDATION_SEQ_LEN * 1u);
    zero_buffer(&debug_initial_conv[0u][0u], VALIDATION_SEQ_LEN * 4u);
    zero_buffer(&debug_conv_block_0[0u][0u], VALIDATION_SEQ_LEN * 8u);
    zero_buffer(&debug_post_dense_1[0u][0u], VALIDATION_SEQ_LEN * 8u);
    zero_buffer(&debug_post_dense_2[0u][0u], VALIDATION_SEQ_LEN * 8u);
    zero_buffer(&debug_output_scaled[0u][0u], VALIDATION_SEQ_LEN * 1u);
}

static void run_generated_record(const port_float input_sequence[VALIDATION_SEQ_LEN][CONV_STACK_INPUT_DIM], port_float output_sequence[VALIDATION_SEQ_LEN])
{
    uint32_t step_index;
    uint32_t channel_index;

    clear_debug_buffers();
    for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
        debug_input_scaled[step_index][0u] = scale_input(input_sequence[step_index][0u]);
        for (channel_index = 0u; channel_index < 4u; ++channel_index) {
            port_float raw_value = conv1d_causal_step(&debug_input_scaled[0u][0u], step_index, CONV_STACK_INPUT_DIM, 20u, 1u, 4u, &conv_stack_initial_kernel[0u][0u][0u], &conv_stack_initial_bias[0u], channel_index);
            debug_initial_conv[step_index][channel_index] = apply_activation_code(raw_value, 2u);
        }
        for (channel_index = 0u; channel_index < 8u; ++channel_index) {
            port_float raw_value = conv1d_causal_step(&debug_initial_conv[0u][0u], step_index, 4u, 20u, 1u, 8u, &conv_2_kernel[0u][0u][0u], &conv_2_bias[0u], channel_index);
            debug_conv_block_0[step_index][channel_index] = apply_activation_code(raw_value, 2u);
        }
        dense_pointwise_forward(&debug_conv_block_0[step_index][0u], 8u, 8u, &post_dense_1_kernel[0u][0u][0u], &post_dense_1_bias[0u], 1u, &debug_post_dense_1[step_index][0u]);
        dense_pointwise_forward(&debug_post_dense_1[step_index][0u], 8u, 8u, &post_dense_2_kernel[0u][0u][0u], &post_dense_2_bias[0u], 1u, &debug_post_dense_2[step_index][0u]);
        dense_pointwise_forward(&debug_post_dense_2[step_index][0u], 8u, 1u, &conv_stack_output_kernel[0u][0u][0u], &conv_stack_output_bias[0u], 0u, &debug_output_scaled[step_index][0u]);
        output_sequence[step_index] = inverse_scale_output(debug_output_scaled[step_index][0u]);
    }
}

int main(void)
{
    uint32_t iter_index;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t dwt_supported;
    uint32_t total_cycles = 0u;
#if defined(BENCHMARK_PLATFORM_KEIL)
    uint64_t total_tick_us = 0u;
    uint64_t start_tick_us = 0u;
    uint64_t end_tick_us = 0u;
#endif
    uint32_t start_cycles = 0u;
    uint32_t end_cycles = 0u;
    port_float output_value = 0.0f;
#if defined(BENCHMARK_PLATFORM_KEIL)
    benchmark_keil_platform_init();
#endif
    uart_init();
    uart_puts("ONEDCNN_BENCHMARK_VALIDATION\n");
    dwt_supported = dwt_is_counting();
    for (iter_index = 0u; iter_index < BENCHMARK_ITERATIONS; ++iter_index) {
        if (BENCHMARK_RESET_STATE_EACH_RUN != 0u) {
            clear_debug_buffers();
        }
        if (dwt_supported != 0u) {
            dwt_init();
            start_cycles = dwt_read_cycles();
#if defined(BENCHMARK_PLATFORM_KEIL)
            start_tick_us = benchmark_keil_get_tick_us();
#endif
        }
        run_generated_record(validation_input[0u], validation_output[0u]);
        if (dwt_supported != 0u) {
            end_cycles = dwt_read_cycles();
            total_cycles += (end_cycles - start_cycles);
#if defined(BENCHMARK_PLATFORM_KEIL)
            end_tick_us = benchmark_keil_get_tick_us();
            total_tick_us += (end_tick_us - start_tick_us);
#endif
        }
        output_value = validation_output[0u][VALIDATION_SEQ_LEN - 1u];
    }
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
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
#if defined(BENCHMARK_PLATFORM_KEIL)
        uart_puts("\nwall_time_unit=");
        uart_puts("ms");
        uart_puts("\nwall_time_total_ms=");
        uart_put_ms_from_us(total_tick_us);
        uart_puts("\nwall_time_per_iter_ms=");
        uart_put_ms_from_us(BENCHMARK_ITERATIONS == 0u ? 0u : (total_tick_us / (uint64_t)BENCHMARK_ITERATIONS));
#endif
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");
    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        run_generated_record(validation_input[record_index], validation_output[record_index]);
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
#if !defined(BENCHMARK_PLATFORM_KEIL)
        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_input_scaled[0u][0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");

        uart_puts("validation_initial_conv_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_initial_conv[0u][0u], VALIDATION_SEQ_LEN, 4u);
        uart_puts("\n");

        uart_puts("validation_conv_block_0_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_conv_block_0[0u][0u], VALIDATION_SEQ_LEN, 8u);
        uart_puts("\n");

        uart_puts("validation_post_dense_1_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_post_dense_1[0u][0u], VALIDATION_SEQ_LEN, 8u);
        uart_puts("\n");

        uart_puts("validation_post_dense_2_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_post_dense_2[0u][0u], VALIDATION_SEQ_LEN, 8u);
        uart_puts("\n");

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u][0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");

#endif
    }
    uart_puts("validation_complete=1\n");
    while (1) {
    }
}
