#include "frikan.h"
#include "port.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "frikan_test.h"

#define USE_WIN32_MATH 1

#if (defined(_WIN32) && USE_WIN32_MATH)
#include <math.h>
#endif

#define MAX_BASES 32
#define MAX_OUTPUT_SIZE 32
#define EPSILON 1e-6f
#define LUT_INTERP 1
#define ONLY_POSITIVE 1
#define USE_port_float_GRID_RANGE 0

// 快速获取绝对值和恢复符号的内联函数
#if !(defined(_WIN32) && USE_WIN32_MATH)
static inline port_float fabsf(port_float x) {
    union {
        port_float f;
        uint32_t u;
    } tmp;
    tmp.f = x;
    tmp.u &= 0x7FFFFFFF;  // 清除符号位
    return tmp.f;
}
#endif

#if !(defined(_WIN32) && USE_WIN32_MATH)
static inline port_float copysignf(port_float abs_x, port_float x) {
    union {
        port_float f;
        uint32_t u;
    } tmp_abs, tmp_x;
    tmp_abs.f = abs_x;
    tmp_x.f = x;
    tmp_abs.u |= (tmp_x.u & 0x80000000);  // 设置符号位
    return tmp_abs.f;
}
#endif

void KAN_LUT_calc_spline_bases(KAN_LUT* self, port_float x, port_float* bases) {
    // Initialize the order-0 B-spline bases
    uint32_t len_bases = self->grid_size + 2 * self->spline_order;
    if (len_bases > MAX_BASES) {
        printf("The number of bases exceeds the maximum limit.\n");
        return;
    }
    for (uint32_t i = 0; i < len_bases; i++) {
        if (self->grid[i] <= x && x < self->grid[i + 1]) {
            bases[i] = 1.0f;
        } else {
            bases[i] = 0.0f;
        }
    }

    for (uint32_t k = 1; k <= self->spline_order; k++) {
        len_bases--;
        for (uint32_t i = 0; i < len_bases; i++) {
            port_float left_term = 0.0f;
            port_float right_term = 0.0f;

            // Calculate the left term
            if (fabsf(self->grid[i + k] - self->grid[i]) > EPSILON) {
                left_term = ((x - self->grid[i]) /
                             (self->grid[i + k] - self->grid[i])) *
                            bases[i];
            }

            // Calculate the right term
            if (fabsf(self->grid[i + k + 1] - self->grid[i + 1]) > EPSILON) {
                right_term = ((self->grid[i + k + 1] - x) /
                              (self->grid[i + k + 1] - self->grid[i + 1])) *
                             bases[i + 1];
            }

            bases[i] = left_term + right_term;
        }
    }
}

// Function to calculate the output of the KAN LUT
port_float KAN_LUT_calc_spline_output(KAN_LUT* self, port_float x) {
    // Step 1: Use the absolute value of the input
    port_float abs_x = fabsf(x);
    int len_bases = self->grid_size + 2 * self->spline_order;
    // Create a temporary array to store the B-spline bases
    port_float bases_buffer[MAX_BASES];
    port_float* bases = (port_float*)bases_buffer;
    KAN_LUT_calc_spline_bases(self, abs_x, bases_buffer);

    // Calculate the output value
    port_float out = 0.0f;
    uint32_t len_spline_kernel = self->grid_size + self->spline_order;
    for (uint32_t i = 0; i < len_spline_kernel; ++i) {
        out += bases[i] * self->spline_kernel[i];
    }

    // Step 2: Apply positive constraint if required
#if ONLY_POSITIVE
    out = fabsf(out);  // Ensure the output is positive
#endif

    // Step 3: Restore the sign based on the input
    out = copysignf(out, x);

    return out;
}

port_float KAN_LUT_calc_spline_output_lut(KAN_LUT* self, port_float x) {
    port_float x_abs = fabsf(x);

#if USE_port_float_GRID_RANGE
    port_float inv_range = 1.0f / (self->grid_range[1] - self->grid_range[0]);
    x_abs = (x_abs - self->grid_range[0]) * inv_range;
#endif
    int scale = self->lut_points - 1;
    port_float f_index = x_abs * scale;
    int upper_index = (int)f_index + 1;
    int lower_index;

    // Get the indices of the closest points
    if (upper_index >= scale) {
        // 超过上界直接返回0.0
        return 0.0f;
    }
    lower_index = upper_index - 1;

    // Get the LUT values at the closest points
    port_float lower_value = self->lut[lower_index];
    port_float upper_value = self->lut[upper_index];

#if LUT_INTERP
    // Perform linear interpolation
    port_float weight = f_index - lower_index;
    port_float interpolated_value =
        lower_value + weight * (upper_value - lower_value);
#else
    // Use the left value directly
    port_float interpolated_value = lower_value;
#endif

    // Return the result, preserving the sign of `x`
    interpolated_value = copysignf(interpolated_value, x);
    return interpolated_value;
}

