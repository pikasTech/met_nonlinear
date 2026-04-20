#ifndef __SaoPin_H
#define __SaoPin_H

#ifndef LINUX
#include "main.h"
#endif

typedef struct SaoPinItem {
    volatile float w;
    volatile float a;
    volatile float r;
    volatile float phase;
    volatile float g;
    volatile int collected;
} SaoPinItem;

struct SaoPin {
    int Enable;
    int start;
    int state_n;
    float avr;
    float avr_a;

    uint64_t W_target_n;
    uint64_t W_target_n_2;
    float W_target;
    float W_target_2;
	
    uint64_t W_source_n;
    uint64_t W_source_n_2;
    float W_source;
    float W_source_2;

    float W_a;
    int i;
    float t0;
    float t;
    float delay;
    float comp;
    int conti;
    int add;

    float M;
    uint64_t M_n;

    float s_AB;
    float M_2;
    uint64_t M_n_2;
    float det_phy;

    int get_offset;
    int reboot_after_scan;
    int tick;
};

void SaoPin_init(struct SaoPin* sp);
int SaoPin_getNum(void);
void SaoPin_cleanResult(void);

static inline float average(float input, float* output, uint64_t* n) {
    (*n)++;
    (*output) = (*output) * ((*n) - 1) / (*n) + input / (*n);  // ??????
    return *output;
}

#endif
