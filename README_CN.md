# DICOM MCP 服务器

**[English](README.md) | 中文**

从多个中国医院影像系统下载 DICOM 医学影像的 Model Context Protocol (MCP) 服务器。

## 概述

这个 MCP 服务器封装了 [dicom_download](https://github.com/hengqujushi/dicom_download) 项目，为大型语言模型和 AI 助手提供一个干净的接口来从支持的医学影像提供者下载 DICOM 影像。

### 支持的医院

- **tz** (天肿): 天津医科大学癌症研究所 - zlyy.tjmucih.cn
- **fz** (复肿): 复旦大学附属肿瘤医院 - ylyyx.shdc.org.cn
- **nyfy** (宁夏总医院): 宁夏回族自治区人民医院 - zhyl.nyfy.com.cn
- **cloud**: 云端 DICOM 服务 (*.medicalimagecloud.com 及其他)

## 安装

### 前置条件

- Python 3.9+
- Playwright (浏览器自动化)

### 设置

```bash
# 以开发模式安装
pip install -e .

# 安装 Playwright 浏览器 (仅需一次)
playwright install chromium
```

## 使用

### 作为 MCP 服务器运行

```bash
# 启动 MCP 服务器 (stdio 传输)
dicom-mcp

# 或使用 Python 模块运行
python -m dicom_mcp.server
```

### 与 Claude/LLM 集成

#### 方式 1: 本地 Python 部署

编辑 Claude Desktop 配置 (例如 `~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/dicom_mcp"
      }
    }
  }
}
```

#### 方式 2: NPX 部署 (推荐)

使用 npx，可以直接运行 MCP 服务器，无需手动配置。

**⚠️ 重要：必须设置 `DICOM_DEFAULT_OUTPUT_DIR` 为绝对路径，不能使用相对路径 `./dicom_downloads`**

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "npx",
      "args": ["-y", "dicom-mcp"],
      "env": {
        "DICOM_DEFAULT_OUTPUT_DIR": "/Users/你的用户名/Downloads/dicom_downloads",
        "DICOM_DEFAULT_MAX_ROUNDS": "3",
        "DICOM_DEFAULT_STEP_WAIT_MS": "40"
      }
    }
  }
}
```

**配置要求：**
- `DICOM_DEFAULT_OUTPUT_DIR` **[必须修改]**: 使用绝对路径（完整路径）
  - ❌ 不要使用相对路径如 `./dicom_downloads` (相对路径会导致文件保存到 IDE 默认目录)
  - ✅ macOS 示例: `/Users/username/Downloads/dicom_downloads`
  - ✅ Linux 示例: `/home/username/dicom_downloads`
  - ✅ Windows 示例: `C:\\Users\\username\\Downloads\\dicom_downloads`

此方式的优势：
- 自动处理 Python 依赖检测
- 首次运行时自动安装所需包
- 无需手动配置 PYTHONPATH
- 跨操作系统兼容
- 支持环境变量设置默认参数：
  - `DICOM_DEFAULT_OUTPUT_DIR`: 下载文件的绝对路径目录 **[必须修改]**
  - `DICOM_DEFAULT_MAX_ROUNDS`: 默认扫描轮数 (可选，默认值: `3`)
  - `DICOM_DEFAULT_STEP_WAIT_MS`: 默认帧间延迟 (可选，默认值: `40`)

**注意**: 首次运行可能需要 2-3 分钟用于安装 Python 依赖，后续运行会更快。

## 实时进度反馈

下载现在显示实时进度信息：

```
======================================================================
🚀 DICOM 下载开始
======================================================================
📍 下载数量: 2 个URL
📁 输出目录: ./dicom_downloads
⚙️  扫描次数: 3, 帧间延迟: 40ms
⏳ 请稍候，下载中... (可能需要 2-10 分钟)

   >>> 打开检查页面: https://ylyyx.shdc.org.cn/viewer?...
   [1/2] provider=fz
   >>> 已进入 viewer iframe
   
