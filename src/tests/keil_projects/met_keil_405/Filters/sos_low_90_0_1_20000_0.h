#ifndef _SOS_LOW_90_0_1_20000_0_H_
#define _SOS_LOW_90_0_1_20000_0_H_

#include "sos_filter.h"

/*
 * Generated with the following command:
 *   python sos_generator.py low 90 1 20000
 * Filter type: low
 * Cutoff frequency: 90.0
 * Order: 1
 * Sampling frequency: 20000.0
 * SOS coefficients:
 * 0.013941009325039813507296, 0.013941009325039813507296, 0.000000000000000000000000, 1.000000000000000000000000, -0.972117981349920334821491, 0.000000000000000000000000
 */

static SOSFilter* sos_create_sos_low_90_0_1_20000_0(void) {
    double sos_coefficients[] = {
        0.013941009325039813507296, 0.013941009325039813507296, 0.000000000000000000000000, 1.000000000000000000000000, -0.972117981349920334821491, 0.000000000000000000000000,
    };
    int num_sections = 1;
    return sos_create(sos_coefficients, num_sections);
}

#endif  // _SOS_LOW_90_0_1_20000_0_H_
