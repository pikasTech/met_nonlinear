#ifndef __JIAN_BO_H
#define __JIAN_BO_H
#include "SG.h"
#include "SaoPin.h"
#include "contral.h"
void detection(Process_Config_t* config,
               float signal_source,
               float signal_target,
               struct SG* sg,
               struct SaoPin* scanner,
               int t,
               struct PID* pid_controler);
#endif
