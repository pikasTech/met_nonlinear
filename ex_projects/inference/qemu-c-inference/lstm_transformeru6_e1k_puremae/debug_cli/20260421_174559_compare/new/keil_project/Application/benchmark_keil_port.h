#ifndef BENCHMARK_KEIL_PORT_H
#define BENCHMARK_KEIL_PORT_H

#include "main.h"

void benchmark_keil_platform_init(void);
void benchmark_keil_uart_init(void);
void benchmark_keil_uart_putc(char ch);
uint64_t benchmark_keil_get_tick_us(void);

#endif
