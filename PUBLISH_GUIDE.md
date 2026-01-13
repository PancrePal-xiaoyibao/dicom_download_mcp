# PyPI 发布指南 - v1.0.0

**[English](#english-version) | [中文](#中文版本)**

---

## 中文版本

### 前置准备

#### 1. 安装必要工具

```bash
# 安装构建和发布工具
pip install build twine keyring

# 验证安装
python -m build --version
twine --version
```

#### 2. 配置 PyPI 账户

##### 方案 A: 使用 API Token（推荐）

1. 访问 https://pypi.org/account/tokens/
2. 创建新的 API Token
3. 将 token 保存到 `~/.pypirc`：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 你的 token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 你的测试 token
```

##### 方案 B: 使用用户名和密码

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = your_username
password = your_password
```

#### 3. 文件权限

确保 `.pypirc` 权限正确：
```bash
chmod 600 ~/.pypirc
```

### 发布步骤

#### Step 1: 更新版本号

编辑 `pyproject.toml`：
```toml
[project]
version = "1.0.0"  # 更新版本
```

#### Step 2: 更新变更日志

编辑 `CHANGELOG.md`（创建新文件）：
```markdown
## [1.0.0] - 2025-01-13

### Added
- 完整的中英文文档
- 两种部署方式（本地开发 + PyPI 包）
- 非商业使用许可证
- 实时进度反馈功能
- 5 个 MCP 工具
- 4 家医院支持

### Changed
- 改进了错误消息
- 优化了代码结构

### Fixed
- 修复了路径解析问题
```

#### Step 3: 提交 Git 变更

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# 添加所有文件
git add -A

# 提交更改
git commit -m "Release v1.0.0: Complete package with docs and license"

# 创建 tag
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送到远程
git push origin main
git push origin v1.0.0
```

#### Step 4: 清理旧文件

```bash
# 清理之前的构建文件
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
```

#### Step 5: 构建包

```bash
# 构建 wheel 和源代码包
python -m build

# 验证构建输出
ls -lah dist/
# 应该看到：
# dicom_mcp-1.0.0-py3-none-any.whl
# dicom_mcp-1.0.0.tar.gz
```

#### Step 6: 验证包内容（可选但推荐）

```bash
# 检查 wheel 文件
unzip -l dist/dicom_mcp-1.0.0-py3-none-any.whl | head -20

# 检查源代码包
tar -tzf dist/dicom_mcp-1.0.0.tar.gz | head -20
```

#### Step 7: 测试上传到 TestPyPI（可选但强烈推荐）

```bash
# 上传到测试服务器
python -m twine upload --repository testpypi dist/*

# 在另一个虚拟环境测试安装
pip install -i https://test.pypi.org/simple/ dicom-mcp

# 测试命令
dicom-mcp --version
```

#### Step 8: 上传到 PyPI（正式发布）

```bash
# 上传到 PyPI
python -m twine upload dist/*

# 系统会提示输入用户名和密码（如使用 token，用户名是 __token__）

# 验证上传成功
# 访问 https://pypi.org/project/dicom-mcp/
```

### 验证发布成功

#### 方法 1: 在 PyPI 上检查

1. 访问 https://pypi.org/project/dicom-mcp/
2. 验证版本是 1.0.0
3. 检查所有文件都已上传

#### 方法 2: 安装验证

在新的虚拟环境中：

```bash
# 创建新的虚拟环境
python -m venv test_env
source test_env/bin/activate

# 从 PyPI 安装
pip install dicom-mcp

# 验证安装
python -c "import dicom_mcp; print(dicom_mcp.__version__)"

# 验证命令行工具
dicom-mcp --help
```

#### 方法 3: 检查元数据

```bash
# 安装后查看元数据
pip show dicom-mcp

# 应该看到：
# Name: dicom-mcp
# Version: 1.0.0
# Summary: MCP server for DICOM image downloading...
# License: DICOM-MCP Non-Commercial License
```

### 发布后的任务

#### 1. 更新项目主页

在 GitHub 上：
1. 创建 Release: https://github.com/hengqujushi/dicom_mcp/releases
2. 标签: v1.0.0
3. 标题: "Release v1.0.0"
4. 描述: 从 CHANGELOG.md 复制内容

#### 2. 通知用户

- 更新文档中的安装说明
- 在 issue tracker 中标记为已解决
- 发布公告（如有社区渠道）

#### 3. 准备下一个版本

```bash
# 更新版本为开发版本
# pyproject.toml: version = "1.1.0-dev"

git commit -m "Start development for v1.1.0"
git push origin main
```

### 故障排除

#### 问题 1: 上传被拒绝 - 已存在版本

**原因**: 同一版本号只能上传一次

**解决**:
```bash
# 删除本地旧文件
rm -rf dist/

# 更新版本号
# pyproject.toml: version = "1.0.1"

# 重新构建
python -m build

# 重新上传
python -m twine upload dist/*
```

#### 问题 2: 身份验证失败

**原因**: 用户名或密码错误

**解决**:
```bash
# 使用命令行参数而不是 .pypirc
python -m twine upload \
  --username __token__ \
  --password pypi-... \
  dist/*

# 或重新配置 .pypirc
nano ~/.pypirc
```

#### 问题 3: 缺少必需的元数据

**原因**: pyproject.toml 缺少必需字段

**解决**: 检查以下字段都已填充：
- `name`
- `version`
- `description`
- `readme`
- `license`
- `authors`

#### 问题 4: 文件太大

**原因**: 包含了不必要的文件

**解决**: 
```bash
# 更新 MANIFEST.in 排除大文件
# 重新构建

# 或使用 setuptools 配置限制
# 检查 .gitignore 是否已应用
```

### 版本管理策略

#### 语义化版本 (Semantic Versioning)

遵循 MAJOR.MINOR.PATCH 格式：

```
1.0.0
│ │ └─ PATCH: 错误修复
│ └─── MINOR: 新功能 (向后兼容)
└───── MAJOR: 重大变更 (可能不兼容)
```

#### 版本更新指南

- **1.0.0** → **1.0.1**: Bug 修复
- **1.0.0** → **1.1.0**: 新功能
- **1.0.0** → **2.0.0**: 重大变更

### 维护 PyPI 包

#### 定期更新

```bash
# 更新依赖版本
pip list --outdated

# 更新 pyproject.toml 中的依赖
# 运行测试
python test_tools.py

# 提交变更
git add -A
git commit -m "Update dependencies"
```

#### 安全更新

监控依赖的安全漏洞：

```bash
# 使用 safety 检查
pip install safety
safety check
```

#### 弃用政策

如需弃用某个版本：

```bash
# 访问 PyPI 项目设置
# https://pypi.org/project/dicom-mcp/

# 标记为已弃用
# 添加到 release notes
```

---

## English Version

### Prerequisites

#### 1. Install Required Tools

```bash
# Install build and publish tools
pip install build twine keyring

# Verify installation
python -m build --version
twine --version
```

#### 2. Configure PyPI Account

##### Option A: Using API Token (Recommended)

1. Visit https://pypi.org/account/tokens/
2. Create a new API Token
3. Save to `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your test token
```

##### Option B: Using Username and Password

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = your_username
password = your_password
```

#### 3. File Permissions

```bash
chmod 600 ~/.pypirc
```

### Publishing Steps

#### Step 1: Update Version Number

Edit `pyproject.toml`:
```toml
[project]
version = "1.0.0"
```

#### Step 2: Update Changelog

Create/Edit `CHANGELOG.md`:
```markdown
## [1.0.0] - 2025-01-13

### Added
- Complete Chinese and English documentation
- Two deployment methods
- Non-commercial license
- Real-time progress feedback
- 5 MCP tools
- 4 hospital support

### Changed
- Improved error messages
- Optimized code structure

### Fixed
- Fixed path resolution issues
```

#### Step 3: Commit Git Changes

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

git add -A
git commit -m "Release v1.0.0: Complete package with docs and license"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main
git push origin v1.0.0
```

#### Step 4: Clean Old Files

```bash
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
```

#### Step 5: Build Package

```bash
python -m build

ls -lah dist/
```

#### Step 6: Test Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*

# In another venv:
pip install -i https://test.pypi.org/simple/ dicom-mcp
dicom-mcp --help
```

#### Step 7: Upload to PyPI

```bash
python -m twine upload dist/*
```

Visit https://pypi.org/project/dicom-mcp/ to verify.

#### Step 8: Verify Installation

```bash
# In new venv
python -m venv test_env
source test_env/bin/activate

pip install dicom-mcp
dicom-mcp --help
```

### Post-Release Tasks

1. Create GitHub Release
2. Update documentation
3. Notify users
4. Prepare for next version

### Troubleshooting

See Chinese version above for common issues and solutions.

---

## Quick Reference

| Step | Command | Notes |
|------|---------|-------|
| Build | `python -m build` | Creates .whl and .tar.gz |
| Test Upload | `twine upload --repository testpypi dist/*` | Use test server first |
| Publish | `twine upload dist/*` | Final release to PyPI |
| Verify | `pip install dicom-mcp` | Install from PyPI |

---

**Version**: 1.0.0
**Date**: 2025-01-13
**License**: DICOM-MCP Non-Commercial License
