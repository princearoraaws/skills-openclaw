/**
 * index.js — OpenClaw Memory System Plugin (JS shim)
 * Note: Full TypeScript version requires `npm run build` after install
 */
const { execSync } = require('child_process');
const { resolve } = require('path');
const HOMEDIR = require('os').homedir();
const PLUGIN_DIR = resolve(HOMEDIR, '.openclaw/workspace-dev/custom-plugins/openclaw-memory-plugin');
module.exports = { pluginDir: PLUGIN_DIR };
