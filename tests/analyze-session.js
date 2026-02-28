#!/usr/bin/env node
/**
 * Analyze Claude Code session transcripts.
 * Parses .jsonl files to extract useful information.
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

function loadSession(sessionFile) {
  const messages = [];
  const content = fs.readFileSync(sessionFile, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());

  for (const line of lines) {
    try {
      messages.push(JSON.parse(line));
    } catch (e) {
      // Skip invalid lines
    }
  }
  return messages;
}

function extractToolInvocations(messages) {
  const tools = [];

  for (const msg of messages) {
    if (msg.type !== 'assistant') continue;

    const content = msg.message?.content;
    if (!Array.isArray(content)) continue;

    for (const item of content) {
      if (item.type === 'tool_use') {
        tools.push({
          name: item.name,
          input: item.input || {},
          id: item.id
        });
      }
    }
  }
  return tools;
}

function extractSkillInvocations(messages) {
  const skills = [];

  for (const msg of messages) {
    if (msg.type !== 'assistant') continue;

    const content = msg.message?.content;
    if (!Array.isArray(content)) continue;

    for (const item of content) {
      if (item.type === 'tool_use' && item.name === 'Skill') {
        const inputData = item.input || {};
        skills.push({
          skill: inputData.skill,
          args: inputData.args || '',
          id: item.id
        });
      }
    }
  }
  return skills;
}

function calculateTokenUsage(messages) {
  let totalInput = 0;
  let totalOutput = 0;
  let cacheRead = 0;
  let cacheCreation = 0;

  for (const msg of messages) {
    const usage = msg.message?.usage || {};
    totalInput += usage.input_tokens || 0;
    totalOutput += usage.output_tokens || 0;
    cacheRead += usage.cache_read_input_tokens || 0;
    cacheCreation += usage.cache_creation_input_tokens || 0;
  }

  return {
    input: totalInput,
    output: totalOutput,
    cacheRead,
    cacheCreation,
    total: totalInput + totalOutput
  };
}

function extractUserMessages(messages) {
  const userMsgs = [];

  for (const msg of messages) {
    if (msg.type !== 'user') continue;

    const content = msg.message?.content;
    if (!Array.isArray(content)) continue;

    for (const item of content) {
      if (item.type === 'text') {
        userMsgs.push(item.text);
      }
    }
  }
  return userMsgs;
}

function extractAssistantMessages(messages) {
  const assistantMsgs = [];

  for (const msg of messages) {
    if (msg.type !== 'assistant') continue;

    const content = msg.message?.content;
    if (!Array.isArray(content)) continue;

    const textParts = [];
    for (const item of content) {
      if (item.type === 'text') {
        textParts.push(item.text);
      }
    }
    if (textParts.length > 0) {
      assistantMsgs.push(textParts.join('\n'));
    }
  }
  return assistantMsgs;
}

function analyzeSession(sessionFile, verbose = false) {
  if (!fs.existsSync(sessionFile)) {
    console.error(`Error: Session file not found: ${sessionFile}`);
    process.exit(1);
  }

  const messages = loadSession(sessionFile);

  console.log(`\nSession: ${path.basename(sessionFile)}`);
  console.log(`Total messages: ${messages.length}`);

  // Token usage
  const usage = calculateTokenUsage(messages);
  console.log(`\n--- Token Usage ---`);
  console.log(`  Input:        ${usage.input.toLocaleString()}`);
  console.log(`  Output:       ${usage.output.toLocaleString()}`);
  console.log(`  Cache read:   ${usage.cacheRead.toLocaleString()}`);
  console.log(`  Cache create: ${usage.cacheCreation.toLocaleString()}`);
  console.log(`  Total:        ${usage.total.toLocaleString()}`);

  // Skills invoked
  const skills = extractSkillInvocations(messages);
  console.log(`\n--- Skills Invoked (${skills.length}) ---`);
  if (skills.length > 0) {
    for (const skill of skills) {
      const argsPreview = skill.args.length > 50
        ? skill.args.slice(0, 50) + '...'
        : skill.args;
      console.log(`  - ${skill.skill}: ${argsPreview}`);
    }
  } else {
    console.log('  (none)');
  }

  // Tools invoked
  const tools = extractToolInvocations(messages);
  const toolCounts = {};
  for (const tool of tools) {
    toolCounts[tool.name] = (toolCounts[tool.name] || 0) + 1;
  }

  console.log(`\n--- Tools Invoked ---`);
  const sortedTools = Object.entries(toolCounts).sort((a, b) => b[1] - a[1]);
  for (const [toolName, count] of sortedTools) {
    console.log(`  ${toolName}: ${count}`);
  }

  if (verbose) {
    const userMsgs = extractUserMessages(messages);
    console.log(`\n--- User Messages ---`);
    for (let i = 0; i < Math.min(5, userMsgs.length); i++) {
      console.log(`  ${i + 1}. ${userMsgs[i].slice(0, 100)}...`);
    }

    const assistantMsgs = extractAssistantMessages(messages);
    console.log(`\n--- Assistant Messages ---`);
    for (let i = 0; i < Math.min(3, assistantMsgs.length); i++) {
      console.log(`  ${i + 1}. ${assistantMsgs[i].slice(0, 100)}...`);
    }
  }

  return {
    messageCount: messages.length,
    usage,
    skills,
    tools: toolCounts
  };
}

function main() {
  const verbose = args.includes('-v') || args.includes('--verbose');
  const checkSkillIdx = args.indexOf('--check-skill');

  let sessionFile = args[0];
  if (!sessionFile || sessionFile.startsWith('-')) {
    console.log('Usage: node analyze-session.js <session.jsonl> [-v|--verbose] [--check-skill <skill-name>]');
    process.exit(1);
  }

  const result = analyzeSession(sessionFile, verbose);

  if (checkSkillIdx > -1 && args[checkSkillIdx + 1]) {
    const targetSkill = args[checkSkillIdx + 1];
    const skillFound = result.skills.some(s => s.skill === targetSkill);

    if (skillFound) {
      console.log(`\n✓ Skill '${targetSkill}' was invoked`);
      process.exit(0);
    } else {
      console.log(`\n✗ Skill '${targetSkill}' was NOT invoked`);
      process.exit(1);
    }
  }
}

main();
