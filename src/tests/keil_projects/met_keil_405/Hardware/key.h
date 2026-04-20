#ifndef __KEY_H
#define __KEY_H	 
//////////////////////////////////////////////////////////////////////////////////	 
//本程序只供学习使用，未经作者许可，不得用于其它任何用途
//ALIENTEK STM32F407开发板
//按键输入驱动代码	   
//正点原子@ALIENTEK
//技术论坛:www.openedv.com
//创建日期:2014/5/3
//版本：V1.0
//版权所有，盗版必究。
//Copyright(C) 广州市星翼电子科技有限公司 2014-2024
//All rights reserved									  
////////////////////////////////////////////////////////////////////////////////// 	 

/*下面的方式是通过直接操作库函数方式读取IO*/
#define KEY_UP 		PBin(12)
#define KEY_DOWN 		PBin(13)
#define KEY_A 		PBin(14)
#define KEY_B 	PBin(15)

#define KEY_UP_PRES 	1
#define KEY_DOWN_PRES	2
#define KEY_A_PRES	3
#define KEY_B_PRES   4

void KEY_Init(void);	//IO初始化
int KEY_Scan(int);  		//按键扫描函数	

#endif
