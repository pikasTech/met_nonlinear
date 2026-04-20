#ifndef __SG_H
#define __SG_H
#ifndef LINUX
#include "calibration_port.h"
#endif
#ifdef LINUX

#endif
#define pi 3.1415926f

struct SG {
    volatile int Ena;  
    volatile float f;    
    volatile float T;    
    volatile float w;    
    volatile float A;    
    volatile float out;
    volatile float test;
    volatile float A_post; 
    volatile uint64_t tick;
		volatile uint64_t n;
};

float sg_get(struct SG* sg, long int t, long int t0);
void sg_enable(struct SG* sg, int Ena);
void sg_init(struct SG* sg);

#endif
		