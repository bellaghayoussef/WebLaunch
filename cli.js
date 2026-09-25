#!/usr/bin/env node
import { runAgent } from './src/agent.js';
import { config } from './src/config.js';

// ANSI color helpers
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  red: '\x1b[31m',
  bgDark: '\x1b[40m'
};

async function main() {
  const args = process.argv.slice(2);
  const prompt = args.join(' ').trim();

  if (!prompt) {
    console.log(`\n${colors.cyan}${colors.bright}🤖 AgentX - Autonomous Claude Agent CLI${colors.reset}`);
    console.log(`${colors.dim}Endpoint:${colors.reset} ${config.baseURL}`);
    console.log(`${colors.dim}Model:${colors.reset}    ${config.model} (fallback: ${config.fallbackModel})\n`);
    console.log(`Usage:`);
    console.log(`  node cli.js "<your prompt here>"`);
    console.log(`\nExample:`);
    console.log(`  node cli.js "cherche sur le web les dernières nouvelles de SpaceX"\n`);
    process.exit(0);
  }

  console.log(`\n${colors.cyan}${colors.bright}🤖 AgentX Running...${colors.reset}`);
  console.log(`${colors.dim}Prompt:${colors.reset} ${prompt}`);
  console.log(`${colors.dim}Model:${colors.reset}  ${config.model}`);
  console.log(`${colors.dim}─`.repeat(60) + colors.reset);

  try {
    const result = await runAgent(prompt, (event) => {
      switch (event.type) {
        case 'agent:thought':
          console.log(`\n${colors.magenta}💭 [Thinking]${colors.reset}`);
          console.log(`${colors.dim}${event.thought.trim()}${colors.reset}`);
          break;

        case 'agent:tool_call':
          console.log(`\n${colors.yellow}⚡ [Tool Call]${colors.reset} ${colors.bright}${event.name}${colors.reset}`);
          console.log(`${colors.dim}Input:${colors.reset} ${JSON.stringify(event.input)}`);
          break;

        case 'agent:tool_result': {
          const resStr = JSON.stringify(event.result);
          const preview = resStr.length > 250 ? resStr.slice(0, 250) + '...' : resStr;
          console.log(`${colors.green}✔ [Tool Result]${colors.reset} ${colors.dim}${preview}${colors.reset}`);
          break;
        }

        case 'agent:step_start':
          console.log(`\n${colors.blue}▶ Step ${event.step}...${colors.reset}`);
          break;

        case 'agent:error':
          console.error(`\n${colors.red}❌ Error:${colors.reset} ${event.error}`);
          break;
      }
    });

    console.log(`\n${colors.dim}─`.repeat(60) + colors.reset);
    console.log(`\n${colors.green}${colors.bright}💬 Final Answer:${colors.reset}\n`);
    console.log(result.answer);
    console.log(`\n${colors.dim}Completed in ${result.steps.length} step(s).${colors.reset}\n`);

  } catch (err) {
    console.error(`\n${colors.red}Agent execution failed:${colors.reset}`, err.message);
    process.exit(1);
  }
}

main();
