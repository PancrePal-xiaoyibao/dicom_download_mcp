#!/usr/bin/env node

/**
 * DICOM MCP Server - Node.js Wrapper
 * This script launches the Python MCP server
 */

import { spawn } from 'child_process';
import { execSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');

/**
 * Check if Python is installed and accessible
 */
function checkPython() {
  try {
    const version = execSync('python3 --version', { encoding: 'utf-8' }).trim();
    console.log(`✓ Found Python: ${version}`);
    return 'python3';
  } catch {
    try {
      const version = execSync('python --version', { encoding: 'utf-8' }).trim();
      console.log(`✓ Found Python: ${version}`);
      return 'python';
    } catch {
      console.error('✗ Error: Python is not installed or not in PATH');
      console.error('Please install Python 3.9 or later from https://www.python.org/');
      process.exit(1);
    }
  }
}

/**
 * Check if required Python dependencies are installed
 */
function checkDependencies(pythonCmd) {
  try {
    execSync(`${pythonCmd} -c "import mcp; import pydantic; import playwright"`, {
      stdio: 'pipe',
    });
    console.log('✓ All Python dependencies are installed');
  } catch {
    console.error('✗ Error: Required Python packages are not installed');
    console.error('\nPlease install the dependencies:');
    console.error('  pip install mcp pydantic playwright');
    console.error('  playwright install chromium');
    process.exit(1);
  }
}

/**
 * Install the local dicom_mcp package
 */
function installLocalPackage(pythonCmd) {
  console.log('Setting up local dicom_mcp package...');
  try {
    execSync(`${pythonCmd} -m pip install -e "${rootDir}"`, {
      stdio: 'inherit',
    });
    console.log('✓ Local dicom_mcp package installed');
  } catch (error) {
    console.error('✗ Error: Failed to install dicom_mcp');
    console.error(error.message);
    process.exit(1);
  }
}

/**
 * Launch the MCP server
 */
function launchServer(pythonCmd) {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 Starting DICOM MCP Server');
  console.log('='.repeat(70));
  console.log('Listening on stdio transport\n');

  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
  };

  const server = spawn(pythonCmd, ['-m', 'dicom_mcp.server'], {
    env,
    stdio: 'inherit',
  });

  server.on('error', (error) => {
    console.error('✗ Error: Failed to start server');
    console.error(error.message);
    process.exit(1);
  });

  server.on('exit', (code) => {
    if (code !== 0) {
      console.error(`✗ Server exited with code ${code}`);
      process.exit(code);
    }
  });

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n\nShutting down DICOM MCP Server...');
    server.kill();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n\nShutting down DICOM MCP Server...');
    server.kill();
    process.exit(0);
  });
}

/**
 * Main execution
 */
function main() {
  console.log('DICOM MCP Server - Node.js Launcher\n');

  // Check Python installation
  const pythonCmd = checkPython();

  // Check dependencies
  checkDependencies(pythonCmd);

  // Install local package
  installLocalPackage(pythonCmd);

  // Launch server
  launchServer(pythonCmd);
}

main();