======================================================================
✅ 下载完成！处理结果中...
======================================================================
```

**预期下载时间** (根据参数和影像大小而异):
- 快速模式 (2 轮, 30ms): 1-5 分钟
- 平衡模式 (3 轮, 40ms): 2-8 分钟  [推荐]
- 完整模式 (5 轮, 80ms): 4-15 分钟
- 深度扫描 (10 轮, 100ms): 8-30 分钟

详见 [PROGRESS_FEEDBACK.md](PROGRESS_FEEDBACK.md)

## 目录结构

```
dicom_mcp/
├── bin/                    # 可执行脚本
├── dicom_mcp/              # MCP 服务器核心代码
│   ├── __init__.py
│   └── server.py           # 主服务器实现
├── dicom_download/         # 下载引擎(子模块)
│   ├── multi_download.py   # 多URL调度
│   ├── shdc_download_dicom.py  # 复肿提供商
│   ├── tjmucih_download_dicom.py  # 天肿提供商
│   ├── nyfy_download_dicom.py     # 宁夏总医院
│   ├── password_manager.py        # 密码管理
│   └── urls_example.txt          # URL格式示例
├── scripts/                # 安装和验证脚本
├── test/                   # 测试文件和文档
│   ├── test_tools.py       # 单元测试
│   ├── test_mcp_inspector.sh  # MCP Inspector测试
│   └── (开发文档和测试记录)
├── README.md               # 英文文档
├── README_CN.md            # 中文文档
├── CHANGELOG.md            # 版本变更日志
└── package.json            # npm包配置
```

**注意**: `test/` 目录包含测试文件和开发文档,不会发布到npm。实际URL和敏感信息已通过.gitignore排除。

## 可用工具

### 1. `download_dicom`

从单个 URL 下载 DICOM 影像。

**参数:**
- `url` (必需): 医学影像查看器 URL
- `output_dir` (默认: `./dicom_downloads`): 保存文件的目录
- `provider` (默认: `auto`): 提供者类型 (auto, tz, fz, nyfy, cloud)
- `mode` (默认: `all`): 下载模式 (all, diag, nondiag)
- `headless` (默认: `true`): 是否无界面运行浏览器
- `password` (可选): 分享密码/验证码
- `create_zip` (默认: `true`): 创建 ZIP 压缩包
- `max_rounds` (默认: `3`): 扫描轮数 - 控制逐帧播放次数
- `step_wait_ms` (默认: `40`): 帧间延迟 (毫秒) - 帧播放时的延迟

**返回:**
- `success`: 是否下载成功
- `output_dir`: 包含下载文件的目录
- `zip_path`: ZIP 压缩包路径 (如创建)
- `file_count`: 下载的文件数
- `message`: 状态或错误消息

### 2. `batch_download_dicom`

从多个 URL 批量下载。

**参数:**
- `urls` (必需): 要下载的 URL 列表
- `output_parent` (默认: `./dicom_downloads`): 所有下载的父目录
- `provider` (默认: `auto`): 提供者类型
- `mode` (默认: `all`): 下载模式
- `headless` (默认: `true`): 无界面模式
- `create_zip` (默认: `true`): 为每个 URL 创建 ZIP
- `max_rounds` (默认: `3`): 扫描轮数 - 应用于所有 URL
- `step_wait_ms` (默认: `40`): 帧间延迟 - 应用于所有 URL

**返回:**
每个 URL 的下载结果列表，包含成功状态和文件计数

### 3. `detect_provider_from_url`

识别 URL 属于哪个提供者。

**参数:**
- `url` (必需): 要检查的 URL

**返回:**
- `detected_provider`: 提供者标识符
- `provider_info`: 提供者详细信息
- `is_auto_detected`: 检测是否成功

### 4. `list_supported_providers`

获取所有支持的提供者信息。

**返回:** 提供者信息列表，包括支持的域名和描述

### 5. `validate_url`

检查 URL 是否来自支持的提供者。

**参数:**
- `url` (必需): 要验证的 URL

**返回:**
- `valid`: URL 是否来自支持的提供者
- `provider`: 有效时的检测到的提供者
- `error`: 无效时的错误消息

## 使用示例

### 单 URL 下载

```python
# 从单个 URL 下载
download_dicom(
    url="https://zlyy.tjmucih.cn/viewer?share_id=AAAA",
    output_dir="./my_downloads",
    mode="all",
    create_zip=True
)
```

### 批量下载

```python
# 从多个 URL 下载
batch_download_dicom(
    urls=[
        "https://zlyy.tjmucih.cn/viewer?share_id=AAAA",
        "https://ylyyx.shdc.org.cn/viewer?share_id=BBBB",
    ],
    output_parent="./batch_downloads",
    create_zip=True
)
```

### 密码保护的 URL

**支持多种密码格式自动识别**:

```python
# 方式1: 单个URL - 直接传递password参数
download_dicom(
    url="https://ylyyx.shdc.org.cn/code.html?share_id=xxx",
    password="1234",
    provider="fz"
)

