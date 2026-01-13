#!/usr/bin/env python3
"""
测试 DICOM MCP 服务器的所有工具
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from dicom_mcp.server import (
    download_dicom,
    batch_download_dicom,
    detect_provider_from_url,
    list_supported_providers,
    validate_url,
    DownloadRequest,
    BatchDownloadRequest,
)


def print_header(title):
    """打印分隔符"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_test(name, status, details=""):
    """打印测试结果"""
    symbol = "✓" if status else "✗"
    print(f"{symbol} {name}")
    if details:
        print(f"  → {details}")


async def test_list_providers():
    """测试：列出所有支持的医院"""
    print_header("测试 1: list_supported_providers()")
    
    try:
        providers = list_supported_providers()
        print_test("列出支持的医院", True)
        print(f"\n找到 {len(providers)} 个医院/服务商：\n")
        
        for provider in providers:
            print(f"  📍 {provider.display_name}")
            print(f"     ID: {provider.name}")
            print(f"     域名: {', '.join(provider.domains[:2])}{'...' if len(provider.domains) > 2 else ''}")
            print(f"     {provider.description}\n")
        
        print_test("返回数据格式", len(providers) == 4, f"返回了 {len(providers)} 个提供者")
        return True
    except Exception as e:
        print_test("列出支持的医院", False, str(e))
        return False


async def test_detect_provider():
    """测试：自动检测医院"""
    print_header("测试 2: detect_provider_from_url()")
    
    test_urls = [
        ("https://zlyy.tjmucih.cn/viewer?share_id=ABC123", "tz"),
        ("https://ylyyx.shdc.org.cn/viewer?share_id=DEF456", "fz"),
        ("https://zhyl.nyfy.com.cn/viewer?share_id=GHI789", "nyfy"),
        ("https://example.medicalimagecloud.com/viewer?id=XYZ", "cloud"),
        ("https://unknown-hospital.com/viewer", "fz"),  # 默认为 fz
    ]
    
    all_passed = True
    for url, expected_provider in test_urls:
        try:
            result = detect_provider_from_url(url)
            detected = result.get("detected_provider")
            passed = detected == expected_provider
            all_passed = all_passed and passed
            
            status = "✓" if passed else "✗"
            print(f"{status} {url}")
            print(f"  检测到: {detected} (预期: {expected_provider})")
            if result.get("provider_info"):
                print(f"  名称: {result['provider_info'].get('display_name')}\n")
        except Exception as e:
            print_test(f"检测 {url}", False, str(e))
            all_passed = False
    
    return all_passed


async def test_validate_url():
    """测试：URL 验证"""
    print_header("测试 3: validate_url()")
    
    test_cases = [
        ("https://zlyy.tjmucih.cn/viewer?share_id=ABC123", True),
        ("https://ylyyx.shdc.org.cn/viewer?share_id=ABC123", True),
        ("not-a-valid-url", False),
        ("https://", False),
    ]
    
    all_passed = True
    for url, should_be_valid in test_cases:
        try:
            result = validate_url(url)
            is_valid = result.get("valid", False)
            passed = is_valid == should_be_valid
            all_passed = all_passed and passed
            
            status = "✓" if passed else "✗"
            print(f"{status} {url}")
            if is_valid:
                print(f"  ✓ 有效 - 提供者: {result.get('provider')}")
            else:
                print(f"  ✗ 无效 - {result.get('error', '未知错误')}")
            print()
        except Exception as e:
            print_test(f"验证 {url}", False, str(e))
            all_passed = False
    
    return all_passed


async def test_download_request_model():
    """测试：DownloadRequest 数据模型"""
    print_header("测试 4: DownloadRequest 数据模型")
    
    try:
        # 有效的请求
        req = DownloadRequest(
            url="https://zlyy.tjmucih.cn/viewer?share_id=ABC123",
            output_dir="./downloads",
            provider="auto",
            mode="all",
            headless=True,
        )
        print_test("创建 DownloadRequest", True, f"URL: {req.url}")
        print(f"  参数: provider={req.provider}, mode={req.mode}, headless={req.headless}\n")
        
        # 测试默认值
        req2 = DownloadRequest(url="https://example.com/viewer")
        print_test("使用默认参数", True)
        print(f"  output_dir: {req2.output_dir}")
        print(f"  create_zip: {req2.create_zip}\n")
        
        return True
    except Exception as e:
        print_test("DownloadRequest 模型", False, str(e))
        return False


async def test_batch_request_model():
    """测试：BatchDownloadRequest 数据模型"""
    print_header("测试 5: BatchDownloadRequest 数据模型")
    
    try:
        req = BatchDownloadRequest(
            urls=[
                "https://zlyy.tjmucih.cn/viewer?share_id=STUDY1",
                "https://ylyyx.shdc.org.cn/viewer?share_id=STUDY2",
            ],
            output_parent="./batch_downloads",
            mode="diag",
        )
        print_test("创建 BatchDownloadRequest", True)
        print(f"  URL 数量: {len(req.urls)}")
        print(f"  输出目录: {req.output_parent}")
        print(f"  下载模式: {req.mode}\n")
        return True
    except Exception as e:
        print_test("BatchDownloadRequest 模型", False, str(e))
        return False


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  DICOM MCP 服务器 - 工具测试".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # 运行所有测试
    results.append(("列出支持的医院", await test_list_providers()))
    results.append(("自动检测医院", await test_detect_provider()))
    results.append(("URL 验证", await test_validate_url()))
    results.append(("DownloadRequest 模型", await test_download_request_model()))
    results.append(("BatchDownloadRequest 模型", await test_batch_request_model()))
    
    # 总结
    print_header("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
