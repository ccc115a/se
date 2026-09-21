// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const lessons = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "src/content/lessons" }),
	schema: z.object({
		title: z.string(),
		slug: z.string(),
		description: z.string(),
		order: z.number(),
		quiz: z.boolean(),
		modifiesGlobalConfig: z.boolean().default(false),
		agentOnly: z.boolean().default(false),
		agentInstructions: z.string(),
	}),
});

const exercises = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "src/content/exercises" }),
	schema: z.object({
		title: z.string(),
		slug: z.string(),
		description: z.string(),
		order: z.number(),
		agentInstructions: z.string(),
	}),
});

export const collections = { lessons, exercises };
