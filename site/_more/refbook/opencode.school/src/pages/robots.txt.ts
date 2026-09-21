// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import type { APIRoute } from "astro";

export const GET: APIRoute = (context) => {
	const origin = new URL(context.request.url).origin;
	const content = `User-agent: *
Allow: /

Sitemap: ${origin}/sitemap-index.xml
`;
	return new Response(content, {
		status: 200,
		headers: { "Content-Type": "text/plain; charset=utf-8" },
	});
};
