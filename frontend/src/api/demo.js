// Local demo backend client (FAST-DEMO-004) — the ONLY place the UI talks to the
// backend (docs/coding-rules.md §2). No business logic lives in components.
//
// The body is the raw file: no multipart, no FormData, no HTTP client dependency
// (DEC-0009 §8 — `python-multipart` is deliberately absent from the backend image).
// Backend failures arrive as a fixed code; this module maps each one to a safe
// sentence. No path, checkpoint reference, status code or raw server text is ever
// surfaced to the user.

const MESSAGES = {
  unsupported_media_type: 'Upload MP3 or WAV.',
  payload_too_large: 'File is too large. Max 20 MB.',
  empty_body: 'The file was empty.',
  local_model_not_configured: 'Local model is not configured.',
  local_checkpoint_unavailable: 'Local checkpoint is unavailable.',
  local_dependency_missing: 'Local AI dependency is unavailable.',
  unsupported_or_corrupt_audio: 'The audio file could not be read.',
  separation_failed: 'Separation failed. Try another file.',
}

const FALLBACK = 'Something went wrong. Try again.'

/**
 * Separate one file into its stems.
 *
 * @param {File} file
 * @returns {Promise<Array<{stem: string, url: string}>>} backend-served stem URLs,
 *   used exactly as returned — the UI never builds a URL or a path.
 * @throws {Error} with a message that is already safe to render.
 */
export async function separate(file) {
  let response
  try {
    response = await fetch('/demo/separate', {
      method: 'POST',
      body: file,
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
    })
  } catch {
    throw new Error(FALLBACK)
  }

  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(MESSAGES[body?.error] ?? FALLBACK)
  }
  if (!Array.isArray(body?.stems) || body.stems.length === 0) {
    throw new Error(FALLBACK)
  }
  return body.stems
}
