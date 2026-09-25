import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { config, updateConfig } from './src/config.js';
import { runAgent } from './src/agent.js';
import { getAvailableModels } from './src/claudeClient.js';
import { listFiles } from './src/tools.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Configuration API
app.get('/api/config', async (req, res) => {
  const models = await getAvailableModels();
  res.json({
    baseURL: config.baseURL,
    model: config.model,
    fallbackModel: config.fallbackModel,
    theme: config.theme,
    models,
    hasApiKey: !!config.apiKey
  });
});

app.post('/api/config', (req, res) => {
  try {
    updateConfig(req.body);
    res.json({ success: true, config });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Available models
app.get('/api/models', async (req, res) => {
  try {
    const models = await getAvailableModels();
    res.json({ models });
  } catch (err) {
    res.json({ models: ['claude-opus-4-8', 'claude-opus-5'] });
  }
});

// Workspace files inspector
app.get('/api/workspace', (req, res) => {
  const dir = req.query.dir || '';
  const result = listFiles(dir);
  res.json(result);
});

// SSE Streaming Agent endpoint
app.post('/api/agent/stream', async (req, res) => {
  const { prompt, messages, model } = req.body;

  if (!prompt && (!messages || messages.length === 0)) {
    return res.status(400).json({ error: 'Prompt or messages required' });
  }

  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders?.();

  const sendEvent = (data) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  try {
    const input = messages && messages.length > 0 ? messages : prompt;
    await runAgent(input, (event) => {
      sendEvent(event);
    }, { model: model || config.model });

    res.write('data: [DONE]\n\n');
    res.end();
  } catch (err) {
    console.error('Agent execution error:', err);
    sendEvent({ type: 'agent:error', error: err.message });
    res.write('data: [DONE]\n\n');
    res.end();
  }
});

// Standard non-streaming chat endpoint
app.post('/api/agent/run', async (req, res) => {
  const { prompt, messages, model } = req.body;
  if (!prompt && (!messages || messages.length === 0)) {
    return res.status(400).json({ error: 'Prompt or messages required' });
  }

  const events = [];
  try {
    const input = messages && messages.length > 0 ? messages : prompt;
    const result = await runAgent(input, (event) => events.push(event), { model: model || config.model });
    res.json({ success: true, result, events });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message, events });
  }
});

let currentPort = config.port || 3500;

function startServer(port) {
  const server = app.listen(port, () => {
    console.log(`\n=================================================`);
    console.log(`🚀 AgentX Server running at http://localhost:${port}`);
    console.log(`   Model: ${config.model} (fallback: ${config.fallbackModel})`);
    console.log(`   Theme: ${config.theme}`);
    console.log(`=================================================\n`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`Port ${port} in use, trying port ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('Server error:', err);
    }
  });
}

startServer(currentPort);
