# Project Structure Overview

## Directory Layout

```
/Users/qinxiaoqiang/Downloads/dicom_mcp/
├── pyproject.toml                      # Project configuration and dependencies
├── .gitignore                          # Git ignore rules
│
├── README.md                           # User-facing documentation
├── QUICKSTART.md                       # Quick start guide with examples
├── ARCHITECTURE.md                     # Technical architecture and design
├── PROJECT_STRUCTURE.md                # This file
│
├── claude_desktop_config.json          # Claude Desktop MCP configuration
│
└── dicom_mcp/                          # Main package directory
    ├── __init__.py                     # Package initialization
    └── server.py                       # MCP server implementation
```

## File Descriptions

### Configuration & Build

#### `pyproject.toml`
- **Purpose**: Python project configuration (PEP 517/518)
- **Contains**:
  - Package metadata (name, version, description)
  - Dependencies (mcp, httpx, pydantic, playwright, etc.)
  - Entry point: `dicom-mcp` command
  - Optional dev dependencies for testing

#### `.gitignore`
- **Purpose**: Git ignore rules
- **Excludes**: `__pycache__/`, `*.pyc`, virtual environments, IDE files, downloads

### Documentation

#### `README.md`
- **Audience**: End users and developers
- **Covers**:
  - Overview and supported providers
  - Installation instructions
  - Usage examples
  - Available tools and their parameters
  - Security considerations
  - Integration with Claude

#### `QUICKSTART.md`
- **Audience**: Users setting up the server
- **Covers**:
  - Step-by-step installation
  - Running the server
  - Basic usage examples
  - Common tasks and troubleshooting
  - Understanding output formats

#### `ARCHITECTURE.md`
- **Audience**: Developers and maintainers
- **Covers**:
  - System architecture diagrams
  - Component details
  - Data models
  - Tool specifications
  - Data flow diagrams
  - Provider-specific behavior
  - Error handling strategy
  - Extension points

#### `PROJECT_STRUCTURE.md` (this file)
- **Purpose**: Guide to the project organization
- **Helps**: Quickly understand what each file does

### Configuration

#### `claude_desktop_config.json`
- **Purpose**: Configuration for Claude Desktop integration
- **Contains**:
  - MCP server registration
  - Command and arguments
  - Environment variables (PYTHONPATH)
  - Copy to `~/.config/Claude/claude_desktop_config.json`

### Source Code

#### `dicom_mcp/__init__.py`
- **Purpose**: Package initialization
- **Contains**: Version string and basic imports

#### `dicom_mcp/server.py`
- **Size**: ~400 lines
- **Purpose**: Main MCP server implementation
- **Key Components**:
  - Import statements and path configuration
  - Pydantic models for requests/responses
  - Helper functions (provider detection, file counting)
  - 5 MCP tools via `@mcp.tool()` decorator
  - Server initialization (`main()` function)

**Tools Implemented**:
1. `download_dicom` - Single URL download
2. `batch_download_dicom` - Multiple URLs
3. `detect_provider_from_url` - Provider identification
4. `list_supported_providers` - Provider capabilities
5. `validate_url` - URL validation

## Dependencies

### Runtime Dependencies
- **mcp**: Model Context Protocol framework
- **httpx**: HTTP client (async support)
- **pydantic**: Data validation and serialization
- **pydicom**: DICOM file handling (from dicom_download)
- **playwright**: Browser automation
- **aiofiles**: Async file operations

### Optional Dev Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **black**: Code formatter
- **mypy**: Type checker

## Integration Points

### With dicom_download
- **Path**: `../dicom_download/` (relative to dicom_mcp)
- **Imports**: `common_utils.py` functions
- **Subprocess**: Calls `multi_download.py`
- **Shared Code**: URL parsing, file management

### With MCP Framework
- **Import**: `from mcp.server.fastmcp import FastMCP`
- **Decorator**: `@mcp.tool()` for tool registration
- **Transport**: `mcp.run(transport="stdio")` for stdio mode
- **Protocol**: Uses FastMCP built on MCP spec

### With Claude Desktop
- **Config File**: `claude_desktop_config.json`
- **Location**: `~/.config/Claude/claude_desktop_config.json`
- **Launch**: Claude starts server as subprocess
- **Communication**: Stdio protocol

## Data Models

### Request Models (in `server.py`)
```python
DownloadRequest
├── url: str
├── output_dir: str
├── provider: Optional[str]
├── mode: str
├── headless: bool
├── password: Optional[str]
└── create_zip: bool

BatchDownloadRequest
├── urls: list[str]
├── output_parent: str
├── provider: str
├── mode: str
├── headless: bool
└── create_zip: bool
```

### Response Models (in `server.py`)
```python
DownloadResult
├── success: bool
├── url: str
├── output_dir: str
├── zip_path: Optional[str]
├── message: str
└── file_count: Optional[int]

ProviderInfo
├── name: str
├── display_name: str
├── domains: list[str]
└── description: str
```

## How It Works

### 1. Startup
```
python -m dicom_mcp.server
    ↓
Imports FastMCP framework
    ↓
Initializes MCP server instance
    ↓
Registers 5 tools with @mcp.tool() decorators
    ↓
Starts stdio transport
    ↓
Waits for requests from MCP client (Claude, etc.)
```

