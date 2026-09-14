// Local MVP auth backend client (P3-004) — the ONLY place the UI talks to the
// auth routes (docs/coding-rules.md §2). No business logic lives in components.
//
// The session lives entirely in the backend's httpOnly cookie: nothing here reads,
// stores or forwards a token, and nothing auth-related is written to localStorage
// or sessionStorage. The browser attaches the cookie itself, which is why every
// call sets `credentials: 'same-origin'` and nothing else.
//
// Backend failures arrive as a fixed code; this module maps each one to a safe
// sentence — the same pattern ./demo.js uses. An unknown email and a wrong
// password share one code, so they stay indistinguishable in the UI too.

const MESSAGES = {
  invalid_email: 'Enter a valid email address.',
  invalid_password: 'Use a password of 8–128 characters.',
  email_taken: 'That email is already registered. Sign in instead.',
  invalid_credentials: 'Those sign-in details did not match. Try again.',
  not_authenticated: 'Sign in to continue.',
  account_not_active: 'This account is not available.',
}

const FALLBACK = 'Something went wrong. Try again.'

/** Mirrors the backend's own rule so an obviously short password is caught before
 *  a round trip. The backend still enforces it — this is a courtesy check. */
export const MIN_PASSWORD_LENGTH = 8

async function post(path, body) {
  const init = { method: 'POST', credentials: 'same-origin' }
  if (body !== undefined) {
    init.headers = { 'Content-Type': 'application/json' }
    init.body = JSON.stringify(body)
  }

  let response
  try {
    response = await fetch(path, init)
  } catch {
    throw new Error(FALLBACK)
  }

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    // Only the fixed code is read. Server text, status codes and any other
    // detail never reach the user.
    throw new Error(MESSAGES[payload?.detail?.error] ?? FALLBACK)
  }
  return payload
}

/**
 * Read the signed-in account, once, on load.
 *
 * @returns {Promise<object|null>} the safe user object, or null when signed out.
 *   A 401 is not an error here — it is simply the signed-out state.
 */
export async function currentUser() {
  try {
    const response = await fetch('/auth/me', { credentials: 'same-origin' })
    return response.ok ? await response.json() : null
  } catch {
    return null
  }
}

/**
 * Create an account and sign in.
 *
 * @throws {Error} with a message that is already safe to render.
 */
export function signUp(email, password) {
  return post('/auth/signup', { email, password })
}

/**
 * Sign in to an existing account.
 *
 * @throws {Error} with a message that is already safe to render.
 */
export function signIn(email, password) {
  return post('/auth/login', { email, password })
}

/** Sign in or sign up with a Google ID token. */
export function googleLogin(credential) {
  return post('/auth/google', { credential })
}

/** Sign out. Safe to call when already signed out. */
export function signOut() {
  return post('/auth/logout')
}
