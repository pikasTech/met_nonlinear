#include "SaoPin.h"

SaoPinItem g_saoPinItems[] = {
#define _SCAN_TEMPLATE_ARRAY
#include "scan_table.h"
};

#define SAO_PIN_NUM (sizeof(g_saoPinItems) / sizeof(SaoPinItem))

void SaoPin_init(struct SaoPin* sp) {
    (*sp).start = 1;
    (*sp).avr_a = 0.00001f;
    (*sp).W_a = 0.00001f;
    (*sp).delay = 1000;
    (*sp).t0 = 0;
    (*sp).conti = 1;
    (*sp).add = 0;
    (*sp).t = 0;
    (*sp).i = 0;
    (*sp).reboot_after_scan = 0;

    /* 振幅增强 */
    for (int i = 0; i < SAO_PIN_NUM; i++) {
        g_saoPinItems[i].a = g_saoPinItems[i].a * CONF_MAGNITUDE_COEFFICIENT;
    }

    
    /* 限制振幅不超过 0.5 */
    for (int i = 0; i < SAO_PIN_NUM; i++) {
        if (g_saoPinItems[i].a > CONF_SG_A_MAX) {
            g_saoPinItems[i].a = CONF_SG_A_MAX;
        }
    }

    
		#if 0
    if (CONF_MAGNITUDE_COEFFICIENT >= 2) {
        /* 小于10Hz的点振幅削减 */
        for (int i = 0; i < SAO_PIN_NUM; i++) {
            if (g_saoPinItems[i].w < 10) {
                g_saoPinItems[i].a *= 0.2;
            }
        }
    }
		#endif
}

int SaoPin_getNum(void) {
    return SAO_PIN_NUM;
}

void SaoPin_cleanResult(void) {
    for (int i = 0; i < SAO_PIN_NUM; i++) {
        g_saoPinItems[i].collected = 0;
        g_saoPinItems[i].g = 0;
        g_saoPinItems[i].phase = 0;
        g_saoPinItems[i].r = 0;
    }
}
