#include "MET_SignalGenerator.h"
#include "process.h"

void MET_SignalGenerator_disable(PikaObj *self){
    sg.Ena = 0;
}
void MET_SignalGenerator_enable(PikaObj *self){
    sg.Ena = 1;
}
void MET_SignalGenerator_setAmp(PikaObj *self, double A){
    sg.A = A;
}
void MET_SignalGenerator_setFre(PikaObj *self, double f){
    sg.f = f;
}
