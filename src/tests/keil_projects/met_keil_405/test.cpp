#include <iostream>
#include "my_test_tool.h"
#include "test_Wfb_get_output.h"
#include "test_update_siganl_buf.h"
#include "test_JianBo.h"
extern "C"
{
#include "measure.h"
#include "contral.h"
#include "w_fb.h"
#include <math.h>
#include "SG.h"
#include "jian_bo.h"
}


void test()
{
    std::cout << std::endl
              << "Test starting..." << std::endl
              << "------------" << std::endl;

    ASSERT_RETURN(test_update_siganl_buf, 0);
    ASSERT_RETURN(test_Wfb_get_output, 0);
    ASSERT_RETURN(test_JianBo, 0);
}

int main()
{
    test();
    return 0;
}

