#ifndef _SOS_LOW_10_0_1_20000_0_H_
#define _SOS_LOW_10_0_1_20000_0_H_

#include "sos_filter.h"

/*
 * Generated with the following command:
 *   python sos_generator.py low 10 1 20000
 * Filter type: low
 * Cutoff frequency: 10.0
 * Order: 1
 * Sampling frequency: 20000.0
 * SOS coefficients:
 * 0.001568334083280984543249, 0.001568334083280984543249, 0.000000000000000000000000, 1.000000000000000000000000, -0.996863331833438004458969, 0.000000000000000000000000
 */

static SOSFilter* sos_create_sos_low_10_0_1_20000_0(void) {
    double sos_coefficients[] = {
        0.001568334083280984543249, 0.001568334083280984543249, 0.000000000000000000000000, 1.000000000000000000000000, -0.996863331833438004458969, 0.000000000000000000000000,
    };
    int num_sections = 1;
    return sos_create(sos_coefficients, num_sections);
}

#endif  // _SOS_LOW_10_0_1_20000_0_H_
