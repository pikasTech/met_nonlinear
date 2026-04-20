#ifndef _SOS_FILTER_H_
#define _SOS_FILTER_H_
#include "user_config.h"

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <limits.h>
#include "calibration_port.h"
#include "process.h"

/*
 * SOS 滤波器 (sos_filter.h)
 * =========================
 *
 * 这是一个 SOS_Filter.c 模块的头文件，提供了一个用 C
 * 语言实现的具有多个级联二阶节 （Second Order Sections，简称 SOS）的滤波器。
 *
 * SOS
 * 滤波器的主要优点是在处理高阶滤波器时具有较好的数值稳定性。通过将高阶滤波器分解为
 * 多个二阶节，可以更有效地处理数字滤波器中可能出现的数值问题。
 *
 * 使用方法：
 *
 * 1. 在您的项目中包含此头文件：`#include "sos_filter.h"`
 * 2. 使用 `sos_create` 函数创建 SOSFilter 结构体的实例，传入 SOS
 * 系数和节的数量。
 * 3. 使用 `sos_filter` 函数对输入信号进行滤波处理。
 * 4. 当滤波器不再需要时，使用 `sos_destroy` 函数释放其所占用的资源。
 *
 * 示例代码：
 *
 * #include "sos_filter.h"
 *
 * int main() {
 *     // 示例 SOS 系数
 *     float sos_coefficients[] = {
 *         0.003363, 0.006726, 0.003363, 1.000000, -1.195164, 0.385402,
 *         1.000000, 2.000000, 1.000000, 1.000000, -1.376839, 0.687350
 *     };
 *     int num_sections = 2;
 *
 *     // 创建 SOS 滤波器
 *     SOSFilter *filter = sos_create(sos_coefficients, num_sections);
 *
 *     // 对输入信号进行滤波
 *     float input_signal = 0.5;
 *     float filtered_signal = sos_filter(filter, input_signal);
 *     printf("Filtered signal: %f\n", filtered_signal);
 *
 *     // 销毁滤波器
 *     sos_destroy(filter);
 *
 *     return 0;
 * }
 *
 * 请注意，此模块不提供 SOS 滤波器系数的计算。您可以使用其他工具（如 Python 的
 * SciPy 库）计算滤波器的 SOS 系数。
 *
 */


SOSFilter* sos_create(double* sos_coefficients, int num_sections);

void sos_destroy(SOSFilter* filter);


// 转换函数
static inline filter_float double_to_filter_float(double d) {
		#if CONF_FILTER_FLOAT_TYPE_FIXED
			return (fix_t)(d * (1LL << fix_Q));
		#else
			return (filter_float)d;
		#endif
}

static inline double filter_float_to_double(filter_float f) {
		#if CONF_FILTER_FLOAT_TYPE_FIXED
			return (double)f / (1LL << fix_Q);
		#else
			return (double)f;
		#endif
}

static inline uint64_t high64(uint64_t a, uint64_t b) {
    uint64_t a_lo = (uint32_t)a;
    uint64_t a_hi = a >> 32;
    uint64_t b_lo = (uint32_t)b;
    uint64_t b_hi = b >> 32;

    uint64_t hi_hi = a_hi * b_hi;
    uint64_t hi_lo = a_hi * b_lo;
    uint64_t lo_hi = a_lo * b_hi;
    uint64_t lo_lo = a_lo * b_lo;

    uint64_t cross = (hi_lo + lo_hi + (lo_lo >> 32)) >> 32;

    return hi_hi + cross;
}

static inline int64_t int128_multiply(int64_t a, int64_t b, int q) {
		#if CONF_FILTER_BIGNUM_ENABLE
				struct bn num_a={0}, num_b={0}, result_mul={0}, result_shift={0};

				/* determine the sign of the result */
				bool negative = ((a < 0) != (b < 0));

				/* convert int64_t to uint64_t, then to bignum */
				bignum_from_uint64(&num_a, (uint64_t)a);
				bignum_from_uint64(&num_b, (uint64_t)b);

				/* multiply */
				bignum_mul(&num_a, &num_b, &result_mul);

				/* right shift q bits */
				bignum_rshift(&result_mul, &result_shift, q);

				/* convert back to uint64_t, then to int64_t */
				int64_t result = (int64_t)bignum_to_uint64(&result_shift);

				/* apply the sign to the result */
				return negative ? -result : result;
		#else
        /* determine the sign of the result */
        bool negative = ((a < 0) != (b < 0));

        /* convert int64_t to uint64_t */
        uint64_t abs_a = (uint64_t)llabs(a);
        uint64_t abs_b = (uint64_t)llabs(b);

        /* perform multiplication */
        uint64_t low = abs_a * abs_b;  // Automatically takes the low 64 bits
        uint64_t high = high64(abs_a, abs_b);

        /* right shift q bits */
        uint64_t result;
				result = (low >> q) | (high << (64 - q));

        /* apply the sign to the result */
        return negative ? -result : result;
		#endif
}


