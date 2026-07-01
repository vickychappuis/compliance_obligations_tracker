import type { NextConfig } from "next";

import { MAX_UPLOAD_MB } from "./lib/constants";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      // Document uploads flow through a Server Action, so this must clear the
      // MAX_UPLOAD_MB the UI accepts, plus headroom for multipart overhead.
      bodySizeLimit: `${MAX_UPLOAD_MB + 5}mb`,
    },
  },
};

export default nextConfig;