// Function for `forward_once`
void LayerKAN_LUT_forward_once(LayerKAN_LUT* layer,
                               const port_float* inputs,
                               port_float* outputs,
                               int use_lut) {
    if (inputs == NULL || outputs == NULL) {
        printf("Invalid inputs or outputs.\n");
        return;
    }

    // Initialize outputs to 0
    for (uint32_t o = 0; o < layer->out_size; ++o) {
        outputs[o] = 0.0f;
    }

    // Loop through each output and calculate its value
    for (uint32_t o = 0; o < layer->out_size; ++o) {
        for (uint32_t i = 0; i < layer->in_size; ++i) {
            KAN_LUT* lut = (KAN_LUT*)layer->kan_luts[i * layer->out_size + o];
            port_float output = 0.0f;
            if (use_lut) {
                output = KAN_LUT_calc_spline_output_lut(
                    lut, inputs[i]);  // LUT calculation
            } else {
                output = KAN_LUT_calc_spline_output(
                    lut, inputs[i]);  // Normal calculation
            }
            outputs[o] += output;
        }
    }
}

// Function for `forward`
void LayerKAN_LUT_forward(LayerKAN_LUT* layer,
                          const port_float** inputs_list,
                          uint32_t batch_size,
                          port_float** outputs_list,
                          int use_lut) {
    if (inputs_list == NULL || outputs_list == NULL) {
        printf("Invalid inputs_list or outputs_list.\n");
        return;
    }

    // Loop through each input in the batch and calculate the output
    for (uint32_t b = 0; b < batch_size; ++b) {
        // Each element in the outputs_list corresponds to one forward pass
        // (batch)
        LayerKAN_LUT_forward_once(layer, inputs_list[b], outputs_list[b],
                                  use_lut);
    }
}

// IIR 单滤波器的前向传播实现
port_float IIR_forward_once(IIR* filter, port_float input) {
    if (filter == NULL) {
        printf("IIR_filter is NULL.\n");
        return 0.0f;
    }

    // 保存当前输入
    // 将历史输入向后移动
    for (int i = filter->order; i > 0; --i) {
        filter->x[i] = filter->x[i - 1];
    }
    filter->x[0] = input;

    // 计算输出
    port_float output = 0.0f;
    // 分子部分（b 系数）
    for (int i = 0; i <= filter->order; ++i) {
        output += filter->b[i] * filter->x[i];
    }
    // 分母部分（a 系数），从1开始，因为 a[0] 通常为1
    for (int i = 1; i <= filter->order; ++i) {
        output -= filter->a[i] * filter->y[i - 1];
    }

    // 保存当前输出
    // 将历史输出向后移动
    for (int i = filter->order - 1; i > 0; --i) {
        filter->y[i] = filter->y[i - 1];
    }
    filter->y[0] = output;

    return output;
}

// LayerIIR 的单次前向传播实现
void LayerIIR_forward_once(LayerIIR* layer,
                           const port_float* inputs,
                           port_float* outputs) {
    if (layer == NULL || inputs == NULL || outputs == NULL) {
        printf("Invalid layer, inputs, or outputs.\n");
        return;
    }

    // 初始化输出为0
    for (int o = 0; o < layer->out_size; ++o) {
        outputs[o] = 0.0f;
    }

    // 遍历每个输出
    for (int o = 0; o < layer->out_size; ++o) {
        // 遍历每个输入
        for (int i = 0; i < layer->in_size; ++i) {
            // 获取对应的IIR滤波器
            const IIR* filter = layer->iirs[i * layer->out_size + o];
            if (filter == NULL) {
                printf("IIR filter at input %d, output %d is NULL.\n", i, o);
                continue;
            }

            // 执行单次滤波
            port_float filtered_output =
                IIR_forward_once((IIR*)filter, inputs[i]);

            // 累加到对应的输出
            outputs[o] += filtered_output;
        }
    }
}

int ModelKAN_LUT_init(ModelKAN_LUT* model) {
    if (model == NULL) {
        printf("Invalid model.\n");
        return -1;
    }
    for (uint32_t i = 0; i < model->num_rnn_layers; i++) {
        LayerIIR* layer = (LayerIIR*)model->rnn_layers[i];
        for (int j = 0; j < layer->in_size * layer->out_size; j++) {
            IIR* filter = (IIR*)layer->iirs[j];
            memset(filter->x, 0, sizeof(port_float) * IIR_MAX_ORDER + 1);
            memset(filter->y, 0, sizeof(port_float) * IIR_MAX_ORDER + 1);
        }
    }
    return 0;
}

