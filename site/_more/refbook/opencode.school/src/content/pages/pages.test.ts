// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { describe, expect, it } from "vitest";
import cheatsheetRaw from "./cheatsheet.md?raw";
import glossaryRaw from "./glossary.md?raw";

describe("standalone markdown pages", () => {
	it("loads the cheatsheet markdown with expected frontmatter", () => {
		expect(cheatsheetRaw).toMatch(/^---[\s\S]*?slug:\s*cheatsheet[\s\S]*?---/);
		expect(cheatsheetRaw).toMatch(/title:\s*"Cheatsheet"/);
		expect(cheatsheetRaw.length).toBeGreaterThan(500);
	});

	it("loads the cheatsheet body content", () => {
		expect(cheatsheetRaw).toContain("## Slash commands");
	});

	it("loads the glossary markdown with expected frontmatter", () => {
		expect(glossaryRaw).toMatch(/^---[\s\S]*?slug:\s*glossary[\s\S]*?---/);
		expect(glossaryRaw).toMatch(/title:\s*"Glossary"/);
		expect(glossaryRaw.length).toBeGreaterThan(500);
	});

	it("loads the glossary body content", () => {
		expect(glossaryRaw).toContain("## agent");
		expect(glossaryRaw).toContain("## AGENTS.md");
	});
});
