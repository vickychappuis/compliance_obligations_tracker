import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      // Document uploads flow through a Server Action; the default 1 MB cap is
      // far below the 10 MB the UI advertises. Allow headroom for multipart overhead.
      bodySizeLimit: "15mb",
    },
  },
};

export default nextConfig;