### 2. Single Download Request Flow
```
Claude: "Download from https://zlyy.tjmucih.cn/viewer?share_id=ABC"
    ↓
MCP Server receives DownloadRequest
    ↓
download_dicom(request) called
    ↓
run_multi_download() invokes multi_download.py as subprocess
    ↓
subprocess: python multi_download.py --urls-file temp.txt ...
    ↓
dicom_download detects provider (tz)
    ↓
Playwright launches browser, downloads DICOM files
    ↓
Files saved to ./dicom_downloads/zlyy.tjmucih.cn_ABC_xxxxx/
    ↓
ZIP archive created
    ↓
DownloadResult returned to Claude
    ↓
Claude: "Downloaded 142 files to [path], ZIP at [zip_path]"
```

### 3. Batch Download Request Flow
```
Claude: "Download from 3 different URLs"
    ↓
MCP Server receives BatchDownloadRequest
    ↓
batch_download_dicom(request) called
    ↓
run_multi_download([url1, url2, url3], ...) called
    ↓
Single subprocess run with all 3 URLs:
python multi_download.py --urls-file temp.txt ...
    ↓
For each URL:
├─ Detect provider (auto)
├─ Create subdirectory
└─ Download files
    ↓
List[DownloadResult] returned
    ↓
Claude: "3 downloads complete:
        - URL1: 142 files
        - URL2: 89 files
        - URL3: 156 files"
```

## Development Workflow

### Adding a New Tool

1. **Define Input Model**:
   ```python
   class MyToolRequest(BaseModel):
       param1: str = Field(description="...")
       param2: int = Field(default=10)
   ```

2. **Implement Tool**:
   ```python
   @mcp.tool()
   async def my_tool(request: MyToolRequest) -> dict:
       """Tool description."""
       # Implementation
       return result
   ```

3. **Register Automatically**: `@mcp.tool()` handles registration

4. **Test**: Use MCP Inspector or direct calls

### Adding Provider Support

1. **Extend detect_provider()**:
   ```python
   if "new-domain.com" in host:
       return "new_provider_id"
   ```

2. **Add to list_supported_providers()**:
   ```python
   ProviderInfo(
       name="new_provider_id",
       display_name="Provider Display Name",
       domains=["new-domain.com"],
       description="..."
   )
   ```

3. **Ensure dicom_download supports it**: Provider scripts must exist in dicom_download

## Testing

### Manual Testing
```bash
# Test server starts
python -m dicom_mcp.server

# In another terminal, send JSON via stdin
echo '{"jsonrpc":"2.0","method":"tools/call",...}' | python -m dicom_mcp.server
```

### Unit Testing (future)
```bash
pytest tests/
```

### Integration Testing
- Use MCP Inspector: `npx @modelcontextprotocol/inspector`
- Test with Claude Desktop
- Run against test URLs

## Deployment

### Local Development
```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
pip install -e .
python -m dicom_mcp.server
```

### Claude Desktop
```bash
# Edit ~/.config/Claude/claude_desktop_config.json
# Add server configuration
# Restart Claude Desktop
```

### Docker (future)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
ENTRYPOINT ["python", "-m", "dicom_mcp.server"]
```

## Maintenance

### Code Quality
- **Type Hints**: Full type coverage in `server.py`
- **Docstrings**: All functions documented
- **Error Handling**: Comprehensive error messages
- **Logging**: Via subprocess output

### Version Management
- **Version File**: `dicom_mcp/__init__.py` (currently 0.1.0)
- **Changelog**: Would go in `CHANGELOG.md` (not yet created)
- **Compatibility**: Requires Python 3.9+, mcp 0.8.0+

### Dependencies
- Update via: `pip install --upgrade -e .`
- Pin versions in `pyproject.toml`
- Test after updates

## Related Projects

### Upstream: dicom_download
- **Purpose**: Core DICOM downloading implementation
- **Location**: `../dicom_download/`
- **Files Used**: `multi_download.py`, `common_utils.py`, provider scripts
- **Link**: https://github.com/hengqujushi/dicom_download

### Upstream: cloud-dicom-downloader
- **Purpose**: Cloud provider support
- **Location**: `../dicom_download/cloud-dicom-downloader/`
- **Integration**: Subprocess wrapper in multi_download.py
- **Link**: https://github.com/Kaciras/cloud-dicom-downloader

## Quick Reference

| What? | Where? | How? |
|-------|--------|------|
| Start server | `dicom_mcp/server.py` | `python -m dicom_mcp.server` |
| Configure Claude | `claude_desktop_config.json` | Copy to `~/.config/Claude/` |
| View tools | `dicom_mcp/server.py:@mcp.tool()` | 5 tools defined |
| Download logic | `dicom_mcp/server.py:run_multi_download()` | Calls subprocess |
| Actual downloads | `../dicom_download/multi_download.py` | Separate project |
| Add tool | `dicom_mcp/server.py` | Use `@mcp.tool()` decorator |
| Modify requests | `dicom_mcp/server.py:class *Request` | Pydantic models |

## File Sizes (Approximate)

```
server.py              ~420 lines (~12 KB)
README.md              ~280 lines (~8 KB)
ARCHITECTURE.md        ~300 lines (~10 KB)
QUICKSTART.md          ~320 lines (~9 KB)
pyproject.toml         ~40 lines (~1 KB)
Total (dicom_mcp):     ~1.3 KB code + ~27 KB docs
```

## Next Steps

1. **Install**: Run `pip install -e .` in dicom_mcp directory
2. **Configure**: Copy claude_desktop_config.json to Claude Desktop
3. **Test**: Use QUICKSTART.md examples
4. **Integrate**: Add to your Claude workflow
5. **Extend**: Add new tools or providers as needed
