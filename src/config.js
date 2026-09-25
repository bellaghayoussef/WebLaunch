import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const configJsonPath = path.join(rootDir, 'config.json');

let jsonConfig = {};
if (fs.existsSync(configJsonPath)) {
  try {
    jsonConfig = JSON.parse(fs.readFileSync(configJsonPath, 'utf8'));
  } catch (e) {
    console.warn('Could not read config.json:', e.message);
  }
}

export const config = {
  baseURL: process.env.ANTHROPIC_BASE_URL || jsonConfig.env?.ANTHROPIC_BASE_URL || 'https://api.justwoker.icu',
  apiKey: process.env.ANTHROPIC_AUTH_TOKEN || jsonConfig.env?.ANTHROPIC_AUTH_TOKEN || '',
  model: process.env.ANTHROPIC_MODEL || jsonConfig.env?.ANTHROPIC_MODEL || 'claude-opus-5',
  fallbackModel: process.env.FALLBACK_MODEL || jsonConfig.fallback_model || 'claude-opus-4-8',
  theme: jsonConfig.theme || process.env.THEME || 'dark',
  port: parseInt(process.env.PORT || '3000', 10),
  workspaceDir: rootDir
};

export function updateConfig(newConfig) {
  if (newConfig.model) config.model = newConfig.model;
  if (newConfig.apiKey) config.apiKey = newConfig.apiKey;
  if (newConfig.baseURL) config.baseURL = newConfig.baseURL;
  if (newConfig.theme) config.theme = newConfig.theme;

  const toSave = {
    env: {
      ANTHROPIC_BASE_URL: config.baseURL,
      ANTHROPIC_AUTH_TOKEN: config.apiKey,
      ANTHROPIC_MODEL: config.model
    },
    fallback_model: config.fallbackModel,
    theme: config.theme
  };

  fs.writeFileSync(configJsonPath, JSON.stringify(toSave, null, 2), 'utf8');
}
