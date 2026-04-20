#include "process.h"
#include "jian_bo.h"
#include "sos_filter.h"
#include "sos_low_10_0_1_20000_0.h"
#include "sos_low_1_0_1_20000_0.h"
#include "sos_low_20_0_1_20000_0.h"
#include "sos_low_30_0_1_20000_0.h"
#include "sos_low_90_0_1_20000_0.h"
#include "sos_low_80_0_4_20000_0.h"
#include "sos_low_60_0_4_20000_0.h"
#include "sos_low_40_0_4_20000_0.h"
#include "sos_low_300_0_4_20000_0.h"
#include "sos_band_1_0_300_0_4_20000_0.h"
#include "sos_band_10_0_300_0_4_20000_0.h"


#include "user_config.h"
#include "w_fb.h"

#if CONF_WP_FILTER_FROM_SOS_COEFFICIENTS
static SOSFilter* sos_create_wp(void) {
#if CONF_WP_USE_SELECT
    double sos_coefficients[] = {1.000000000000000,  -1.988411797774249,
                                 0.989206762587646,  1.000000000000000,
                                 -1.956732578860067, 0.957514878357164};
		int num_sections = 1;
#elif CONF_WP_USE_MUTI
    double sos_coefficients[] = {1.000000000000000,  -1.987562825065961,
                                 0.988429669204976,  1.000000000000000,
                                 -1.955880565866274, 0.956733592288258,
																 0.403560164908043,  -0.391692948547899,
                                 0.000000000000000,  1.000000000000000,
                                 -0.988132783639856, 0.000000000000000};
		int num_sections = 2;
#else
    double sos_coefficients[] = {CONF_WP_SOS};
		int num_sections = 1;
#endif
    return sos_create(sos_coefficients, num_sections);
}
#endif

#if CONF_WB_FILTER_FROM_SOS_COEFFICIENTS
static SOSFilter* sos_create_wb(void) {
    double sos_coefficients[] = {CONF_WB_SOS};
    int num_sections = 1;
    return sos_create(sos_coefficients, num_sections);
}
#endif

struct SIGNAL sDAC_OUT;
float A_show = 0.1;
float ADC_IN_avr = 0;
struct SaoPin saoPin;
struct SG sg;

float offset_feedback = CONF_FEEDBACK_OFFSET;
uint64_t systime_tim2;
uint64_t systime_tim3;
float low_pass;
float high_pass;

float offset_output = CONF_OUTPUT_OFFSET;

ADC_collect_t ADC_collect;  // ADC采集相关
volatile struct PID DAC_pid;

/* Process config global struct */
volatile Process_Config_t g_process_config;

SOSFilterItem* g_detectorFilterInUse = NULL;
SOSFilterItem* g_detectorFilterInUse2 = NULL;

SOSFilter* g_sos_wf = NULL;
SOSFilter* g_sos_wp = NULL;
SOSFilter* g_sos_wb = NULL;

char g_raw_frame[6] = {0xAA, 0x04, 0x00, 0x00, 0x00, 0x00};

extern SOSFilterItem g_detectorFilterItems[];
extern SOSFilterItem g_detectorFilterItems2[];

volatile CalibrationChannel* g_ch1 = NULL;
volatile CalibrationChannel* g_ch2 = NULL;
void calibration_init(Process_Config_t* config) {
    calibration_init_port_hardware();
    sg_init(&sg);
    pid_init(&DAC_pid);
    SaoPin_init(&saoPin);
    memset(config, 0, sizeof(Process_Config_t));
    config->output_amp = CONF_OUTPUT_AMP;
    config->process_freq_hz = CONF_FREQ_HZ;
    config->process_period_us = 1000000.0 / config->process_freq_hz;
    config->raw_output = 0;

    g_sos_wf = CONF_WF_FILTER();
    g_sos_wp = CONF_WP_FILTER();
    g_sos_wb = CONF_WB_FILTER();

    FilterItems_init(g_detectorFilterItems);
    FilterItems_init(g_detectorFilterItems2);

    g_ch1 = CalibrationChannel_create(calibration_target_get_val);
    g_ch2 = CalibrationChannel_create(calibration_source_get_val);
    g_ch1->detectorFilterInUse_p = &g_detectorFilterInUse;
    g_ch2->detectorFilterInUse_p = &g_detectorFilterInUse2;

    DAC_pid.Enable = 1;
    DAC_pid.kd = CONF_PID_KD;
    DAC_pid.kp = CONF_PID_KP;
    DAC_pid.ki = CONF_PID_KI;
    saoPin.Enable = CONF_SELF_TEST_ON_BOOT;
#if CONF_SELF_TEST_ON_BOOT
    printf("[Info] start self test after boot\r\n");
#endif
		saoPin.conti = CONF_SELF_TEST_ON_CONTINUE;
#if CONF_SELF_TEST_ON_CONTINUE
    printf("[Info]: self test continue after finished\r\n");
#endif
}

static inline float detection_filter(SOSFilterItem* filterItem, float input) {
    float output;
    /* 选择检波的滤波模式 */
#if CONF_USING_SCAN_FILTTER_HIGH_LOW
    // 输出滤波——低通
    float low_pass = SOS_filter(input, &s1);
    // 输出滤波——高通
    float high_pass = SOS_filter(input, &s2);
    if (sg.f > 50) {
        // 高频检测时滤掉中低频噪声
        output = high_pass;
    } else {
        // 低频检测时滤掉高频噪声
        output = low_pass;
    }
#elif CONF_USING_SCAN_FILTTER_SELECT
    if (NULL == filterItem) {
        output = input;
    } else {
        output = sos_filter(filterItem->filter, input);
    }
#else
    output = input;
#endif
    return output;
}

