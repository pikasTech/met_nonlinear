#ifndef _USER_CONFIG_H_
#define _USER_CONFIG_H_
#endif

/* digital data output config */
#define CONF_USING_UART_RAW_OUTPUT 1

/* DSP config */
#define CONF_FREQ_HZ 20000
#define CONF_WF_ENABLE 0 	/* frontend filter */
#define CONF_WFB_ENABLE 0 /* feedback */
#define CONF_WP_ENABLE 0 	/* phase compensate */
#define CONF_WB_ENABLE 0 	/* bakend filter */

/* test config */
#define CONF_SELF_TEST_ON_BOOT 0 /* start self test after boot */
#define CONF_MAGNITUDE_COEFFICIENT 1
#define CONF_SELF_TEST_ON_CONTINUE 0 /* self test continue after finished */

/* time config */

#define CONF_SCAN_DELAY_MIN_10MS 2000
#define CONF_SCAN_OFFSET_TEST_DURATION_10MS 500

/* test sorce channel */
#define CONF_TEST_SOURCE_INNER 1
#define CONF_TEST_SOURCE_CH1 0
#define CONF_TEST_SOURCE_CH2 0

/* test target channel */
#define CONF_TEST_TARGET_INNER 0
#define CONF_TEST_TARGET_CH1 1
#define CONF_TEST_TARGET_CH2 0

/* filter for detection */
#define CONF_USING_SCAN_FILTTER_SELECT 0
#define CONF_USING_SCAN_FILTTER_HIGH_LOW 0

/* external test points */
#define CONF_USING_SAOPIN_0d1_0d5 0
#define CONF_USING_SAOPIN_0d5_10 1
#define CONF_USING_SAOPIN_10_80 1
#define CONF_USING_SAOPIN_80_300 1
#define CONF_USING_SAOPIN_300_500 0
#define CONF_USING_SAOPIN_500_1500 0

#define CONF_SG_A_MAX 1.5f

/* test mode */
#define CONF_TEST_TARGET_SYSTEM 1
#define CONF_TEST_TARGET_LOOP_GAIN_ENABLE 0
#define CONF_TEST_TARGET_WP_ENABLE 0
#define CONF_TEST_TARGET_WB_ENABLE 0
#define CONF_TEST_TARGET_WFB_ENABLE 0

/* channel config */
#define CONF_CH1_SIGNAL_PROCESS_ENABLE 1
#define CONF_CH2_SIGNAL_PROCESS_ENABLE 0

/* detect config */
#define DETECTION_SIGNAL_PROCESS_ENABLE 0

/* Terminal Config */
#define CONF_BAUDRATE 2000000
#define CONF_SHELL_ENABLE 0

/* WP config */
#define CONF_WP_USE_SELECT 0
#define CONF_WP_USE_MUTI 0

/* WFB config */
#if CONF_WFB_ENABLE
#define CONF_PID_KP 0
#define CONF_PID_KD 0.02f
#define CONF_PID_KI 0
#else
#define CONF_PID_KP 0
#define CONF_PID_KD 0
#define CONF_PID_KI 0
#endif

/* OUTPUT config */
#define CONF_OUTPUT_AMP 0.86f
#define CONF_OUTPUT_OFFSET 1.7f
#define CONF_INPUT_OFFSET_DEFAULT 1.6f
#define CONF_FEEDBACK_OFFSET 1.609f

#define CONF_WB_FILTER_FROM_SOS_COEFFICIENTS 0
#define CONF_WP_FILTER_FROM_SOS_COEFFICIENTS 1

#if CONF_WB_FILTER_FROM_SOS_COEFFICIENTS
#define CONF_WB_FILTER sos_create_wb
#define CONF_WB_SOS 1.000000000000000, -1.990756788773228, 0.992417735848810, 1.000000000000000, -1.961018862727894, 0.962654998575115
#else
#define CONF_WB_FILTER sos_create_sos_low_300_0_4_20000_0
#endif

#if CONF_WP_FILTER_FROM_SOS_COEFFICIENTS
#define CONF_WP_FILTER sos_create_wp
#define CONF_WP_SOS 0.504668390437081, -0.485994828688757, 0.000000000000000, 1.000000000000000, -0.981326438251676, 0.000000000000000
#endif

/* user config end */
// #define CONF_TOTLE_MODE 1

#ifdef CONF_TOTLE_MODE
#define CONF_SCAN_DELAY_MIN_10MS 3000
#define CONF_SCAN_OFFSET_TEST_DURATION_10MS 2000
#endif

#ifndef CONF_USING_SAOPIN_0d1_0d5
#define CONF_USING_SAOPIN_0d1_0d5 0
#endif

#ifndef CONF_USING_SAOPIN_300_1500
#define CONF_USING_SAOPIN_300_1500 0
#endif

#define CONF_TEST_FADE_RANGE 0.2f

#define CONF_USING_SWITCH 0

#define CONF_FS 200000

/* config for WF */
#define CONF_WF_FILTER sos_create_sos_low_60_0_4_20000_0

/* config for filter */
#define CONF_FILTER_FLOAT_TYPE_FLOAT 0
#define CONF_FILTER_FLOAT_TYPE_DOUBLE 0
#define CONF_FILTER_FLOAT_TYPE_FIXED 1
#define CONF_FILTER_BIGNUM_ENABLE 0


/* debug */
#define CONF_DEBUG_ENABLE 0
#define CONF_FILTER_INFO_ENABLE 0

#if CONF_FILTER_FLOAT_TYPE_FLOAT
#define filter_float float
#elif CONF_FILTER_FLOAT_TYPE_DOUBLE
#define filter_float double
#elif CONF_FILTER_FLOAT_TYPE_FIXED
#define filter_float fix_t
#endif

/* assert */

#if CONF_TEST_TARGET_LOOP_GAIN_ENABLE + CONF_TEST_TARGET_WP_ENABLE + CONF_TEST_TARGET_WB_ENABLE + CONF_TEST_TARGET_WFB_ENABLE > 1
#error "only one test target can be selected"
#endif

#if CONF_TEST_SOURCE_INNER + CONF_TEST_SOURCE_CH1 + CONF_TEST_SOURCE_CH2 > 1
#error "only one test source can be selected"
#endif

#if CONF_TEST_TARGET_INNER + CONF_TEST_TARGET_CH1 + CONF_TEST_TARGET_CH2 > 1
#error "only one test target can be selected"
#endif

#if CONF_FILTER_FLOAT_TYPE_FLOAT + CONF_FILTER_FLOAT_TYPE_DOUBLE + CONF_FILTER_FLOAT_TYPE_FIXED > 1
#error "only one float type can be selected"
#endif

#if CONF_USING_SCAN_FILTTER_SELECT + CONF_USING_SCAN_FILTTER_HIGH_LOW > 1
#error "only one scan filter can be selected"
#endif
