/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Instagram CDN domains are dynamic; we render thumbnails with plain <img>,
  // so Next's image optimizer is left out of the loop on purpose.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
