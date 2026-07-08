import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 3000;

const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
};

const server = http.createServer((req, res) => {
  let filePath = '.' + req.url;

  if (filePath === './') {
    filePath = './index.html';
  }

  const extname = path.extname(filePath);
  const contentType = mimeTypes[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>', 'utf-8');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${error.code}`, 'utf-8');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('🎮 Meta Ray-Ban Neural Fighter Demo Running');
  console.log('='.repeat(50));
  console.log(`\n📍 Local: http://localhost:${PORT}`);
  console.log(`\n🎯 Keyboard Controls:`);
  console.log(`   A - Attack (Fist clench)`);
  console.log(`   G - Guard (Palm open + wrist rotate)`);
  console.log(`   C - Counter (Pinch + upward wrist flick)`);
  console.log(`   H - Holy Strike (Double tap + forward wrist)`);
  console.log(`   S - Smite (Double tap + backward wrist)`);
  console.log(`   P - Potion (Peace sign)`);
  console.log(`\n🧟 Demo: Levels 1-3, Darkest Dungeon style\n`);
  console.log('Press Ctrl+C to stop server\n');
});