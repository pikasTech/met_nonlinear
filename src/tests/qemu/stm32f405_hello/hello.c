#include <stdint.h>

#define RCC_BASE 0x40023800u
#define USART1_BASE 0x40011000u

#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))

#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

int main(void)
{
    uart_init();
    uart_puts("Hello World!\n");

    while (1) {
    }
}