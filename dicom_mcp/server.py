"""MCP server for DICOM image downloading."""

import os
import sys
import json
import asyncio
import tempfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Union, Dict
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Resolve path to dicom_download - supports multiple deployment methods:
# 1. Local development: git clone后，dicom_download 在 dicom_mcp 的上级目录
# 2. NPM package: npx安装时，dicom_download 在node_modules同级
# 3. Installed package: 从 PyPI 安装时，dicom_download 作为依赖已安装
def _resolve_dicom_download_path() -> Path:
    """Resolve path to dicom_download module."""
    current_dir = Path(__file__).parent
    
    # Method 1: Local development - check parent directory
    local_dev_path = current_dir.parent.parent / "dicom_download"
    if local_dev_path.exists() and (local_dev_path / "multi_download.py").exists():
        print(f"[dicom-mcp] Found dicom_download at: {local_dev_path}", file=sys.stderr)
        return local_dev_path
    
    # Method 2: NPM package - check in the same package directory
    npm_pkg_path = current_dir.parent / "dicom_download"
    if npm_pkg_path.exists() and (npm_pkg_path / "multi_download.py").exists():
        print(f"[dicom-mcp] Found dicom_download at: {npm_pkg_path}", file=sys.stderr)
        return npm_pkg_path
    
    # Method 3: Check site-packages or installation location
    try:
        import dicom_download as dd_module
        if dd_module.__file__:
            dd_path = Path(dd_module.__file__).parent
            if (dd_path / "multi_download.py").exists():
                print(f"[dicom-mcp] Found dicom_download at: {dd_path}", file=sys.stderr)
                return dd_path
    except ImportError:
        pass
    
    # Method 4: Try to find in Python path
    for path_item in sys.path:
        candidate = Path(path_item) / "dicom_download"
        if candidate.exists() and (candidate / "multi_download.py").exists():
            print(f"[dicom-mcp] Found dicom_download at: {candidate}", file=sys.stderr)
            return candidate
    
    # Fallback - return the most likely path with diagnostic message
    print(f"[dicom-mcp] WARNING: Could not find dicom_download. Tried paths:", file=sys.stderr)
    print(f"  1. {local_dev_path}", file=sys.stderr)
    print(f"  2. {npm_pkg_path}", file=sys.stderr)
    print(f"  3. Python path entries", file=sys.stderr)
    return local_dev_path

DICOM_DOWNLOAD_PATH = _resolve_dicom_download_path()
if DICOM_DOWNLOAD_PATH.exists():
    sys.path.insert(0, str(DICOM_DOWNLOAD_PATH))

mcp = FastMCP("dicom-downloader")


# ============================================================================
# Configuration from environment variables
# ============================================================================

# 从环境变量读取配置，支持在 Claude Desktop 中预设默认值
_DEFAULT_OUTPUT_DIR = os.getenv("DICOM_DEFAULT_OUTPUT_DIR", "./dicom_downloads")
_DEFAULT_MAX_ROUNDS = int(os.getenv("DICOM_DEFAULT_MAX_ROUNDS", "3"))
_DEFAULT_STEP_WAIT_MS = int(os.getenv("DICOM_DEFAULT_STEP_WAIT_MS", "40"))


# ============================================================================
# Models
# ============================================================================


class DownloadRequest(BaseModel):
    """Request to download DICOM images from a URL."""

    url: str = Field(description="Medical imaging viewer URL to download from")
    output_dir: str = Field(
        default=_DEFAULT_OUTPUT_DIR,
        description="Directory to save downloaded DICOM files",
    )
    provider: Optional[str] = Field(
        default="auto",
        description="Provider type: auto, tz (天肿), fz (复肿), nyfy (宁夏总医院), or cloud",
    )
    mode: str = Field(
        default="all",
        description="Download mode: all, diag (diagnostic only), or nondiag",
    )
    headless: bool = Field(
        default=True, description="Run browser in headless mode (no UI)"
    )
    password: Optional[str] = Field(
        default=None, description="Password/share code if required by the site"
    )
    create_zip: bool = Field(
        default=True, description="Create ZIP archive of downloaded files"
    )
    max_rounds: int = Field(
        default=_DEFAULT_MAX_ROUNDS,
        description="Maximum number of scan rounds (扫描次数，默认 3)",
    )
    step_wait_ms: int = Field(
        default=_DEFAULT_STEP_WAIT_MS,
        description="Delay between steps in milliseconds (延迟时间，默认 40ms)",
    )