// 加法和减法
static inline filter_float filter_float_add(filter_float a, filter_float b) {
    return a + b;
}

static inline filter_float filter_float_sub(filter_float a, filter_float b) {
    return a - b;
}

static inline filter_float filter_float_mul(filter_float a, filter_float b) {
    #if CONF_FILTER_FLOAT_TYPE_FIXED
				filter_float result;
        result = int128_multiply(a, b, fix_Q);
		#if CONF_DEBUG_ENABLE
				printf("mul(%lld,%lld,%d) / %lld\r\n", a, b, fix_Q, result);
		#endif
        return result;  // Convert to filter_float
    #else
        return a * b;
    #endif
}


// 对单个SOS滤波器进行滤波操作
static inline filter_float single_sos_filter(SingleSOS* filter, filter_float input) {
    // 根据二阶节滤波器的公式计算新的输入和输出
    filter_float x_new = input;

    filter_float y_new = filter_float_add(filter_float_add(filter_float_mul(filter->b[0], input), filter_float_mul(filter->b[1], filter->x_history[0])), filter_float_mul(filter->b[2], filter->x_history[1]));
    y_new = filter_float_sub(y_new, filter_float_add(filter_float_mul(filter->a[1], filter->y_history[0]), filter_float_mul(filter->a[2], filter->y_history[1])));

    // 将历史值向后移动，为下一次滤波做准备
    filter->x_history[1] = filter->x_history[0];
    filter->x_history[0] = x_new;
    filter->y_history[1] = filter->y_history[0];
    filter->y_history[0] = y_new;
	
		#if CONF_FILTER_INFO_ENABLE
			float xf = filter_float_to_double(x_new);
			float yf = filter_float_to_double(y_new);
			if (xf > g_sosFilterInfo.max_x){
					g_sosFilterInfo.max_x = xf;
			}
			if (yf > g_sosFilterInfo.max_y){
					g_sosFilterInfo.max_y = yf;
			}
			if (xf < g_sosFilterInfo.min_x){
					g_sosFilterInfo.min_x = xf;
			}
			if (yf < g_sosFilterInfo.min_y){
					g_sosFilterInfo.min_y = yf;
			}
			
			float a = -0.1;
			float b = -0.1;
			float c = a * b;
			filter_float af = double_to_filter_float(a);
			filter_float bf = double_to_filter_float(b);
			filter_float cf = filter_float_mul(af, bf);
			float cc = filter_float_to_double(cf);
		#endif
		// 返回滤波后的新值
    return y_new;
}


// 对输入进行SOS滤波
static inline float sos_filter(SOSFilter* filter, float input) {
    filter_float output = double_to_filter_float(input);
    uint64_t tic = calibration_get_tick_us();
    // 对每个分段的SOS滤波器进行滤波
    for (int i = 0; i < filter->num_sections; i++) {
        output = single_sos_filter(&filter->sos_filters[i], output);
    }
    // 返回滤波后的值
    uint64_t toc = calibration_get_tick_us();
    filter->tick = toc - tic;
    return filter_float_to_double(output);
}


SOSFilterItem* sos_find(SOSFilterItem* filterItems, float center_freq);
int FilterItems_size(void);
void FilterItems_init(SOSFilterItem* items);
void compute_sos_coefficients(double f_c, double f_s, double gain, double* b, double* a);
SOSFilter* sos_create_low_pass_order1(double f_c, double f_s, double gain);

typedef struct {
	float max_x;
	float max_y;
	float min_x;
	float min_y;
}SOSFilterInfo;

#endif
