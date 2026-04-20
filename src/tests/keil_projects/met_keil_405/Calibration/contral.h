#ifndef __CONTRAL_H
#define __CONTRAL_H
#include "measure.h"
#include <stdint.h>

void contral_fun_1(void);

struct STATE_SPACE {
    float A;
    float B;
    float x;
    float r;

    float output;
};

struct PID {
    int Enable;

    float goal;
    float now;

    struct SIGNAL p;
    float i;
    struct SIGNAL d;

    float diff;

    float kp;
    float ki;
    float kd;

    struct SIGNAL d_low;

    float avr_n_d;
    float avr_d;

    float ki_last;

    float output;
    float start;

    float A;
		
		uint64_t tick;
};

struct TURN {
    struct PID pid;
    float output_maped_positive;
    float output_maped_nagetive;  // ӳ�������
};

extern struct TURN turn;

void pid_init(struct PID* pid);
void init_state_feedback(void);
float get_pid_output(struct PID* p, float now, float dt);
/* ����ֵ�޷� */


/* 绝对值限幅 */

static inline float XianFu(float input, float fuzhi) {
    float output;

    if (input > fuzhi) {
        output = fuzhi;
    }

    else if (input < -fuzhi) {
        output = -fuzhi;
    }

    else {
        output = input;
    }

    return output;
}

#endif
