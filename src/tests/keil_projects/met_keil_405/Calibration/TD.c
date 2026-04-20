#include "TD.h"
#ifndef LINUX
#include "arm_const_structs.h"
#include "arm_math.h"
#include "calibration_port.h"
#endif
#ifdef LINUX
#include <math.h>
#include "config.h"
#endif
float r1;
float r2;
float kh = 2;
float r = 10 * CaoYangLv * 1000;
float h;
float A = 1;

float my_abs(float x) {
    if (x > 0)
        return x;
    else
        return -x;
}

int my_sign(float x) {
    if (x >= 0)
        return 1;
    else
        return -1;
}

float my_sqrt(float x) {
    float result;
#ifndef LINUX
    arm_sqrt_f32(x, &result);
#endif
#ifdef LINUX
    result = sqrt(x);
#endif
    return result;
}

float fst(float x1, float x2, float r, float h) {
    float a;
    float y = x1 + h * x2;
    float d = r * h;
    float d0 = h * d;
    float a0;
    float fsn;
    a0 = my_sqrt(d * d + 8 * r * my_abs(y));

    if (my_sqrt(y) > d0) {
        a = x2 + (a0 - d) / 2 * my_sign(y);
    }

    else {
        a = x2 + y / h;
    }

    if (my_abs(a) > d) {
        fsn = -1 * r * my_sign(a);
    }

    else {
        fsn = -1 * r * a / d;
    }

    return fsn;
}

float my_diff(float v) {
    float T = 1.0f / (CaoYangLv * 1000);

    h = kh * T;

    r2 = r2 + T * fst(r1 - v, r2, r, h);
    r1 = r1 + T * r2;

    return A * r2;
}
