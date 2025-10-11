#!/bin/bash
# 备份 inference 模块

echo "备份 inference 模块..."

# 1. 创建备份目录
mkdir -p inference/backup

# 2. 复制所有Python文件
cp inference/*.py inference/backup/ 2>/dev/null || echo "No .py files in root inference/"

# 3. 记录备份信息
echo "# Inference 模块备份" > inference/backup/README.md
echo "" >> inference/backup/README.md
echo "备份时间: $(date)" >> inference/backup/README.md
echo "备份原因: 重构前备份" >> inference/backup/README.md
echo "Git commit: $(git rev-parse HEAD)" >> inference/backup/README.md
echo "" >> inference/backup/README.md
echo "## 注意事项" >> inference/backup/README.md
echo "- 本目录仅作参考，不参与实际运行" >> inference/backup/README.md
echo "- 新旧代码严格分离，避免混放" >> inference/backup/README.md
echo "- 重构完成验证后应删除本目录" >> inference/backup/README.md

echo "备份完成，文件保存在 inference/backup/"