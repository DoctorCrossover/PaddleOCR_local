# PaddleOCR 文字识别工具 - 部署指南

## 项目简介

这是一个基于 PaddleOCR 的图形界面文字识别工具，支持以下功能：
- 本地图片识别
- 区域截图识别
- 可自定义快捷键
- 识别结果导出为文本
- 优化的边缘文字识别（添加白边框机制）

## 系统要求

- 操作系统：Windows / Linux / macOS
- Python 版本：3.8 或更高版本
- 内存：建议 4GB 以上
- 磁盘空间：至少 2GB（用于模型下载）

## 硬件配置

### ⚠️ 重要声明

**本项目当前默认运行于 CPU 上，而非 GPU。**

### CPU 配置（当前默认）

**CPU 配置要求：**
- CPU：任何现代 x86/x64 处理器（Intel i3 及以上 / AMD Ryzen 3 及以上）
- 内存：最低 4GB，推荐 8GB 以上
- 存储：至少 2GB 可用空间

**CPU 运行优势：**
- 无需特殊硬件，大多数电脑都能运行
- 无需配置 CUDA 或其他 GPU 驱动
- 适合轻量级 OCR 任务

**当前配置：**
本项目已针对 CPU 进行了优化：
- 设置 `ONEDNN_MAX_CPU_ISA=SSE4_1` 确保兼容性
- 使用 `paddlepaddle`（CPU 版本）
- 添加了白边框机制优化边缘识别

### GPU 配置（可选升级）

如需使用 GPU 加速，需要以下硬件配置：

**NVIDIA GPU 要求：**
- GPU：NVIDIA 显卡，建议 GTX 1060 或更高
- VRAM：至少 4GB，推荐 6GB 以上
- CUDA 版本：CUDA 11.x 或 12.x（与 PaddlePaddle 版本匹配）
- cuDNN：与 CUDA 版本匹配的 cuDNN

**AMD GPU 支持：**
PaddlePaddle 对 AMD GPU 支持有限，推荐使用 NVIDIA GPU。

---

## 如何切换到 GPU 运行

### 步骤 1：安装 GPU 版本的 PaddlePaddle

首先需要卸载 CPU 版本，然后安装 GPU 版本：

```bash
# 卸载 CPU 版本
pip uninstall paddlepaddle -y

# 安装 GPU 版本（请根据你的 CUDA 版本选择）
# 支持的 CUDA 版本：11.7, 11.8, 12.0, 12.1, 12.2, 12.3
pip install paddlepaddle-gpu==3.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**或根据 CUDA 版本选择：**

```bash
# CUDA 11.7
pip install paddlepaddle-gpu==3.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# CUDA 11.8
pip install paddlepaddle-gpu==3.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# CUDA 12.x
pip install paddlepaddle-gpu==3.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤 2：修改启动脚本（可选）

当前启动脚本已针对 CPU 优化，如需 GPU 运行，可以：

#### Windows 用户
编辑 `启动PaddleOCR.bat`，删除或注释掉以下行：

```batch
set ONEDNN_MAX_CPU_ISA=SSE4_1
set FLAGS_USE_ONEDNN=0
set PADDLE_ENABLE_ONEDNN_OPTS=0
```

#### Linux/macOS 用户
编辑 `启动PaddleOCR.sh`，删除或注释掉以下行：

```bash
export ONEDNN_MAX_CPU_ISA=SSE4_1
export FLAGS_USE_ONEDNN=0
export PADDLE_ENABLE_ONEDNN_OPTS=0
```

### 步骤 3：验证 GPU 是否生效

运行程序后，PaddleOCR 会自动检测并使用 GPU。你可以通过以下方式验证：

1. 查看程序启动日志，应该显示类似 `PaddlePaddle is installed with GPU` 的信息
2. 运行 OCR 任务时，在任务管理器（Windows）或 nvidia-smi（Linux）中观察 GPU 使用率

### GPU 性能对比

| 配置 | 单张图片识别时间 |
|------|-----------------|
| CPU (i5-10400) | 约 1-2 秒 |
| GPU (GTX 1060) | 约 0.1-0.3 秒 |
| GPU (RTX 3060) | 约 0.05-0.15 秒 |

**注意：** 对于单张图片识别，GPU 优势可能不明显，但批量处理大量图片时，GPU 速度会显著快于 CPU。

### 切回 CPU 运行

如需切回 CPU 运行：

```bash
# 卸载 GPU 版本
pip uninstall paddlepaddle-gpu -y

# 重新安装 CPU 版本
pip install paddlepaddle==3.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 快速部署（3步）

### 第1步：下载项目

将项目文件下载到本地任意目录，例如：
```
/path/to/paddleocr-project/
```

### 第2步：安装依赖

在项目目录下运行：

```bash
pip install paddlepaddle
pip install paddleocr
pip install pillow
pip install pyautogui
pip install keyboard
```

对于国内用户，建议使用清华源加速安装：

```bash
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr pillow pyautogui keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第3步：启动程序

#### Windows 用户
双击运行：
```
启动PaddleOCR.bat
```

