#include "main.h"
#include "calibration_port.h"
#include "SG.h"
#include "dac.h"

/* global value */
DMA_HandleTypeDef hdma_adc1;

extern Process_Config_t g_process_config;
u8 calibration_main_handler(Process_Config_t* config);

static void calibration_thread_entry(void *parameter){
    while(1){
        calibration_main_handler(&g_process_config);
    }
}

void sg_enable_hook(int Ena){

}

void MX_ADC1_Init(void);
void MX_DMA_Init(void);

void calibration_init_port_hardware(void){

}

int port_calibartion_init(void){
    printf("[info] calibration init\r\n");
		calibration_init(&g_process_config);
    return 0;
}

/* tick */
uint64_t calibration_get_tick_ns(void) {
    return user_tim3_get_tick_ns();
}


uint64_t calibration_get_tick_ms(void) {
    return calibration_get_tick_us() / 1000ULL;
}

uint64_t calibration_get_tick_s(void) {
    return calibration_get_tick_ms() / 1000ULL;
}

/* DAC port */
void calibration_output_ceil(float val){
    DAC1_Set_Vol(val);
}

void calibration_output_val(float val){
    DAC2_Set_Vol(val);
}


u8 calibration_main_handler(Process_Config_t* config);

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc){
	
}


#define USING_HEAP 1
/* ADC init */
uint16_t adcBuffer_[2] = {0};

extern struct SG sg;

float calibration_target_get_val(void){
#if CONF_TEST_TARGET_INNER
    return sg.test;
#elif CONF_TEST_TARGET_CH1
    return (float)adcBuffer_[0] / 4096.0f * 3.3f;
#elif CONF_TEST_TARGET_CH2
    return (float)adcBuffer_[1] / 65535.0f * 3.3f;
#endif
}

float calibration_source_get_val(void){
#if CONF_TEST_SOURCE_INNER
    return sg.test;
#elif CONF_TEST_SOURCE_CH1
    return (float)adcBuffer[0] / 65535.0f * 3.3f;
#elif CONF_TEST_SOURCE_CH2
    return (float)adcBuffer[1] / 65535.0f * 3.3f;
#endif
}

void calibration_row_output(uint8_t* data, size_t size){
    LL_DMA_ConfigAddresses(DMA1, LL_DMA_STREAM_3, (uint32_t)data,
                           (uint32_t)&USART3->DR, LL_DMA_DIRECTION_MEMORY_TO_PERIPH);
    LL_DMA_SetDataLength(DMA1, LL_DMA_STREAM_3, size);
    LL_USART_EnableDMAReq_TX(USART3);
    LL_DMA_ClearFlag_TC3(DMA1);
    LL_DMA_EnableStream(DMA1, LL_DMA_STREAM_3);
}
