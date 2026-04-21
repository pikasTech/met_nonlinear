#include "benchmark_keil_port.h"

#include "gpio.h"
#include "tim.h"
#include "usart.h"

static void SystemClock_Config(void);
static void MX_DMA_Init(void);
static void SWITCH_GPIO_Init(void);
static void benchmark_keil_write_string(const char *message);
static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch);

void benchmark_keil_uart_init(void)
{
}

void benchmark_keil_uart_putc(char ch)
{
    if ((USART1->CR1 & USART_CR1_UE) != 0U) {
        benchmark_console_write_byte(USART1, (uint8_t)ch);
    }
    if ((USART3->CR1 & USART_CR1_UE) != 0U) {
        benchmark_console_write_byte(USART3, (uint8_t)ch);
    }
}

uint64_t benchmark_keil_get_tick_us(void)
{
    return met_tim3_get_tick_us();
}

void benchmark_keil_platform_init(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();
    SWITCH_GPIO_Init();
    MX_TIM3_Init();
    HAL_TIM_Base_Start_IT(&htim3);
    MX_USART1_UART_Init();
    MX_USART3_UART_Init();

    benchmark_keil_write_string("[  OK]: hardware init ok\r\n");
    benchmark_keil_write_string("[Info]: NN benchmark bring-up enabled\r\n");
    benchmark_keil_write_string("[Info]: UART1+UART3 mirrored at 115200 baud\r\n");
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim == &htim3) {
        g_tim3_tick_ms++;
    }
}

void HAL_GPIO_EXTI_Callback(uint16_t gpio_pin)
{
    (void)gpio_pin;
}

void Error_Handler(void)
{
    while (1) {
    }
}

static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch)
{
    while (!LL_USART_IsActiveFlag_TXE(console_usart)) {
    }
    LL_USART_TransmitData8(console_usart, ch);
}

static void benchmark_keil_write_string(const char *message)
{
    while (*message != '\0') {
        benchmark_keil_uart_putc(*message++);
    }
}

static void MX_DMA_Init(void)
{
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_DMA1);
    NVIC_SetPriority(DMA1_Stream3_IRQn, NVIC_EncodePriority(NVIC_GetPriorityGrouping(), 0, 0));
    NVIC_EnableIRQ(DMA1_Stream3_IRQn);
}

static void SWITCH_GPIO_Init(void)
{
    GPIO_InitTypeDef gpio_init_struct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();

    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);

    gpio_init_struct.Pin = GPIO_PIN_2 | GPIO_PIN_3;
    gpio_init_struct.Mode = GPIO_MODE_OUTPUT_PP;
    gpio_init_struct.Pull = GPIO_NOPULL;
    gpio_init_struct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &gpio_init_struct);
}

static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef rcc_osc_init_struct = {0};
    RCC_ClkInitTypeDef rcc_clk_init_struct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    rcc_osc_init_struct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    rcc_osc_init_struct.HSEState = RCC_HSE_ON;
    rcc_osc_init_struct.PLL.PLLState = RCC_PLL_ON;
    rcc_osc_init_struct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    rcc_osc_init_struct.PLL.PLLM = 4;
    rcc_osc_init_struct.PLL.PLLN = 168;
    rcc_osc_init_struct.PLL.PLLP = RCC_PLLP_DIV2;
    rcc_osc_init_struct.PLL.PLLQ = 4;
    if (HAL_RCC_OscConfig(&rcc_osc_init_struct) != HAL_OK) {
        Error_Handler();
    }

    rcc_clk_init_struct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                    RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    rcc_clk_init_struct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    rcc_clk_init_struct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    rcc_clk_init_struct.APB1CLKDivider = RCC_HCLK_DIV4;
    rcc_clk_init_struct.APB2CLKDivider = RCC_HCLK_DIV2;

    if (HAL_RCC_ClockConfig(&rcc_clk_init_struct, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}
