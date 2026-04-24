#include <stdint.h>
#include <math.h>

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
static port_float debug_scaled_input[VALIDATION_SEQ_LEN];
static port_float debug_iir_output[VALIDATION_SEQ_LEN][FRIKAN_FEATURES];
static port_float debug_kan_output[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

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

#define FRIKAN_LUT_LAST_INDEX (FRIKAN_LUT_POINTS - 1u)
#define FRIKAN_LUT_LAST_INDEX_FLOAT ((port_float)(FRIKAN_LUT_POINTS - 1u))

#if FRIKAN_USE_SYMMETRY
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (((raw_value) < 0.0f) ? -(raw_value) : (raw_value))
#else
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (raw_value)
#endif

#define FRIKAN_LUT_MAP_INDEX(lookup_value, lut_scale, lut_offset) (((lookup_value) * (lut_scale)) + (lut_offset))

#define FRIKAN_LUT_SCALE_LAYER_0 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_0 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_0(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_0,
        FRIKAN_LUT_OFFSET_LAYER_0
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_0[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_1 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_1 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_1(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_1,
        FRIKAN_LUT_OFFSET_LAYER_1
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_1[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_2 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_2 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_2(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_2,
        FRIKAN_LUT_OFFSET_LAYER_2
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_2[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_3 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_3 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_3(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_3,
        FRIKAN_LUT_OFFSET_LAYER_3
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_3[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_4 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_4 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_4(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_4,
        FRIKAN_LUT_OFFSET_LAYER_4
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_4[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_5 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_5 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_5(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_5,
        FRIKAN_LUT_OFFSET_LAYER_5
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_5[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
            outputs[1u] += output_sign * row[1u];
            outputs[2u] += output_sign * row[2u];
            outputs[3u] += output_sign * row[3u];
            outputs[4u] += output_sign * row[4u];
            outputs[5u] += output_sign * row[5u];
    }
}

#define FRIKAN_LUT_SCALE_LAYER_6 614.40000000f
#define FRIKAN_LUT_OFFSET_LAYER_6 -0.00000000f

static inline void frikan_lut_accumulate_fast_layer_6(
    port_float outputs[FRIKAN_MAX_LAYER_OUTPUTS],
    uint32_t input_index,
    port_float raw_value)
{
    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
        lookup_value,
        FRIKAN_LUT_SCALE_LAYER_6,
        FRIKAN_LUT_OFFSET_LAYER_6
    );

    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {
        return;
    }

    {
        port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
        uint32_t lut_index = (uint32_t)mapped_index;
        const port_float *row = frikan_layer_lut_6[input_index][lut_index];
            outputs[0u] += output_sign * row[0u];
    }
}




static void frikan_iir_reset(port_float x1[FRIKAN_FEATURES],
                             port_float x2[FRIKAN_FEATURES],
                             port_float y1[FRIKAN_FEATURES],
                             port_float y2[FRIKAN_FEATURES])
{
    zero_buffer(x1, FRIKAN_FEATURES);
    zero_buffer(x2, FRIKAN_FEATURES);
    zero_buffer(y1, FRIKAN_FEATURES);
    zero_buffer(y2, FRIKAN_FEATURES);
}

static void frikan_forward_core(port_float current_values[FRIKAN_MAX_LAYER_INPUTS],
                                port_float *output_scaled_value,
                                port_float debug_kan_step[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS],
                                port_float *output_value)
{
    {
        port_float layer_0_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_0_outputs[0u] = frikan_layer_bias[0u][0u];
        layer_0_outputs[1u] = frikan_layer_bias[0u][1u];
        layer_0_outputs[2u] = frikan_layer_bias[0u][2u];
        layer_0_outputs[3u] = frikan_layer_bias[0u][3u];
        layer_0_outputs[4u] = frikan_layer_bias[0u][4u];
        layer_0_outputs[5u] = frikan_layer_bias[0u][5u];
        uint32_t layer_0_input_index;
        for (layer_0_input_index = 0u; layer_0_input_index < 8u; ++layer_0_input_index) {
            frikan_lut_accumulate_fast_layer_0(
                layer_0_outputs,
                layer_0_input_index,
                current_values[layer_0_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[0u][0u] = layer_0_outputs[0u];
            debug_kan_step[0u][1u] = layer_0_outputs[1u];
            debug_kan_step[0u][2u] = layer_0_outputs[2u];
            debug_kan_step[0u][3u] = layer_0_outputs[3u];
            debug_kan_step[0u][4u] = layer_0_outputs[4u];
            debug_kan_step[0u][5u] = layer_0_outputs[5u];
        }
        current_values[0u] = layer_0_outputs[0u];
        current_values[1u] = layer_0_outputs[1u];
        current_values[2u] = layer_0_outputs[2u];
        current_values[3u] = layer_0_outputs[3u];
        current_values[4u] = layer_0_outputs[4u];
        current_values[5u] = layer_0_outputs[5u];
    }
    {
        port_float layer_1_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_1_outputs[0u] = frikan_layer_bias[1u][0u];
        layer_1_outputs[1u] = frikan_layer_bias[1u][1u];
        layer_1_outputs[2u] = frikan_layer_bias[1u][2u];
        layer_1_outputs[3u] = frikan_layer_bias[1u][3u];
        layer_1_outputs[4u] = frikan_layer_bias[1u][4u];
        layer_1_outputs[5u] = frikan_layer_bias[1u][5u];
        uint32_t layer_1_input_index;
        for (layer_1_input_index = 0u; layer_1_input_index < 6u; ++layer_1_input_index) {
            frikan_lut_accumulate_fast_layer_1(
                layer_1_outputs,
                layer_1_input_index,
                current_values[layer_1_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[1u][0u] = layer_1_outputs[0u];
            debug_kan_step[1u][1u] = layer_1_outputs[1u];
            debug_kan_step[1u][2u] = layer_1_outputs[2u];
            debug_kan_step[1u][3u] = layer_1_outputs[3u];
            debug_kan_step[1u][4u] = layer_1_outputs[4u];
            debug_kan_step[1u][5u] = layer_1_outputs[5u];
        }
        current_values[0u] = layer_1_outputs[0u];
        current_values[1u] = layer_1_outputs[1u];
        current_values[2u] = layer_1_outputs[2u];
        current_values[3u] = layer_1_outputs[3u];
        current_values[4u] = layer_1_outputs[4u];
        current_values[5u] = layer_1_outputs[5u];
    }
    {
        port_float layer_2_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_2_outputs[0u] = frikan_layer_bias[2u][0u];
        layer_2_outputs[1u] = frikan_layer_bias[2u][1u];
        layer_2_outputs[2u] = frikan_layer_bias[2u][2u];
        layer_2_outputs[3u] = frikan_layer_bias[2u][3u];
        layer_2_outputs[4u] = frikan_layer_bias[2u][4u];
        layer_2_outputs[5u] = frikan_layer_bias[2u][5u];
        uint32_t layer_2_input_index;
        for (layer_2_input_index = 0u; layer_2_input_index < 6u; ++layer_2_input_index) {
            frikan_lut_accumulate_fast_layer_2(
                layer_2_outputs,
                layer_2_input_index,
                current_values[layer_2_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[2u][0u] = layer_2_outputs[0u];
            debug_kan_step[2u][1u] = layer_2_outputs[1u];
            debug_kan_step[2u][2u] = layer_2_outputs[2u];
            debug_kan_step[2u][3u] = layer_2_outputs[3u];
            debug_kan_step[2u][4u] = layer_2_outputs[4u];
            debug_kan_step[2u][5u] = layer_2_outputs[5u];
        }
        current_values[0u] = layer_2_outputs[0u];
        current_values[1u] = layer_2_outputs[1u];
        current_values[2u] = layer_2_outputs[2u];
        current_values[3u] = layer_2_outputs[3u];
        current_values[4u] = layer_2_outputs[4u];
        current_values[5u] = layer_2_outputs[5u];
    }
    {
        port_float layer_3_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_3_outputs[0u] = frikan_layer_bias[3u][0u];
        layer_3_outputs[1u] = frikan_layer_bias[3u][1u];
        layer_3_outputs[2u] = frikan_layer_bias[3u][2u];
        layer_3_outputs[3u] = frikan_layer_bias[3u][3u];
        layer_3_outputs[4u] = frikan_layer_bias[3u][4u];
        layer_3_outputs[5u] = frikan_layer_bias[3u][5u];
        uint32_t layer_3_input_index;
        for (layer_3_input_index = 0u; layer_3_input_index < 6u; ++layer_3_input_index) {
            frikan_lut_accumulate_fast_layer_3(
                layer_3_outputs,
                layer_3_input_index,
                current_values[layer_3_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[3u][0u] = layer_3_outputs[0u];
            debug_kan_step[3u][1u] = layer_3_outputs[1u];
            debug_kan_step[3u][2u] = layer_3_outputs[2u];
            debug_kan_step[3u][3u] = layer_3_outputs[3u];
            debug_kan_step[3u][4u] = layer_3_outputs[4u];
            debug_kan_step[3u][5u] = layer_3_outputs[5u];
        }
        current_values[0u] = layer_3_outputs[0u];
        current_values[1u] = layer_3_outputs[1u];
        current_values[2u] = layer_3_outputs[2u];
        current_values[3u] = layer_3_outputs[3u];
        current_values[4u] = layer_3_outputs[4u];
        current_values[5u] = layer_3_outputs[5u];
    }
    {
        port_float layer_4_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_4_outputs[0u] = frikan_layer_bias[4u][0u];
        layer_4_outputs[1u] = frikan_layer_bias[4u][1u];
        layer_4_outputs[2u] = frikan_layer_bias[4u][2u];
        layer_4_outputs[3u] = frikan_layer_bias[4u][3u];
        layer_4_outputs[4u] = frikan_layer_bias[4u][4u];
        layer_4_outputs[5u] = frikan_layer_bias[4u][5u];
        uint32_t layer_4_input_index;
        for (layer_4_input_index = 0u; layer_4_input_index < 6u; ++layer_4_input_index) {
            frikan_lut_accumulate_fast_layer_4(
                layer_4_outputs,
                layer_4_input_index,
                current_values[layer_4_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[4u][0u] = layer_4_outputs[0u];
            debug_kan_step[4u][1u] = layer_4_outputs[1u];
            debug_kan_step[4u][2u] = layer_4_outputs[2u];
            debug_kan_step[4u][3u] = layer_4_outputs[3u];
            debug_kan_step[4u][4u] = layer_4_outputs[4u];
            debug_kan_step[4u][5u] = layer_4_outputs[5u];
        }
        current_values[0u] = layer_4_outputs[0u];
        current_values[1u] = layer_4_outputs[1u];
        current_values[2u] = layer_4_outputs[2u];
        current_values[3u] = layer_4_outputs[3u];
        current_values[4u] = layer_4_outputs[4u];
        current_values[5u] = layer_4_outputs[5u];
    }
    {
        port_float layer_5_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_5_outputs[0u] = frikan_layer_bias[5u][0u];
        layer_5_outputs[1u] = frikan_layer_bias[5u][1u];
        layer_5_outputs[2u] = frikan_layer_bias[5u][2u];
        layer_5_outputs[3u] = frikan_layer_bias[5u][3u];
        layer_5_outputs[4u] = frikan_layer_bias[5u][4u];
        layer_5_outputs[5u] = frikan_layer_bias[5u][5u];
        uint32_t layer_5_input_index;
        for (layer_5_input_index = 0u; layer_5_input_index < 6u; ++layer_5_input_index) {
            frikan_lut_accumulate_fast_layer_5(
                layer_5_outputs,
                layer_5_input_index,
                current_values[layer_5_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[5u][0u] = layer_5_outputs[0u];
            debug_kan_step[5u][1u] = layer_5_outputs[1u];
            debug_kan_step[5u][2u] = layer_5_outputs[2u];
            debug_kan_step[5u][3u] = layer_5_outputs[3u];
            debug_kan_step[5u][4u] = layer_5_outputs[4u];
            debug_kan_step[5u][5u] = layer_5_outputs[5u];
        }
        current_values[0u] = layer_5_outputs[0u];
        current_values[1u] = layer_5_outputs[1u];
        current_values[2u] = layer_5_outputs[2u];
        current_values[3u] = layer_5_outputs[3u];
        current_values[4u] = layer_5_outputs[4u];
        current_values[5u] = layer_5_outputs[5u];
    }
    {
        port_float layer_6_outputs[FRIKAN_MAX_LAYER_OUTPUTS];
        layer_6_outputs[0u] = frikan_layer_bias[6u][0u];
        uint32_t layer_6_input_index;
        for (layer_6_input_index = 0u; layer_6_input_index < 6u; ++layer_6_input_index) {
            frikan_lut_accumulate_fast_layer_6(
                layer_6_outputs,
                layer_6_input_index,
                current_values[layer_6_input_index]
            );
        }
        if (debug_kan_step != 0) {
            debug_kan_step[6u][0u] = layer_6_outputs[0u];
        }
        current_values[0u] = layer_6_outputs[0u];
    }

    if (output_scaled_value != 0) {
        *output_scaled_value = current_values[0u];
    }
    *output_value = inverse_scale_output(current_values[0u]);
}

static inline void frikan_forward_core_benchmark(
    port_float current_values[FRIKAN_MAX_LAYER_INPUTS],
    port_float *output_scaled_value)
{
    {
        port_float layer_0_out_0 = frikan_layer_bias[0u][0u];
        port_float layer_0_out_1 = frikan_layer_bias[0u][1u];
        port_float layer_0_out_2 = frikan_layer_bias[0u][2u];
        port_float layer_0_out_3 = frikan_layer_bias[0u][3u];
        port_float layer_0_out_4 = frikan_layer_bias[0u][4u];
        port_float layer_0_out_5 = frikan_layer_bias[0u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[0u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[1u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[2u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[3u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[4u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[5u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[6u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[6u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[7u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_0,
                FRIKAN_LUT_OFFSET_LAYER_0
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_0[7u][lut_index];
                layer_0_out_0 += output_sign * row[0u];
                layer_0_out_1 += output_sign * row[1u];
                layer_0_out_2 += output_sign * row[2u];
                layer_0_out_3 += output_sign * row[3u];
                layer_0_out_4 += output_sign * row[4u];
                layer_0_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_0_out_0;
        current_values[1u] = layer_0_out_1;
        current_values[2u] = layer_0_out_2;
        current_values[3u] = layer_0_out_3;
        current_values[4u] = layer_0_out_4;
        current_values[5u] = layer_0_out_5;
    }
    {
        port_float layer_1_out_0 = frikan_layer_bias[1u][0u];
        port_float layer_1_out_1 = frikan_layer_bias[1u][1u];
        port_float layer_1_out_2 = frikan_layer_bias[1u][2u];
        port_float layer_1_out_3 = frikan_layer_bias[1u][3u];
        port_float layer_1_out_4 = frikan_layer_bias[1u][4u];
        port_float layer_1_out_5 = frikan_layer_bias[1u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[0u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[1u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[2u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[3u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[4u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_1,
                FRIKAN_LUT_OFFSET_LAYER_1
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_1[5u][lut_index];
                layer_1_out_0 += output_sign * row[0u];
                layer_1_out_1 += output_sign * row[1u];
                layer_1_out_2 += output_sign * row[2u];
                layer_1_out_3 += output_sign * row[3u];
                layer_1_out_4 += output_sign * row[4u];
                layer_1_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_1_out_0;
        current_values[1u] = layer_1_out_1;
        current_values[2u] = layer_1_out_2;
        current_values[3u] = layer_1_out_3;
        current_values[4u] = layer_1_out_4;
        current_values[5u] = layer_1_out_5;
    }
    {
        port_float layer_2_out_0 = frikan_layer_bias[2u][0u];
        port_float layer_2_out_1 = frikan_layer_bias[2u][1u];
        port_float layer_2_out_2 = frikan_layer_bias[2u][2u];
        port_float layer_2_out_3 = frikan_layer_bias[2u][3u];
        port_float layer_2_out_4 = frikan_layer_bias[2u][4u];
        port_float layer_2_out_5 = frikan_layer_bias[2u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[0u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[1u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[2u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[3u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[4u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_2,
                FRIKAN_LUT_OFFSET_LAYER_2
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_2[5u][lut_index];
                layer_2_out_0 += output_sign * row[0u];
                layer_2_out_1 += output_sign * row[1u];
                layer_2_out_2 += output_sign * row[2u];
                layer_2_out_3 += output_sign * row[3u];
                layer_2_out_4 += output_sign * row[4u];
                layer_2_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_2_out_0;
        current_values[1u] = layer_2_out_1;
        current_values[2u] = layer_2_out_2;
        current_values[3u] = layer_2_out_3;
        current_values[4u] = layer_2_out_4;
        current_values[5u] = layer_2_out_5;
    }
    {
        port_float layer_3_out_0 = frikan_layer_bias[3u][0u];
        port_float layer_3_out_1 = frikan_layer_bias[3u][1u];
        port_float layer_3_out_2 = frikan_layer_bias[3u][2u];
        port_float layer_3_out_3 = frikan_layer_bias[3u][3u];
        port_float layer_3_out_4 = frikan_layer_bias[3u][4u];
        port_float layer_3_out_5 = frikan_layer_bias[3u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[0u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[1u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[2u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[3u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[4u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_3,
                FRIKAN_LUT_OFFSET_LAYER_3
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_3[5u][lut_index];
                layer_3_out_0 += output_sign * row[0u];
                layer_3_out_1 += output_sign * row[1u];
                layer_3_out_2 += output_sign * row[2u];
                layer_3_out_3 += output_sign * row[3u];
                layer_3_out_4 += output_sign * row[4u];
                layer_3_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_3_out_0;
        current_values[1u] = layer_3_out_1;
        current_values[2u] = layer_3_out_2;
        current_values[3u] = layer_3_out_3;
        current_values[4u] = layer_3_out_4;
        current_values[5u] = layer_3_out_5;
    }
    {
        port_float layer_4_out_0 = frikan_layer_bias[4u][0u];
        port_float layer_4_out_1 = frikan_layer_bias[4u][1u];
        port_float layer_4_out_2 = frikan_layer_bias[4u][2u];
        port_float layer_4_out_3 = frikan_layer_bias[4u][3u];
        port_float layer_4_out_4 = frikan_layer_bias[4u][4u];
        port_float layer_4_out_5 = frikan_layer_bias[4u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[0u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[1u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[2u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[3u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[4u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_4,
                FRIKAN_LUT_OFFSET_LAYER_4
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_4[5u][lut_index];
                layer_4_out_0 += output_sign * row[0u];
                layer_4_out_1 += output_sign * row[1u];
                layer_4_out_2 += output_sign * row[2u];
                layer_4_out_3 += output_sign * row[3u];
                layer_4_out_4 += output_sign * row[4u];
                layer_4_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_4_out_0;
        current_values[1u] = layer_4_out_1;
        current_values[2u] = layer_4_out_2;
        current_values[3u] = layer_4_out_3;
        current_values[4u] = layer_4_out_4;
        current_values[5u] = layer_4_out_5;
    }
    {
        port_float layer_5_out_0 = frikan_layer_bias[5u][0u];
        port_float layer_5_out_1 = frikan_layer_bias[5u][1u];
        port_float layer_5_out_2 = frikan_layer_bias[5u][2u];
        port_float layer_5_out_3 = frikan_layer_bias[5u][3u];
        port_float layer_5_out_4 = frikan_layer_bias[5u][4u];
        port_float layer_5_out_5 = frikan_layer_bias[5u][5u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[0u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[1u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[2u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[3u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[4u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_5,
                FRIKAN_LUT_OFFSET_LAYER_5
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_5[5u][lut_index];
                layer_5_out_0 += output_sign * row[0u];
                layer_5_out_1 += output_sign * row[1u];
                layer_5_out_2 += output_sign * row[2u];
                layer_5_out_3 += output_sign * row[3u];
                layer_5_out_4 += output_sign * row[4u];
                layer_5_out_5 += output_sign * row[5u];
            }
        }
        current_values[0u] = layer_5_out_0;
        current_values[1u] = layer_5_out_1;
        current_values[2u] = layer_5_out_2;
        current_values[3u] = layer_5_out_3;
        current_values[4u] = layer_5_out_4;
        current_values[5u] = layer_5_out_5;
    }
    {
        port_float layer_6_out_0 = frikan_layer_bias[6u][0u];
        {
            port_float raw_value = current_values[0u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[0u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        {
            port_float raw_value = current_values[1u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[1u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        {
            port_float raw_value = current_values[2u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[2u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        {
            port_float raw_value = current_values[3u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[3u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        {
            port_float raw_value = current_values[4u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[4u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        {
            port_float raw_value = current_values[5u];
            port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);
            port_float mapped_index = FRIKAN_LUT_MAP_INDEX(
                lookup_value,
                FRIKAN_LUT_SCALE_LAYER_6,
                FRIKAN_LUT_OFFSET_LAYER_6
            );
            if (mapped_index <= FRIKAN_LUT_LAST_INDEX_FLOAT) {
                port_float output_sign = raw_value < 0.0f ? -1.0f : 1.0f;
                uint32_t lut_index = (uint32_t)mapped_index;
                const port_float *row = frikan_layer_lut_6[5u][lut_index];
                layer_6_out_0 += output_sign * row[0u];
            }
        }
        current_values[0u] = layer_6_out_0;
    }

    *output_scaled_value = current_values[0u];
}

static void frikan_forward_step(port_float input_value,
                                port_float x1[FRIKAN_FEATURES],
                                port_float x2[FRIKAN_FEATURES],
                                port_float y1[FRIKAN_FEATURES],
                                port_float y2[FRIKAN_FEATURES],
                                port_float *output_scaled_value,
                                port_float *debug_scaled_input_value,
                                port_float debug_iir_step[FRIKAN_FEATURES],
                                port_float debug_kan_step[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS],
                                port_float *output_value)
{
    uint32_t feature_index;
    port_float scaled_input = scale_input(input_value);
    port_float current_values[FRIKAN_MAX_LAYER_INPUTS];

    if (debug_scaled_input_value != 0) {
        *debug_scaled_input_value = scaled_input;
    }

    for (feature_index = 0u; feature_index < FRIKAN_FEATURES; ++feature_index) {
        port_float response = frikan_iir_b0[feature_index] * scaled_input
            + frikan_iir_b1[feature_index] * x1[feature_index]
            + frikan_iir_b2[feature_index] * x2[feature_index]
            - frikan_iir_a1[feature_index] * y1[feature_index]
            - frikan_iir_a2[feature_index] * y2[feature_index];

        x2[feature_index] = x1[feature_index];
        x1[feature_index] = scaled_input;
        y2[feature_index] = y1[feature_index];
        y1[feature_index] = response;
        current_values[feature_index] = response;
        if (debug_iir_step != 0) {
            debug_iir_step[feature_index] = response;
        }
    }

    frikan_forward_core(
        current_values,
        output_scaled_value,
        debug_kan_step,
        output_value
    );
}

static void frikan_forward_step_benchmark(port_float input_value,
                                          port_float x1[FRIKAN_FEATURES],
                                          port_float x2[FRIKAN_FEATURES],
                                          port_float y1[FRIKAN_FEATURES],
                                          port_float y2[FRIKAN_FEATURES],
                                          port_float *output_scaled_value)
{
    port_float scaled_input = scale_input(input_value);
    port_float current_values[FRIKAN_MAX_LAYER_INPUTS];

    {
        port_float x1_value = x1[0u];
        port_float y1_value = y1[0u];
        port_float response = frikan_iir_b0[0u] * scaled_input
            + frikan_iir_b1[0u] * x1_value
            + frikan_iir_b2[0u] * x2[0u]
            - frikan_iir_a1[0u] * y1_value
            - frikan_iir_a2[0u] * y2[0u];
        x2[0u] = x1_value;
        x1[0u] = scaled_input;
        y2[0u] = y1_value;
        y1[0u] = response;
        current_values[0u] = response;
    }
    {
        port_float x1_value = x1[1u];
        port_float y1_value = y1[1u];
        port_float response = frikan_iir_b0[1u] * scaled_input
            + frikan_iir_b1[1u] * x1_value
            + frikan_iir_b2[1u] * x2[1u]
            - frikan_iir_a1[1u] * y1_value
            - frikan_iir_a2[1u] * y2[1u];
        x2[1u] = x1_value;
        x1[1u] = scaled_input;
        y2[1u] = y1_value;
        y1[1u] = response;
        current_values[1u] = response;
    }
    {
        port_float x1_value = x1[2u];
        port_float y1_value = y1[2u];
        port_float response = frikan_iir_b0[2u] * scaled_input
            + frikan_iir_b1[2u] * x1_value
            + frikan_iir_b2[2u] * x2[2u]
            - frikan_iir_a1[2u] * y1_value
            - frikan_iir_a2[2u] * y2[2u];
        x2[2u] = x1_value;
        x1[2u] = scaled_input;
        y2[2u] = y1_value;
        y1[2u] = response;
        current_values[2u] = response;
    }
    {
        port_float x1_value = x1[3u];
        port_float y1_value = y1[3u];
        port_float response = frikan_iir_b0[3u] * scaled_input
            + frikan_iir_b1[3u] * x1_value
            + frikan_iir_b2[3u] * x2[3u]
            - frikan_iir_a1[3u] * y1_value
            - frikan_iir_a2[3u] * y2[3u];
        x2[3u] = x1_value;
        x1[3u] = scaled_input;
        y2[3u] = y1_value;
        y1[3u] = response;
        current_values[3u] = response;
    }
    {
        port_float x1_value = x1[4u];
        port_float y1_value = y1[4u];
        port_float response = frikan_iir_b0[4u] * scaled_input
            + frikan_iir_b1[4u] * x1_value
            + frikan_iir_b2[4u] * x2[4u]
            - frikan_iir_a1[4u] * y1_value
            - frikan_iir_a2[4u] * y2[4u];
        x2[4u] = x1_value;
        x1[4u] = scaled_input;
        y2[4u] = y1_value;
        y1[4u] = response;
        current_values[4u] = response;
    }
    {
        port_float x1_value = x1[5u];
        port_float y1_value = y1[5u];
        port_float response = frikan_iir_b0[5u] * scaled_input
            + frikan_iir_b1[5u] * x1_value
            + frikan_iir_b2[5u] * x2[5u]
            - frikan_iir_a1[5u] * y1_value
            - frikan_iir_a2[5u] * y2[5u];
        x2[5u] = x1_value;
        x1[5u] = scaled_input;
        y2[5u] = y1_value;
        y1[5u] = response;
        current_values[5u] = response;
    }
    {
        port_float x1_value = x1[6u];
        port_float y1_value = y1[6u];
        port_float response = frikan_iir_b0[6u] * scaled_input
            + frikan_iir_b1[6u] * x1_value
            + frikan_iir_b2[6u] * x2[6u]
            - frikan_iir_a1[6u] * y1_value
            - frikan_iir_a2[6u] * y2[6u];
        x2[6u] = x1_value;
        x1[6u] = scaled_input;
        y2[6u] = y1_value;
        y1[6u] = response;
        current_values[6u] = response;
    }
    {
        port_float x1_value = x1[7u];
        port_float y1_value = y1[7u];
        port_float response = frikan_iir_b0[7u] * scaled_input
            + frikan_iir_b1[7u] * x1_value
            + frikan_iir_b2[7u] * x2[7u]
            - frikan_iir_a1[7u] * y1_value
            - frikan_iir_a2[7u] * y2[7u];
        x2[7u] = x1_value;
        x1[7u] = scaled_input;
        y2[7u] = y1_value;
        y1[7u] = response;
        current_values[7u] = response;
    }

    frikan_forward_core_benchmark(current_values, output_scaled_value);
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float x1[FRIKAN_FEATURES],
                                  port_float x2[FRIKAN_FEATURES],
                                  port_float y1[FRIKAN_FEATURES],
                                  port_float y2[FRIKAN_FEATURES],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN],
                                  port_float debug_iir_output_buffer[VALIDATION_SEQ_LEN][FRIKAN_FEATURES],
                                  port_float debug_kan_output_buffer[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float step_kan_debug[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS];
        uint32_t layer_index;
        uint32_t output_index;

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                step_kan_debug[layer_index][output_index] = 0.0f;
            }
        }

        frikan_forward_step(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            debug_output_scaled_buffer != 0 ? &debug_output_scaled_buffer[step] : 0,
            debug_scaled_input_buffer != 0 ? &debug_scaled_input_buffer[step] : 0,
            debug_iir_output_buffer != 0 ? debug_iir_output_buffer[step] : 0,
            debug_kan_output_buffer != 0 ? step_kan_debug : 0,
            &output_sequence[step]
        );

        if (debug_kan_output_buffer != 0) {
            for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
                for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                    debug_kan_output_buffer[layer_index][step][output_index] = step_kan_debug[layer_index][output_index];
                }
            }
        }
    }
}

static void run_benchmark_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                 uint32_t reset_state_each_run,
                                 port_float x1[FRIKAN_FEATURES],
                                 port_float x2[FRIKAN_FEATURES],
                                 port_float y1[FRIKAN_FEATURES],
                                 port_float y2[FRIKAN_FEATURES],
                                 port_float *output_value)
{
    uint32_t step;
    port_float current_output_scaled = 0.0f;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        frikan_forward_step_benchmark(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            &current_output_scaled
        );
    }

    *output_value = inverse_scale_output(current_output_scaled);
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t layer_index;
    uint32_t dwt_supported;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;
#if defined(BENCHMARK_PLATFORM_KEIL)
    uint64_t total_tick_us = 0u;
    uint64_t start_tick_us = 0u;
    uint64_t end_tick_us = 0u;
#endif
    port_float x1[FRIKAN_FEATURES];
    port_float x2[FRIKAN_FEATURES];
    port_float y1[FRIKAN_FEATURES];
    port_float y2[FRIKAN_FEATURES];
    port_float output_value = 0.0f;

#if defined(BENCHMARK_PLATFORM_KEIL)
    benchmark_keil_platform_init();
#endif
    uart_init();
    dwt_supported = dwt_is_counting();
    frikan_iir_reset(x1, x2, y1, y2);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
#if defined(BENCHMARK_PLATFORM_KEIL)
        start_tick_us = benchmark_keil_get_tick_us();
#endif
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_benchmark_record(
                validation_input[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                x1,
                x2,
                y1,
                y2,
                &output_value
            );
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
#if defined(BENCHMARK_PLATFORM_KEIL)
        end_tick_us = benchmark_keil_get_tick_us();
        total_tick_us = end_tick_us - start_tick_us;
#endif
    }

    uart_puts("FRIKAN_BENCHMARK_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\nfeature_count=");
    uart_put_u32(FRIKAN_FEATURES);
    uart_puts("\nkan_layer_count=");
    uart_put_u32(FRIKAN_KAN_LAYER_COUNT);
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
        frikan_iir_reset(x1, x2, y1, y2);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            x1,
            x2,
            y1,
            y2,
            debug_scaled_input,
            debug_iir_output,
            debug_kan_output,
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

#if !defined(BENCHMARK_PLATFORM_KEIL)
        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");

        uart_puts("validation_iir_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_iir_output[0u][0u], VALIDATION_SEQ_LEN, FRIKAN_FEATURES);
        uart_puts("\n");

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            uart_puts("validation_kan_layer_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(
                &debug_kan_output[layer_index][0u][0u],
                VALIDATION_SEQ_LEN,
                (uint32_t)frikan_layer_output_dims[layer_index]
            );
            uart_puts("\n");
        }

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
#endif
    }

    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
