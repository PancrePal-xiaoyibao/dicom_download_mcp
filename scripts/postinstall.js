#!/usr/bin/env node

/**
 * Post-install script for dicom-mcp npm package
 * Sets up Python dependencies after npm installation
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const pythonCmd = (() => {
  try {
    execSync('python3 --version', { stdio: 'pipe' });
    return 'python3';
  } catch {
    try {
      execSync('python --version', { stdio: 'pipe' });
      return 'python';
    } catch {
      return null;
    }
  }
})();

if (!pythonCmd) {
  console.warn('\n⚠️  Warning: Python 3 is not installed');
  console.warn('Please install Python 3.9+ from https://www.python.org/');
  console.warn('After installing Python, run: dicom-mcp\n');
  process.exit(0);
}

try {
  console.log('📦 Installing Python dependencies for DICOM MCP...\n');

  // Install Python package
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'package.json'), 'utf-8')
  );

  const pythonRequirements = [
    'mcp>=0.8.0',
    'pydantic>=2.0',
    'playwright>=1.40.0',
    'httpx>=0.24.0',
    'aiofiles>=23.0.0',
    'pydicom>=2.3.0',
  ];

  console.log('Installing required Python packages...');
  for (const pkg of pythonRequirements) {
    try {
      execSync(`${pythonCmd} -m pip install "${pkg}"`, { stdio: 'pipe' });
      console.log(`  ✓ ${pkg}`);
    } catch (error) {
      console.log(`  ⚠ ${pkg} (may already be installed)`);
    }
  }

  // Install Playwright browsers
  console.log('\nInstalling Playwright browsers...');
  try {
    execSync(`${pythonCmd} -m playwright install chromium`, {
      stdio: 'pipe',
    });
    console.log('  ✓ Chromium browser installed');
  } catch (error) {
    console.warn('  ⚠ Could not install Playwright browsers');
    console.warn('  Run manually: playwright install chromium\n');
  }

  console.log('\n✅ Setup complete!');
  console.log('\nYou can now run: dicom-mcp\n');
} catch (error) {
  console.error('\n❌ Setup failed:');
  console.error(error.message);
  console.error('\nPlease ensure Python 3.9+ is installed and try again.\n');
  process.exit(1);
}
