#!/usr/bin/env node

/**
 * Validation script for npm package
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

console.log('Validating DICOM MCP npm package...\n');

// Check required files
const requiredFiles = [
  'package.json',
  'README.md',
  'README_CN.md',
  'LICENSE',
  'bin/dicom-mcp.js',
  'pyproject.toml',
  'dicom_mcp/server.py',
];

console.log('Checking required files...');
for (const file of requiredFiles) {
  const filePath = path.join(rootDir, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✓ ${file}`);
  } else {
    console.error(`  ✗ ${file} NOT FOUND`);
    process.exit(1);
  }
}

// Check package.json validity
console.log('\nValidating package.json...');
try {
  const pkg = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf-8'));
  if (pkg.name === 'dicom-mcp' && pkg.version === '1.0.0') {
    console.log('  ✓ package.json is valid');
  } else {
    console.error('  ✗ package.json version mismatch');
    process.exit(1);
  }
} catch (error) {
  console.error('  ✗ Invalid package.json:', error.message);
  process.exit(1);
}

console.log('\n✅ Validation passed!\n');
