// 包含所需的头文件
#include "sos_filter.h"
#include <stdio.h>
#include <stdlib.h>
#include "filter_include.h"
#include "process.h"
#include "user_config.h"

SOSFilterItem g_detectorFilterItems[] = {
#define _FILTER_TEMPLATE_ARRAY
#include "filter_talbe.h"
};

SOSFilterItem g_detectorFilterItems2[] = {
#define _FILTER_TEMPLATE_ARRAY
#include "filter_talbe.h"
};

SOSFilterInfo g_sosFilterInfo = {
	.max_x = -99999,
	.max_y = -99999,
	.min_x = 99999,
	.min_y = 99999
};

int FilterItems_size(void) {
    return sizeof(g_detectorFilterItems) / sizeof(SOSFilterItem);
}

void FilterItems_init(SOSFilterItem* items) {
    for (int i = 0; i < FilterItems_size(); i++) {
        items[i].filter = items[i].filterFactory();
    }
}

#ifndef FLT_MAX
#define FLT_MAX 999999999.0f
#endif
SOSFilterItem* sos_find(SOSFilterItem* filterItems, float center_freq) {
    SOSFilterItem* closest = NULL;  // 用于存储距离目标频率最近的滤波器
    float min_diff = FLT_MAX;  // 初始化最小的差值为浮点数的最大值

    int n =
        FilterItems_size();  // 使用FilterItems_size函数获取g_detectorFilterItems的大小

    // 遍历g_detectorFilterItems数组中的每个元素
    for (int i = 0; i < n; i++) {
        // 计算中心频率与目标频率之间的差值
        float diff = fabs(filterItems[i].centerFreq - center_freq);

        // 如果计算得到的差值小于当前最小的差值
        if (diff < min_diff) {
            min_diff = diff;            // 更新最小的差值
            closest = &filterItems[i];  // 更新距离目标频率最近的滤波器
        }
    }

    // 返回距离目标频率最近的滤波器
    return closest;
}

/*
 * 该代码实现了一个称为“二阶节（Second-Order
 * Section）”的数字滤波器，通常缩写为SOS。SOS滤波器是数字滤波器设计中的一个关键组成部分，可以解决在处理高阶滤波器时可能遇到的数值稳定性问题。

 * 二阶节滤波器的公式如下：

 * y[n] = b[0]*x[n] + b[1]*x[n-1] + b[2]*x[n-2] - a[1]*y[n-1] - a[2]*y[n-2]

 * 其中，x[n]是输入信号，y[n]是输出信号，a[i]和b[i]是滤波器的系数。
*/

/* 创建SOS滤波器
 * sos_coefficients: 滤波器系数数组，每6个数为一组（分别对应b[0], b[1], b[2],
 * a[0], a[1], a[2]的值） num_sections:
 * 滤波器分段（每段都是一个独立的SOS滤波器）的数量
 */

SOSFilter* sos_create(double* sos_coefficients, int num_sections) {
    // 为SOS滤波器结构体分配内存
    SOSFilter* filter = (SOSFilter*)calloc(sizeof(SOSFilter), 1);
    filter->num_sections = num_sections;
    // 为每个分段的SOS滤波器分配内存
    filter->sos_filters = (SingleSOS*)calloc(num_sections * sizeof(SingleSOS), 1);

    // 初始化每个分段的SOS滤波器的系数
    for (int i = 0; i < num_sections; i++) {
        if (sos_coefficients[i * 6 + 3] != 1.0f) {  // 检查a[0]的值
            printf("Error: a[0] is not equal to 1!\n");
            free(filter->sos_filters);
            free(filter);
            return NULL;
        }
        for (int j = 0; j < 3; j++) {
						filter->sos_filters[i].b[j] =
									double_to_filter_float(sos_coefficients[i * 6 + j]); 
						filter->sos_filters[i].a[j] =
									double_to_filter_float(sos_coefficients[i * 6 + j + 3]); 
        }
    }
    // 返回创建的滤波器
    return filter;
}

// 销毁滤波器，释放内存
void sos_destroy(SOSFilter* filter) {
    free(filter->sos_filters);
    free(filter);
}

#define M_PI 3.1415926
void compute_sos_coefficients(double f_c, double f_s, double gain, double* b, double* a) {
	  double coe[3] = {0};
    double w_c = 2 * M_PI * f_c / f_s;
    coe[2] = (1 - tan(w_c / 2)) / (1 + tan(w_c / 2)); // a1
    coe[0] = (1 - coe[2]) / 2; // b0
    coe[1] = coe[0]; // b1

    // Scale b0 and b1 so that their sum is equal to the specified gain
    double scale = gain / (coe[0] + coe[1]);
    coe[0] *= scale;
    coe[1] *= scale;
		a[1] = coe[2];
		b[0] = coe[0];
		b[1] = coe[1];
}

SOSFilter* sos_create_low_pass_order1(double f_c, double f_s, double gain){
		double sos_coefficients[6] = {0};
		compute_sos_coefficients(f_c, f_s, gain, sos_coefficients, sos_coefficients + 3);
		return sos_create(sos_coefficients, 1);
}
