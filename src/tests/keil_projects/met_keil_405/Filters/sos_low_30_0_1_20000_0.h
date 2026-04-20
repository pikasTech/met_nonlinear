#ifndef _SOS_LOW_30_0_1_20000_0_H_
#define _SOS_LOW_30_0_1_20000_0_H_

#include "sos_filter.h"

/*
 * Generated with the following command:
 *   python sos_generator.py low 30 1 20000
 * Filter type: low
 * Cutoff frequency: 30.0
 * Order: 1
 * Sampling frequency: 20000.0
 * SOS coefficients:
 * 0.004690321081766101601884, 0.004690321081766101601884, 0.000000000000000000000000, 1.000000000000000000000000, -0.990619357836467706590611, 0.000000000000000000000000
 */

static SOSFilter* sos_create_sos_low_30_0_1_20000_0(void) {
    double sos_coefficients[] = {
        0.004690321081766101601884, 0.004690321081766101601884, 0.000000000000000000000000, 1.000000000000000000000000, -0.990619357836467706590611, 0.000000000000000000000000,
    };
    int num_sections = 1;
    return sos_create(sos_coefficients, num_sections);
}

#endif  // _SOS_LOW_30_0_1_20000_0_H_