class BatchDownloadRequest(BaseModel):
    """Request to download from multiple URLs.
    
    密码支持三种模式：
    1. 全局密码：password="1234"，所有URL共用
    2. URL密码映射：passwords={"url1": "pwd1", "url2": "pwd2"}
    3. 自动读文件：密码通过 urls.txt 中 "URL 安全码:xxx" 格式指定
    """

    urls: list[str] = Field(description="List of URLs to download from")
    output_parent: str = Field(
        default=_DEFAULT_OUTPUT_DIR,
        description="Parent directory for all downloads",
    )
    provider: str = Field(
        default="auto", description="Provider type to use for all URLs"
    )
    mode: str = Field(default="all", description="Download mode")
    headless: bool = Field(default=True, description="Run in headless mode")
    password: Optional[str] = Field(
        default=None, 
        description="[废弃] 全局密码（对所有URL生效）。建议改用 passwords 字典"
    )
    passwords: Optional[Dict[str, Optional[str]]] = Field(
        default=None,
        description="[推荐] URL到密码的映射字典。格式: {'url1': 'pwd1', 'url2': None, ...}"
    )
    create_zip: bool = Field(default=True, description="Create ZIP archives")
    max_rounds: int = Field(
        default=_DEFAULT_MAX_ROUNDS,
        description="Maximum number of scan rounds (扫描次数，默认 3)",
    )
    step_wait_ms: int = Field(
        default=_DEFAULT_STEP_WAIT_MS,
        description="Delay between steps in milliseconds (延迟时间，默认 40ms)",
    )


class DownloadResult(BaseModel):
    """Result of a download operation."""

    success: bool = Field(description="Whether download succeeded")
    url: str = Field(description="Source URL")
    output_dir: str = Field(description="Output directory path")
    zip_path: Optional[str] = Field(default=None, description="Path to ZIP file if created")
    message: str = Field(description="Status message or error details")
    file_count: Optional[int] = Field(default=None, description="Number of files downloaded")


class ProviderInfo(BaseModel):
    """Information about a supported provider."""

    name: str = Field(description="Provider identifier")
    display_name: str = Field(description="Human-readable name")
    domains: list[str] = Field(description="Supported domains")
    description: str = Field(description="Provider description")


# ============================================================================
# Helper Functions
# ============================================================================


def detect_provider(url: str) -> str:
    """Auto-detect provider from URL."""
    host = urlparse(url).netloc.lower()

    if "zlyy.tjmucih.cn" in host:
        return "tz"
    if "zhyl.nyfy.com.cn" in host:
        return "nyfy"
    if "shdc.org.cn" in host or "ylyyx.shdc.org.cn" in host:
        return "fz"
    if host.endswith(".medicalimagecloud.com"):
        return "cloud"

    cloud_hosts = [
        "mdmis.cq12320.cn",
        "qr.szjudianyun.com",
        "zscloud.zs-hospital.sh.cn",
        "app.ftimage.cn",
        "yyx.ftimage.cn",
        "m.yzhcloud.com",
        "ss.mtywcloud.com",
        "work.sugh.net",
        "cloudpacs.jdyfy.com",
    ]
    if host in cloud_hosts:
        return "cloud"

    return "fz"  # Default fallback


def count_files_recursive(directory: str) -> int:
    """Count total files in directory recursively."""
    count = 0
    try:
        for root, dirs, files in os.walk(directory):
            count += len(files)
    except Exception:
        pass
    return count


