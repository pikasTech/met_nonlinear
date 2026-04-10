# tf26 环境配置

## 概述

训练环境使用名为 `tf26` 的 Conda 环境 Python，而不是硬编码某台机器的绝对路径。

## 路径规律

tf26 环境的 Python 可执行文件常见位置：

- `C:\Users\<用户名>\.conda\envs\tf26\python.exe`
- `C:\Users\<用户名>\MiniConda3\envs\tf26\python.exe`
- `C:\Users\<用户名>\miniconda3\envs\tf26\python.exe`

## 定位方法

先找 `tf26` 这个环境名，再拼接到对应的 Conda 根目录，不要先假设用户名或 Conda 安装目录固定。

**推荐定位命令**：

```bash
# 查看所有 conda 环境
conda env list

# 查找 conda 位置
where conda

# 在常见位置搜索
ls /c/Users/*/.conda/envs/tf26/python.exe
ls /c/Users/*/MiniConda3/envs/tf26/python.exe
```

## 直接调用

需要执行 `python cli.py` 时，如果默认 Python 不是 tf26，需使用完整路径调用：

```bash
/c/Users/lyon/MiniConda3/envs/tf26/python.exe cli.py --metrics --all-projects
```

## 调用时机

当出现 `ModuleNotFoundError: No module named 'tensorflow'` 等依赖错误时，说明默认 Python 不是 tf26，需要使用完整路径调用训练/评估命令。
