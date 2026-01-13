# 部署指南

DICOM MCP 支持两种部署方式：本地开发和包管理器安装。

## 部署方式对比

| 方面 | 本地开发 | 包管理器安装 |
|------|--------|-----------|
| 方法 | git clone + pip install -e . | pip/pipx install dicom-mcp |
| 命令 | python -m dicom_mcp.server | dicom-mcp |
| 适用场景 | 开发、修改、测试 | 生产、简单部署 |
| 依赖关系 | 本地 dicom_download 文件夹 | PyPI 依赖 |

## 方式 1：本地开发部署

适合开发者和需要修改代码的用户。

### 前置条件
- Git
- Python 3.9+
- pip

### 安装步骤

```bash
# Step 1: Clone 仓库（需要 dicom_download 和 dicom_mcp 两个项目）
git clone https://github.com/hengqujushi/dicom_download.git
git clone https://github.com/hengqujushi/dicom_mcp.git

# 确保目录结构如下：
# .
# ├── dicom_download/
# │   ├── multi_download.py
# │   ├── common_utils.py
# │   └── ...
# └── dicom_mcp/
#     ├── dicom_mcp/
#     ├── pyproject.toml
#     └── ...

# Step 2: 安装 dicom_mcp（开发模式）
cd dicom_mcp
pip install -e .

# Step 3: 安装 Playwright 浏览器
playwright install chromium
```

### 运行

```bash
# 作为模块运行
python -m dicom_mcp.server

# 或使用安装的命令
dicom-mcp
```

### 修改和测试

```bash
# 在 dicom_mcp 目录运行单元测试
python test_tools.py

# 启动 MCP Inspector 测试
bash test_mcp_inspector.sh
```

## 方式 2：包管理器安装

适合普通用户和生产环境。

### 前置条件
- Python 3.9+
- pip 或 pipx

### 从 PyPI 安装

```bash
# 使用 pip（与其他包共享环境）
pip install dicom-mcp

# 或使用 pipx（隔离的虚拟环境，推荐）
pipx install dicom-mcp
```

### 运行

```bash
# 直接运行命令
dicom-mcp

# 或作为模块
python -m dicom_mcp.server
```

### 升级

```bash
# pip 升级
pip install --upgrade dicom-mcp

# pipx 升级
pipx upgrade dicom-mcp
```

### 卸载

```bash
# pip 卸载
pip uninstall dicom-mcp

# pipx 卸载
pipx uninstall dicom-mcp
```

## 目录结构说明

### 本地开发模式

```
parent_dir/
├── dicom_download/               ← 必需的下载脚本
│   ├── multi_download.py
│   ├── common_utils.py
│   ├── shdc_download_dicom.py
│   ├── tjmucih_download_dicom.py
│   ├── nyfy_download_dicom.py
│   └── cloud-dicom-downloader/
└── dicom_mcp/                    ← MCP 服务器
    ├── dicom_mcp/
    │   ├── __init__.py
    │   └── server.py
    ├── pyproject.toml
    └── README.md
```

服务器会自动在上级目录寻找 `dicom_download` 文件夹。

### 包管理器安装模式

```
site-packages/
├── dicom_mcp/                    ← 已安装的包
│   ├── __init__.py
│   └── server.py
└── dicom_download/               ← 作为依赖自动安装
    ├── multi_download.py
    └── ...
```

服务器会自动在 Python path 中查找 `dicom_download`。

## 路径解析逻辑

服务器使用以下优先级查找 `dicom_download`：

1. **本地开发路径** (最高优先级)
   - `../dicom_download/` (相对于 server.py)
   - 用于 git clone 开发场景

2. **已安装的模块**
   - 通过 `import dicom_download` 查找
   - 用于 pip/pipx 安装场景

3. **Python path 搜索**
   - 遍历 `sys.path` 查找 `dicom_download`
   - 作为备选方案

4. **回退** (最低优先级)
   - 如果以上都找不到，使用本地开发路径作为默认

## Claude Desktop 集成

### 本地开发模式配置

编辑 `~/.config/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/dicom_mcp:/path/to/dicom_download"
      }
    }
  }
}
```

### 包管理器安装模式配置

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "dicom-mcp"
    }
  }
}
```

或

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"]
    }
  }
}
```

## 故障排除

### 问题：找不到 dicom_download

**症状**: `RuntimeError: multi_download.py not found`

**解决**：
1. 检查是否在正确的目录：
   ```bash
   ls ../dicom_download/multi_download.py  # 本地开发
   pip list | grep dicom  # 包安装
   ```
2. 确认已安装 dicom-mcp：
   ```bash
   pip list | grep dicom-mcp
   ```
3. 重新安装：
   ```bash
   pip install --force-reinstall dicom-mcp
   ```

### 问题：模块导入失败

**症状**: `ModuleNotFoundError: No module named 'dicom_mcp'`

**解决**（本地开发）：
```bash
cd dicom_mcp
pip install -e .
```

**解决**（包安装）：
```bash
pip install dicom-mcp
```

### 问题：Claude Desktop 无法连接

**症状**: "Server connection refused"

**解决**：
1. 测试服务器是否能直接运行：
   ```bash
   dicom-mcp
   ```
2. 检查 Claude 配置是否正确
3. 重启 Claude Desktop

## 发布到 PyPI

为了让用户能通过 `pip install dicom-mcp` 安装，需要发布到 PyPI。

### 发布步骤

```bash
# 1. 安装构建工具
pip install build twine

# 2. 更新版本号 (pyproject.toml)
# 修改 version = "X.Y.Z"

# 3. 构建包
python -m build

# 4. 上传到 PyPI
python -m twine upload dist/*

# 5. 验证安装
pip install dicom-mcp
dicom-mcp --version
```

### 环境变量

创建 `~/.pypirc` 存储 PyPI 认证信息：

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

## 配置文件

### 本地配置（可选）

创建 `~/.config/dicom_mcp/config.json`：

```json
{
  "default_output_dir": "./dicom_downloads",
  "default_headless": true,
  "default_max_rounds": 3,
  "default_step_wait_ms": 40
}
```

注：当前版本还不支持此功能，但未来可以添加。

## 更新日志

### v0.3.0 (2025-01-13)
- ✅ 支持两种部署方式
- ✅ 灵活的路径解析
- ✅ 完整的部署文档
- ✅ PyPI 发布准备
- ✅ 进度反馈功能
- ✅ 实时输出流

### v0.2.0 (2025-01-13)
- 扫描参数支持
- 文档完善

### v0.1.0 (2025-01-13)
- 初始版本
- 5 个 MCP 工具
- 4 家医院支持

## 问题反馈

如遇到部署问题，请：

1. 检查日志中的错误信息
2. 查阅相关文档
3. 提交 Issue：https://github.com/hengqujushi/dicom_mcp/issues

## 许可证

本项目采用 **DICOM MCP 非商业许可证**。

### 关键点

✓ **允许**：
- 个人学习和研究
- 非营利性教学
- 学术用途
- 修改源代码

✗ **禁止**：
- 直接或间接的商业使用
- 出售或收费服务
- 在商业产品中集成
- 营利性医疗应用

⚠️ **必须**：
- 保留许可证声明
- 署名原作者
- 遵守医疗数据隐私法规

### 商业使用

如需在商业项目中使用，请联系：
📧 support@dicom-mcp.com

详见 LICENSE 文件
