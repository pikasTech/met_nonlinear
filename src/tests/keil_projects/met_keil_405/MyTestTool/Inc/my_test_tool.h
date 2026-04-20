#ifndef __MY_TEST_TOOL_H
#define __MY_TEST_TOOL_H
#define ASSERT_RETURN(fun_name,input) assert_return(fun_name(input), #fun_name)

int assert_return(int ret, char *test_name);

#endif