void calibration_sync(Process_Config_t* config){
    /* sync for process frequency */
    uint64_t tick_now = calibration_get_tick_us();
    uint64_t tick_entry = tick_now;
    config->process_free_us =
        config->process_period_us - (tick_now - config->t_last);
    while (1) {
        tick_now = calibration_get_tick_us();
        if (tick_now - config->t_last >= config->process_period_us) {
            break;
        }
    }
    uint64_t tic = calibration_get_tick_us();
    config->t = tic;
    config->dt = config->t - config->t_last;
    if(config->dt < 0){
        printf("ERROR on tick\r\n");
    }
    config->t_last = config->t;
	
    /*计算采样率*/
    config->f_khz = config->f_khz * 0.99f + 1000 / (float)config->dt * 0.01f;
    uint64_t toc = calibration_get_tick_us();
    config->tick_sync = toc - tick_entry;
}

CalibrationChannel* CalibrationChannel_create(float (*fn_input)(void)){
    CalibrationChannel* ch = pika_platform_malloc(sizeof(CalibrationChannel));
    pika_platform_memset(ch, sizeof(CalibrationChannel), 0);
    ch->fn_input = fn_input;
    ch->offset = CONF_INPUT_OFFSET_DEFAULT;
    return ch;
};

void CalibrationChannel_main_handler(CalibrationChannel* ch){
    // 处理偏置
    ch->ac = (ch->dc - ch->offset);
    /* Wf */
#if CONF_WF_ENABLE
    ch->Wf_out = sos_filter(g_sos_wf, ch->ac);
#else
    /* not use Wf */
    ch->Wf_out = ch->ac;
#endif
#if CONF_WP_ENABLE
    ch->Wp_out = sos_filter(g_sos_wp, ch->Wf_out);
#else
    ch->Wp_out = ch->Wf_out;
#endif
#if CONF_WB_ENABLE
    ch->Wb_out = sos_filter(g_sos_wb, ch->Wp_out);
#else
    ch->Wb_out = ch->Wp_out;
#endif
    ch->Wdetect_out = detection_filter(*ch->detectorFilterInUse_p, ch->Wb_out);
}

void CalibrationChannel_adjust_offset(CalibrationChannel* ch){
    ch->offset = ch->offset * (1 - 0.0001f) + ch->dc_avr * 0.0001f;
}

u8 calibration_main_handler(Process_Config_t* config) {
    calibration_sync(config);
    uint64_t tic = calibration_get_tick_us();
    
    g_ch1->dc = g_ch1->fn_input();
    g_ch2->dc = g_ch2->fn_input();
    g_ch1->dc_avr = g_ch1->dc_avr * 0.999f + g_ch1->dc * 0.001f;
    g_ch2->dc_avr = g_ch2->dc_avr * 0.999f + g_ch2->dc * 0.001f;

/****************处理采集信号*************/
#if CONF_CH1_SIGNAL_PROCESS_ENABLE
    CalibrationChannel_main_handler(g_ch1);
#endif
#if CONF_CH2_SIGNAL_PROCESS_ENABLE
    CalibrationChannel_main_handler(g_ch2);
#endif
/*****************线圈驱动信号**************/
    float Wfb_in;
    float Wfb_out;
    Wfb_in = g_ch1->Wp_out;
    // 获得Wfb环节的输出值
    Wfb_out = Wfb_get_output(Wfb_in, config->dt, &DAC_pid);
    /* signal generator */
    // 获得信号发生器的输出值
    float sg_out = sg_get(&sg, 0, 0);
    /* output */
    // 线圈驱动的输出值
    float ceil_out = 0;
    /* signal generator output */
    ceil_out += sg_out;
    /* add feedback to output in nomal mode */
#if !CONF_TEST_TARGET_LOOP_GAIN_ENABLE
    /* feedback output */
    ceil_out += Wfb_out;
#endif
    /* limit */
    // 线圈力输出限幅
    // DAC 限幅
    float XianFu_val = 1.8f;
    ceil_out = XianFu(ceil_out, XianFu_val);
/****************数字输出*********************/
    uint64_t tic_send_row = calibration_get_tick_us();
    int16_t sg_val = (int16_t)((g_ch2->dc/3.3f*4096));
    g_raw_frame[2] = sg_val & 0xFF;
    g_raw_frame[3] = (sg_val >> 8) & 0xFF;
    int16_t adc_val = (int16_t)((g_ch1->dc/3.3f*4096));
    g_raw_frame[4] = adc_val & 0xFF;
    g_raw_frame[5] = (adc_val >> 8) & 0xFF;
#if CONF_USING_UART_RAW_OUTPUT
    if(config->raw_output){
        calibration_row_output((uint8_t*) g_raw_frame, sizeof(g_raw_frame));
    }
#endif
    config->tick_row = calibration_get_tick_us() - tic_send_row;
    /****************DAC 输出*********************/
    float signal_out;
    /* 传感器的对外输出信号 */
    signal_out = g_ch1->Wb_out;
    // 驱动线圈
    calibration_output_ceil((ceil_out + offset_feedback) * 1000);
    // 输出信号
    calibration_output_val((signal_out * config->output_amp + offset_output) * 1000);
    /* detection */
    /******************幅度、相位检波******************/

    /* 检波算法 */
    uint64_t tic_detection = calibration_get_tick_us();
    detection(config, g_ch2->Wdetect_out, g_ch1->Wdetect_out, &sg,
              &saoPin, 0, &DAC_pid);
    uint64_t toc = calibration_get_tick_us();
    config->tick_main_handle = toc - tic;
    config->tick_detection = toc - tic_detection;
    return 0;
}

extern UART_HandleTypeDef huart1;



