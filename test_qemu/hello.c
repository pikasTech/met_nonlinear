#include <stdint.h>

#define UART0_BASE 0x40004000u

#define UART_DATA (*(volatile uint32_t *)(UART0_BASE + 0x00u))
#define UART_STATE (*(volatile uint32_t *)(UART0_BASE + 0x04u))
#define UART_CTRL (*(volatile uint32_t *)(UART0_BASE + 0x08u))
#define UART_BAUDDIV (*(volatile uint32_t *)(UART0_BASE + 0x10u))

#define UART_STATE_TXFULL (1u << 0)
#define UART_CTRL_TX_EN (1u << 0)

static void uart_init(void)
{
    UART_BAUDDIV = 16u;
    UART_CTRL = UART_CTRL_TX_EN;
}

static void uart_putc(char ch)
{
    while ((UART_STATE & UART_STATE_TXFULL) != 0u) {
    }

    UART_DATA = (uint32_t)ch;
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