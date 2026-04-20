#ifndef __PROCESS_H

#define __PROCESS_H

#include "SaoPin.h"
#include "arm_const_structs.h"
#include "arm_math.h"
#include "calibration_port.h"
#include "SG.h"
#include "user_config.h"
#include "sos_filter.h"
#include "calibration_typedef.h"

extern struct SG sg;
extern struct SaoPin saoPin;

u8 calibration_main_handler(Process_Config_t* config);
void calibration_init(Process_Config_t* config);
void calibration_init_port_hardware(void);
CalibrationChannel* CalibrationChannel_create(float (*fn_input)(void));
void CalibrationChannel_adjust_offset(CalibrationChannel* ch);
void CalibrationChannel_main_handler(CalibrationChannel* ch);

#endif
