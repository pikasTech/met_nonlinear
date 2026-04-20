#include "MET_Process.h"
#include "MET_Scanner.h"
#include "process.h"

/* extern global */
extern Process_Config_t g_process_config;

void MET_Process_disableWp(PikaObj *self){
}
void MET_Process_enableWp(PikaObj *self){
}

extern struct SaoPin saoPin;

void MET_Scanner_enable(PikaObj *self){
    saoPin.Enable = 1;
}

void MET_Scanner_rebootAfterScanEnable(PikaObj *self){
	  saoPin.reboot_after_scan = 1;
}

void MET_Scanner_setContinue(PikaObj *self, int val){
	  saoPin.conti = val;
}