void ModelKAN_LUT_forward_once(ModelKAN_LUT* model,
                               port_float* inputs_list,
                               port_float* outputs_list,
                               int use_lut) {
    if (model == NULL || inputs_list == NULL || outputs_list == NULL) {
        printf("Invalid model, inputs_list, or outputs_list.\n");
        return;
    }

    port_float buffer[2][MAX_OUTPUT_SIZE];
    port_float* input_ptr = inputs_list;
    port_float* output_ptr = buffer[0];
    int buffer_sweap = 0;
    // process each iir layer in the model
    for (uint32_t layer_idx = 0; layer_idx < model->num_rnn_layers;
         ++layer_idx) {
        LayerIIR* layer = (LayerIIR*)model->rnn_layers[layer_idx];
        LayerIIR_forward_once(layer, input_ptr, output_ptr);

        // Swap the input and output pointers
        input_ptr = output_ptr;
        output_ptr = buffer[++buffer_sweap % 2];
    }
    // Process each layer in the model
    for (uint32_t layer_idx = 0; layer_idx < model->num_layers; ++layer_idx) {
        LayerKAN_LUT* layer = (LayerKAN_LUT*)model->layers[layer_idx];
        // Forward pass through the current layer
        LayerKAN_LUT_forward_once(layer, input_ptr, output_ptr, use_lut);

        // Swap the input and output pointers
        input_ptr = output_ptr;
        if (layer_idx < model->num_layers - 2) {
            output_ptr = buffer[++buffer_sweap % 2];
        } else {
            output_ptr = outputs_list;
        }
    }
}

volatile uint32_t _v = 0;
int frikan_test() {
    port_float inputs_list1[] = 
        {
        -0.134608, -0.01416376,  0.09679188,  0.19213376,  0.27019358, 
        0.32785921,  0.36118882,  0.36900093,  0.34995077,  0.29789033, 
        0.2067393 ,  0.08077618, -0.06309036, -0.20268761, -0.31820919, 
        -0.39525722, -0.42567891, -0.40796613, -0.34648711, -0.25029685, 
        -0.13295631, -0.0111407 ,  0.10046783,  0.19420414,  0.26883797, 
        0.32472147,  0.36016445,  0.37106056,  0.35191118,  0.2971452 , 
        0.20412728,  0.07792265, -0.06632008, -0.20689891, -0.32267931, 
        -0.39880289, -0.42843426, -0.41100117, -0.34992405, -0.25315913, 
        -0.13486827, -0.01280301,  0.0986115 ,  0.19283346,  0.26915583, 
        0.32707076,  0.36322721,  0.37316656,  0.35334659,  0.29996581, 
        0.2092653 ,  0.08372725, -0.06189446, -0.20353328, -0.31827818, 
        -0.39247661, -0.42142594, -0.40460528, -0.34421664, -0.24830599, 
        -0.13201974, -0.0125216 ,  0.09793298,  0.19355139,  0.27134422, 
        0.32834067,  0.3621886 ,  0.37148351,  0.3531069 ,  0.3004344 , 
        0.20808154,  0.08069443, -0.06437274, -0.20434542, -0.31978812, 
        -0.39724535, -0.42858463, -0.41144096, -0.34965854, -0.25267806, 
        -0.13497723, -0.0138596 ,  0.09650853,  0.19026254,  0.26750817, 
        0.32706955,  0.36401957,  0.37366638,  0.35328408,  0.299023  , 
        0.20677396,  0.08006908, -0.06499275, -0.20509006, -0.31941217, 
        -0.39477089, -0.42485266, -0.40806042, -0.3473346 , -0.25152296
        };
    #define LEN_INPOUT (sizeof(inputs_list1) / sizeof(inputs_list1[0]))

    port_float output[LEN_INPOUT] = {0};
    int test_time = 10;
    ModelKAN_LUT_init(&ModelKAN_LUT_test);
    uint64_t start_time = port_get_tick_ms();
    for (int i = 0; i < test_time; i++) {
        _v++;
        ModelKAN_LUT_init(&ModelKAN_LUT_test);
        for (int k = 0; k < LEN_INPOUT; k++) {
            ModelKAN_LUT_forward_once(&ModelKAN_LUT_test, inputs_list1 + k,
                                      output + k, 0);
        }
    }
    uint64_t end_time = port_get_tick_ms();
    for (int k = 0; k < LEN_INPOUT; k++) {
        printf("FRIKAN(no lut): %f\r\n", output[k]);
    }
    port_float elapsed_time = (port_float)(end_time - start_time) / 1000;
    printf("Time taken %d times: %f seconds\r\n", test_time * LEN_INPOUT,
           elapsed_time);

    uint64_t start_time2 = port_get_tick_ms();
    for (int i = 0; i < test_time; i++) {
        _v++;
        ModelKAN_LUT_init(&ModelKAN_LUT_test);
        for (int k = 0; k < LEN_INPOUT; k++) {
            ModelKAN_LUT_forward_once(&ModelKAN_LUT_test, inputs_list1 + k,
                                      output + k, 1);
        }
    }
    uint64_t end_time2 = port_get_tick_ms();
    for (int k = 0; k < LEN_INPOUT; k++) {
        printf("FRIKAN(lut): %f\r\n", output[k]);
    }
    port_float elapsed_time2 = (port_float)(end_time2 - start_time2) / 1000;
    printf("Time taken %d times: %f seconds\r\n", test_time * LEN_INPOUT,
           elapsed_time2);
    return 0;
}
