/**
 * Memory Import Parser
 * Imports memories from various sources and maps to profile layers
 */

import fs from 'fs';
import path from 'path';

// Parse ChatGPT export format
function parseChatGPT(content) {
  const memories = [];
  const lines = content.split('\n');
  let currentLayer = null;
  let currentEntry = [];
  
  for (const line of lines) {
    // Detect layer headers
    if (line.startsWith('## Food') || line.startsWith('## Recipe')) {
      currentLayer = 'cookbook';
      continue;
    }
    if (line.startsWith('## Journal') || line.startsWith('## Feelings')) {
      currentLayer = 'journal';
      continue;
    }
    if (line.startsWith('## Travel') || line.startsWith('## Trip')) {
      currentLayer = 'travel';
      continue;
    }
    if (line.startsWith('## Gaming') || line.startsWith('## Build')) {
      currentLayer = 'gaming';
      continue;
    }
    if (line.startsWith('## Finance') || line.startsWith('## Portfolio')) {
      currentLayer = 'finance';
      continue;
    }
    
    // Capture content under current layer
    if (currentLayer && line.trim()) {
      currentEntry.push(line.trim());
    }
    
    // Empty line = end of entry
    if (!line.trim() && currentEntry.length > 0) {
      memories.push({
        layer: currentLayer,
        content: currentEntry.join('\n'),
        source: 'chatgpt',
        date: new Date().toISOString()
      });
      currentEntry = [];
    }
  }
  
  // Final entry
  if (currentEntry.length > 0) {
    memories.push({
      layer: currentLayer,
      content: currentEntry.join('\n'),
      source: 'chatgpt',
      date: new Date().toISOString()
    });
  }
  
  return memories;
}

// Parse Claude export format
function parseClaude(content) {
  const memories = [];
  const data = JSON.parse(content);
  
  if (data.messages) {
    for (const msg of data.messages) {
      if (msg.role === 'user') {
        const detected = detectLayer(msg.content);
        if (detected) {
          memories.push({
            layer: detected.layer,
            content: msg.content,
            confidence: detected.confidence,
            source: 'claude',
            date: msg.timestamp || new Date().toISOString()
          });
        }
      }
    }
  }
  
  return memories;
}

// Parse Obsidian vault notes
function parseObsidian(content) {
  const memories = [];
  
  // Extract YAML frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  let tags = [];
  
  if (frontmatterMatch) {
    const yaml = frontmatterMatch[1];
    const tagMatch = yaml.match(/tags:\s*\[([^\]]+)\]/);
    if (tagMatch) {
      tags = tagMatch[1].split(',').map(t => t.trim());
    }
  }
  
  // Detect layer from tags
  let layer = null;
  if (tags.some(t => ['recipe', 'cooking', 'food'].includes(t))) layer = 'cookbook';
  if (tags.some(t => ['journal', 'feelings', 'reflection'].includes(t))) layer = 'journal';
  if (tags.some(t => ['travel', 'trip', 'vacation'].includes(t))) layer = 'travel';
  if (tags.some(t => ['gaming', 'poe2', 'build'].includes(t))) layer = 'gaming';
  if (tags.some(t => ['finance', 'portfolio', 'defi'].includes(t))) layer = 'finance';
  
  // If no tags, detect from content
  if (!layer) {
    const detected = detectLayer(content);
    if (detected) layer = detected.layer;
  }
  
  if (layer) {
    memories.push({
      layer,
      content,
      source: 'obsidian',
      date: new Date().toISOString()
    });
  }
  
  return memories;
}

// Parse CSV/Spreadsheet
function parseCSV(content) {
  const memories = [];
  const lines = content.split('\n');
  const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
  
  // Detect layer from headers
  let layer = null;
  if (headers.includes('dish') || headers.includes('recipe') || headers.includes('food')) {
    layer = 'cookbook';
  } else if (headers.includes('mood') || headers.includes('feeling') || headers.includes('entry')) {
    layer = 'journal';
  } else if (headers.includes('destination') || headers.includes('trip') || headers.includes('flight')) {
    layer = 'travel';
  } else if (headers.includes('character') || headers.includes('build') || headers.includes('class')) {
    layer = 'gaming';
  } else if (headers.includes('token') || headers.includes('portfolio') || headers.includes('yield')) {
    layer = 'finance';
  }
  
  if (layer) {
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const entry = {};
      headers.forEach((h, idx) => {
        entry[h] = values[idx];
      });
      
      memories.push({
        layer,
        content: entry,
        source: 'csv',
        date: entry.date || new Date().toISOString()
      });
    }
  }
  
  return memories;
}

