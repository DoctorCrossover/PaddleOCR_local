#!/bin/bash

# PaddleOCR 文字识别工具 - Linux/macOS 启动脚本

echo "========================================"
echo "    PaddleOCR 文字识别工具"
echo "========================================"
echo ""

# 设置环境变量（解决CPU兼容性）
export ONEDNN_MAX_CPU_ISA=SSE4_1
export FLAGS_USE_ONEDNN=0
export PADDLE_ENABLE_ONEDNN_OPTS=0

# 检查 Python 是否可用
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "错误: 未找到 Python，请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "正在启动 PaddleOCR..."
echo ""

# 启动程序
$PYTHON_CMD ocr_gui.py

# 程序退出后的提示
if [ $? -ne 0 ]; then
    echo ""
    echo "程序异常退出，按回车键退出..."
    read -p ""
fi