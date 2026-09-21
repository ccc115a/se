// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { env } from "cloudflare:workers";
import type { APIRoute } from "astro";
import { createStudent } from "../../lib/progress";
import { generateStudentId } from "../../lib/student-id";

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "POST, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
};

export const OPTIONS: APIRoute = async () => {
	return new Response(null, { status: 204, headers: corsHeaders });
};

export const POST: APIRoute = async ({ request }) => {
	const kv = env.PROGRESS;
	const studentId = await generateStudentId(kv);

	let deviceId: string | undefined;
	try {
		const body = await request.json();
		if (typeof body?.deviceId === "string") deviceId = body.deviceId;
	} catch {
		// Body is optional; ignore parse errors
	}

	const progress = await createStudent(kv, studentId, deviceId);

	return new Response(JSON.stringify({ studentId, progress }), {
		status: 201,
		headers: {
			"Content-Type": "application/json",
			...corsHeaders,
		},
	});
};
