// Copyright (c) 2026 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import { env } from "cloudflare:workers";
import type { APIRoute } from "astro";
import {
	getProfile,
	type StudentProfile,
	updateProfile,
} from "../../../lib/progress";
import { isValidStudentId } from "../../../lib/student-id";

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
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

	const profile = await getProfile(env.PROGRESS, studentId);
	if (profile === null) {
		return notFound("Student not found");
	}

	return new Response(JSON.stringify({ profile }), {
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
};

const VALID_CODING_EXPERIENCE = ["rookie", "dabbler", "builder", "sage"];
const VALID_AI_TOOLS = [
	"chatgpt",
	"gemini",
	"claude",
	"claude-code",
	"openai-codex",
	"copilot",
];
const VALID_EDITORS = [
	"vscode",
	"cursor",
	"windsurf",
	"zed",
	"vim",
	"emacs",
	"other",
	"none",
];
const VALID_TERMINAL_COMFORT = ["none", "some", "very"];
const VALID_LEARNING_STYLE = ["concepts-first", "hands-on", "examples"];
const VALID_DEPTH_PREFERENCE = ["brief", "some-context", "all-details"];
const VALID_LANGUAGES = ["javascript", "typescript", "python", "go", "rust"];

function validateProfile(body: Record<string, unknown>): {
	profile: Partial<StudentProfile>;
	errors: string[];
} {
	const profile: Partial<StudentProfile> = {};
	const errors: string[] = [];

	if ("codingExperience" in body) {
		if (VALID_CODING_EXPERIENCE.includes(body.codingExperience as string)) {
			profile.codingExperience =
				body.codingExperience as StudentProfile["codingExperience"];
		} else {
			errors.push(
				`Invalid codingExperience: must be one of ${VALID_CODING_EXPERIENCE.join(", ")}`,
			);
		}
	}

	if ("aiTools" in body) {
		if (
			Array.isArray(body.aiTools) &&
			body.aiTools.every((t: unknown) => VALID_AI_TOOLS.includes(t as string))
		) {
			profile.aiTools = body.aiTools as string[];
		} else {
			errors.push(
				`Invalid aiTools: must be an array of ${VALID_AI_TOOLS.join(", ")}`,
			);
		}
	}

	if ("editor" in body) {
		if (VALID_EDITORS.includes(body.editor as string)) {
			profile.editor = body.editor as string;
		} else {
			errors.push(`Invalid editor: must be one of ${VALID_EDITORS.join(", ")}`);
		}
	}

	if ("terminalComfort" in body) {
		if (VALID_TERMINAL_COMFORT.includes(body.terminalComfort as string)) {
			profile.terminalComfort =
				body.terminalComfort as StudentProfile["terminalComfort"];
		} else {
			errors.push(
				`Invalid terminalComfort: must be one of ${VALID_TERMINAL_COMFORT.join(", ")}`,
			);
		}
	}

	if ("learningStyle" in body) {
		if (VALID_LEARNING_STYLE.includes(body.learningStyle as string)) {
			profile.learningStyle =
				body.learningStyle as StudentProfile["learningStyle"];
		} else {
			errors.push(
				`Invalid learningStyle: must be one of ${VALID_LEARNING_STYLE.join(", ")}`,
			);
		}
	}

	if ("depthPreference" in body) {
		if (VALID_DEPTH_PREFERENCE.includes(body.depthPreference as string)) {
			profile.depthPreference =
				body.depthPreference as StudentProfile["depthPreference"];
		} else {
			errors.push(
				`Invalid depthPreference: must be one of ${VALID_DEPTH_PREFERENCE.join(", ")}`,
			);
		}
	}

	if ("languages" in body) {
		if (
			Array.isArray(body.languages) &&
			body.languages.every((l: unknown) =>
				VALID_LANGUAGES.includes(l as string),
			)
		) {
			profile.languages = body.languages as string[];
		} else {
			errors.push(
				`Invalid languages: must be an array of ${VALID_LANGUAGES.join(", ")}`,
			);
		}
	}

	if ("os" in body) {
		if (typeof body.os === "string" && body.os.trim()) {
			profile.os = body.os.trim().toLowerCase();
		} else {
			errors.push("Invalid os: must be a non-empty string");
		}
	}

	return { profile, errors };
}

export const PUT: APIRoute = async ({ params, request }) => {
	const { studentId } = params;
	if (!studentId || !isValidStudentId(studentId)) {
		return badRequest("Invalid student ID format");
	}

	let body: Record<string, unknown>;
	try {
		body = await request.json();
	} catch {
		return badRequest("Invalid JSON body");
	}

	const { profile, errors } = validateProfile(body);
	if (errors.length > 0) {
		return badRequest(errors.join("; "));
	}
	if (Object.keys(profile).length === 0) {
		return badRequest("No valid profile fields provided");
	}

	const updated = await updateProfile(env.PROGRESS, studentId, profile);
	if (updated === null) {
		return notFound("Student not found");
	}

	return new Response(JSON.stringify({ profile: updated }), {
		headers: { "Content-Type": "application/json", ...corsHeaders },
	});
};
