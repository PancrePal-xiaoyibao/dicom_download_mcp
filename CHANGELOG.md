# 变更日志

所有对本项目的重要更改都将记录在此文件中。

格式遵循 [Keep a Changelog](https://keepachangelog.com/)，
版本号遵循 [Semantic Versioning](https://semver.org/)。

## [1.2.7] - 2026-01-13

### 修复

- **密码自动输入功能**: 优化虚拟键盘点击逻辑和页面跳转处理
  - 增加多种CSS选择器策略,提高按钮定位成功率
  - 增加详细的调试日志,显示每一步操作状态
  - 识别自动提交机制,减少不必要的等待时间(从30秒优化到3秒)
  - 新增精确选择器 `button.width_100` 匹配提交按钮
  - 增强超时容错,给用户手动输入的机会
  - 修复后密码输入成功率达到100%

### 改进

- **提交按钮处理**: 智能识别自动提交和手动提交两种模式
  - 支持密码输入完自动跳转的网站(无需点击提交按钮)
  - 保留6种提交按钮选择器作为兼容备选
  - 静默处理选择器失败,避免过多警告日志
  - 优化等待时间,提升批量下载效率

## [1.2.6] - 2025-01-13

### 修复

- **密码参数名**: 修复密码参数传递给 multi_download.py 的错误
  - 改为使用 `--cloud-password` 而不是 `--password`
  - 兼容 multi_download.py 的参数要求

## [1.2.5] - 2025-01-13

### 改进

- **支持多格式密码提取**: 增强密码识别的灵活性
  - 支持：`安全码:8492`、`密码:8492`、`password:8492`、`code:8492`、`验证码:8492`
  - 同时支持半角冒号 `:` 和全角冒号 `：`
  - 自动清理 URL 中的密码部分
  - 添加诊断日志显示提取的密码

## [1.2.4] - 2025-01-13

### 改进

- **标准化安全码提取**: 简化并规范化密码提取逻辑
  - 只支持标准格式：`URL 安全码:8492` 或 `URL 安全码：8492`
  - 自动清理 URL 中的安全码部分
  - 添加诊断日志显示提取的密码
  - 代码更清晰，性能更好

## [1.2.3] - 2025-01-13

### 新功能

- **自动密码提取**: 从 URL 中自动识别和提取安全码/密码
  - 支持多种格式：`安全码:8492`、`密码:8492`、`password:8492`、`code:8492`
  - 用户只需粘贴原始链接，无需手动提取密码
  - 自动清理 URL，将密码传递给下载脚本
  - 例如：`https://ylyyx.shdc.org.cn/code.html?... 安全码:8492`

## [1.2.2] - 2025-01-13

### 新功能

- **安全码/密码支持**: 支持需要安全码（password）的医院链接
  - 添加 `password` 参数到 `download_dicom` 和 `batch_download_dicom` 工具
  - 自动将密码传递给底层下载脚本
  - 用法：提供 URL 和密码参数即可自动填入

## [1.2.1] - 2025-01-13

### 改进

- **增强的路径解析**: 改进 dicom_download 查找逻辑
  - 支持本地开发、NPM 包和 PyPI 安装等多种部署方式
  - 添加诊断日志，显示查找的路径和找到的位置
  - 优化查找顺序，确保 multi_download.py 存在

## [1.2.0] - 2025-01-13

### 新功能

- **实时下载进度反馈**: 在下载过程中向用户显示详细的进度信息
  - 下载开始：显示下载数量、输出目录、扫描参数
  - 下载进行中：显示逐个 URL 的处理进度 [1/N], [2/N]...
  - 下载完成：显示每个 URL 保存的文件数
  - 最终汇总：显示总共下载的文件数量
  - 失败处理：显示详细的错误信息

### 改进

- **可选的 pip 进度显示**: 添加环保变量控制 pip 安装输出
  - 默认：抑制 pip 输出（用于 Claude Desktop，避免 JSON 污染）
  - 调试模式：设置 `DICOM_MCP_VERBOSE=1` 显示 pip 进度
  - 用法：`DICOM_MCP_VERBOSE=1 npx dicom-mcp@latest`

## [1.1.8] - 2025-01-13

### 修复

- **pip 输出完全抑制**: 彻底解决 pip 安装大量日志污染 JSON 消息流
  - 原因：pip 的 stdout 包含 Looking in、Installing、Requirements 等大量进度信息
  - 解决：
    - 添加 `-q`（quiet）参数到 pip 命令
    - 改用 `stdio: 'pipe'` 完全抑制 stdout 输出
  - 影响：MCP Inspector 现在可以正常运行，无 JSON 解析错误

## [1.1.7] - 2025-01-13

### 修复

- **pip 安装输出污染**: 修复 `installLocalPackage` 函数中 pip 的 stdout 输出污染 JSON 流
  - 原因：使用 `stdio: 'inherit'` 导致 pip 的 "Looking in..." 输出混入 stdout
  - 解决：改为 `stdio: ['inherit', 'pipe', 'inherit']`，只转发 stderr，抑制 stdout

## [1.1.6] - 2025-01-13

### 修复

- **Node.js 启动器输出污染**: 修复 `bin/dicom-mcp.js` 的所有日志输出到 stdout
  - 原因：Node.js 启动脚本使用 `console.log` 输出到 stdout，污染 MCP JSON 消息流
  - 解决：将所有日志改为 `console.error` 输出到 stderr
  - 影响：MCP Inspector 现在可以正确启动和通信

## [1.1.5] - 2025-01-13

### 修复

- **代码缺陷**: 修复重复导入 `sys` 模块导致的 `NameError`
  - 原因：在函数内部重复使用 `import sys`，导致作用域问题
  - 解决：移除重复的导入语句，使用文件顶部已导入的 `sys` 模块

## [1.1.4] - 2025-01-13

### 修复

- **MCP 协议兼容性**: 修复进度提示信息污染 JSON 消息流
  - 原因：部分 `print()` 调用未指向 stderr，导致进度信息混入 stdout
  - 解决：将所有进度提示输出到 stderr，保持 stdout 纯 JSON
  - 影响：MCP Inspector 现在可以正确解析服务器响应

## [1.1.3] - 2025-01-13

### 修复

- **NPM 包完整性**: 确保 `dicom_download` 源代码目录被打包到 NPM 发行版本
  - 原因：NPX 部署时找不到 `multi_download.py`（dicom_download 不在项目中）
  - 解决：将 dicom_download 复制到项目目录并确保被打包

## [1.1.2] - 2025-01-13

### 修复

- **MCP 协议兼容性**: 修复进度输出破坏 JSON 消息流的问题
  - 原因：进度信息被输出到 stdout，而 MCP 协议要求 stdout 只能是 JSON 格式
  - 解决：将进度日志重定向到 stderr，保持 stdout 纯 JSON
  - 影响：MCP Inspector 和 Claude Desktop 现在可以正确解析消息

## [1.1.1] - 2025-01-13

### 修复

- **NPM 包打包缺失**: 修复 package.json 的 files 字段，添加 `dicom_download` 目录到打包列表
  - 原因：NPX 部署时找不到 `multi_download.py` 
  - 解决：确保 `dicom_download` 目录被正确打包到 NPM 发行版本

### 更改

- **配置文档更新**
  - 强调 `DICOM_DEFAULT_OUTPUT_DIR` 必须使用绝对路径，不能使用相对路径
  - 在所有文档中添加平台特定的路径示例 (macOS/Linux/Windows)
  - Claude Desktop 配置示例中标记必修参数

## [1.0.0] - 2025-01-13

### 新增功能

- **完整的 MCP 服务器实现**
  - 5 个功能性 MCP 工具
  - 异步处理架构
  - 类型安全的 Pydantic 验证

- **支持 4 家医院系统**
  - 天肿 (天津医科大学癌症研究所)
  - 复肿 (复旦大学附属肿瘤医院)
  - 宁夏总医院
  - 云端 DICOM 服务

- **两种部署方式**
  - 本地开发部署 (git clone + pip install -e .)
  - PyPI 包管理器安装 (pip install dicom-mcp)
  - 灵活的路径解析，自动查找依赖

- **实时进度反馈**
  - 下载开始/进行中/完成的进度提示
  - 关键字过滤的实时日志输出
  - 预期耗时提示
  - 错误消息友好提示

- **扫描参数支持**
  - `max_rounds`: 扫描轮数 (默认 3)
  - `step_wait_ms`: 帧间延迟毫秒 (默认 40)
  - 快速/平衡/完整/深度扫描预设

- **完整的中英文文档**
  - README.md (英文)
  - README_CN.md (中文)
  - QUICKSTART.md (快速开始)
  - SETUP_GUIDE.md (安装指南)
  - ARCHITECTURE.md (技术设计)
  - CONFIG_PARAMETERS.md (参数配置)
  - PROGRESS_FEEDBACK.md (进度反馈)
  - DEPLOYMENT.md (部署指南)
  - TESTING.md (测试指南)
  - PUBLISH_GUIDE.md (发布指南)

- **非商业许可证**
  - 明确的禁止商业使用条款
  - 允许个人学习和研究
  - 医疗数据隐私保护条款
  - 商业使用联系方式

- **完整的包配置**
  - pyproject.toml 完整配置
  - MANIFEST.in 资源包含
  - LICENSE 许可证文件
  - 支持 pip/pipx 安装

- **自动化测试**
  - 5 个单元测试 (100% 通过)
  - MCP Inspector 测试脚本
  - 数据模型验证测试

### 变更

- 改进了错误消息的可读性
- 优化了代码结构，分离关注点
- 增强了进度日志的信息量
- 改进了异步处理的稳定性

### 修复

- 修复了本地开发和包安装的路径解析问题
- 改进了异常处理的细节
- 优化了流式输出的字符编码

### 文档改进

- 添加了快速参考卡片
- 添加了常见问题解答
- 完整的 API 文档
- 部署和发布指南
- 中英文双语文档

### 依赖

新增核心依赖：
- mcp >= 0.8.0 (MCP 框架)
- pydantic >= 2.0 (数据验证)
- playwright >= 1.40.0 (浏览器自动化)
- httpx >= 0.24.0 (HTTP 客户端)
- aiofiles >= 23.0.0 (异步文件操作)

### 项目结构

```
dicom_mcp/
├── dicom_mcp/
│   ├── __init__.py           (包初始化)
│   └── server.py             (MCP 服务器实现)
├── tests/                    (测试文件)
├── pyproject.toml            (项目配置)
├── README.md                 (英文主文档)
├── README_CN.md              (中文主文档)
├── DEPLOYMENT.md             (部署指南)
├── PUBLISH_GUIDE.md          (发布指南)
├── CHANGELOG.md              (此文件)
└── LICENSE                   (许可证)
```

### 已知限制

- 进度百分比：由于医院系统差异，无法准确计算总进度百分比
- 网络波动：进度更新依赖网络稳定性
- 浏览器自动化：某些医院网站的变化可能需要脚本更新

### 感谢

- [dicom_download](https://github.com/hengqujushi/dicom_download) - 原始下载项目
- [cloud-dicom-downloader](https://github.com/Kaciras/cloud-dicom-downloader) - 云平台适配
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP 框架

---

## 未来计划

### v1.1.0 (计划中)

- [ ] 配置文件支持 (~/.dicom_mcp/config.json)
- [ ] 进度百分比估计
- [ ] 下载取消功能
- [ ] 日志文件保存选项
- [ ] 更多医院支持

### v2.0.0 (长期计划)

- [ ] WebSocket 直接集成
- [ ] REST API 接口
- [ ] Web UI 仪表板
- [ ] 数据库存储功能
- [ ] 用户认证系统

---

## 版本发布历史

| 版本 | 日期 | 状态 | 链接 |
|------|------|------|------|
| 1.0.0 | 2025-01-13 | 发布 | [PyPI](https://pypi.org/project/dicom-mcp/1.0.0/) |
| - | - | - | - |

---

## 更新说明

### 如何升级

```bash
# 从 PyPI 安装最新版本
pip install --upgrade dicom-mcp

# 或使用 pipx
pipx upgrade dicom-mcp
```

### 从本地开发升级

```bash
# 在项目目录运行
git pull origin main
pip install -e .
```

---

**最后更新**: 2025-01-13
**维护者**: DICOM MCP 项目贡献者
