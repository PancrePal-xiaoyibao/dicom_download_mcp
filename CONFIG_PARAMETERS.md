# MCP 配置参数说明

## 新增参数

MCP 服务器现已支持以下扩展参数：

### 1. 扫描次数 (max_rounds)
- **参数名**: `max_rounds`
- **类型**: 整数 (int)
- **默认值**: 3
- **描述**: 逐帧播放的扫描轮数上限
- **适用**: 复肿 (fz) 提供者

### 2. 延迟时间 (step_wait_ms)
- **参数名**: `step_wait_ms`
- **类型**: 整数 (int)
- **默认值**: 40
- **单位**: 毫秒 (ms)
- **描述**: 逐帧播放时，每一帧之间的延迟时间
- **适用**: 复肿 (fz) 提供者

## 在 MCP Tools 中的使用

### download_dicom (单 URL 下载)

**参数列表**:
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./downloads",
  "provider": "auto",
  "mode": "all",
  "headless": true,
  "password": null,
  "create_zip": true,
  "max_rounds": 3,
  "step_wait_ms": 40
}
```

**示例 1: 默认参数**
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./downloads"
}
```

**示例 2: 自定义扫描参数**
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./downloads",
  "max_rounds": 5,
  "step_wait_ms": 50
}
```

**示例 3: 加快扫描（较少轮数，更短延迟）**
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./downloads",
  "max_rounds": 2,
  "step_wait_ms": 30
}
```

**示例 4: 完整扫描（更多轮数，更长延迟）**
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./downloads",
  "max_rounds": 5,
  "step_wait_ms": 100
}
```

### batch_download_dicom (批量 URL 下载)

**参数列表**:
```json
{
  "urls": [
    "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
    "https://ylyyx.shdc.org.cn/viewer?share_id=DEF456"
  ],
  "output_parent": "./downloads",
  "provider": "auto",
  "mode": "all",
  "headless": true,
  "create_zip": true,
  "max_rounds": 3,
  "step_wait_ms": 40
}
```

**示例: 批量下载带自定义扫描参数**
```json
{
  "urls": [
    "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
    "https://ylyyx.shdc.org.cn/viewer?share_id=DEF456"
  ],
  "output_parent": "./batch_downloads",
  "max_rounds": 5,
  "step_wait_ms": 50
}
```

## 参数选择建议

### 场景 1: 快速下载 (推荐用于时间紧张)
```
max_rounds: 2
step_wait_ms: 30
```
- 扫描 2 轮
- 每帧延迟 30ms
- 总耗时最少
- 可能遗漏部分帧

### 场景 2: 平衡速度和完整性 (推荐用于常规下载)
```
max_rounds: 3
step_wait_ms: 40
```
- 扫描 3 轮
- 每帧延迟 40ms
- 默认配置
- 在速度和完整性之间平衡

### 场景 3: 完整下载 (推荐用于重要数据)
```
max_rounds: 5
step_wait_ms: 80
```
- 扫描 5 轮
- 每帧延迟 80ms
- 总耗时较长
- 最大可能获得所有帧

### 场景 4: 深度扫描 (推荐用于大数据集)
```
max_rounds: 10
step_wait_ms: 100
```
- 扫描 10 轮
- 每帧延迟 100ms
- 总耗时最长
- 最详尽的扫描

## 在 Claude 中使用

在 Claude 中与 MCP 交互时，可以这样指定参数：

```
"Download DICOM from https://ylyyx.shdc.org.cn/viewer?share_id=ABC123 
with 5 scan rounds and 50ms delay between frames,
save to ./my_downloads"
```

Claude 会自动将其转换为:
```json
{
  "url": "https://ylyyx.shdc.org.cn/viewer?share_id=ABC123",
  "output_dir": "./my_downloads",
  "max_rounds": 5,
  "step_wait_ms": 50
}
```

## 技术细节

### 参数传递链路

```
Claude/MCP Inspector
    ↓
download_dicom(DownloadRequest)
    ↓
request.max_rounds, request.step_wait_ms
    ↓
run_multi_download(..., max_rounds, step_wait_ms)
    ↓
--max-rounds X --step-wait-ms Y
    ↓
multi_download.py
    ↓
shdc_download_dicom.py
```

### 实现代码

```python
# server.py 中的数据模型
class DownloadRequest(BaseModel):
    max_rounds: int = Field(
        default=3,
        description="Maximum number of scan rounds (扫描次数，默认 3)",
    )
    step_wait_ms: int = Field(
        default=40,
        description="Delay between steps in milliseconds (延迟时间，默认 40ms)",
    )

# 传递给 multi_download.py
cmd.extend(["--max-rounds", str(max_rounds)])
cmd.extend(["--step-wait-ms", str(step_wait_ms)])
```

## 兼容性

- ✅ download_dicom: 完全支持
- ✅ batch_download_dicom: 完全支持
- ⚠️ detect_provider_from_url: 不适用
- ⚠️ validate_url: 不适用
- ⚠️ list_supported_providers: 不适用

## 其他参数速查表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| url | string | 必需 | 医院影像查看器 URL |
| output_dir | string | ./dicom_downloads | 输出目录 |
| provider | string | auto | 提供者类型 (tz/fz/nyfy/cloud) |
| mode | string | all | 下载模式 (all/diag/nondiag) |
| headless | bool | true | 是否无界面运行 |
| password | string | null | 分享密码或验证码 |
| create_zip | bool | true | 是否创建 ZIP 压缩包 |
| max_rounds | int | 3 | 扫描轮数 |
| step_wait_ms | int | 40 | 帧间延迟 (毫秒) |

## 故障排除

### 问题: 下载速度很慢
**解决**:
- 减少 `max_rounds` (如从 5 改为 2)
- 减少 `step_wait_ms` (如从 80 改为 30)

### 问题: 下载文件不完整
**解决**:
- 增加 `max_rounds` (如从 3 改为 5)
- 增加 `step_wait_ms` (如从 40 改为 80)

### 问题: 浏览器超时
**解决**:
- 减少 `max_rounds`
- 减少 `step_wait_ms`
- 确保网络连接稳定

## 更新日志

### v0.2.0 (2025-01-13)
- ✅ 添加 `max_rounds` 参数
- ✅ 添加 `step_wait_ms` 参数
- ✅ 更新 DownloadRequest 和 BatchDownloadRequest 模型
- ✅ 完整的参数文档和使用示例
