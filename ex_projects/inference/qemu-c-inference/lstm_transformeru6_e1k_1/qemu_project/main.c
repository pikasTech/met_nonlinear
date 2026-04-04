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
static port_float debug_scaled_input[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM];
static port_float debug_lstm_hidden[VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_transformer_ln_attn[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_transformer_ln_ffn[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float debug_post_dense[VALIDATION_SEQ_LEN][POST_DENSE_UNITS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];
static port_float scratch_sequence_a[VALIDATION_SEQ_LEN][LSTM_UNITS];
static port_float scratch_sequence_b[VALIDATION_SEQ_LEN][LSTM_UNITS];

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

static port_float exp_approx(port_float value)
{
    const port_float ln2 = 0.6931471805599453f;
    int32_t exponent = 0;
    port_float squared;
    port_float polynomial;

    if (value < -16.0f) {
        return 0.0f;
    }

    while (value < -ln2) {
        value += ln2;
        exponent += 1;
    }
    while (value > ln2) {
        value -= ln2;
        exponent -= 1;
    }

    squared = value * value;
    polynomial = 1.0f
        + value
        + (squared * 0.5f)
        + (squared * value * 0.16666666666666666f)
        + (squared * squared * 0.041666666666666664f)
        + (squared * squared * value * 0.008333333333333333f);

    while (exponent > 0) {
        polynomial *= 0.5f;
        exponent -= 1;
    }
    while (exponent < 0) {
        polynomial *= 2.0f;
        exponent += 1;
    }

    return polynomial;
}

static port_float sqrt_approx(port_float value)
{
    uint32_t scale_up = 0u;
    uint32_t scale_down = 0u;
    uint32_t iteration;
    port_float guess;
    port_float normalized;

    if (value <= 0.0f) {
        return 0.0f;
    }

    normalized = value;
    while (normalized < 0.25f) {
        normalized *= 4.0f;
        scale_up += 1u;
    }
    while (normalized > 4.0f) {
        normalized *= 0.25f;
        scale_down += 1u;
    }

    guess = normalized > 1.0f ? normalized : 1.0f;
    for (iteration = 0u; iteration < 6u; ++iteration) {
        guess = 0.5f * (guess + normalized / guess);
    }

    while (scale_down > 0u) {
        guess *= 2.0f;
        scale_down -= 1u;
    }
    while (scale_up > 0u) {
        guess *= 0.5f;
        scale_up -= 1u;
    }

    return guess;
}

static port_float apply_activation(port_float value, uint32_t activation_code)
{
    if (activation_code == ACT_LINEAR) {
        return value;
    }
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

static void dense_forward_generic(const port_float *input,
                                  uint32_t input_dim,
                                  const port_float *kernel,
                                  const port_float *bias,
                                  uint32_t output_dim,
                                  uint32_t activation_code,
                                  port_float *output)
{
    uint32_t output_index;
    for (output_index = 0u; output_index < output_dim; ++output_index) {
        uint32_t input_index;
        port_float sum = bias[output_index];
        for (input_index = 0u; input_index < input_dim; ++input_index) {
            sum += input[input_index] * kernel[input_index * output_dim + output_index];
        }
        output[output_index] = apply_activation(sum, activation_code);
    }
}

static void layer_norm_forward(const port_float *input,
                               const port_float *gamma,
                               const port_float *beta,
                               port_float *output)
{
    uint32_t feature_index;
    port_float mean = 0.0f;
    port_float variance = 0.0f;
    port_float denominator;

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        mean += input[feature_index];
    }
    mean /= (port_float)LSTM_UNITS;

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        port_float centered = input[feature_index] - mean;
        variance += centered * centered;
    }
    variance /= (port_float)LSTM_UNITS;
    denominator = sqrt_approx(variance + TRANSFORMER_LAYER_NORM_EPSILON);
    if (denominator <= 0.0f) {
        denominator = 1.0f;
    }

    for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
        output[feature_index] = ((input[feature_index] - mean) / denominator) * gamma[feature_index] + beta[feature_index];
    }
}

static void transformer_average_pool_same(const port_float input_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                          port_float pooled_sequence[TRANSFORMER_CONTEXT_LEN][LSTM_UNITS])
{
    uint32_t output_index;
    uint32_t padded_length = ((TRANSFORMER_CONTEXT_LEN - 1u) * ATTENTION_POOL_SIZE) + ATTENTION_POOL_SIZE;
    uint32_t total_padding = padded_length > VALIDATION_SEQ_LEN ? padded_length - VALIDATION_SEQ_LEN : 0u;
    int32_t pad_left = (int32_t)(total_padding / 2u);

    for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
        uint32_t feature_index;
        int32_t window_start = (int32_t)(output_index * ATTENTION_POOL_SIZE) - pad_left;
        int32_t window_end = window_start + (int32_t)ATTENTION_POOL_SIZE;
        uint32_t valid_count = 0u;

        for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
            pooled_sequence[output_index][feature_index] = 0.0f;
        }

        for (; window_start < window_end; ++window_start) {
            if (window_start >= 0 && window_start < (int32_t)VALIDATION_SEQ_LEN) {
                for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
                    pooled_sequence[output_index][feature_index] += input_sequence[(uint32_t)window_start][feature_index];
                }
                valid_count += 1u;
            }
        }

        if (valid_count > 0u) {
            for (feature_index = 0u; feature_index < LSTM_UNITS; ++feature_index) {
                pooled_sequence[output_index][feature_index] /= (port_float)valid_count;
            }
        }
    }
}

