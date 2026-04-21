#include "benchmark_keil_port.h"

#include "stm32f405xx.h"

#define BENCHMARK_USART_BRR_16MHZ 0x008BU
#define BENCHMARK_DEMCR_TRCENA (1UL << 24)
#define BENCHMARK_DWT_CTRL_CYCCNTENA (1UL << 0)

static uint32_t g_benchmark_keil_ready = 0U;

static void benchmark_enable_cycle_counter(void);
static void benchmark_gpio_config_usart(GPIO_TypeDef *gpio_port, uint32_t pin_index);
static void benchmark_uart_config(USART_TypeDef *usart_instance);
static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch);
static void benchmark_keil_write_string(const char *message);

void benchmark_keil_uart_init(void)
{
    if (g_benchmark_keil_ready == 0U) {
        benchmark_keil_platform_init();
    }
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
    return (uint64_t)(DWT->CYCCNT / 16U);
}

void benchmark_keil_platform_init(void)
{
    if (g_benchmark_keil_ready != 0U) {
        return;
    }

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    RCC->APB1ENR |= RCC_APB1ENR_USART3EN;
    __DSB();

    benchmark_gpio_config_usart(GPIOA, 9U);
    benchmark_gpio_config_usart(GPIOA, 10U);
    benchmark_gpio_config_usart(GPIOB, 10U);
    benchmark_gpio_config_usart(GPIOB, 11U);

    benchmark_uart_config(USART1);
    benchmark_uart_config(USART3);
    benchmark_enable_cycle_counter();

    g_benchmark_keil_ready = 1U;

    benchmark_keil_write_string("[  OK]: hardware init ok\r\n");
    benchmark_keil_write_string("[Info]: lean benchmark bring-up enabled\r\n");
    benchmark_keil_write_string("[Info]: UART1+UART3 mirrored at 115200 baud\r\n");
}

void Error_Handler(void)
{
    while (1) {
    }
}

static void benchmark_enable_cycle_counter(void)
{
    CoreDebug->DEMCR |= BENCHMARK_DEMCR_TRCENA;
    DWT->CYCCNT = 0U;
    DWT->CTRL |= BENCHMARK_DWT_CTRL_CYCCNTENA;
}

static void benchmark_gpio_config_usart(GPIO_TypeDef *gpio_port, uint32_t pin_index)
{
    uint32_t mode_shift = pin_index * 2U;
    uint32_t afr_index = pin_index >> 3U;
    uint32_t afr_shift = (pin_index & 7U) * 4U;

    gpio_port->MODER = (gpio_port->MODER & ~(3UL << mode_shift)) | (2UL << mode_shift);
    gpio_port->OSPEEDR = (gpio_port->OSPEEDR & ~(3UL << mode_shift)) | (3UL << mode_shift);
    gpio_port->OTYPER &= ~(1UL << pin_index);
    gpio_port->PUPDR = (gpio_port->PUPDR & ~(3UL << mode_shift)) | (1UL << mode_shift);
    gpio_port->AFR[afr_index] = (gpio_port->AFR[afr_index] & ~(0xFUL << afr_shift)) | (7UL << afr_shift);
}

static void benchmark_uart_config(USART_TypeDef *usart_instance)
{
    usart_instance->CR1 = 0U;
    usart_instance->CR2 = 0U;
    usart_instance->CR3 = 0U;
    usart_instance->BRR = BENCHMARK_USART_BRR_16MHZ;
    usart_instance->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch)
{
    while ((console_usart->SR & USART_SR_TXE) == 0U) {
    }
    console_usart->DR = (uint32_t)ch;
}

static void benchmark_keil_write_string(const char *message)
{
    while (*message != '\0') {
        benchmark_keil_uart_putc(*message++);
    }
}
