cmake_minimum_required(VERSION 3.0)

project(MET_KEIL_TEST)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX__FLAGS} -Wall")

set(CMAKE_BUILD_TYPE Debug)

include_directories(
    Drivers/STM32F4xx_HAL_Driver/Inc
    Drivers/STM32F4xx_HAL_Driver/Inc/Legacy
    Drivers/CMSIS/Device/ST/stm32f4xx/Include
    Drivers/CMSIS/Include
    MEASURE
    CONTRAL 
    KEY
    LED
    CORE
    Inc
    Drivers/CMSIS/lib/ARM
    Drivers/CMSIS/DSP/Include
    MyTestTool/Inc
    TEST/Inc
)

add_definitions(-D LINUX)

aux_source_directory(${PROJECT_SOURCE_DIR}/TEST/Src DIR_TEST_SRCS)

add_executable(
    test
    test.cpp
    MEASURE/measure.c
    CORE/w_fb.c
    CONTRAL/contral.c
    MEASURE/TD.c
    MyTestTool/Src/my_test_tool.cpp
    Src/SG.c
    Src/jian_bo.c
    Src/SaoPin.c
    ${DIR_TEST_SRCS}
    # Src/filter.c
    )