#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port.h"
#include "lstm_test.h"
#include <stdint.h>
// sigmoid函数
port_float sigmoid(port_float x) {
    return 1.0f / (1 + expf(-x));
}

port_float silu(port_float x) {
    return x / (1.0f + expf(-x));
}

#define LSTM_NUM_UNITS \
    (sizeof(lstm_lstm_cell_kernel[0]) / sizeof(lstm_lstm_cell_kernel[0][0]) / 4)
#define LSTM_NUM_INPUTS \
    (sizeof(lstm_lstm_cell_kernel) / sizeof(lstm_lstm_cell_kernel[0]))

#define DENSE_INNER_NUM_UNITS \
    (sizeof(dense_kernel[0]) / sizeof(dense_kernel[0][0]))
#define DENSE_INNER_NUM_INPUTS (sizeof(dense_kernel) / sizeof(dense_kernel[0]))

#define DENSE_OUT_NUM_UNITS \
    (sizeof(dense_1_kernel[0]) / sizeof(dense_1_kernel[0][0]))
#define DENSE_OUT_NUM_INPUTS \
    (sizeof(dense_1_kernel) / sizeof(dense_1_kernel[0]))

typedef struct LSTM {
    port_float hidden_stat[LSTM_NUM_UNITS];
    port_float carry_stat[LSTM_NUM_UNITS];
    const port_float** weights;
    const port_float** rec_weights;
    const port_float* bias;
} LSTM;

// LSTM循环层前向算法函数
void recurrent_forward(port_float* x,
                       int seq_len,
                       const port_float** weights,
                       const port_float** rec_weights,
                       const port_float* bias,
                       port_float* hidden_stat,
                       port_float* carry_stat) {
    port_float h_tm1[LSTM_NUM_UNITS] = {0};
    port_float c_tm1[LSTM_NUM_UNITS] = {0};

    // 循环层按每一步骤计算
    int step = 0;
    for (; step < seq_len; step++) {
        port_float* fv = (port_float*)x + step * LSTM_NUM_INPUTS;
        memcpy(h_tm1, hidden_stat, sizeof(port_float) * LSTM_NUM_UNITS);
        memcpy(c_tm1, carry_stat, sizeof(port_float) * LSTM_NUM_UNITS);

        for (int j = 0; j < LSTM_NUM_UNITS; j++) {
            // 计算输入数据与各门的加权和部分
            port_float zi = 0.0, zf = 0.0, zc = 0.0, zo = 0.0;
            for (int k = 0; k < LSTM_NUM_INPUTS; k++) {
                zi +=
                    fv[k] * (((port_float*)weights +
                              k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 0]);
                zf +=
                    fv[k] * (((port_float*)weights +
                              k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 1]);
                zc +=
                    fv[k] * (((port_float*)weights +
                              k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 2]);
                zo +=
                    fv[k] * (((port_float*)weights +
                              k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 3]);
            }

            // 计算隐含状态与各门的加权和部分
            port_float ih = 0.0, fh = 0.0, ch = 0.0, oh = 0.0;
            for (int k = 0; k < LSTM_NUM_UNITS; k++) {
                ih += h_tm1[k] *
                      (((port_float*)rec_weights +
                        k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 0]);
                fh += h_tm1[k] *
                      (((port_float*)rec_weights +
                        k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 1]);
                ch += h_tm1[k] *
                      (((port_float*)rec_weights +
                        k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 2]);
                oh += h_tm1[k] *
                      (((port_float*)rec_weights +
                        k * LSTM_NUM_UNITS * 4)[j + LSTM_NUM_UNITS * 3]);
            }

            // 计算ifco的加权和
            zi += (ih + bias[j + LSTM_NUM_UNITS * 0]);
            zf += (fh + bias[j + LSTM_NUM_UNITS * 1]);
            zc += (ch + bias[j + LSTM_NUM_UNITS * 2]);
            zo += (oh + bias[j + LSTM_NUM_UNITS * 3]);

            // 计算各gate的值
            port_float i = tanhf(zi);
            port_float f = tanhf(zf);
            port_float c = f * c_tm1[j] + i * tanhf(zc);
            port_float o = tanhf(zo);
            port_float h = o * tanhf(c);

            //  更新隐藏状态和单元状态
            hidden_stat[j] = h;
            carry_stat[j] = c;
        }
    }
}

int LSTM_init(LSTM* lstm) {
    lstm->weights = (const port_float**)lstm_lstm_cell_kernel;
    lstm->rec_weights = (const port_float**)lstm_lstm_cell_recurrent_kernel;
    lstm->bias = lstm_lstm_cell_bias;
    memset(lstm->hidden_stat, 0, sizeof(lstm->hidden_stat));
    memset(lstm->carry_stat, 0, sizeof(lstm->carry_stat));
    return 0;
}

int LSTM_forward(LSTM* lstm, port_float* x, int seq_len) {
    recurrent_forward(x, seq_len, lstm->weights, lstm->rec_weights, lstm->bias,
                      lstm->hidden_stat, lstm->carry_stat);
    return 0;
}

/**@brief 全连接层前向算法函数 */
void dense_forward(port_float* x,
                   int input_len,
                   int units_num,
                   const port_float** weights,
                   const port_float* bias,
                   port_float* y) {
    port_float sum = 0;
    for (int k = 0; k < units_num; k++) {
        sum = 0;
        for (int j = 0; j < input_len; j++) {
            //    sum += (x[j] * (*((port_float*)weights+j*LSTM_NUM_UNITS+k)));
            sum += (x[j] * (((port_float*)weights + j * units_num)[k]));
        }
        y[k] = (port_float)silu(sum + bias[k]);
    }
}

volatile uint32_t _v2 = 0;
int lstm_test() {
    LSTM lstm;
    LSTM_init(&lstm);
    port_float x[4] = {0.1f, 0.2f, 0.3f, 0.4f};
    port_float dense_inner_relt[DENSE_INNER_NUM_UNITS];
    port_float dense_out_relt[DENSE_OUT_NUM_UNITS];
    int test_time = 1000;

    uint64_t start_time = port_get_tick_ms();
    for (int i = 0; i < test_time; i++) {
        _v2++;
        LSTM_forward(&lstm, x, 1);
        dense_forward(lstm.hidden_stat, DENSE_INNER_NUM_INPUTS,
                      DENSE_INNER_NUM_UNITS, (const port_float**)dense_kernel,
                      dense_bias, dense_inner_relt);
        dense_forward(dense_inner_relt, DENSE_OUT_NUM_UNITS,
                      DENSE_OUT_NUM_UNITS, (const port_float**)dense_1_kernel,
                      dense_1_bias, dense_out_relt);
    }
    uint64_t end_time = port_get_tick_ms();

    port_float elapsed_time = (port_float)(end_time - start_time) / 1000;

    printf("LSTM out: %f\r\n", dense_out_relt[0]);
    printf("LSTM Time taken %d times: %f seconds\r\n", test_time, elapsed_time);

    return 0;
}