static void lstm_backbone_forward(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  uint32_t reset_state_each_run,
                                  port_float hidden_state[LSTM_UNITS],
                                  port_float cell_state[LSTM_UNITS],
                                  port_float output_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS])
{
    uint32_t step;

    if (reset_state_each_run != 0u) {
        zero_buffer(hidden_state, LSTM_UNITS);
        zero_buffer(cell_state, LSTM_UNITS);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        uint32_t unit;
        uint32_t input_index;
        port_float previous_hidden[LSTM_UNITS];
        port_float previous_cell[LSTM_UNITS];
        port_float scaled_input_step[LSTM_INPUT_DIM];

        for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
            scaled_input_step[input_index] = scale_input(sequence[step][input_index]);
            if (debug_scaled_input_buffer != 0) {
                debug_scaled_input_buffer[step][input_index] = scaled_input_step[input_index];
            }
        }

        for (unit = 0u; unit < LSTM_UNITS; ++unit) {
            previous_hidden[unit] = hidden_state[unit];
            previous_cell[unit] = cell_state[unit];
        }

        for (unit = 0u; unit < LSTM_UNITS; ++unit) {
            uint32_t hidden_index;
            port_float input_gate_acc = lstm_bias[unit + LSTM_UNITS * 0u];
            port_float forget_gate_acc = lstm_bias[unit + LSTM_UNITS * 1u];
            port_float candidate_acc = lstm_bias[unit + LSTM_UNITS * 2u];
            port_float output_gate_acc = lstm_bias[unit + LSTM_UNITS * 3u];

            for (input_index = 0u; input_index < LSTM_INPUT_DIM; ++input_index) {
                port_float input_value = scaled_input_step[input_index];
                input_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 0u];
                forget_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 1u];
                candidate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 2u];
                output_gate_acc += input_value * lstm_kernel[input_index][unit + LSTM_UNITS * 3u];
            }

            for (hidden_index = 0u; hidden_index < LSTM_UNITS; ++hidden_index) {
                port_float hidden_value = previous_hidden[hidden_index];
                input_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 0u];
                forget_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 1u];
                candidate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 2u];
                output_gate_acc += hidden_value * lstm_recurrent_kernel[hidden_index][unit + LSTM_UNITS * 3u];
            }

            {
                port_float input_gate = sigmoid_approx(input_gate_acc);
                port_float forget_gate = sigmoid_approx(forget_gate_acc);
                port_float candidate = tanh_approx(candidate_acc);
                port_float output_gate = sigmoid_approx(output_gate_acc);
                port_float cell_value = forget_gate * previous_cell[unit] + input_gate * candidate;
                port_float hidden_value = output_gate * tanh_approx(cell_value);

                cell_state[unit] = cell_value;
                hidden_state[unit] = hidden_value;
                output_sequence[step][unit] = hidden_value;
                if (debug_lstm_hidden_buffer != 0) {
                    debug_lstm_hidden_buffer[step][unit] = hidden_value;
                }
            }
        }
    }
}

