#ifndef _FRIKAN_H_
#define _FRIKAN_H_
#include <stdint.h>
#include "port.h"

#define IIR_MAX_ORDER 10
typedef struct KAN_LUT {
    uint32_t grid_size;
    uint32_t spline_order;
    port_float grid_range[2];
    const port_float* grid;
    const port_float* spline_kernel;
    uint32_t lut_points;
    const port_float* lut;
} KAN_LUT;

typedef struct LayerKAN_LUT {
    uint32_t in_size;
    uint32_t out_size;
    uint32_t spline_kernel_size;
    const KAN_LUT** kan_luts;
} LayerKAN_LUT;

typedef struct IIR {
    int order;
    const port_float* a;
    const port_float* b;
    port_float x[IIR_MAX_ORDER + 1];
    port_float y[IIR_MAX_ORDER + 1];
} IIR;

typedef struct LayerIIR {
    int in_size;
    int out_size;
    int order;
    const IIR** iirs;
} LayerIIR;

typedef struct ModelKAN_LUT {
    uint32_t num_layers;
    const LayerKAN_LUT** layers;
    uint32_t num_rnn_layers;
    const LayerIIR** rnn_layers;
} ModelKAN_LUT;

#endif