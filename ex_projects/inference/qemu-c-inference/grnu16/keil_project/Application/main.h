#ifndef BENCHMARK_MAIN_H
#define BENCHMARK_MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include "stm32f4xx_hal.h"
#include "stm32f4xx_ll_bus.h"
#include "stm32f4xx_ll_cortex.h"
#include "stm32f4xx_ll_dma.h"
#include "stm32f4xx_ll_exti.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_pwr.h"
#include "stm32f4xx_ll_rcc.h"
#include "stm32f4xx_ll_system.h"
#include "stm32f4xx_ll_usart.h"
#include "stm32f4xx_ll_utils.h"
#include "user_config.h"

extern uint64_t g_tim3_tick_ms;
uint64_t met_tim3_get_tick_us(void);
uint64_t met_tim3_get_tick_ns(void);

void Error_Handler(void);

#ifdef __cplusplus
}
#endif

#endif
