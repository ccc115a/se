// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

/// <reference types="astro/client" />

interface CloudflareEnv {
	PROGRESS: KVNamespace;
}

declare module "cloudflare:workers" {
	const env: CloudflareEnv;
	export { env };
}
