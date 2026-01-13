# MCP Inspector 手动测试指南

## 准备工作

### Step 1: 验证环境

```bash
# 检查 Node.js
node --version
# 应该输出: v22.x.x 或更新

# 检查 npm
npm --version
# 应该输出: 9.x.x 或更新

# 检查 Python
python --version
# 应该输出: Python 3.9+

# 检查 MCP 项目是否安装
pip list | grep mcp
# 应该看到: mcp xxx
```

### Step 2: 进入项目目录

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
```

## 启动 MCP Inspector

### 方法 A: 使用脚本（推荐）

最简单的方式，一行命令启动：

```bash
bash test_mcp_inspector.sh
```

脚本会：
1. 检查依赖
2. 自动安装 MCP 项目（如果需要）
3. 启动 Inspector
4. 在浏览器中打开 Web 界面

### 方法 B: 手动启动（更清楚）

如果你想看到每一步的细节：

```bash
# 确保项目已安装
pip install -e .

# 启动 Inspector (会在终端输出)
npx @modelcontextprotocol/inspector python -m dicom_mcp.server
```

**预期输出**:
```
Starting MCP Inspector...
🚀 Server process started with PID: 12345
📡 Connecting to server...
✓ Connected to server
🌐 Inspector server listening on http://localhost:5173
```

### 方法 C: 在另一个终端启动（用于调试）

如果你想分别监看服务器和 Inspector：

**终端 1 - 启动 MCP 服务器**:
```bash
python -m dicom_mcp.server
```

应该看到类似的输出（等待连接）。

**终端 2 - 启动 Inspector**:
```bash
npx @modelcontextprotocol/inspector
```

然后输入服务器命令（会提示）。

## Web 界面导览

### 打开浏览器

当看到 `🌐 Inspector server listening on http://localhost:5173` 时：

1. 自动打开浏览器，或
2. 手动访问 `http://localhost:5173`

### Web 界面说明

```
┌─────────────────────────────────────────────────────────┐
│  MCP Inspector - localhost:5173                    X    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  左侧面板                右侧面板                      │
│  ┌──────────┐         ┌────────────────┐               │
│  │ 可用工具 │         │  工具参数输入  │               │
│  ├──────────┤         ├────────────────┤               │
│  │ 1. list_│         │ 参数 1: ___   │               │
│  │    supported       │ 参数 2: ___   │               │
│  │ 2. detect_         │ [执行] [重置] │               │
│  │    provider        │               │               │
│  │ 3. validate        └────────────────┘               │
│  │ 4. download        ┌────────────────┐               │
│  │ 5. batch           │    返回结果    │               │
│  │    download        │ (JSON 格式)    │               │
│  │                    │                │               │
│  │                    │                │               │
│  └──────────┘         └────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 交互式测试

### 测试 1: 列出支持的医院

1. **左侧面板** 找到 `list_supported_providers`
2. **点击** 该工具
3. **右侧面板** 应该显示 (无需输入参数)
4. **点击 "执行"** 或 **"Call Tool"** 按钮
5. **查看结果** - 应该返回 4 个医院的信息

**预期返回值**:
```json
[
  {
    "name": "tz",
    "display_name": "天肿 (圆心云影)",
    "domains": ["zlyy.tjmucih.cn"],
    "description": "Tianjin Medical University Cancer Institute..."
  },
  ... (更多医院)
]
```

### 测试 2: 检测医院 (detect_provider_from_url)

1. **点击** 左侧的 `detect_provider_from_url`
2. **在右侧输入框** 输入参数:
   ```
   url: https://zlyy.tjmucih.cn/viewer?share_id=ABC123
   ```
3. **点击执行**
4. **查看结果** - 应该识别为 "tz"

**尝试不同的 URL**:

点击 "执行" 后，修改 URL 再次执行：

```
测试 1:
  url: https://ylyyx.shdc.org.cn/viewer?share_id=XYZ
  → 应识别为 "fz"

测试 2:
  url: https://zhyl.nyfy.com.cn/viewer?share_id=ABC
  → 应识别为 "nyfy"

测试 3:
  url: https://example.medicalimagecloud.com/viewer?id=123
  → 应识别为 "cloud"

测试 4:
  url: https://unknown-hospital.com/viewer
  → 应默认识别为 "fz"
```

### 测试 3: URL 验证 (validate_url)

1. **点击** `validate_url`
2. **输入有效的 URL**:
   ```
   url: https://zlyy.tjmucih.cn/viewer?share_id=ABC123
   ```
3. **点击执行**
4. **查看结果** - 应返回 `valid: true` 和医院信息

**测试无效 URL**:

```
测试 1:
  url: not-a-valid-url
  → 应返回 valid: false, error: "Invalid URL format"

测试 2:
  url: https://
  → 应返回 valid: false

测试 3:
  url: https://ylyyx.shdc.org.cn/viewer?share_id=ABC123
  → 应返回 valid: true, provider: "fz"