// Parse plain text
function parseText(content) {
  const memories = [];
  const paragraphs = content.split('\n\n');
  
  for (const para of paragraphs) {
    if (para.trim()) {
      const detected = detectLayer(para);
      if (detected) {
        memories.push({
          layer: detected.layer,
          content: para.trim(),
          confidence: detected.confidence,
          source: 'text',
          date: new Date().toISOString()
        });
      }
    }
  }
  
  return memories;
}

// Auto-detect layer from content
function detectLayer(content) {
  const lower = content.toLowerCase();
  
  // Cookbook
  const cookbookKeywords = ['recipe', 'cooked', 'made', 'ingredients', 'dish', 'meal', 'food', 'restaurant'];
  const cookbookPatterns = [/made (.+?) tonight/i, /cooked (.+?) with/i, /recipe for (.+?)/i];
  
  if (cookbookKeywords.some(k => lower.includes(k)) || cookbookPatterns.some(p => p.test(content))) {
    return { layer: 'cookbook', confidence: 0.8 };
  }
  
  // Journal
  const journalKeywords = ['feeling', 'today was', 'stressed', 'happy', 'sad', 'grateful', 'reflection'];
  const journalPatterns = [/today I (felt|was|am) (.+?)/i, /feeling (.+?) today/i];
  
  if (journalKeywords.some(k => lower.includes(k)) || journalPatterns.some(p => p.test(content))) {
    return { layer: 'journal', confidence: 0.7 };
  }
  
  // Travel
  const travelKeywords = ['trip', 'flight', 'hotel', 'vacation', 'travel', 'booking', 'packing'];
  const travelPatterns = [/flying to (.+?) on/i, /trip to (.+?)/i, /packing for (.+?)/i];
  
  if (travelKeywords.some(k => lower.includes(k)) || travelPatterns.some(p => p.test(content))) {
    return { layer: 'travel', confidence: 0.8 };
  }
  
  // Gaming
  const gamingKeywords = ['build', 'character', 'class', 'skills', 'level', 'quest', 'poe2', 'monk', 'sorceress'];
  const gamingPatterns = [/new (.+?) build/i, /playing (.+?) in/i, /(.+) class build/i];
  
  if (gamingKeywords.some(k => lower.includes(k)) || gamingPatterns.some(p => p.test(content))) {
    return { layer: 'gaming', confidence: 0.8 };
  }
  
  // Finance
  const financeKeywords = ['portfolio', 'yield', 'staking', 'lp position', 'defi', 'token', 'price'];
  const financePatterns = [/bought (.+?) at/i, /sold (.+?) for/i, /staking (.+?) on/i];
  
  if (financeKeywords.some(k => lower.includes(k)) || financePatterns.some(p => p.test(content))) {
    return { layer: 'finance', confidence: 0.8 };
  }
  
  return null;
}

// Main import function
export async function importMemory(filePath, source) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const ext = path.extname(filePath).toLowerCase();
  
  let parser;
  switch (source) {
    case 'chatgpt':
      parser = parseChatGPT;
      break;
    case 'claude':
      parser = parseClaude;
      break;
    case 'obsidian':
      parser = parseObsidian;
      break;
    case 'csv':
      parser = parseCSV;
      break;
    case 'text':
    default:
      parser = parseText;
      break;
  }
  
  const memories = parser(content);
  
  // Group by layer
  const byLayer = {};
  for (const mem of memories) {
    if (!byLayer[mem.layer]) {
      byLayer[mem.layer] = [];
    }
    byLayer[mem.layer].push(mem);
  }
  
  return {
    total: memories.length,
    byLayer,
    sources: [...new Set(memories.map(m => m.source))]
  };
}

// Export parsers for testing
export { parseChatGPT, parseClaude, parseObsidian, parseCSV, parseText, detectLayer };
