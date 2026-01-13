"""MCP server for DICOM image downloading."""

import os
import sys
import asyncio
import tempfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Resolve path to dicom_download - supports two deployment methods:
# 1. Local development: git clone后，dicom_download 在 dicom_mcp 的上级目录
# 2. Installed package: 从 PyPI/npm 安装时，dicom_download 作为依赖已安装
def _resolve_dicom_download_path() -> Path:
    """Resolve path to dicom_download module."""
    # Method 1: Local development (git clone)
    local_dev_path = Path(__file__).parent.parent.parent / "dicom_download"
    if local_dev_path.exists():
        return local_dev_path
    
    # Method 2: Check site-packages or installation location
    try:
        import dicom_download as dd_module
        if dd_module.__file__:
            return Path(dd_module.__file__).parent
    except ImportError:
        pass
    
    # Method 3: Try to find in Python path
    for path_item in sys.path:
        candidate = Path(path_item) / "dicom_download"
        if candidate.exists():
            return candidate
    
    # Fallback to local dev path even if not exists
    return local_dev_path

DICOM_DOWNLOAD_PATH = _resolve_dicom_download_path()
if DICOM_DOWNLOAD_PATH.exists():
    sys.path.insert(0, str(DICOM_DOWNLOAD_PATH))

mcp = FastMCP("dicom-downloader")


# ============================================================================
# Models
# ============================================================================


class DownloadRequest(BaseModel):
    """Request to download DICOM images from a URL."""

    url: str = Field(description="Medical imaging viewer URL to download from")
    output_dir: str = Field(
        default="./dicom_downloads",
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
        default=3,
        description="Maximum number of scan rounds (扫描次数，默认 3)",
    )
    step_wait_ms: int = Field(
        default=40,
        description="Delay between steps in milliseconds (延迟时间，默认 40ms)",
    )


class BatchDownloadRequest(BaseModel):
    """Request to download from multiple URLs."""

    urls: list[str] = Field(description="List of URLs to download from")
    output_parent: str = Field(
        default="./dicom_downloads",
        description="Parent directory for all downloads",
    )
    provider: str = Field(
        default="auto", description="Provider type to use for all URLs"
    )
    mode: str = Field(default="all", description="Download mode")
    headless: bool = Field(default=True, description="Run in headless mode")
    create_zip: bool = Field(default=True, description="Create ZIP archives")
    max_rounds: int = Field(
        default=3,
        description="Maximum number of scan rounds (扫描次数，默认 3)",
    )
    step_wait_ms: int = Field(
        default=40,
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
                # Print key progress lines
                if any(keyword in text for keyword in 
                       ["下载", "provider=", "URL", "成功", "失败", "文件", 
                        ">>>", "###", "错误", "Error", "WARNING"]):
                    print(f"   {text}")
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
    create_zip: bool = True,
    max_rounds: int = 3,
    step_wait_ms: int = 40,
) -> list[DownloadResult]:
    """Run multi_download.py with given parameters."""

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

    # Create temporary URLs file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, dir=output_parent
    ) as f:
        for url in urls:
            f.write(url + "\n")
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

        # Show progress banner
        print("\n" + "=" * 70)
        print("🚀 DICOM 下载开始")
        print("=" * 70)
        print(f"📍 下载数量: {len(urls)} 个URL")
        print(f"📁 输出目录: {output_parent}")
        print(f"⚙️  扫描次数: {max_rounds}, 帧间延迟: {step_wait_ms}ms")
        print("⏳ 请稍候，下载中... (可能需要 2-10 分钟)\n")

        # Run subprocess with real-time output streaming
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Stream stdout in real time
        task_stdout = asyncio.create_task(_stream_output(process.stdout, "stdout"))
        task_stderr = asyncio.create_task(_stream_output(process.stderr, "stderr"))
        
        returncode = await process.wait()
        stdout = await task_stdout
        stderr = await task_stderr

        if returncode == 0:
            print("\n" + "=" * 70)
            print("✅ 下载完成！处理结果中...")
            print("=" * 70 + "\n")
            
            # Parse output directories from stdout
            results = []
            for url in urls:
                # Extract share_id and construct output dir
                from common_utils import extract_share_id

                share_id = extract_share_id(url)
                out_dir = os.path.join(output_parent, share_id)
                file_count = count_files_recursive(out_dir)
                zip_path = (
                    os.path.join(output_parent, f"{share_id}.zip")
                    if create_zip
                    else None
                )

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
            return results
        else:
            error_msg = stderr if stderr else "Unknown error"
            print("\n" + "=" * 70)
            print("❌ 下载失败")
            print("=" * 70)
            print(f"错误信息: {error_msg}\n")
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
    """
    os.makedirs(request.output_dir, exist_ok=True)
    results = await run_multi_download(
        [request.url],
        request.output_dir,
        provider=request.provider or "auto",
        mode=request.mode,
        headless=request.headless,
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

    Each URL gets its own subdirectory. Supports auto-detection of provider
    based on domain, or manual provider specification.
    """
    os.makedirs(request.output_parent, exist_ok=True)
    return await run_multi_download(
        request.urls,
        request.output_parent,
        provider=request.provider,
        mode=request.mode,
        headless=request.headless,
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
