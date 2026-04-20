#include "w_fb.h"
#include "contral.h"
#include "process.h"

float Wfb_get_output(float in, int dt, struct PID* pid)  // 获得Wfb环节的输出值
{
    uint64_t tic = calibration_get_tick_us();
    float out = 0;
    out = 0;  // 初始化线圈力输出
    pid->now = in;
    out += get_pid_output(pid, pid->now, dt / 1000.0f);  // pid控制器
    uint64_t toc = calibration_get_tick_us();
    pid->tick = toc - tic;
    return out;
}
