#include "jian_bo.h"
#include "SG.h"
#include "TD.h"
#include "contral.h"
#include "process.h"
#include "SaoPin.h"
#include "sos_filter.h"
#include "user_config.h"

#ifndef LINUX
#include "arm_const_structs.h"
#include "arm_math.h"
#endif
#ifdef LINUX
#include <math.h>
#include <stdio.h>
#endif

extern SaoPinItem g_saoPinItems[];

extern SOSFilterItem g_detectorFilterItems[];
extern SOSFilterItem g_detectorFilterItems2[];

extern SOSFilterItem* g_detectorFilterInUse;
extern SOSFilterItem* g_detectorFilterInUse2;

extern  CalibrationChannel* g_ch1;
extern  CalibrationChannel* g_ch2;

void rectifySignal(float signal_target, float* signal_target_abs) {
    // 全波整流
#ifndef LINUX
    /* use the arm dsp */
    arm_abs_f32(&signal_target, signal_target_abs, 1);
#endif
#ifdef LINUX
    /* use soft dsp */
    signal_target_abs = my_abs(IN_AC);
#endif
}

void detection(Process_Config_t* config,
               float signal_source,
               float signal_target,
               struct SG* sg,
               struct SaoPin* scanner,
               int t,
               struct PID* pid_controler){
#define my_t (calibration_get_tick_ms() / 10)
#define sp (*scanner)
#if DETECTION_SIGNAL_PROCESS_ENABLE
    /******************幅度、相位检波******************/
    /*********配置检波器的输入输出**********/
    // 整流
    float signal_target_abs;
    rectifySignal(signal_target, &signal_target_abs);
    float signal_source_abs;
    rectifySignal(signal_source, &signal_source_abs);

    // 相位检波
    sp.s_AB = signal_source * signal_target;
    average(sp.s_AB, &sp.M, &sp.M_n);
    average(sp.M, &sp.M_2, &sp.M_n_2);

    // 有效值检波 - 被测量
    average(signal_target_abs / 0.637087f, &sp.W_target, &sp.W_target_n);
    average(sp.W_target, &sp.W_target_2, &sp.W_target_n_2);
		
    // 有效值检波 - 激励源
    average(signal_source_abs / 0.637087f, &sp.W_source, &sp.W_source_n);
    average(sp.W_source, &sp.W_source_2, &sp.W_source_n_2);
#endif
    // 扫频使能
    if (sp.Enable) {
        sp.t = my_t - sp.t0;

        // 控制测试信号振幅
        do {
            /* 自动校准偏置时线圈驱动信号关闭 */
            if (sp.get_offset) {
                sg->test = 0;
                break;
						}
            /* 淡入 */
            if (sp.t < sp.delay * CONF_TEST_FADE_RANGE) {
                /* 平缓增大测试信号幅度 */
                sg->A = (sp.t / (sp.delay * CONF_TEST_FADE_RANGE)) *
                        g_saoPinItems[sp.i].a;
                break;
            }
            /* 淡出 */
            if (sp.t > sp.delay &&
                sp.t < sp.delay * (1 + CONF_TEST_FADE_RANGE)) {
                /* 平缓减小测试信号幅度 */
                sg->A = ((sp.delay * (1 + CONF_TEST_FADE_RANGE) - sp.t) /
                         (sp.delay * CONF_TEST_FADE_RANGE)) *
                        g_saoPinItems[sp.i].a;

                break;
            }
        } while (0);

        /* 自动校准输入偏置 */
        if (sp.get_offset) {
            CalibrationChannel_adjust_offset(g_ch1);
            CalibrationChannel_adjust_offset(g_ch2);
        }

#if DETECTION_SIGNAL_PROCESS_ENABLE
        /***********第一次检波************/
        if (sp.t > sp.delay * CONF_TEST_FADE_RANGE &&
            sp.t < sp.delay * (1.0f / 2.0f)) {
            sp.W_target_n = 0;
            sp.W_source_n = 0;
            sp.M_n = 0;
        }
        /*********第二次检波****************/
        if (sp.t < sp.delay * (2.0f / 3.0f)) {
            sp.W_target_n_2 = 0;
            sp.W_source_n_2 = 0;
            sp.M_n_2 = 0;
        }
#endif
        /*********** ROW OUTPUT **********/
        if ((sp.start == 0) && (sp.get_offset == 0) && (sp.t > sp.delay * CONF_TEST_FADE_RANGE) && (sp.t < sp.delay)){
            config->raw_output = 1;
        }else{
            config->raw_output = 0;
        }

        /*********扫频启动(重启)**********/
        if (sp.start) {
            calibration_printf(
                "\r\n\r\n====================== start self test "
                "======================\r\n");
            sp.get_offset = 1;  // 测量直流偏置
            sp.start = 0;
            sg_enable(sg, 1);
            sp.i = 0;
            sp.W_target_n = 0;
            sp.W_target_n_2 = 0;
            sp.M_n = 0;
            sp.t0 = my_t;
            sg->f = 1;
            sg->A = 0;
            sp.delay = CONF_SCAN_OFFSET_TEST_DURATION_10MS;
            SaoPin_cleanResult();
            return;
        }

#if DETECTION_SIGNAL_PROCESS_ENABLE
        if ((!sp.get_offset) && (sp.t > sp.delay) &&
            (g_saoPinItems[sp.i].collected == 0)) {
            /* 在采样周期的末尾进行数据收集 */
            g_saoPinItems[sp.i].g = sp.W_target_2;
            g_saoPinItems[sp.i].r = sp.W_target_2 / sp.W_source_2 / sg->A_post;
            g_saoPinItems[sp.i].phase =
                180 / 3.1415 * acos(2 * sp.M_2 / (sg->A * sp.W_target_2));
            g_saoPinItems[sp.i].collected = 1;
        }
#endif
        if (sp.t > sp.delay * (1 + CONF_TEST_FADE_RANGE)) {
            /* 切换到下一个频点 */
            // 复位
            sp.W_target_n = 0;
            sp.W_target_n_2 = 0;
            sp.M_n = 0;
            sp.M_n_2 = 0;
            sp.t0 = my_t;
            if (!sp.get_offset) {
#if !CONF_USING_UART_RAW_OUTPUT
                if ((*pid_controler).Enable) {
                    printf("%f\t%f\t%f\t%f\t%f\t%f\r\n", g_saoPinItems[sp.i].w,
                           g_saoPinItems[sp.i].r, g_saoPinItems[sp.i].phase,
                           g_saoPinItems[sp.i].g,
                           (*pid_controler).kp * (*pid_controler).A,
                           (*pid_controler).kd * (*pid_controler).A);
                } else {
                    printf("%f\t%f\t%f\t%f\t%f\t%f\r\n", g_saoPinItems[sp.i].w,
                           g_saoPinItems[sp.i].r, g_saoPinItems[sp.i].phase,
                           g_saoPinItems[sp.i].g, 0.0f, 0.0f);
                }
#else
                printf("\r\n```\r\nver=1,ctl=end\r\n```\r\n");
#endif
            }
            /* 扫完一个频点，但还未扫完一轮(例如 0.1Hz-150Hz是一轮) */
            if (sp.i < SaoPin_getNum() - 1) {
                if (!sp.get_offset) {
                    sp.i++;
                }
                /* 切换信号发生器给出的频率， 频率表在sp.w里面 */
                sg->f = g_saoPinItems[sp.i].w;
                /* 切换选频滤波器 */
                g_detectorFilterInUse = sos_find(g_detectorFilterItems, sg->f);
                g_detectorFilterInUse2 = sos_find(g_detectorFilterItems2, sg->f);
                /* delay是每个频点的扫描时间，随着频率会调整 */
                sp.delay = 3 * 100 / sg->f + CONF_SCAN_DELAY_MIN_10MS;
#if CONF_USING_UART_RAW_OUTPUT
                printf("\r\n```\r\nver=1,freq=%f\r\n```\r\n", g_saoPinItems[sp.i].w);
#endif
            }
            /* 已经扫完一轮了 */
            else {
                printf(
                    "====================== end self test "
                    "======================\r\n");
                /* 复位到刚开始的阶段 */
                sp.start = 1;
                sg_enable(sg, 0);
                /* continue标志，决定是否继续扫频 */
                if (!sp.conti) {
                    /* continue为0时，关闭扫频 */
                    sp.Enable = 0;
                    if (sp.reboot_after_scan) {
                        NVIC_SystemReset();
                    }
                }
                /* sp.add 为1时，在下一轮调整反馈参数 */
                if (sp.add) {
                    /* kp 从初始遍历到0.1(结束的位置，可以调整） */
                    if ((*pid_controler).kp < 0.1f) {
                        /* 每次增加的步长,可以调整 */
                        (*pid_controler).kp += 0.01f;
                    }
                    /* config step of kd */
                    else {
                        /* kp 回到的位置 */
                        (*pid_controler).kp = 0;
                        /* kd 增加的步长 */
                        (*pid_controler).kd += 0.005f;
                    }
                }
            }
            /* exit from auto adjust the offset */
            sp.get_offset = 0;
        }
    }
}
