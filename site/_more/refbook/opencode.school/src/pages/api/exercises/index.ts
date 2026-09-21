// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { getCollection } from "astro:content";
import type { APIRoute } from "astro";
import { mdxToProse } from "../../../lib/mdx-to-prose";

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
};

export const OPTIONS: APIRoute = async () => {
	return new Response(null, { status: 204, headers: corsHeaders });
};

export const GET: APIRoute = async ({ request }) => {
	const origin = new URL(request.url).origin;
	const exercises = (await getCollection("exercises")).sort(
		(a, b) => a.data.order - b.data.order,
	);

	const result = exercises.map((exercise) => {
		const agentInstructions = exercise.data.agentInstructions.replaceAll(
			"{origin}",
			origin,
		);

		return {
			order: exercise.data.order,
			slug: exercise.data.slug,
			title: exercise.data.title,
			description: exercise.data.description,
			agentInstructions,
			content: mdxToProse(exercise.body),
		};
	});

	return new Response(JSON.stringify(result), {
		status: 200,
		headers: {
			"Content-Type": "application/json",
			...corsHeaders,
		},
	});
};
