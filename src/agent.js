import { callClaude } from './claudeClient.js';
import { TOOL_DEFINITIONS, executeTool } from './tools.js';
import { config } from './config.js';

const SYSTEM_PROMPT = `You are AgentX, a powerful, versatile autonomous AI assistant.
You are equipped with a suite of tools that allow you to act in the physical and digital world:
1. web_search: Use this whenever the user asks you to look up or search the web for information, current news, facts, people, companies, or events.
2. fetch_url: Use this to read the full contents of a specific webpage or article found via search.
3. run_javascript: Use this to compute calculations, solve math problems, or format data with JavaScript.
4. read_file / write_file / list_files: Use these to inspect, read, or write code, notes, and documentation in the workspace.
5. get_current_time: Use this whenever temporal reasoning or current time is needed.

Guidelines:
- If a user asks in French (e.g. "cherche sur le web..."), respond in French. If in English, respond in English. Always match the user's preferred language.
- Proactively call tools when external or factual information is needed.
- Provide comprehensive, well-structured, clear answers with citations and links when using web search.
- Use markdown formatting, bullet points, and code blocks for readability.`;

/**
 * Runs the autonomous ReAct agent loop
 * @param {string|Array} input - Prompt string or existing message history
 * @param {Function} onEvent - Optional event listener for streaming updates
 * @param {Object} options - Custom options (model, maxSteps, etc.)
 */
export async function runAgent(input, onEvent = () => {}, options = {}) {
  const maxSteps = options.maxSteps || 8;
  const model = options.model || config.model;

  // Build message history
  let messages = [];
  if (typeof input === 'string') {
    messages = [{ role: 'user', content: input }];
  } else if (Array.isArray(input)) {
    messages = [...input];
  } else {
    throw new Error('Input must be a prompt string or an array of messages');
  }

  const steps = [];
  let stepCount = 0;
  let finalAnswer = '';
  let lastResponse = null;

  onEvent({
    type: 'agent:start',
    prompt: typeof input === 'string' ? input : messages[messages.length - 1]?.content,
    model
  });

  while (stepCount < maxSteps) {
    stepCount++;
    onEvent({ type: 'agent:step_start', step: stepCount });

    let response;
    try {
      response = await callClaude({
        messages,
        system: SYSTEM_PROMPT,
        tools: TOOL_DEFINITIONS,
        model
      });
      lastResponse = response;
    } catch (err) {
      onEvent({ type: 'agent:error', error: err.message });
      throw err;
    }

    const contentBlocks = response.content || [];

    // Extract thinking blocks if present
    const thinkingBlock = contentBlocks.find(b => b.type === 'thinking');
    if (thinkingBlock && thinkingBlock.thinking) {
      onEvent({
        type: 'agent:thought',
        thought: thinkingBlock.thinking,
        step: stepCount
      });
    }

    // Extract text blocks
    const textBlocks = contentBlocks.filter(b => b.type === 'text');
    const stepText = textBlocks.map(b => b.text).join('\n');
    if (stepText) {
      onEvent({
        type: 'agent:message_chunk',
        text: stepText,
        step: stepCount
      });
    }

    // Check for tool calls
    const toolUseBlocks = contentBlocks.filter(b => b.type === 'tool_use');

    // Record step in history
    steps.push({
      step: stepCount,
      stop_reason: response.stop_reason,
      content: contentBlocks
    });

    if (toolUseBlocks.length > 0) {
      // Append assistant's turn with tool_use blocks to message history
      messages.push({
        role: 'assistant',
        content: contentBlocks
      });

      const toolResults = [];

      for (const toolUse of toolUseBlocks) {
        onEvent({
          type: 'agent:tool_call',
          id: toolUse.id,
          name: toolUse.name,
          input: toolUse.input,
          step: stepCount
        });

        let toolOutput;
        try {
          toolOutput = await executeTool(toolUse.name, toolUse.input);
        } catch (err) {
          toolOutput = { error: err.message };
        }

        onEvent({
          type: 'agent:tool_result',
          id: toolUse.id,
          name: toolUse.name,
          result: toolOutput,
          step: stepCount
        });

        toolResults.push({
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: JSON.stringify(toolOutput)
        });
      }

      // Add user message containing all tool results
      messages.push({
        role: 'user',
        content: toolResults
      });

      // Continue to next step in the loop
      continue;
    }

    // No tool calls, assistant has finished its turn
    finalAnswer = stepText || '';
    messages.push({
      role: 'assistant',
      content: contentBlocks
    });
    break;
  }

  onEvent({
    type: 'agent:finish',
    answer: finalAnswer,
    stepsCount: stepCount,
    model: lastResponse?.model || model
  });

  return {
    success: true,
    answer: finalAnswer,
    steps,
    messages
  };
}
