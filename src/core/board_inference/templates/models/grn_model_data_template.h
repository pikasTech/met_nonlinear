#ifndef GENERATED_GRN_MODEL_DATA_H
#define GENERATED_GRN_MODEL_DATA_H

#include <stdint.h>

typedef float port_float;

#define GRU_INPUT_DIM {{GRU_INPUT_DIM}}u
#define GRU_UNITS {{GRU_UNITS}}u
#define DENSE_UNITS {{DENSE_UNITS}}u
#define OUTPUT_UNITS {{OUTPUT_UNITS}}u
#define BENCHMARK_ITERATIONS {{BENCHMARK_ITERATIONS}}u
#define BENCHMARK_REPEAT_RUNS {{BENCHMARK_REPEAT_RUNS}}u
#define BENCHMARK_RESET_STATE_EACH_RUN {{BENCHMARK_RESET_STATE_EACH_RUN}}u
#define VALIDATION_RECORD_COUNT {{VALIDATION_RECORD_COUNT}}u
#define VALIDATION_SEQ_LEN {{VALIDATION_SEQ_LEN}}u

#define SCALER_INPUT_DATA_RANGE {{SCALER_INPUT_DATA_RANGE}}
#define SCALER_OUTPUT_DATA_RANGE {{SCALER_OUTPUT_DATA_RANGE}}

static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][GRU_INPUT_DIM] = {{VALIDATION_INPUT_INITIALIZER}};

static const port_float gru_kernel[GRU_INPUT_DIM][GRU_UNITS * 3u] = {{GRU_KERNEL_INITIALIZER}};

static const port_float gru_recurrent_kernel[GRU_UNITS][GRU_UNITS * 3u] = {{GRU_RECURRENT_KERNEL_INITIALIZER}};

static const port_float gru_input_bias[GRU_UNITS * 3u] = {{GRU_INPUT_BIAS_INITIALIZER}};

static const port_float gru_recurrent_bias[GRU_UNITS * 3u] = {{GRU_RECURRENT_BIAS_INITIALIZER}};

static const port_float dense_kernel[GRU_UNITS][DENSE_UNITS] = {{DENSE_KERNEL_INITIALIZER}};

static const port_float dense_bias[DENSE_UNITS] = {{DENSE_BIAS_INITIALIZER}};

static const port_float output_kernel[DENSE_UNITS][OUTPUT_UNITS] = {{OUTPUT_KERNEL_INITIALIZER}};

static const port_float output_bias[OUTPUT_UNITS] = {{OUTPUT_BIAS_INITIALIZER}};

#endif
