#ifndef _NN_PORT_H_
#define _NN_PORT_H_
#include <stdint.h>
#ifdef _WIN32
#include <time.h>
#endif

#define port_float float

uint64_t port_get_tick_ms(void);

#ifdef _WIN32
static inline uint64_t port_get_tick_ms(void) {
    return (uint64_t)clock();
}
#endif
#endif
