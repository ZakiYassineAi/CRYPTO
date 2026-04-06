const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const BASE_DIR = __dirname;

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf'
};

const server = http.createServer((req, res) => {
    // Remove query strings and decode URI
    let filePath = decodeURIComponent(req.url.split('?')[0]);
    
    // Default to index.html
    if (filePath === '/') {
        filePath = '/index.html';
    }
    
    const fullPath = path.join(BASE_DIR, filePath);
    
    // Security: prevent directory traversal
    if (!fullPath.startsWith(BASE_DIR)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }
    
    const ext = path.extname(fullPath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    
    fs.readFile(fullPath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                // Serve index.html for SPA-like behavior
                fs.readFile(path.join(BASE_DIR, 'index.html'), (err2, indexContent) => {
                    if (err2) {
                        res.writeHead(500);
                        res.end('Server Error');
                        return;
                    }
                    res.writeHead(200, { 
                        'Content-Type': 'text/html',
                        'Cache-Control': 'no-cache'
                    });
                    res.end(indexContent);
                });
            } else {
                res.writeHead(500);
                res.end('Server Error');
            }
        } else {
            // Set caching headers
            const cacheControl = ext === '.html' ? 'no-cache' : 'public, max-age=31536000';
            
            res.writeHead(200, {
                'Content-Type': contentType,
                'Cache-Control': cacheControl,
                'Access-Control-Allow-Origin': '*'
            });
            res.end(content);
        }
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`SwapVault server running on http://0.0.0.0:${PORT}`);
    console.log(`Ready to serve crypto exchange platform`);
});
