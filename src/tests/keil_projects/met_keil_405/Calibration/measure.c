#include "measure.h"

/* 更新信号的当前值和历史值 */

void updata_signal_buf(struct SIGNAL* p, float new_value) {
    int i;

    for (i = SIGNAL_VALUE_BUF_NUM - 1; i > 0; i--)  // 左移信号值的缓存区
    {
        (*p).last[i] = (*p).last[i - 1];
    }

    (*p).last[0] = new_value;  // 将新值存入缓存区
    (*p).now = (*p).last[0];   // last[0]即为当前值

    if ((*p).max < (*p).now) {
        (*p).max = (*p).now;
    }
}

/* 将周期信号调整到[-cycle/2,cycle/2] */

float cycle_value_adjust(float input, float cycle) {
    float output;
    if (input >= cycle / 2.0f)
        output = input - cycle;
    else if (input <= -cycle / 2.0f)
        output = input + cycle;
    return output;
}

/* 在周期信号中找到幅值最小的bios */

float get_cycle_bios_with_adjust(float goal,
                                 float now,
                                 float cycle,
                                 float d_t) {
    float output;
    float bios_0, bios_1, bios_2;
    float abs_0, abs_1, abs_2;

    bios_0 = goal - now;
    bios_1 = goal - now + cycle;
    bios_2 = goal - now - cycle;

    abs_0 = bios_0 * bios_0;
    abs_1 = bios_1 * bios_1;
    abs_2 = bios_2 * bios_2;

    if (abs_0 <= abs_1 && abs_0 <= abs_2)
        output = bios_0;
    else if (abs_1 <= abs_0 && abs_1 <= abs_2)
        output = bios_1;
    else
        output = bios_2;

    return output / d_t * 1000;
}

/* 将脉冲转化为角度制 */
float puls_to_angle_unit(float input, int puls_num) {
    float output;
    output = input * 360.f / (float)puls_num;
    return output;
}
