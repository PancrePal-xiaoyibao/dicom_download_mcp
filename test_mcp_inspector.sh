#!/bin/bash

# DICOM MCP Inspector 测试脚本

echo "════════════════════════════════════════════════════════════════"
echo "  DICOM MCP Inspector 测试"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚙️  启动 MCP Inspector..."
echo ""

# 确保在项目目录
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# 检查依赖
echo "📦 检查依赖..."
python -c "from dicom_mcp.server import mcp; print('✓ dicom_mcp 已安装')" || {
    echo "❌ dicom_mcp 未安装，正在安装..."
    pip install -e . > /dev/null
}

# 启动 MCP Inspector
echo ""
echo "🚀 启动 MCP Inspector..."
echo "   按照下面的说明连接您的 MCP 服务器"
echo ""

npx @modelcontextprotocol/inspector python -m dicom_mcp.server

echo ""
echo "✅ 测试完成"
