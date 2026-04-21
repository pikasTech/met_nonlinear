#ifndef _CALIBRATION_PORT_H_
#define _CALIBRATION_PORT_H_

#include <stdint.h>
#include "PikaObj.h"
#include "main.h"
#include "calibration_typedef.h"
#include "user_config.h"

#define CaoYangLv 19.0f

uint64_t user_tim3_get_tick_ns(void);
uint64_t calibration_get_tick_ns(void);
// uint64_t calibration_get_tick_us(void);
uint64_t calibration_get_tick_ms(void);
uint64_t calibration_get_tick_s(void);


extern uint64_t g_tim3_tick_ms;
extern uint64_t g_tim3_tick_us;
extern uint64_t g_tim3_tick_us_last;
extern TIM_HandleTypeDef htim3;

#define _tick_us_raw() (met_tim3_get_tick_us())

// #define calibration_get_tick_us _tick_us_raw

#ifndef calibration_get_tick_us
static inline uint64_t calibration_get_tick_us(void){
    uint64_t tmp_tick = _tick_us_raw(); 
    if(tmp_tick < g_tim3_tick_us_last) { 
        tmp_tick += 1000ULL; 
    } 
    g_tim3_tick_us = tmp_tick; 
    g_tim3_tick_us_last = g_tim3_tick_us; 
    return g_tim3_tick_us;
}
#endif

void calibration_output_ceil(float val);
void calibration_output_val(float val);

void calibration_row_output(uint8_t* data, size_t size);

float calibration_target_get_val(void);
float calibration_source_get_val(void);

int port_calibartion_init(void);

void calibration_init(Process_Config_t* config);
void calibration_init_port(Process_Config_t* config);
#define calibration_printf pika_platform_printf

#endif