或在命令行中运行：
```bash
python ocr_gui.py
```

#### Linux / macOS 用户
在命令行中运行：
```bash
python3 ocr_gui.py
```

## 项目文件结构

```
/path/to/paddleocr-project/
├── ocr_gui.py              # 主程序文件
├── hotkey_config.json      # 快捷键配置（自动生成）
├── 启动PaddleOCR.bat       # Windows一键启动脚本
├── 启动PaddleOCR.sh        # Linux/macOS一键启动脚本
├── test.jpg                # 测试图片
└── uploads/                # 临时文件目录（自动创建）
```

## 详细配置

### 快捷键设置

程序默认快捷键为 `Ctrl+Shift+S`，可通过以下方式修改：

1. 点击界面上的「快捷键设置」按钮
2. 输入新的快捷键组合（例如：`Alt+A`, `Win+D`, `Ctrl+Alt+X`）
3. 点击「测试快捷键」验证是否可用
4. 点击「确定」保存配置

快捷键会保存到 `hotkey_config.json`，下次启动自动生效。

### 首次运行

首次运行时，PaddleOCR 会自动下载以下模型文件（约 500MB）：
- 文字检测模型
- 文字识别模型
- 方向分类模型（可选）

请确保网络连接正常，下载完成后即可正常使用。

## 使用说明

### 方式1：选择本地图片

1. 点击「选择图片」按钮
2. 在弹出的文件选择器中选择图片
3. 图片会显示在左侧区域
4. 点击「开始识别」按钮
5. 识别结果会显示在右侧区域
6. 可点击「保存结果」保存识别结果

### 方式2：区域截图

1. 点击「区域截图」按钮，或按下快捷键
2. 程序窗口会最小化，屏幕变暗
3. 按住鼠标左键拖动选择要识别的区域
4. 松开鼠标，程序窗口恢复，截图显示在左侧
5. 点击「开始识别」按钮
6. 查看识别结果

## 常见问题

### 1. 模型下载失败

**问题**：首次运行时模型下载太慢或失败

**解决**：
- 使用国内镜像源安装 `paddlepaddle` 和 `paddleocr`
- 或手动下载模型文件并放置到指定目录

### 2. 快捷键不生效

**问题**：设置的快捷键没有反应

**解决**：
- 确认快捷键没有被其他程序占用
- 尝试使用不同的组合键
- 以管理员/root权限运行程序

### 3. 识别效果不佳

**问题**：边缘文字识别不到，或识别准确率低

**解决**：
- 本程序已内置白边框优化机制，边缘文字识别效果已大幅提升
- 尝试提高图片分辨率
- 确保图片光线充足，文字清晰

### 4. 程序启动失败

**问题**：双击 `启动PaddleOCR.bat` 没有反应

**解决**：
- 检查是否正确安装了 Python
- 在命令行中运行 `python ocr_gui.py` 查看错误信息
- 确保所有依赖都已正确安装

## 高级功能

### 修改默认快捷键

编辑 `hotkey_config.json`（首次运行后会自动生成）：

```json
{
  "hotkey": "ctrl+shift+s"
}
```

修改后重新启动程序生效。

### 自定义边框大小

编辑 `ocr_gui.py`，找到以下代码：

```python
bordered_image_path = self.add_border_to_image(self.current_image_path, border_size=30)
```

将 `border_size=30` 修改为你想要的值（像素）。

## 技术架构

- GUI 框架：Tkinter（Python内置）
- OCR 引擎：PaddleOCR
- 截图工具：PyAutoGUI
- 快捷键监听：Keyboard 库

## 开发说明

### 本地开发环境搭建

```bash
# 1. 克隆或下载项目
cd /path/to/paddleocr-project/

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python ocr_gui.py
```

### requirements.txt（可选）

创建 `requirements.txt` 文件：

```
paddlepaddle>=3.2.0
paddleocr>=2.7.0
Pillow>=10.0.0
pyautogui>=0.9.50
keyboard>=0.13.0
```

## 更新日志

### v2.0
- 添加区域截图功能
- 添加快捷键自定义功能
- 修复 numpy 数组处理问题
- 添加白边框优化机制

### v1.0
- 初始版本发布
- 支持本地图片识别

## 许可证

本项目基于 PaddleOCR 开发，使用相关开源协议。

## 技术支持

如有问题，请访问：
- PaddleOCR 官方文档：https://github.com/PaddlePaddle/PaddleOCR
- 本项目问题反馈：提交 Issue 或 PR

## 快速复制粘贴命令（Windows）

打开命令行，依次执行：

```cmd
cd /d D:\path\to\your\paddleocr-project
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr pillow pyautogui keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple
python ocr_gui.py
```

## 快速复制粘贴命令（Linux/macOS）

打开终端，依次执行：

```bash
cd /path/to/your/paddleocr-project
pip3 install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install paddleocr pillow pyautogui keyboard -i https://pypi.tuna.tsinghua.edu.cn/simple
python3 ocr_gui.py
```

---

**祝你使用愉快！** 🎉
