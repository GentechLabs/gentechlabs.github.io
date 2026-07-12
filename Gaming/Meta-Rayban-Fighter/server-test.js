const http = require('http');

// Test that the server is serving the files correctly
const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/',
  method: 'GET'
};

const req = http.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);

  if (res.statusCode === 200) {
    console.log('✓ Server is running and serving files');
  } else {
    console.log('✗ Server returned non-200 status');
  }

  process.exit(0);
});

req.on('error', (error) => {
  console.error('✗ Server test failed:', error.message);
  process.exit(1);
});

req.end();