# 方式2: 批量URL - 使用passwords字典映射
batch_download_dicom(
    urls=[
        "https://ylyyx.shdc.org.cn/code.html?share_id=xxx-1",
        "https://ylyyx.shdc.org.cn/code.html?share_id=xxx-2",
        "https://ylyyx.shdc.org.cn/code.html?share_id=xxx-3",
    ],
    passwords={
        "https://ylyyx.shdc.org.cn/code.html?share_id=xxx-1": "1234",
        "https://ylyyx.shdc.org.cn/code.html?share_id=xxx-3": "5678"
        # xxx-2 无密码,自动跳过
    }
)

# 方式3: 从文件读取(支持多种密码格式)
# urls.txt 示例:
# https://ylyyx.shdc.org.cn/code.html?share_id=xxx-1 安全码:1234
# https://ylyyx.shdc.org.cn/code.html?share_id=xxx-2 密码:5678
# https://ylyyx.shdc.org.cn/code.html?share_id=xxx-3 password:9012
# https://ylyyx.shdc.org.cn/code.html?share_id=xxx-4 #无密码
```

**密码功能特性** (v1.2.7):
- ✅ **自动识别**: 支持`安全码:`、`密码:`、`password:`、`code:`等格式
- ✅ **自动输入**: 虚拟键盘自动点击输入密码
- ✅ **智能提交**: 识别自动提交机制,优化等待时间
- ✅ **手动兜底**: 自动输入失败时支持手动输入(headless=false)
- ✅ **混合模式**: 批量下载支持有密码和无密码URL混合

详见示例文件: `dicom_download/urls_example.txt`

## 在 Claude 中使用

### 示例 1: 检查支持的医院

```
用户: "支持哪些医学影像提供者？"

Claude 会调用 list_supported_providers() 并显示：
- 所有 4 个提供者类型
- 它们的域名
- 支持的功能
```

### 示例 2: 单 URL 下载

```
用户: "从 https://zlyy.tjmucih.cn/viewer?share_id=ABC123 下载 DICOM 影像"

Claude 会：
1. 调用 download_dicom 工具
2. 自动检测提供者为 "tz"
3. 下载到 ./dicom_downloads/...
4. 创建 ZIP 压缩包
5. 报告成功和文件计数
```

### 示例 3: 自定义扫描参数

```
用户: "从 [URL] 下载，使用 5 轮扫描和 50ms 延迟以完整捕获"

