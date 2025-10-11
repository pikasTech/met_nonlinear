@echo off
REM 设置命令行编码为UTF-8
chcp 65001 >nul
REM 运行pytest测试，使用tf26环境

REM 激活conda环境
call conda activate tf26 || echo 错误：无法激活tf26环境。请确保该环境已创建。 && exit /b 1

echo -----------------------------------------------------
echo 测试环境：tf26 (Python 3.9 with TensorFlow 2.6)
echo 开始执行测试...
echo -----------------------------------------------------

REM 运行pytest
pytest %*

REM 保存退出码
set EXIT_CODE=%ERRORLEVEL%

REM 如果没有提供参数，显示帮助信息
if "%1"=="" (
    echo.
    echo -----------------------------------------------------
    echo 常用pytest命令：
    echo -----------------------------------------------------
    echo pytest                             - 运行所有测试
    echo pytest -v                          - 显示详细输出
    echo pytest -x                          - 遇到失败时停止
    echo pytest -k test_kan                 - 运行包含"test_kan"的测试
    echo pytest spice_simulator/tests       - 运行特定目录的测试
    echo pytest tests/test_cli.py       - 运行特定测试文件
    echo pytest --cov=. --cov-report=html   - 生成HTML覆盖率报告
    echo pytest --cov=. --cov-report=term   - 在终端显示覆盖率
    echo -----------------------------------------------------
)

exit /b %EXIT_CODE%