static void transformer_forward_layer(uint32_t layer_index,
                                      const port_float input_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float output_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float debug_ln_attn_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                      port_float debug_ln_ffn_sequence[VALIDATION_SEQ_LEN][LSTM_UNITS])
{
    port_float pooled_sequence[TRANSFORMER_CONTEXT_LEN][LSTM_UNITS];
    port_float key_cache[TRANSFORMER_CONTEXT_LEN][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
    port_float value_cache[TRANSFORMER_CONTEXT_LEN][TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
    uint32_t context_index;

    transformer_average_pool_same(input_sequence, pooled_sequence);

    for (context_index = 0u; context_index < TRANSFORMER_CONTEXT_LEN; ++context_index) {
        uint32_t head_index;
        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t dim_index;
            for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                uint32_t input_index;
                port_float key_sum = transformer_key_bias[layer_index][head_index][dim_index];
                port_float value_sum = transformer_value_bias[layer_index][head_index][dim_index];
                for (input_index = 0u; input_index < LSTM_UNITS; ++input_index) {
                    port_float input_value = pooled_sequence[context_index][input_index];
                    key_sum += input_value * transformer_key_kernel[layer_index][input_index][head_index][dim_index];
                    value_sum += input_value * transformer_value_kernel[layer_index][input_index][head_index][dim_index];
                }
                key_cache[context_index][head_index][dim_index] = key_sum;
                value_cache[context_index][head_index][dim_index] = value_sum;
            }
        }
    }

    for (context_index = 0u; context_index < VALIDATION_SEQ_LEN; ++context_index) {
        uint32_t head_index;
        port_float query_cache[TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
        port_float head_output[TRANSFORMER_HEADS][TRANSFORMER_KEY_DIM];
        port_float attention_projected[LSTM_UNITS];
        port_float residual_buffer[LSTM_UNITS];
        port_float ln_attn_output[LSTM_UNITS];
        port_float ffn_expand_output[TRANSFORMER_FF_DIM];
        port_float ffn_project_output[LSTM_UNITS];
        port_float ln_ffn_output[LSTM_UNITS];

        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t dim_index;
            for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                uint32_t input_index;
                port_float sum = transformer_query_bias[layer_index][head_index][dim_index];
                for (input_index = 0u; input_index < LSTM_UNITS; ++input_index) {
                    sum += input_sequence[context_index][input_index] * transformer_query_kernel[layer_index][input_index][head_index][dim_index];
                }
                query_cache[head_index][dim_index] = sum;
            }
        }

        for (head_index = 0u; head_index < TRANSFORMER_HEADS; ++head_index) {
            uint32_t output_index;
            port_float scores[TRANSFORMER_CONTEXT_LEN];
            port_float max_score = -1.0e30f;
            port_float softmax_sum = 0.0f;

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                uint32_t dim_index;
                port_float score = 0.0f;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    score += query_cache[head_index][dim_index] * key_cache[output_index][head_index][dim_index];
                }
                score *= ATTENTION_SCALE;
                scores[output_index] = score;
                if (score > max_score) {
                    max_score = score;
                }
            }

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                scores[output_index] = exp_approx(scores[output_index] - max_score);
                softmax_sum += scores[output_index];
            }

            if (softmax_sum <= 0.0f) {
                for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                    scores[output_index] = output_index == 0u ? 1.0f : 0.0f;
                }
                softmax_sum = 1.0f;
            }

            for (output_index = 0u; output_index < TRANSFORMER_KEY_DIM; ++output_index) {
                head_output[head_index][output_index] = 0.0f;
            }

            for (output_index = 0u; output_index < TRANSFORMER_CONTEXT_LEN; ++output_index) {
                uint32_t dim_index;
                port_float normalized_score = scores[output_index] / softmax_sum;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    head_output[head_index][dim_index] += normalized_score * value_cache[output_index][head_index][dim_index];
                }
            }
        }

        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            uint32_t input_index;
            port_float sum = transformer_attention_output_bias[layer_index][head_index];
            for (input_index = 0u; input_index < TRANSFORMER_HEADS; ++input_index) {
                uint32_t dim_index;
                for (dim_index = 0u; dim_index < TRANSFORMER_KEY_DIM; ++dim_index) {
                    sum += head_output[input_index][dim_index] * transformer_attention_output_kernel[layer_index][input_index][dim_index][head_index];
                }
            }
            attention_projected[head_index] = sum;
            residual_buffer[head_index] = input_sequence[context_index][head_index] + sum;
        }

        layer_norm_forward(
            residual_buffer,
            transformer_ln_attn_gamma[layer_index],
            transformer_ln_attn_beta[layer_index],
            ln_attn_output
        );
        if (debug_ln_attn_sequence != 0) {
            for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
                debug_ln_attn_sequence[context_index][head_index] = ln_attn_output[head_index];
            }
        }

        dense_forward_generic(
            ln_attn_output,
            LSTM_UNITS,
            &transformer_ffn_expand_kernel[layer_index][0u][0u],
            transformer_ffn_expand_bias[layer_index],
            TRANSFORMER_FF_DIM,
            ACT_RELU,
            ffn_expand_output
        );
        dense_forward_generic(
            ffn_expand_output,
            TRANSFORMER_FF_DIM,
            &transformer_ffn_project_kernel[layer_index][0u][0u],
            transformer_ffn_project_bias[layer_index],
            LSTM_UNITS,
            ACT_LINEAR,
            ffn_project_output
        );

        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            residual_buffer[head_index] = ln_attn_output[head_index] + ffn_project_output[head_index];
        }
        layer_norm_forward(
            residual_buffer,
            transformer_ln_ffn_gamma[layer_index],
            transformer_ln_ffn_beta[layer_index],
            ln_ffn_output
        );
        for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
            output_sequence[context_index][head_index] = ln_ffn_output[head_index];
        }
        if (debug_ln_ffn_sequence != 0) {
            for (head_index = 0u; head_index < LSTM_UNITS; ++head_index) {
                debug_ln_ffn_sequence[context_index][head_index] = ln_ffn_output[head_index];
            }
        }
    }
}

