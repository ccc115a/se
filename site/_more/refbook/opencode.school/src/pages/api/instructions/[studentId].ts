// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { env } from "cloudflare:workers";
import type { APIRoute } from "astro";
import { getProgress } from "../../../lib/progress";
import { isValidStudentId } from "../../../lib/student-id";

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
};

export const OPTIONS: APIRoute = async () => {
	return new Response(null, { status: 204, headers: corsHeaders });
};

export const GET: APIRoute = async ({ params, request }) => {
	const { studentId } = params;
	if (!studentId || !isValidStudentId(studentId)) {
		return new Response(
			JSON.stringify({ error: "Invalid student ID format" }),
			{
				status: 400,
				headers: { "Content-Type": "application/json", ...corsHeaders },
			},
		);
	}

	const progress = await getProgress(env.PROGRESS, studentId);
	if (!progress) {
		return new Response(JSON.stringify({ error: "Student not found" }), {
			status: 404,
			headers: { "Content-Type": "application/json", ...corsHeaders },
		});
	}

	const origin = new URL(request.url).origin;

	const content = `My OpenCode School student ID is ${studentId}

When I mention school, lessons, progress, exercises, enrollment, or my student ID, use this ID to fetch my OpenCode School data as needed.

For the full OpenCode School agent protocol, fetch ${origin}/llms.txt
`;

	return new Response(content, {
		status: 200,
		headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders },
	});
};
