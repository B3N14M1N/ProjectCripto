// setupProxy.js
// Configureaza proxy-ul pentru development in Docker
// In Docker, containerele comunica prin numele serviciului, nu localhost

const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Determinam URL-ul backend-ului
  // In Docker: http://backend:5000
  // Local: http://localhost:5000
  const target = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  
  app.use(
    '/api',
    createProxyMiddleware({
      target: target,
      changeOrigin: true,
      // Log pentru debugging
      onProxyReq: (proxyReq, req, res) => {
        console.log(`[Proxy] ${req.method} ${req.url} -> ${target}${req.url}`);
      },
      onError: (err, req, res) => {
        console.error('[Proxy Error]', err.message);
      }
    })
  );
};