static void lstm_transformer_forward_sequence(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                              uint32_t reset_state_each_run,
                                              port_float hidden_state[LSTM_UNITS],
                                              port_float cell_state[LSTM_UNITS],
                                              port_float output_sequence[VALIDATION_SEQ_LEN],
                                              port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                              port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_ln_attn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_ln_ffn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                              port_float debug_post_dense_buffer[VALIDATION_SEQ_LEN][POST_DENSE_UNITS],
                                              port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t layer_index;
    uint32_t step_index;
    port_float (*current_sequence)[LSTM_UNITS] = scratch_sequence_a;
    port_float (*next_sequence)[LSTM_UNITS] = scratch_sequence_b;

    lstm_backbone_forward(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        current_sequence,
        debug_scaled_input_buffer,
        debug_lstm_hidden_buffer
    );

    for (layer_index = 0u; layer_index < TRANSFORMER_LAYER_COUNT; ++layer_index) {
        port_float (*temp_sequence)[LSTM_UNITS];
        transformer_forward_layer(
            layer_index,
            current_sequence,
            next_sequence,
            debug_ln_attn_buffer != 0 ? debug_ln_attn_buffer[layer_index] : 0,
            debug_ln_ffn_buffer != 0 ? debug_ln_ffn_buffer[layer_index] : 0
        );
        temp_sequence = current_sequence;
        current_sequence = next_sequence;
        next_sequence = temp_sequence;
    }

    for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
        port_float post_dense_output[POST_DENSE_UNITS];
        port_float output_scaled_vector[OUTPUT_UNITS];

        if (HAS_POST_DENSE != 0u) {
            dense_forward_generic(
                current_sequence[step_index],
                POST_DENSE_INPUT_UNITS,
                &post_dense_kernel[0u][0u],
                post_dense_bias,
                POST_DENSE_UNITS,
                POST_DENSE_ACTIVATION,
                post_dense_output
            );
            if (debug_post_dense_buffer != 0) {
                uint32_t post_index;
                for (post_index = 0u; post_index < POST_DENSE_UNITS; ++post_index) {
                    debug_post_dense_buffer[step_index][post_index] = post_dense_output[post_index];
                }
            }
            dense_forward_generic(
                post_dense_output,
                OUTPUT_INPUT_UNITS,
                &output_kernel[0u][0u],
                output_bias,
                OUTPUT_UNITS,
                ACT_LINEAR,
                output_scaled_vector
            );
        } else {
            dense_forward_generic(
                current_sequence[step_index],
                OUTPUT_INPUT_UNITS,
                &output_kernel[0u][0u],
                output_bias,
                OUTPUT_UNITS,
                ACT_LINEAR,
                output_scaled_vector
            );
        }

        if (debug_output_scaled_buffer != 0) {
            debug_output_scaled_buffer[step_index] = output_scaled_vector[0u];
        }
        output_sequence[step_index] = inverse_scale_output(output_scaled_vector[0u]);
    }
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                  port_float debug_lstm_hidden_buffer[VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_ln_attn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_ln_ffn_buffer[TRANSFORMER_LAYER_COUNT][VALIDATION_SEQ_LEN][LSTM_UNITS],
                                  port_float debug_post_dense_buffer[VALIDATION_SEQ_LEN][POST_DENSE_UNITS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];

    zero_buffer(hidden_state, LSTM_UNITS);
    zero_buffer(cell_state, LSTM_UNITS);
    lstm_transformer_forward_sequence(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        output_sequence,
        debug_scaled_input_buffer,
        debug_lstm_hidden_buffer,
        debug_ln_attn_buffer,
        debug_ln_ffn_buffer,
        debug_post_dense_buffer,
        debug_output_scaled_buffer
    );
}

