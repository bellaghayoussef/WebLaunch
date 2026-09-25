import { config } from './config.js';

const BROWSER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

/**
 * Creates Anthropic HTTP headers
 */
function getHeaders(apiKey) {
  return {
    'x-api-key': apiKey || config.apiKey,
    'anthropic-version': '2023-06-01',
    'content-type': 'application/json',
    'user-agent': BROWSER_USER_AGENT
  };
}

/**
 * Send request to Claude API with auto-fallback for model access errors
 */
export async function callClaude({
  messages,
  system = undefined,
  tools = undefined,
  model = config.model,
  maxTokens = 4096,
  apiKey = config.apiKey,
  baseURL = config.baseURL
}) {
  const url = `${baseURL.replace(/\/+$/, '')}/v1/messages`;
  let currentModel = model;

  const payload = {
    model: currentModel,
    max_tokens: maxTokens,
    messages
  };

  if (system) payload.system = system;
  if (tools && tools.length > 0) payload.tools = tools;

  let res = await fetch(url, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify(payload)
  });

  // Check if model access or channel error occurs (e.g. 503 model_not_found, 403 no access)
  if (!res.ok) {
    const errorText = await res.text();
    let isModelError = false;
    try {
      const errJson = JSON.parse(errorText);
      const msg = (errJson.error?.message || '').toLowerCase();
      const code = (errJson.error?.code || '').toLowerCase();
      if (
        msg.includes('no access to model') ||
        msg.includes('no available channel') ||
        msg.includes('model not found') ||
        code === 'model_not_found' ||
        res.status === 403 ||
        res.status === 503
      ) {
        isModelError = true;
      }
    } catch {
      if (
        errorText.includes('no access to model') ||
        errorText.includes('model_not_found') ||
        errorText.includes('No available channel')
      ) {
        isModelError = true;
      }
    }

    if (isModelError && currentModel !== config.fallbackModel) {
      console.warn(`[AgentX] Model "${currentModel}" unavailable on token/channel. Auto-switching to fallback "${config.fallbackModel}"...`);
      payload.model = config.fallbackModel;
      res = await fetch(url, {
        method: 'POST',
        headers: getHeaders(apiKey),
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const fallbackErr = await res.text();
        throw new Error(`Claude API error with fallback model: ${fallbackErr}`);
      }
    } else {
      throw new Error(`Claude API error (${res.status}): ${errorText}`);
    }
  }

  return await res.json();
}

/**
 * Query available models from the proxy endpoint
 */
export async function getAvailableModels(apiKey = config.apiKey, baseURL = config.baseURL) {
  try {
    const url = `${baseURL.replace(/\/+$/, '')}/v1/models`;
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'x-api-key': apiKey,
        'user-agent': BROWSER_USER_AGENT
      }
    });
    if (!res.ok) return ['claude-opus-4-8', 'claude-opus-5'];
    const data = await res.json();
    if (data.data && Array.isArray(data.data)) {
      return data.data.map(m => m.id);
    }
    return ['claude-opus-4-8', 'claude-opus-5'];
  } catch (e) {
    return ['claude-opus-4-8', 'claude-opus-5'];
  }
}
