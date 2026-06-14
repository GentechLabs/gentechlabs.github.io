const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 633 });
  
  const htmlPath = path.resolve(__dirname, 'thumbnail-gen.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
  
  await page.screenshot({
    path: path.resolve(__dirname, 'dashboard-thumbnail.png'),
    type: 'png',
    clip: { x: 0, y: 0, width: 1280, height: 633 }
  });
  
  console.log('Thumbnail saved to assets/dashboard-thumbnail.png');
  await browser.close();
})();
