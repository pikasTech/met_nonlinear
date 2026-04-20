#include "SG.h"
#ifndef LINUX
#include "arm_const_structs.h"
#include "arm_math.h"
#include "calibration_port.h"
#include "process.h"
#endif
#ifdef LINUX
#include "math.h"
#endif

float sg_get(struct SG* sg, long int t, long int t0) {
		sg->n++;
    uint64_t tic = calibration_get_tick_us();
    sg->T = 1.0f / sg->f;
    sg->w = 2.0f * pi / sg->T;
#ifndef LINUX

    uint64_t tick_us = calibration_get_tick_us();

    // Calculate the number of nanoseconds in a full sin cycle
    uint64_t period_us = 1000000ULL / sg->f;

    // Use integer modulus to get the time within the current cycle
    uint64_t time_in_period_us = (uint64_t)(tick_us - saoPin.t0) % period_us;
		float x = sg->w * (time_in_period_us)/1000000.0f;
		sg->test =
        sg->A * arm_sin_f32(x);
#endif
#ifdef LINUX
    sg->test = sg->A * sin(sg->w * ((t - t0) / 100.0f));
#endif
    sg->out = sg->test;
    uint64_t toc = calibration_get_tick_us();
    sg->tick = toc - tic;
    if (sg->Ena) {
        return sg->out;
    } else {
        return 0;
    }
}

PIKA_WEAK void sg_enable_hook(int Ena){
		return;
}

void sg_enable(struct SG* sg, int Ena){
    sg->Ena = Ena;
    sg_enable_hook(Ena);
}


void sg_init(struct SG* sg) {
    (*sg).f = 1.0f;    // 频率
    (*sg).A = 0.0f;    // 幅值
    // sg_enable(sg, 0);
    sg_enable(sg, 1);
    (*sg).A_post = 1;  // 后置功放的增益，默认1是不带功放
}
