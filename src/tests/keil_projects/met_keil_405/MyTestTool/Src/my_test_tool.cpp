#include "my_test_tool.h"
#include <iostream>
int assert_return(int ret, char *test_name)
{
    // std::cout << "Testing: " << test_name << std::endl;

    if (ret != 0)
    {
        std::cout << "Testing: " << test_name << " error!"
                  << " return: " << ret << std::endl
                  << "-------------" << std::endl;
        return ret;
    }

    std::cout << "Testing: " << test_name << " ok!" << std::endl
              << "---------------" << std::endl;
    return 0;
}