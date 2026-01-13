# npm 发布指南 - v1.0.0

**[English](#english-version) | [中文](#中文版本)**

---

## 中文版本

### 前置准备

#### 1. 注册 npm 账户

访问 https://www.npmjs.com/signup 创建账户（如未有）

#### 2. 本地登录

```bash
npm login

# 输入用户名、密码、邮箱
# 可选：启用双因素认证 (推荐)
```

#### 3. 验证登录状态

```bash
npm whoami
# 应该显示你的用户名
```

### 发布步骤

#### Step 1: 验证环境

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# 清理旧文件
rm -rf node_modules package-lock.json

# 验证包配置
npm run validate
```

#### Step 2: 更新版本号

编辑 `package.json`：
```json
{
  "version": "1.0.0"
}
```

同时更新 `pyproject.toml`：
```toml
[project]
version = "1.0.0"
```

#### Step 3: 更新 CHANGELOG

已在 `CHANGELOG.md` 中更新 v1.0.0 信息

#### Step 4: Git 提交和标签

```bash
git add -A
git commit -m "Release v1.0.0: npm package with Node.js wrapper"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main
git push origin v1.0.0
```

#### Step 5: 测试本地安装

```bash
# 在临时目录测试
mkdir -p /tmp/test-dicom-mcp
cd /tmp/test-dicom-mcp

# 从本地目录安装
npm install /Users/qinxiaoqiang/Downloads/dicom_mcp

# 测试命令
npx dicom-mcp --help

# 或
npm list -g dicom-mcp
```

#### Step 6: 发布到 npm

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# 执行最终验证
npm run validate

# 发布到 npm registry
npm publish

# 如果这是您第一次发布，可能需要确认许可证
```

#### Step 7: 验证发布成功

```bash
# 在 npm 上查看
npm view dicom-mcp

# 或访问
# https://www.npmjs.com/package/dicom-mcp

# 在新环境测试安装
npm install -g dicom-mcp

# 验证命令
dicom-mcp
```

### 安装验证

用户可以通过以下方式安装：

```bash
# 全局安装（推荐）
npm install -g dicom-mcp

# 启动服务
dicom-mcp

# 或在项目中本地安装
npm install dicom-mcp

# 本地运行
npx dicom-mcp
```

### Claude Desktop 集成

编辑 `~/.config/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "dicom-mcp"
    }
  }
}
```

### 包结构说明

```
dicom-mcp (npm package)
├── bin/
│   └── dicom-mcp.js          (Node.js 启动脚本)
├── scripts/
│   ├── postinstall.js        (安装后脚本)
│   └── validate.js           (验证脚本)
├── package.json              (npm 配置)
├── pyproject.toml            (Python 配置)
├── dicom_mcp/                (Python 源代码)
│   └── server.py
├── README.md                 (英文文档)
├── README_CN.md              (中文文档)
└── LICENSE                   (许可证)
```

### 工作流程

```
npm install -g dicom-mcp
    ↓
npm runs postinstall.js
    ↓
检查 Python 和依赖
    ↓
安装 Python 包
    ↓
用户运行 dicom-mcp
    ↓
bin/dicom-mcp.js 启动
    ↓
验证 Python 环境
    ↓
启动 Python MCP 服务器
    ↓
等待 MCP 请求
```

### 版本更新

#### 小更新 (1.0.1)

```bash
# 更新版本
npm version patch

# 自动更新 package.json 和创建 tag
# 发布
npm publish
```

#### 功能更新 (1.1.0)

```bash
npm version minor
npm publish
```

#### 重大更新 (2.0.0)

```bash
npm version major
npm publish
```

### 故障排除

#### 问题 1: 发布被拒绝 - 已存在版本

**解决**:
```bash
# 更新版本号
npm version patch

# 重新发布
npm publish
```

#### 问题 2: 身份验证失败

**解决**:
```bash
npm logout
npm login

# 重新输入凭证
npm publish
```

#### 问题 3: Python 依赖检查失败

**用户安装时的解决**:
```bash
npm install -g dicom-mcp

# 如果 postinstall 失败，手动安装
pip install mcp pydantic playwright httpx aiofiles pydicom
playwright install chromium
```

#### 问题 4: 许可证问题

确保 `package.json` 中的许可证与 `LICENSE` 文件一致：
```json
{
  "license": "DICOM-MCP Non-Commercial License"
}
```

### 维护和更新

#### 监控 npm 包

```bash
# 查看包信息
npm view dicom-mcp

# 查看下载统计
npm view dicom-mcp downloads

# 查看依赖
npm view dicom-mcp dependencies
```

#### 发布更新

```bash
# 更新 Python 依赖版本
# 编辑 package.json 中的 dependencies

# 更新版本
npm version [patch|minor|major]

# 发布
npm publish
```

---

## English Version

### Prerequisites

#### 1. Create npm Account

Visit https://www.npmjs.com/signup

#### 2. Login Locally

```bash
npm login
```

#### 3. Verify Login

```bash
npm whoami
```

### Publishing Steps

#### Step 1: Verify Environment

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
npm run validate
```

#### Step 2: Update Version

Edit `package.json`:
```json
{
  "version": "1.0.0"
}
```

#### Step 3: Git Commit

```bash
git add -A
git commit -m "Release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main v1.0.0
```

#### Step 4: Test Local Installation

```bash
npm install -g /Users/qinxiaoqiang/Downloads/dicom_mcp
dicom-mcp
```

#### Step 5: Publish to npm

```bash
npm publish
```

#### Step 6: Verify

```bash
npm view dicom-mcp
npm install -g dicom-mcp
dicom-mcp
```

### User Installation

```bash
npm install -g dicom-mcp
dicom-mcp
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `npm login` | Authenticate |
| `npm run validate` | Verify package |
| `npm version patch` | Bump patch version |
| `npm publish` | Publish to npm |
| `npm view dicom-mcp` | Check package info |

---

**Version**: 1.0.0
**License**: DICOM-MCP Non-Commercial License