async def _stream_output(stream, label: str) -> str:
    """Stream subprocess output in real time."""
    output = []
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="ignore").rstrip()
            if text:
                # Print key progress lines to stderr (not stdout, which is for MCP JSON)
                if any(keyword in text for keyword in 
                       ["下载", "provider=", "URL", "成功", "失败", "文件", 
                        ">>>", "###", "错误", "Error", "WARNING"]):
                    print(f"   {text}", file=sys.stderr)
                output.append(text)
    except Exception:
        pass
    return "\n".join(output)


async def run_multi_download(
    urls: list[str],
    output_parent: str,
    provider: str = "auto",
    mode: str = "all",
    headless: bool = True,
    password: Optional[str] = None,
    passwords: Optional[Dict[str, Optional[str]]] = None,
    create_zip: bool = True,
    max_rounds: int = 3,
    step_wait_ms: int = 40,
) -> list[DownloadResult]:
    """
    Run multi_download.py with given parameters.
    
    ✨ 改进：支持 passwords 字典，确保URL与密码的准确映射
    
    参数说明：
    - password: [废弃] 全局密码，对所有URL生效
    - passwords: [推荐] URL->密码映射字典，确保一一对应
    """

    script_path = DICOM_DOWNLOAD_PATH / "multi_download.py"
    if not script_path.exists():
        return [
            DownloadResult(
                success=False,
                url=urls[0] if urls else "unknown",
                output_dir=output_parent,
                message=f"multi_download.py not found at {script_path}",
            )
        ]

    # ✨ 安全性改进：通过环境变量传递密码（而非磁盘文件）
    # 构建 URL -> 密码的字典
    url_password_dict: Dict[str, Optional[str]] = {}
    for url in urls:
        pwd = None
        if passwords and url in passwords:
            pwd = passwords[url]
        elif password:
            pwd = password
        url_password_dict[url] = pwd
    
    # 序列化为 JSON 并设置环境变量（仅包含有密码的项以减小体积）
    passwords_json = json.dumps({url: pwd for url, pwd in url_password_dict.items() if pwd})
    
    # 生成纯 urls.txt（不含密码）
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, dir=output_parent
    ) as f:
        for url in urls:
            f.write(f"{url}\n")
        urls_file = f.name

    try:
        cmd = [
            sys.executable,
            str(script_path),
            "--urls-file",
            urls_file,
            "--out-parent",
            output_parent,
        ]

        if provider != "auto":
            cmd.extend(["--provider", provider])

        cmd.extend(["--mode", mode])

        if headless:
            cmd.append("--headless")
        else:
            cmd.append("--no-headless")

        if not create_zip:
            cmd.append("--no-zip")
        
        # Add scan rounds and delay parameters
        cmd.extend(["--max-rounds", str(max_rounds)])
        cmd.extend(["--step-wait-ms", str(step_wait_ms)])

        # ✨ 安全性改进：通过环境变量传递密码
        env = os.environ.copy()
        if passwords_json:
            env["DICOM_URL_PASSWORDS_JSON"] = passwords_json
            pwd_count = len(json.loads(passwords_json))
            print(f"[run_multi_download] ✅ 通过环境变量传递 {pwd_count} 个密码映射（非磁盘文件）", file=sys.stderr)
        
        # Show progress banner (to stderr, visible to Claude)
        print("\n" + "=" * 70, file=sys.stderr)
        print("🚀 DICOM 下载开始", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"📍 下载数量: {len(urls)} 个URL", file=sys.stderr)
        print(f"📁 输出目录: {output_parent}", file=sys.stderr)
        print(f"⚙️  扫描次数: {max_rounds}, 帧间延迟: {step_wait_ms}ms", file=sys.stderr)
        print("⏳ 请稍候，下载中... (可能需要 2-10 分钟)", file=sys.stderr)
        print("", file=sys.stderr)

        # Run subprocess with real-time output streaming
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        # Stream stdout in real time
        task_stdout = asyncio.create_task(_stream_output(process.stdout, "stdout"))
        task_stderr = asyncio.create_task(_stream_output(process.stderr, "stderr"))
        
        returncode = await process.wait()
        stdout = await task_stdout
        stderr = await task_stderr

        if returncode == 0:
            print("\n" + "=" * 70, file=sys.stderr)
            print("✅ 下载完成！", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            print("📊 处理结果中...", file=sys.stderr)
            print("", file=sys.stderr)
            
            # Parse output directories from stdout
            results = []
            for idx, url in enumerate(urls, 1):
                # Extract share_id and construct output dir
                from common_utils import extract_share_id

                print(f"[{idx}/{len(urls)}] 处理: {url}", file=sys.stderr)
                
                share_id = extract_share_id(url)
                out_dir = os.path.join(output_parent, share_id)
                file_count = count_files_recursive(out_dir)
                zip_path = (
                    os.path.join(output_parent, f"{share_id}.zip")
                    if create_zip
                    else None
                )

                print(f"  ✓ 已保存 {file_count} 个文件到: {out_dir}", file=sys.stderr)
                
                results.append(
                    DownloadResult(
                        success=True,
                        url=url,
                        output_dir=out_dir,
                        zip_path=zip_path,
                        message=f"✅ 下载成功 ({file_count} 个文件)",
                        file_count=file_count,
                    )
                )
            
            # Final summary
            total_files = sum(r.file_count or 0 for r in results)
            print("=" * 70, file=sys.stderr)
            print(f"📈 汇总: 共下载 {total_files} 个文件", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            print("", file=sys.stderr)
            return results
        else:
            error_msg = stderr if stderr else "Unknown error"
            print("\n" + "=" * 70, file=sys.stderr)
            print("❌ 下载失败", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            print(f"错误信息: {error_msg}", file=sys.stderr)
            print("", file=sys.stderr)
            return [
                DownloadResult(
                    success=False,
                    url=urls[0] if urls else "unknown",
                    output_dir=output_parent,
                    message=f"❌ 下载失败: {error_msg}",
                )
            ]
    finally:
        # Clean up temporary file
        try:
            os.unlink(urls_file)
        except Exception:
            pass


# ============================================================================
# Helper Functions for Password Extraction
# ============================================================================


def _extract_password_from_url(url: str) -> tuple[str, Optional[str]]:
    """
    Extract security code from URL string.
    
    Supports multiple formats:
    - URL 安全码:8492 or URL 安全码：8492
    - URL 密码:8492 or URL 密码：8492
    - URL password:8492 or URL password：8492
    - URL code:8492 or URL code：8492
    - URL 验证码:8492 or URL 验证码：8492
    
    Returns: (clean_url, security_code)
    """
    import re
    
    # Pattern: look for various security code indicators with both half-width and full-width colons
    patterns = [
        r'\s*安全码[：:]\s*(\d+)',      # 安全码:8492 or 安全码：8492
        r'\s*密码[：:]\s*(\d+)',        # 密码:8492 or 密码：8492
        r'\s*验证码[：:]\s*(\d+)',      # 验证码:8492 or 验证码：8492
        r'\s*password[：:]\s*(\S+)',    # password:8492 or password：8492
        r'\s*code[：:]\s*(\d+)',        # code:8492 or code：8492
    ]
    
    security_code = None
    clean_url = url
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            security_code = match.group(1)
            # Remove security code from URL
            clean_url = re.sub(pattern, '', url).strip()
            print(f"[dicom-mcp] 提取安全码: {security_code}", file=sys.stderr)
            break
    
    return clean_url, security_code


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
async def download_dicom(request: DownloadRequest) -> DownloadResult:
    """
    Download DICOM images from a single medical imaging viewer URL.

    Supports multiple providers:
    - tz: 天肿 (zlyy.tjmucih.cn)
    - fz: 复肿 (ylyyx.shdc.org.cn)
    - nyfy: 宁夏总医院 (zhyl.nyfy.com.cn)
    - cloud: *.medicalimagecloud.com and other cloud-based systems
    
    **密码支持**：
    1. 显式指定：password="安全码" 参数
    2. URL中提取：自动识别 "URL 安全码:8492"、"URL password:8492" 等格式
    3. 优先级：显式指定 > URL中提取
    
    **示例**：
    ```python
    # 方式1：显式指定密码
    request = DownloadRequest(
        url="https://hospital.com/viewer?id=123",
        password="8492"
    )
    
    # 方式2：从URL提取密码
    request = DownloadRequest(
        url="https://hospital.com/viewer?id=123 安全码:8492"
    )
    ```
    """
    # Auto-extract security code from URL if not explicitly provided
    clean_url, extracted_code = _extract_password_from_url(request.url)
    security_code = request.password or extracted_code
    
    os.makedirs(request.output_dir, exist_ok=True)
    
    # ✨ 改进：使用 passwords 字典保留映射关系
    passwords_dict = {clean_url: security_code}
    
    results = await run_multi_download(
        [clean_url],
        request.output_dir,
        provider=request.provider or "auto",
        mode=request.mode,
        headless=request.headless,
        passwords=passwords_dict,
        create_zip=request.create_zip,
        max_rounds=request.max_rounds,
        step_wait_ms=request.step_wait_ms,
    )
    return results[0] if results else DownloadResult(
        success=False,
        url=request.url,
        output_dir=request.output_dir,
        message="Unknown error",
    )


@mcp.tool()
async def batch_download_dicom(request: BatchDownloadRequest) -> list[DownloadResult]:
    """
    Download DICOM images from multiple URLs in batch.
    
    **多链接+密码映射支持**（确保URL与密码的准确匹配）
    
    Each URL gets its own subdirectory with its corresponding password.
    Supports auto-detection of provider based on domain, or manual provider specification.
    
    **密码配置方式**（按优先级）：
    1. passwords 字典映射（推荐）：URLs 与密码一一对应
       - 格式：passwords={"url1": "pwd1", "url2": "pwd2", "url3": None}
       - 优势：清晰明确，不易出错，最安全
       - 最佳实践：生产环境强烈推荐

    2. password 全局密码：所有 URLs 共用同一密码
       - 格式：password="1234"
       - 适用场景：所有URL需要同一密码

    3. URL中嵌入密码：自动提取
       - 格式："URL 安全码:8492"、"URL password:8492"
       - 自动处理，无需额外配置

    **密码优先级**（高→低）：
    passwords字典 > password全局 > URL中提取 > None(无密码)
    
    **示例**：
    ```python
    # ✨ 推荐：多URL多密码精确映射
    request = BatchDownloadRequest(
        urls=[
            "https://hospital1.com/viewer?id=A",
            "https://hospital2.com/viewer?id=B",
            "https://hospital3.com/viewer?id=C"
        ],
        passwords={
            "https://hospital1.com/viewer?id=A": "password_A",
            "https://hospital2.com/viewer?id=B": "password_B",
            "https://hospital3.com/viewer?id=C": None  # 无密码
        }
    )
    # 结果：URL_A + password_A、URL_B + password_B、URL_C + None
    ```
    """
    # ========== 密码处理逻辑 ==========
    clean_urls = []
    url_password_dict: Dict[str, Optional[str]] = {}
    
    for url in request.urls:
        clean_url, code = _extract_password_from_url(url)
        clean_urls.append(clean_url)
        
        # 优先级：passwords字典 > password全局 > URL中提取的密码
        if request.passwords and clean_url in request.passwords:
            pwd = request.passwords[clean_url]
        elif request.passwords and url in request.passwords:
            pwd = request.passwords[url]
        elif request.password:
            pwd = request.password
        else:
            pwd = code
        
        url_password_dict[clean_url] = pwd
        pwd_display = f"({len(pwd)} 位)" if pwd else "(无密码)"
        print(
            f"[batch_download_dicom] {clean_url[:50]}... -> {pwd_display}",
            file=sys.stderr
        )
    
    os.makedirs(request.output_parent, exist_ok=True)
    return await run_multi_download(
        clean_urls,
        request.output_parent,
        provider=request.provider,
        mode=request.mode,
        headless=request.headless,
        passwords=url_password_dict,
        create_zip=request.create_zip,
        max_rounds=request.max_rounds,
        step_wait_ms=request.step_wait_ms,
    )


@mcp.tool()
def detect_provider_from_url(url: str) -> dict:
    """
    Detect which DICOM provider a URL belongs to.

    Returns the detected provider and related information.
    """
    provider = detect_provider(url)
    providers_info = {
        "tz": ProviderInfo(
            name="tz",
            display_name="天肿 (圆心云影)",
            domains=["zlyy.tjmucih.cn"],
            description="Tianjin Medical University Cancer Institute DICOM viewer",
        ),
        "fz": ProviderInfo(
            name="fz",
            display_name="复肿 (复旦肿瘤医院)",
            domains=["ylyyx.shdc.org.cn"],
            description="Fudan University Cancer Hospital DICOM viewer",
        ),
        "nyfy": ProviderInfo(
            name="nyfy",
            display_name="宁夏总医院",
            domains=["zhyl.nyfy.com.cn"],
            description="Ningxia General Hospital DICOM viewer with WebSocket support",
        ),
        "cloud": ProviderInfo(
            name="cloud",
            display_name="Cloud DICOM Services",
            domains=[
                "*.medicalimagecloud.com",
                "mdmis.cq12320.cn",
                "qr.szjudianyun.com",
                "zscloud.zs-hospital.sh.cn",
                "app.ftimage.cn",
                "yyx.ftimage.cn",
            ],
            description="Cloud-based DICOM image systems (Medical Image Cloud and others)",
        ),
    }

    info = providers_info.get(provider)
    return {
        "url": url,
        "detected_provider": provider,
        "provider_info": info.model_dump() if info else None,
        "is_auto_detected": True,
    }


@mcp.tool()
def list_supported_providers() -> list[ProviderInfo]:
    """
    List all supported DICOM providers and their capabilities.

    Returns information about each provider including supported domains
    and download modes.
    """
    return [
        ProviderInfo(
            name="tz",
            display_name="天肿 (圆心云影)",
            domains=["zlyy.tjmucih.cn"],
            description="Tianjin Medical University Cancer Institute DICOM viewer. Supports diag/nondiag/all modes",
        ),
        ProviderInfo(
            name="fz",
            display_name="复肿 (复旦肿瘤医院)",
            domains=["ylyyx.shdc.org.cn"],
            description="Fudan University Cancer Hospital DICOM viewer. Supports high-definition switching and frame-by-frame playback",
        ),
        ProviderInfo(
            name="nyfy",
            display_name="宁夏总医院",
            domains=["zhyl.nyfy.com.cn"],
            description="Ningxia General Hospital DICOM viewer. Uses WebSocket metadata and h5Cache for pixel data",
        ),
        ProviderInfo(
            name="cloud",
            display_name="Cloud DICOM Services",
            domains=[
                "*.medicalimagecloud.com",
                "mdmis.cq12320.cn",
                "qr.szjudianyun.com",
                "zscloud.zs-hospital.sh.cn",
                "app.ftimage.cn",
                "yyx.ftimage.cn",
                "m.yzhcloud.com",
                "ss.mtywcloud.com",
                "work.sugh.net",
                "cloudpacs.jdyfy.com",
            ],
            description="Cloud-based DICOM image systems including Medical Image Cloud and hospital cloud systems",
        ),
    ]


@mcp.tool()
def validate_url(url: str) -> dict:
    """
    Validate if a URL is from a supported DICOM provider.

    Returns validation status and suggested provider.
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "valid": False,
                "url": url,
                "error": "Invalid URL format",
                "suggestion": "URL must include scheme (http/https) and domain",
            }

        provider = detect_provider(url)
        return {
            "valid": True,
            "url": url,
            "provider": provider,
            "message": f"URL belongs to {provider} provider",
        }
    except Exception as e:
        return {
            "valid": False,
            "url": url,
            "error": str(e),
        }


# ============================================================================
# Server Entry Point
# ============================================================================


def main():
    """Start the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
