// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import cloudflare from "@astrojs/cloudflare";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";
import { parse as parseJsonc } from "jsonc-parser";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeSlug from "rehype-slug";
import { changelogEntries } from "./src/lib/changelog.ts";

// Read public, non-secret values from wrangler.jsonc so the deployment config
// is the single source of truth. These get inlined into the build, which is
// needed because all human-facing pages are prerendered — runtime `env`
// bindings aren't available when the HTML is generated.
const projectRoot = dirname(fileURLToPath(import.meta.url));
const wranglerConfig = parseJsonc(
	readFileSync(resolve(projectRoot, "wrangler.jsonc"), "utf-8"),
);
const wranglerVars = wranglerConfig?.vars ?? {};
const siteUrl = wranglerVars.SITE_URL || "https://opencode.school";
const aiSearchApiUrl = wranglerVars.AI_SEARCH_API_URL ?? "";

// Map of changelog slugs to their dates for setting <lastmod> in the sitemap.
const changelogLastmod = new Map(
	changelogEntries.map((entry) => [entry.slug, entry.date]),
);

// Per-page priority based on URL path. Higher = more important to index first.
function priorityFor(path) {
	if (path === "/") return 1.0;
	if (path.startsWith("/lessons/")) return 0.9;
	if (path === "/exercises" || path.startsWith("/exercises/")) return 0.8;
	if (path === "/about" || path === "/tips") return 0.6;
	if (
		path === "/contributing" ||
		path === "/glossary" ||
		path === "/troubleshooting"
	)
		return 0.5;
	if (path === "/changelog") return 0.4;
	if (path === "/disenroll" || path.startsWith("/changelog/")) return 0.3;
	return undefined;
}

export default defineConfig({
	site: siteUrl,
	output: "server",
	adapter: cloudflare(),
	integrations: [
		mdx(),
		sitemap({
			// Exclude prerendered routes that aren't search-relevant. /api/* and
			// /llms.txt are SSR-only so they're already excluded automatically.
			filter: (page) => {
				const path = new URL(page).pathname.replace(/\/$/, "") || "/";
				return path !== "/404" && path !== "/changelog.xml";
			},
			serialize(item) {
				const path = new URL(item.url).pathname.replace(/\/$/, "") || "/";
				const priority = priorityFor(path);
				if (priority !== undefined) item.priority = priority;
				const changelogMatch = path.match(/^\/changelog\/(.+)$/);
				if (changelogMatch) {
					const lastmod = changelogLastmod.get(changelogMatch[1]);
					if (lastmod) item.lastmod = lastmod;
				}
				return item;
			},
		}),
	],
	markdown: {
		rehypePlugins: [
			rehypeSlug,
			[
				rehypeAutolinkHeadings,
				{ behavior: "wrap", properties: { class: "heading-anchor" } },
			],
		],
		shikiConfig: {
			theme: "vesper",
		},
	},
	security: {
		checkOrigin: false,
	},
	vite: {
		plugins: [tailwindcss()],
		define: {
			__AI_SEARCH_API_URL__: JSON.stringify(aiSearchApiUrl),
		},
	},
});