static void run_benchmark_record(const port_float sequence[VALIDATION_SEQ_LEN][LSTM_INPUT_DIM],
                                 uint32_t reset_state_each_run,
                                 port_float hidden_state[LSTM_UNITS],
                                 port_float cell_state[LSTM_UNITS],
                                 port_float *output_value)
{
    port_float output_sequence[VALIDATION_SEQ_LEN];
    lstm_transformer_forward_sequence(
        sequence,
        reset_state_each_run,
        hidden_state,
        cell_state,
        output_sequence,
        0,
        0,
        0,
        0,
        0,
        0
    );
    *output_value = output_sequence[VALIDATION_SEQ_LEN - 1u];
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
    port_float hidden_state[LSTM_UNITS];
    port_float cell_state[LSTM_UNITS];
    port_float output_value = 0.0f;

    uart_init();
    dwt_supported = dwt_is_counting();
    zero_buffer(hidden_state, LSTM_UNITS);
    zero_buffer(cell_state, LSTM_UNITS);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_benchmark_record(
                validation_input[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                hidden_state,
                cell_state,
                &output_value
            );
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("LSTM_TRANSFORMER_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\ninput_dim=");
    uart_put_u32(LSTM_INPUT_DIM);
    uart_puts("\nlstm_units=");
    uart_put_u32(LSTM_UNITS);
    uart_puts("\ntransformer_layers=");
    uart_put_u32(TRANSFORMER_LAYER_COUNT);
    uart_puts("\ntransformer_heads=");
    uart_put_u32(TRANSFORMER_HEADS);
    uart_puts("\ntransformer_ff_dim=");
    uart_put_u32(TRANSFORMER_FF_DIM);
    uart_puts("\nattention_pool_size=");
    uart_put_u32(ATTENTION_POOL_SIZE);
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
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            1u,
            debug_scaled_input,
            debug_lstm_hidden,
            debug_transformer_ln_attn,
            debug_transformer_ln_ffn,
            debug_post_dense,
            debug_output_scaled
        );

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
        uart_put_matrix_rows(&debug_scaled_input[0u][0u], VALIDATION_SEQ_LEN, LSTM_INPUT_DIM);
        uart_puts("\n");

        uart_puts("validation_lstm_hidden_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_lstm_hidden[0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
        uart_puts("\n");

        for (layer_index = 0u; layer_index < TRANSFORMER_LAYER_COUNT; ++layer_index) {
            uart_puts("validation_transformer_ln_attn_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_transformer_ln_attn[layer_index][0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
            uart_puts("\n");

            uart_puts("validation_transformer_ln_ffn_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_transformer_ln_ffn[layer_index][0u][0u], VALIDATION_SEQ_LEN, LSTM_UNITS);
            uart_puts("\n");
        }

        if (HAS_POST_DENSE != 0u) {
            uart_puts("validation_post_dense_");
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(&debug_post_dense[0u][0u], VALIDATION_SEQ_LEN, POST_DENSE_UNITS);
            uart_puts("\n");
        }

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
