# 变更日志

所有对本项目的重要更改都将记录在此文件中。

格式遵循 [Keep a Changelog](https://keepachangelog.com/)，
版本号遵循 [Semantic Versioning](https://semver.org/)。

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
