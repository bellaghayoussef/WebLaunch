import fs from 'fs';
import path from 'path';
import vm from 'vm';
import { config } from './config.js';

/**
 * Searches DuckDuckGo & Wikipedia to provide reliable real-time web search results
 */
export async function webSearch(query) {
  const results = [];
  const trimmed = query.trim();

  // 1. Wikipedia Search for encyclopedic topics
  try {
    const wikiUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(trimmed)}&format=json&utf8=1`;
    const res = await fetch(wikiUrl, { signal: AbortSignal.timeout(6000) });
    if (res.ok) {
      const data = await res.json();
      const hits = data.query?.search || [];
      for (const hit of hits.slice(0, 3)) {
        const cleanSnippet = hit.snippet.replace(/<[^>]+>/g, '').trim();
        results.push({
          title: hit.title,
          snippet: cleanSnippet,
          url: `https://en.wikipedia.org/wiki/${encodeURIComponent(hit.title.replace(/ /g, '_'))}`,
          source: 'Wikipedia'
        });
      }
    }
  } catch (err) {
    // Continue to next strategy
  }

  // 2. DuckDuckGo Instant Answers & Related Topics
  try {
    const ddgApiUrl = `https://api.duckduckgo.com/?q=${encodeURIComponent(trimmed)}&format=json&no_html=1&skip_disambig=1`;
    const res = await fetch(ddgApiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      const data = await res.json();
      if (data.AbstractText) {
        results.unshift({
          title: data.Heading || trimmed,
          snippet: data.AbstractText,
          url: data.AbstractURL || 'https://duckduckgo.com/?q=' + encodeURIComponent(trimmed),
          source: 'DuckDuckGo Instant Answer'
        });
      }
      if (Array.isArray(data.RelatedTopics)) {
        for (const topic of data.RelatedTopics.slice(0, 3)) {
          if (topic.Text && topic.FirstURL) {
            results.push({
              title: topic.Text.split(' - ')[0] || topic.Text.slice(0, 50),
              snippet: topic.Text,
              url: topic.FirstURL,
              source: 'DuckDuckGo Related'
            });
          }
        }
      }
    }
  } catch (err) {
    // Continue
  }

  // 3. DuckDuckGo HTML Lite / HTML scraping for web links
  try {
    const ddgHtmlUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(trimmed)}`;
    const res = await fetch(ddgHtmlUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8'
      },
      signal: AbortSignal.timeout(7000)
    });
    if (res.ok) {
      const html = await res.text();
      // Extract links & snippets
      const linkRegex = /<a[^>]*class="result__snippet"[^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi;
      const titleRegex = /<a[^>]*class="result__url"[^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi;
      
      let match;
      let count = 0;
      while ((match = linkRegex.exec(html)) !== null && count < 4) {
        count++;
        const rawHref = match[1];
        const snippet = match[2].replace(/<[^>]+>/g, '').trim();
        // Decode DDG redirect URL if present
        let finalUrl = rawHref;
        if (rawHref.includes('uddg=')) {
          try {
            const parsed = new URL('https://duckduckgo.com' + rawHref);
            finalUrl = decodeURIComponent(parsed.searchParams.get('uddg') || rawHref);
          } catch {}
        }
        results.push({
          title: `Result ${count} for "${trimmed}"`,
          snippet,
          url: finalUrl,
          source: 'Web Search'
        });
      }
    }
  } catch (err) {
    // Ignore
  }

  if (results.length === 0) {
    return {
      query: trimmed,
      message: `No immediate web search results found for "${trimmed}".`,
      results: []
    };
  }

  return {
    query: trimmed,
    count: results.length,
    results
  };
}

/**
 * Fetch and extract readable text from a URL
 */
export async function fetchUrl(url) {
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      signal: AbortSignal.timeout(8000)
    });
    if (!res.ok) {
      return { error: `Failed to fetch URL. HTTP Status: ${res.status} ${res.statusText}` };
    }
    const html = await res.text();
    // Simple text extraction: remove scripts, styles, html tags
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, '')
      .replace(/<style[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s{2,}/g, ' ')
      .trim();

    return {
      url,
      content: text.slice(0, 4000) + (text.length > 4000 ? '... [truncated]' : '')
    };
  } catch (e) {
    return { error: `Error fetching URL: ${e.message}` };
  }
}

/**
 * Executes a snippet of JavaScript code safely in a sandbox
 */
export function runJavascript(code) {
  try {
    const sandbox = {
      Math,
      Date,
      JSON,
      parseInt,
      parseFloat,
      isNaN,
      isFinite,
      Array,
      Object,
      String,
      Number,
      Boolean,
      RegExp,
      output: null
    };
    const context = vm.createContext(sandbox);
    const result = vm.runInContext(code, context, { timeout: 3000 });
    return {
      success: true,
      result: result !== undefined ? result : sandbox.output
    };
  } catch (err) {
    return {
      success: false,
      error: err.message
    };
  }
}

/**
 * Workspace file operations
 */
export function listFiles(subDir = '') {
  try {
    const targetDir = path.resolve(config.workspaceDir, subDir);
    if (!targetDir.startsWith(config.workspaceDir)) {
      return { error: 'Access denied: Path outside workspace.' };
    }
    if (!fs.existsSync(targetDir)) {
      return { error: `Directory does not exist: ${subDir}` };
    }
    const entries = fs.readdirSync(targetDir, { withFileTypes: true });
    return {
      path: subDir || '.',
      files: entries.map(e => ({
        name: e.name,
        type: e.isDirectory() ? 'directory' : 'file'
      }))
    };
  } catch (e) {
    return { error: e.message };
  }
}

export function readFile(filePath) {
  try {
    const fullPath = path.resolve(config.workspaceDir, filePath);
    if (!fullPath.startsWith(config.workspaceDir)) {
      return { error: 'Access denied: Path outside workspace.' };
    }
    if (!fs.existsSync(fullPath)) {
      return { error: `File not found: ${filePath}` };
    }
    const content = fs.readFileSync(fullPath, 'utf8');
    return {
      path: filePath,
      content: content.slice(0, 8000)
    };
  } catch (e) {
    return { error: e.message };
  }
}

export function writeFile(filePath, content) {
  try {
    const fullPath = path.resolve(config.workspaceDir, filePath);
    if (!fullPath.startsWith(config.workspaceDir)) {
      return { error: 'Access denied: Path outside workspace.' };
    }
    const dir = path.dirname(fullPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(fullPath, content, 'utf8');
    return {
      success: true,
      path: filePath,
      bytesWritten: Buffer.byteLength(content, 'utf8')
    };
  } catch (e) {
    return { error: e.message };
  }
}

/**
 * Tool definitions exposed to Claude
 */
export const TOOL_DEFINITIONS = [
  {
    name: 'web_search',
    description: 'Searches the web for up-to-date real-time information, news, websites, and encyclopedic facts.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'The search query or keywords to look up on the web'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'fetch_url',
    description: 'Fetches and reads the textual content of a specific webpage URL.',
    input_schema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'The HTTP or HTTPS URL of the webpage to fetch'
        }
      },
      required: ['url']
    }
  },
  {
    name: 'run_javascript',
    description: 'Executes JavaScript code in a sandboxed runtime. Useful for mathematical calculations, data transformations, and algorithm checks.',
    input_schema: {
      type: 'object',
      properties: {
        code: {
          type: 'string',
          description: 'The JavaScript code snippet to evaluate (e.g. "Math.sqrt(144) * 5" or "(143 * 37) / 2")'
        }
      },
      required: ['code']
    }
  },
  {
    name: 'read_file',
    description: 'Reads the text content of a file in the project workspace.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Relative path of the file to read (e.g. "config.json" or "package.json")'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'write_file',
    description: 'Creates or updates a file in the project workspace with given content.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Relative path of the file to write (e.g. "notes.txt" or "data/output.json")'
        },
        content: {
          type: 'string',
          description: 'The full text content to write into the file'
        }
      },
      required: ['path', 'content']
    }
  },
  {
    name: 'list_files',
    description: 'Lists all files and folders in a workspace directory.',
    input_schema: {
      type: 'object',
      properties: {
        directory: {
          type: 'string',
          description: 'Relative path to directory (leave empty or use "." for root)'
        }
      }
    }
  },
  {
    name: 'get_current_time',
    description: 'Returns the current server date, time, and timezone.',
    input_schema: {
      type: 'object',
      properties: {}
    }
  }
];

/**
 * Dispatcher to execute a tool by name with arguments
 */
export async function executeTool(name, input) {
  switch (name) {
    case 'web_search':
      return await webSearch(input.query || '');
    case 'fetch_url':
      return await fetchUrl(input.url || '');
    case 'run_javascript':
      return runJavascript(input.code || '');
    case 'read_file':
      return readFile(input.path || '');
    case 'write_file':
      return writeFile(input.path || '', input.content || '');
    case 'list_files':
      return listFiles(input.directory || '');
    case 'get_current_time':
      return {
        iso: new Date().toISOString(),
        locale: new Date().toLocaleString(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      };
    default:
      return { error: `Unknown tool: ${name}` };
  }
}
