/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Enable SWC minification for faster builds
  swcMinify: true,
  // Disable type checking during build for faster dev builds
  typescript: {
    ignoreBuildErrors: false,
  },
  // Disable eslint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig
