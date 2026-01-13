# 快速参考卡片

## 三种启动 MCP Inspector 的方式

### 最简单 (推荐)
```bash
bash /Users/qinxiaoqiang/Downloads/dicom_mcp/test_mcp_inspector.sh
```

### 手动
```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
pip install -e .
npx @modelcontextprotocol/inspector python -m dicom_mcp.server
```

### 两个终端
**终端 1:**
```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
python -m dicom_mcp.server
```

**终端 2:**
```bash
npx @modelcontextprotocol/inspector
```

---

## 浏览器访问
```
http://localhost:5173
```

---

## 5 个可用工具

| 工具 | 主要参数 | 功能 |
|------|---------|------|
| `list_supported_providers` | 无 | 列出 4 个医院 |
| `detect_provider_from_url` | `url` | 识别医院 |
| `validate_url` | `url` | 验证 URL |
| `download_dicom` | `url`, `output_dir`, `max_rounds`, `step_wait_ms` | 单 URL 下载 |
| `batch_download_dicom` | `urls`, `output_parent`, `max_rounds`, `step_wait_ms` | 批量下载 |

---

## 测试用 URL

```
# 天肿
https://zlyy.tjmucih.cn/viewer?share_id=ABC123

# 复肿
https://ylyyx.shdc.org.cn/viewer?share_id=ABC123

# 宁夏总医院
https://zhyl.nyfy.com.cn/viewer?share_id=ABC123

# 云平台
https://example.medicalimagecloud.com/viewer?id=ABC123

# 无效 URL (测试错误处理)
not-a-valid-url
```

---

## 快速测试 (2 分钟)

1. 启动 Inspector → http://localhost:5173
2. 点击 `list_supported_providers` → 点击执行
3. 看到 4 个医院列表 ✓
4. 点击 `detect_provider_from_url`
5. 输入 URL: `https://zlyy.tjmucih.cn/viewer?share_id=ABC123`
6. 点击执行，看到返回 `"detected_provider": "tz"` ✓

## 参数速查表

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `url` | 必需 | 医院影像查看器 URL |
| `output_dir` | `./dicom_downloads` | 输出目录 |
| `provider` | `auto` | 提供者 (tz/fz/nyfy/cloud) |
| `mode` | `all` | 下载模式 (all/diag/nondiag) |
| `headless` | `true` | 是否无界面运行 |
| `create_zip` | `true` | 是否创建 ZIP |
| `max_rounds` | `3` | 扫描轮数（越多越完整） |
| `step_wait_ms` | `40` | 帧间延迟ms（越长越稳定） |

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 页面空白 | F5 刷新或手动访问 http://localhost:5173 |
| 模块找不到 | `pip install -e .` |
| 参数输入问题 | 单参数直接输入，多参数用 JSON |
| 执行很慢 | download_dicom 需要时间，用其他工具先测 |

---

## 工具返回示例

### list_supported_providers
```json
[
  {
    "name": "tz",
    "display_name": "天肿 (圆心云影)",
    "domains": ["zlyy.tjmucih.cn"],
    "description": "..."
  },
  // ... 3 个更多
]
```

### detect_provider_from_url
```json
{
  "url": "https://zlyy.tjmucih.cn/viewer?share_id=ABC123",
  "detected_provider": "tz",
  "provider_info": { ... },
  "is_auto_detected": true
}
```

### validate_url (有效)
```json
{
  "valid": true,
  "url": "https://zlyy.tjmucih.cn/viewer?share_id=ABC123",
  "provider": "tz",
  "message": "URL belongs to tz provider"
}
```

### validate_url (无效)
```json
{
  "valid": false,
  "url": "not-a-valid-url",
  "error": "Invalid URL format",
  "suggestion": "URL must include scheme (http/https) and domain"
}
```

---

## 完整文档

| 文件 | 用途 |
|------|------|
| MANUAL_TESTING.md | 详细测试指南 |
| SETUP_GUIDE.md | 安装和配置 |
| QUICKSTART.md | 5 分钟快速开始 |
| ARCHITECTURE.md | 技术设计 |
| README.md | 完整参考 |

---

**记住**: 测试成功的标志是能看到 5 个工具都在 Web 界面显示！