```

### 测试 4: 下载请求模型 (download_dicom)

⚠️ **注意**: 这个工具会实际尝试下载，需要有效的 URL。

**模拟测试** (不会实际下载):

1. **点击** `download_dicom`
2. **输入参数**:
   ```
   url: https://zlyy.tjmucih.cn/viewer?share_id=TEST_URL
   output_dir: ./test_downloads
   provider: auto
   mode: all
   headless: true
   password: (留空)
   create_zip: true
   ```
3. **点击执行**

**预期行为**:
- 如果 URL 无效或已过期 → 返回错误
- 如果有有效的真实 URL → 开始下载 (需要等待)

### 测试 5: 批量下载 (batch_download_dicom)

类似下载单个 URL，但输入多个 URL：

1. **点击** `batch_download_dicom`
2. **输入参数**:
   ```
   urls: [
     "https://zlyy.tjmucih.cn/viewer?share_id=STUDY1",
     "https://ylyyx.shdc.org.cn/viewer?share_id=STUDY2"
   ]
   output_parent: ./batch_downloads
   provider: auto
   mode: all
   headless: true
   create_zip: true
   ```
3. **点击执行**

## Web 界面按钮说明

| 按钮 | 功能 | 说明 |
|------|------|------|
| Call Tool / 执行 | 调用选中的工具 | 发送参数到服务器 |
| Reset / 重置 | 清空输入框 | 回到初始状态 |
| Clear / 清除 | 清空结果面板 | 隐藏之前的结果 |

## 查看详细信息

### 查看原始 JSON 响应

在返回结果下方，通常有选项查看：
- **Formatted** - 格式化的可读结果
- **Raw** 或 **JSON** - 完整的 JSON 返应
- **Pretty** - 缩进的 JSON

### 查看服务器日志

**在启动 Inspector 的终端中**，会看到实时日志：

```
[2025-01-13 10:45:23] Tool called: list_supported_providers
[2025-01-13 10:45:23] ✓ Returned 4 providers
[2025-01-13 10:45:24] Tool called: detect_provider_from_url
[2025-01-13 10:45:24] Input: {"url": "https://zlyy.tjmucih.cn/..."}
[2025-01-13 10:45:24] ✓ Detected provider: tz
```

## 常见问题

### 问题 1: "Cannot find module 'mcp'"

**解决**:
```bash
pip install -e /Users/qinxiaoqiang/Downloads/dicom_mcp
```

### 问题 2: Inspector 页面空白

**解决**:
1. 刷新浏览器 (F5 或 Cmd+R)
2. 检查浏览器控制台 (F12 → Console) 看是否有错误
3. 检查服务器是否正常运行

### 问题 3: "Server connection refused"

**解决**:
```bash
# 确保 MCP 服务器正在运行
python -m dicom_mcp.server

# 在另一个终端启动 Inspector
npx @modelcontextprotocol/inspector python -m dicom_mcp.server
```

### 问题 4: 无法输入参数

**可能原因**:
- 工具不需要参数 (如 list_supported_providers)
- JSON 格式错误

**解决**:
- 复制示例参数
- 确保 JSON 有效 (可用 JSON 验证器检查)

## 完整测试场景

### 快速健康检查 (5 分钟)

```
1. 启动 Inspector
   bash test_mcp_inspector.sh

2. 测试 list_supported_providers()
   → 应返回 4 个医院

3. 测试 detect_provider_from_url()
   输入: https://ylyyx.shdc.org.cn/viewer?share_id=TEST
   → 应返回 provider: "fz"

4. 测试 validate_url()
   输入: https://unknown.com/viewer
   → 应返回 valid: false

5. 关闭 Inspector (Ctrl+C)
```

✓ 如果以上 4 个测试都通过，说明 MCP 服务器正常工作

### 完整测试套件 (20 分钟)

```
1. list_supported_providers()
   检查返回 4 个医院 ✓

2. detect_provider_from_url() - 4 个 URL
   - zlyy.tjmucih.cn → tz ✓
   - ylyyx.shdc.org.cn → fz ✓
   - zhyl.nyfy.com.cn → nyfy ✓
   - *.medicalimagecloud.com → cloud ✓

3. validate_url() - 有效和无效
   - 有效 URL → valid: true ✓
   - 无效 URL → valid: false ✓

4. download_dicom() - 模型验证
   检查参数接受和默认值 ✓

5. batch_download_dicom() - 批量模型
   检查列表参数处理 ✓
```

## 导出测试结果

### 截图

在 Inspector 中：
1. 执行一个工具
2. 等待结果返回
3. 使用浏览器的截图功能 (Chrome DevTools)

### 保存 JSON 响应

1. 右击结果面板
2. 选择 "Copy" 或 "Export"
3. 粘贴到文本编辑器

### 生成报告

```bash
# 运行自动化测试并保存结果
python test_tools.py > test_results.txt 2>&1

# 查看结果
cat test_results.txt
```

## 故障排除

### 检查清单

- [ ] Node.js 已安装 (node --version)
- [ ] npm 已安装 (npm --version)
- [ ] Python 3.9+ (python --version)
- [ ] MCP 项目已安装 (pip install -e .)
- [ ] Playwright 已安装 (python -c "from playwright.async_api import async_playwright")
- [ ] 防火墙允许 localhost:5173

### 调试模式

启动 Inspector 时查看详细日志：

```bash
# 启用详细日志
DEBUG=* npx @modelcontextprotocol/inspector python -m dicom_mcp.server
```

## 下一步

完成 MCP Inspector 测试后：

1. ✅ **完成本地测试** (你在这里)
2. **配置 Claude Desktop**
   - 见 SETUP_GUIDE.md
   - 编辑 `~/.config/Claude/claude_desktop_config.json`
3. **在 Claude 中测试**
   - 问: "What DICOM providers are supported?"
   - 问: "Is this URL valid? https://..."
4. **实际下载测试**
   - 用真实的医院 URL 进行下载

## 获取帮助

- MCP Inspector 文档: https://github.com/modelcontextprotocol/inspector
- 项目文档: 见 README.md 和其他 .md 文件
- 问题报告: 检查 server.py 中的错误处理逻辑

---

**祝你测试顺利！** 🚀
