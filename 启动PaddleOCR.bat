@echo off
chcp 65001 >nul
echo ========================================
echo       PaddleOCR 文字识别工具
echo ========================================
echo.
set ONEDNN_MAX_CPU_ISA=SSE4_1
set FLAGS_use_onednn=0
set PADDLE_ENABLE_ONEDNN_OPTS=0
echo 正在启动PaddleOCR...
python ocr_gui.py
pause