Claude 会使用：
- max_rounds=5 (更多次迭代 = 更完整)
- step_wait_ms=50 (延迟帧之间的时间)
```

## 常见任务

### 任务 1: 仅下载诊断序列

```
Claude 提示:
"从 [URL] 以诊断模式下载 DICOM
(更快，仅下载诊断序列，不包括所有序列)"
```

MCP 服务器会：
- 设置 `mode="diag"` 参数
- 传递给基层提供者脚本
- 仅返回诊断序列文件

### 任务 2: 批量下载不创建 ZIP

```
Claude 提示:
"从这些 URL 下载到 ./downloads 
但不创建 ZIP 文件，只保留目录"
```

MCP 服务器会：
- 设置 `create_zip=False`
- 返回每个下载的目录路径
- 跳过 ZIP 压缩包创建

### 任务 3: 处理受保护的 URL

```
Claude 提示:
"从 https://example.medicalimagecloud.com/viewer 下载
密码: MY_SECRET_CODE"
```

MCP 服务器会：
- 将密码传递给云提供者
- 认证并下载
- 返回下载的文件

### 任务 4: 优化下载速度

```
Claude 提示:
"快速下载，优先考虑速度而不是完整性"
```

MCP 服务器会使用：
- max_rounds=2 (更少迭代 = 更快)
- step_wait_ms=30 (更短延迟)

### 任务 5: 最大化数据完整性

```
Claude 提示:
"彻底扫描以获取所有帧"
```

MCP 服务器会使用：
- max_rounds=5 (更多迭代 = 更完整)
- step_wait_ms=80 (更长延迟 = 更稳定)

## 故障排除

### 问题: "找不到模块"错误

**解决方案**: 确保安装完成：
```bash
cd /path/to/dicom_mcp
pip install -e .
```

### 问题: Playwright chromium 未找到

**解决方案**: 安装浏览器：
```bash
playwright install chromium
```

### 问题: Claude Desktop 无法连接

**解决方案**:
1. 验证配置在 Claude Desktop 设置中正确
2. 确保 PYTHONPATH 环境变量设置正确
3. 重启 Claude Desktop

### 问题: 下载链接已过期

**原因**: 医学影像分享链接通常在一段时间后过期（数天至数周）

**解决方案**: 
- 从医学提供者获取新的有效分享链接
- 确保 URL 有效且不是太旧

### 问题: 云提供者身份验证失败

**原因**: 某些云提供者需要显式密码

**解决方案**: 
- 在下载请求中使用 password 参数
- 确保密码格式正确

## 部署

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 了解：
- 本地开发部署
- PyPI 包管理器安装
- Claude Desktop 配置
- 发布到 PyPI

## 文档

- [README.md](README.md) - 英文文档
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 安装指南
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术设计
- [CONFIG_PARAMETERS.md](CONFIG_PARAMETERS.md) - 参数配置
- [PROGRESS_FEEDBACK.md](PROGRESS_FEEDBACK.md) - 进度反馈
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [TESTING.md](TESTING.md) - 测试指南

## 架构

```
Claude Desktop / MCP Client
    ↓ (MCP 协议 over stdio)
DICOM MCP Server (dicom_mcp/server.py)
    ↓ (子进程)
multi_download.py (原始项目)
    ↓ (提供者路由)
医院 DICOM 系统
```

## 许可证

本项目采用 **DICOM MCP 非商业许可证**。

✓ **允许**: 个人学习、研究、非营利性教学
✗ **禁止**: 商业使用、出售、收费服务
⚠️ **必须**: 保留许可证、署名原作者

如需商业使用，请联系: support@dicom-mcp.com

详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 支持

如遇问题，请：

1. 检查 [故障排除](#故障排除) 部分
2. 查看相关文档
3. 提交 Issue: https://github.com/hengqujushi/dicom_mcp/issues

## 致谢

- 原项目: [dicom_download](https://github.com/hengqujushi/dicom_download)
- Cloud 提供者适配: [cloud-dicom-downloader](https://github.com/Kaciras/cloud-dicom-downloader)
- MCP 框架: [Model Context Protocol](https://modelcontextprotocol.io)

## 更新日志

### v1.0.0 (2025-01-13)
- ✅ 完整的中英文文档
- ✅ 两种部署方式支持
- ✅ 非商业许可证
- ✅ 进度反馈功能
- ✅ 5 个 MCP 工具
- ✅ 4 家医院支持

## 联系方式

- 📧 Email: support@dicom-mcp.com
- 🐛 Issue: https://github.com/hengqujushi/dicom_mcp/issues
- 📖 文档: https://github.com/hengqujushi/dicom_mcp#readme
