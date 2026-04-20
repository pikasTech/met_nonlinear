#ifndef _CALIBRATION_TYPEDEF_H_
#define _CALIBRATION_TYPEDEF_H_
#include <stdint.h>
#include "user_config.h"

/* 支持定点计算, 64 位定点 */
#define fix_Q 48
#define fix_K (1LL << (fix_Q - 1))
typedef int64_t fix_t;

typedef struct {
    filter_float b[3];
    filter_float a[3];
    filter_float x_history[2];
    filter_float y_history[2];
} SingleSOS;

typedef struct {
    SingleSOS* sos_filters;
    int num_sections;
		uint64_t tick;
} SOSFilter;

typedef SOSFilter* (*SOSFilterFactory)(void);
typedef struct {
    float centerFreq;
    SOSFilterFactory filterFactory;
    SOSFilter* filter;
} SOSFilterItem;

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;

typedef struct ADC_collect_t_ {
    int dt_ADC1, dt_ADC2, dt_ADC3, dt_all;
    float f_khz_all;
    int temp;
    float temp_avr;
    long int n;
    float res;
} ADC_collect_t;

typedef struct {
    float (*fn_input)(void);
    float dc;
    float dc_avr;
    float offset;
    float ac;
    float Wf_out;
    float Wp_out;
    float Wb_out;
    float Wdetect_out;
    SOSFilterItem** detectorFilterInUse_p;
} CalibrationChannel;

typedef struct Process_Config_t_ {
    int dt;
    uint64_t t;
    uint64_t t_last;
    uint64_t tick_sync;
    uint64_t tick_row;
    uint64_t tick_main_handle;
    uint64_t tick_detection;
    float f_khz;
    float output_amp;
    u8 is_use_power_amp;
    int process_freq_hz;
    int process_period_us;
    int process_free_us;
    int raw_output;
} Process_Config_t;

#endif
