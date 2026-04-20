#include "main.h"
#include "SG.h"
#include "SaoPin.h"
#include "TD.h"
#include "adc.h"
#include "arm_const_structs.h"
#include "arm_math.h"
#include "dac.h"
#include "gpio.h"
#include "pikaScript.h"
#include "process.h"
#include "sos_filter.h"
#include "tim.h"
#include "usart.h"
#include "user_config.h"

#define UART_STDIO_UART1 0x00
#define UART_STDIO_UART3 0x01

#ifndef UART_STDIO
#define UART_STDIO UART_STDIO_UART3
#endif

void SystemClock_Config(void);

/* extern global */
extern Process_Config_t g_process_config;
extern SOSFilterItem g_detectorFilterItems[];
extern SOSFilterItem g_detectorFilterItems2[];
extern SOSFilter* g_sos_wf;


static void console_write_byte(USART_TypeDef* console_usart, uint8_t ch) {
    while (!LL_USART_IsActiveFlag_TXE(console_usart))
        ;
    LL_USART_TransmitData8(console_usart, ch);
}

int fputc(int ch, FILE* f) {
    (void)f;

    if ((USART1->CR1 & USART_CR1_UE) != 0U) {
        console_write_byte(USART1, (uint8_t)ch);
    }
    if ((USART3->CR1 & USART_CR1_UE) != 0U) {
        console_write_byte(USART3, (uint8_t)ch);
    }
    return ch;
}

volatile uint8_t RX_ch_buff[] = "";

char __platform_getchar(void) {
    /* wait rx char */
    HAL_UART_Receive(&huart1, (uint8_t*)RX_ch_buff, 1, 0xFFFFFFFF);
    /* recaved char */
    return RX_ch_buff[0];
}

#define NO_MAIN_LOOP 0

int64_t __platform_getTick(void) {
    return HAL_GetTick();
}

void SWITCH_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    /* GPIO Ports Clock Enable */
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /*Configure GPIO pin Output Level */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);

    /*Configure GPIO pin Output Level */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);

    /*Configure GPIO pin : PA2 PA3 */
    GPIO_InitStruct.Pin = GPIO_PIN_2 | GPIO_PIN_3;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

void MX_DMA_Init(void) {
    /* Init with LL driver */
    /* DMA controller clock enable */
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_DMA1);

    /* DMA interrupt init */
    /* DMA1_Stream3_IRQn interrupt configuration */
    NVIC_SetPriority(DMA1_Stream3_IRQn,
                     NVIC_EncodePriority(NVIC_GetPriorityGrouping(), 0, 0));
    NVIC_EnableIRQ(DMA1_Stream3_IRQn);
}

extern uint16_t adcBuffer_[2];
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    // 获得转换完成的ADC值并记录当前时间
    if (hadc == (&hadc1)) {
        adcBuffer_[0] = HAL_ADC_GetValue(&hadc1);
    } else if (hadc == (&hadc2)) {
        adcBuffer_[0] = HAL_ADC_GetValue(&hadc2);
    } else if (hadc == (&hadc3)) {
        adcBuffer_[0] = HAL_ADC_GetValue(&hadc3);
    }
    calibration_main_handler(&g_process_config);
}

int main_old(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();
    SWITCH_GPIO_Init();
#if UART_STDIO == UART_STDIO_UART3
    MX_USART3_UART_Init();
#elif UART_STDIO == UART_STDIO_UART1
    MX_USART1_UART_Init();
#else
#error "UART not supported"
#endif
    MX_ADC1_Init();
    MX_ADC2_Init();
    MX_ADC3_Init();
    MX_DAC_Init();
    MX_TIM3_Init();
    printf("[  OK]: hardware init ok\r\n");

    /* config */
    sg_init(&sg);
    pid_init(&DAC_pid);
    SaoPin_init(&saoPin);
    port_calibartion_init();
    FilterItems_init(g_detectorFilterItems);
    FilterItems_init(g_detectorFilterItems2);

    DAC_pid.Enable = 1;
    DAC_pid.kd = CONF_PID_KD;
    DAC_pid.kp = CONF_PID_KP;
    DAC_pid.ki = CONF_PID_KI;
#if 0
    printf("[Info]: loading python configure...\r\n");
    PikaObj* pikaMain = pikaScriptInit();
    int isLaunchShell = obj_getInt(pikaMain, "isLaunchShell");
    if (isLaunchShell) {
        pikaScriptShell(pikaMain);
    }
    obj_deinit(pikaMain);
    printf("[  OK]: configure finished. \r\n");
#endif
    printf("[Info]: In main process. \r\n");
    printf("-------------------------\r\n");

    saoPin.Enable = CONF_SELF_TEST_ON_BOOT;
#if CONF_SELF_TEST_ON_BOOT
    printf("[Info]: start self test after boot\r\n");
#endif

    saoPin.conti = CONF_SELF_TEST_ON_CONTINUE;
#if CONF_SELF_TEST_ON_CONTINUE
    printf("[Info]: self test continue after finished\r\n");
#endif
#if NO_MAIN_LOOP
    while (1) {
    }
#endif
    /* start main loop */
    HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
    HAL_DAC_Start(&hdac, DAC_CHANNEL_2);
    HAL_TIM_Base_Start_IT(&htim3);
    HAL_ADC_Start_IT(&hadc1);
    HAL_ADC_Start_IT(&hadc2);
    HAL_ADC_Start_IT(&hadc3);

    /* main loop is in process_main() */
    while (1) {
    }
}

uint64_t port_get_tick_ms(void){
    return calibration_get_tick_ms();
}
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    /* Keep the original board-side switch/DMA state so the serial path stays alive after reflashing. */
    MX_DMA_Init();
    SWITCH_GPIO_Init();
    MX_TIM3_Init();
    HAL_TIM_Base_Start_IT(&htim3);
    MX_USART1_UART_Init();
    MX_USART3_UART_Init();

    printf("[  OK]: hardware init ok\r\n");
    printf("[Info]: NN bring-up disabled, serial boot only\r\n");
    printf("[Info]: UART1+UART3 mirrored at %d baud\r\n", CONF_BAUDRATE);
    /* main loop is in process_main() */
    while (1) {
    }
}

void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    /** Configure the main internal regulator output voltage
     */
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
    /** Initializes the CPU, AHB and APB busses clocks
     */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 4;
    RCC_OscInitStruct.PLL.PLLN = 168;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ = 4;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }
    /** Initializes the CPU, AHB and APB busses clocks
     */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_12) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0, GPIO_PIN_RESET);
        DAC_pid.Enable = 0;
        sg.Ena = 1;
    }
    if (GPIO_Pin == GPIO_PIN_13) {
    }
    if (GPIO_Pin == GPIO_PIN_14) {
    }
    if (GPIO_Pin == GPIO_PIN_15) {
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef* htim) {
    if (htim == (&htim3)) {
        g_tim3_tick_ms++;
    }
}

void Error_Handler(void) {
    /* USER CODE BEGIN Error_Handler_Debug */
    /* User can add his own implementation to report the HAL error return state
     */

    /* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t* file, uint32_t line) {
    /* USER CODE BEGIN 6 */
    /* User can add his own implementation to report the file name and line
 number, tex: printf("Wrong parameters value: file %s on line %d\r\n", file,
 line) */
    /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
