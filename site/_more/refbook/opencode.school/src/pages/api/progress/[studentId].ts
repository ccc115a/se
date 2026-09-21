// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { env } from "cloudflare:workers";
import type { APIRoute } from "astro";
import {
	type CompletionSource,
	getProgress,
	markExerciseComplete,
	markExerciseIncomplete,
	markLessonComplete,
	markLessonIncomplete,
	resetProgress,
} from "../../../lib/progress";
import { isValidStudentId } from "../../../lib/student-id";
import {
	getAgentOnlySlugs,
	getValidSlugs,
	validateSlug,
} from "../../../lib/valid-slugs";

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, PUT, DELETE, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
};

function notFound(message: string) {
	return new Response(JSON.stringify({ error: message }), {
		status: 404,
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
}

function badRequest(message: string) {
	return new Response(JSON.stringify({ error: message }), {
		status: 400,
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
}

export const OPTIONS: APIRoute = async () => {
	return new Response(null, { status: 204, headers: corsHeaders });
};

export const GET: APIRoute = async ({ params }) => {
	const { studentId } = params;
	if (!studentId || !isValidStudentId(studentId)) {
		return badRequest("Invalid student ID format");
	}

	const progress = await getProgress(env.PROGRESS, studentId);
	if (!progress) {
		return notFound("Student not found");
	}

	return new Response(JSON.stringify(progress), {
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
};

export const PUT: APIRoute = async ({ params, request }) => {
	const { studentId } = params;
	if (!studentId || !isValidStudentId(studentId)) {
		return badRequest("Invalid student ID format");
	}

	let body: {
		lessonSlug?: string;
		exerciseSlug?: string;
		source?: string;
		model?: string;
	};
	try {
		body = await request.json();
	} catch {
		return badRequest("Invalid JSON body");
	}

	const hasLesson =
		typeof body.lessonSlug === "string" && body.lessonSlug.length > 0;
	const hasExercise =
		typeof body.exerciseSlug === "string" && body.exerciseSlug.length > 0;

	if (!hasLesson && !hasExercise) {
		return badRequest(
			'Missing or invalid "lessonSlug" or "exerciseSlug" field',
		);
	}

	const source: CompletionSource =
		body.source === "agent" ? "agent" : "browser";

	const model =
		typeof body.model === "string" && body.model.trim()
			? body.model.trim()
			: undefined;

	const slug = hasExercise
		? (body.exerciseSlug as string)
		: (body.lessonSlug as string);

	const { lessonSlugs, exerciseSlugs } = await getValidSlugs();
	const slugError = hasExercise
		? validateSlug(slug, exerciseSlugs, "exercise")
		: validateSlug(slug, lessonSlugs, "lesson");
	if (slugError) {
		return badRequest(slugError);
	}

	// Agent-only lessons cannot be completed from the browser
	if (hasLesson && source === "browser") {
		const agentOnlySlugs = await getAgentOnlySlugs();
		if (agentOnlySlugs.has(slug)) {
			return new Response(
				JSON.stringify({
					error: "This lesson can only be completed via OpenCode",
				}),
				{
					status: 403,
					headers: { "Content-Type": "application/json", ...corsHeaders },
				},
			);
		}
	}

	const progress = hasExercise
		? await markExerciseComplete(env.PROGRESS, studentId, slug, source, model)
		: await markLessonComplete(env.PROGRESS, studentId, slug, source, model);
	if (!progress) {
		return notFound("Student not found");
	}

	return new Response(JSON.stringify(progress), {
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
};

export const DELETE: APIRoute = async ({ params, request }) => {
	const { studentId } = params;
	if (!studentId || !isValidStudentId(studentId)) {
		return badRequest("Invalid student ID format");
	}

	let body: {
		lessonSlug?: string;
		exerciseSlug?: string;
		reset?: boolean;
	};
	try {
		body = await request.json();
	} catch {
		return badRequest("Invalid JSON body");
	}

	const isReset = body.reset === true;
	const hasLesson =
		typeof body.lessonSlug === "string" && body.lessonSlug.length > 0;
	const hasExercise =
		typeof body.exerciseSlug === "string" && body.exerciseSlug.length > 0;

	if (!isReset && !hasLesson && !hasExercise) {
		return badRequest('Provide "lessonSlug", "exerciseSlug", or "reset": true');
	}

	if (!isReset) {
		const { lessonSlugs, exerciseSlugs } = await getValidSlugs();
		const slug = hasExercise
			? (body.exerciseSlug as string)
			: (body.lessonSlug as string);
		const slugError = hasExercise
			? validateSlug(slug, exerciseSlugs, "exercise")
			: validateSlug(slug, lessonSlugs, "lesson");
		if (slugError) {
			return badRequest(slugError);
		}
	}

	let progress: Awaited<ReturnType<typeof resetProgress>>;
	if (isReset) {
		progress = await resetProgress(env.PROGRESS, studentId);
	} else if (hasExercise) {
		progress = await markExerciseIncomplete(
			env.PROGRESS,
			studentId,
			body.exerciseSlug as string,
		);
	} else {
		progress = await markLessonIncomplete(
			env.PROGRESS,
			studentId,
			body.lessonSlug as string,
		);
	}

	if (!progress) {
		return notFound("Student not found");
	}

	return new Response(JSON.stringify(progress), {
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
};
