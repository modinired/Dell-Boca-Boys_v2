/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverActions: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/:path*', // FastAPI backend
      },
      {
        source: '/ws/:path*',
        destination: 'http://localhost:8000/ws/:path*', // WebSocket
      },
    ]
  },
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
