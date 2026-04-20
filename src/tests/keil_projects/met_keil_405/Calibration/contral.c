#include "contral.h"
#include "TD.h"

#define USE_PID 1           /* PID速度环 */
#define USE_STATE_SPACE 1   /* 状态反馈 */
#define USE_TURN_SIMPLE 0   /* 线性PID差速环 */
#define USE_TURN_LINE_MAP 0 /* 乘积PID差速环 */

int i_contral_fun_1;

struct TURN turn;

/* 将input从[x1,x2]线性映射到[y1,y2] */

float line_map(float input, float x1, float x2, float y1, float y2) {
    float output;
    float k;

    k = (y2 - y1) / (x2 - x1);

    output = y1 + k * (input - x1);

    return output;
}

/* 初始化PID参数 */

void pid_init(struct PID* pid) {
    (*pid).ki = 0;
    (*pid).kp = 0;
    (*pid).kd = 0;
    (*pid).avr_n_d = 10;
    (*pid).Enable = 0;
    (*pid).A = 1;
}

/* 获取PID输出 */

float get_pid_output(struct PID* p, float now, float d_t /*ms*/) {
    float output;
    if ((*p).Enable == 1) {
        //		int i;
        if ((*p).ki != (*p).ki_last) {
            (*p).i = 0;
        }

        (*p).ki_last = (*p).ki;

        (*p).now = now;

        (*p).p.now = (*p).goal - (*p).now;

        //		updata_signal_buf(&(*p).p , (*p).p.now);

        //		(*p).d.now = ( (*p).p.now - (*p).p.last[1] ) * 1000 /
        // d_t
        //;

        //		updata_signal_buf(&(*p).d , (*p).d.now);

        (*p).i += (*p).p.now / 1000 * d_t;

        //		(*p).avr_d=0;
        //
        //		for(i=0; i<(*p).avr_n_d ;i++)
        //		{
        //			(*p).avr_d += (*p).d.last[i];
        //		}

        //		(*p).avr_d = (*p).avr_d/(float) (*p).avr_n_d;

        (*p).diff = my_diff((*p).p.now);

        //		(*p).d_low.now = 0.9391f*(*p).d_low.last[1]
        //+0.0346f*(*p).d.now + 0.0346f*(*p).d.last[1];

        //		updata_signal_buf(&(*p).d_low , (*p).d_low.now);

        //		output = (*p).A * ( (*p).kp*(*p).p.now + (*p).i*(*p).ki
        //+
        //(*p).kd*(*p).avr_d + (output>0) * (*p).start  + (output<0) * (
        //-(*p).start ) );

        output = (*p).A * ((*p).kp * (*p).p.now + (*p).i * (*p).ki +
                           (*p).kd * (*p).diff + (output > 0) * (*p).start +
                           (output < 0) * (-(*p).start));

    }

    else
        output = 0;

    (*p).output = output;
    return (*p).output;
}

void contral_fun_1(void) {
    i_contral_fun_1++;

    /* 得到差速PID */

    //		get_pid_output(&turn.pid,moto_Left.speed.now -
    // moto_Right.speed.now,div_process_cycle_1);

    /* 差速PID限幅 */

    //		turn.pid.output = XianFu(turn.pid.output,1000);

    /* 差速PID乘积映射 */
    //	  turn.output_maped_positive =
    // line_map(turn.pid.output,-1000,1000,-1,3);//增益线性映射

    /* 获得PID输出 */

    //			get_pid_output(&moto[i].speed_pid,moto[i].speed.now,div_process_cycle_1);
    //
    //			moto[i].pwm = moto[i].speed_pid.output;
    //			moto[i].pwm += moto[i].speed_pid.start;
}
