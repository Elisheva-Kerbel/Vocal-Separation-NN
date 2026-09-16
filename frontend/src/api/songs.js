const FALLBACK = 'Something went wrong. Try again.'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(path, { credentials: 'same-origin', ...options })
  } catch {
    throw new Error(FALLBACK)
  }
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(payload?.detail?.message ?? FALLBACK)
  }
  return payload
}

export async function uploadSong(file, onProgress, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  if (options.modelChoice) formData.append('model_choice', options.modelChoice)
  if (options.visibility) formData.append('visibility', options.visibility)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/upload')
    xhr.withCredentials = true

    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100))
      })
    }

    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText)
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(data)
        } else {
          reject(new Error(data?.detail?.message ?? FALLBACK))
        }
      } catch {
        reject(new Error(FALLBACK))
      }
    }
    xhr.onerror = () => reject(new Error(FALLBACK))
    xhr.send(formData)
  })
}

export function getSong(songId) {
  return request(`/songs/${songId}`)
}

export function getSongStatus(songId) {
  return request(`/songs/${songId}/status`)
}

export function getListenUrl(songId, purpose) {
  return request(`/songs/${songId}/listen-url/${purpose}`)
}

export function getDownloadUrl(songId, purpose) {
  return request(`/songs/${songId}/download-url/${purpose}`)
}

export function renameSong(songId, title) {
  return request(`/songs/${songId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
}

export function getLibrary(params = {}) {
  const q = new URLSearchParams()
  if (params.status) q.set('status', params.status)
  if (params.offset) q.set('offset', params.offset)
  if (params.limit) q.set('limit', params.limit)
  return request(`/library?${q}`)
}

export function deleteSong(songId) {
  return request(`/library/${songId}`, { method: 'DELETE' })
}

export function publishSong(songId) {
  return request(`/public/songs/${songId}/publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rights_confirmed: true }),
  })
}

export function unpublishSong(songId) {
  return request(`/public/songs/${songId}/unpublish`, { method: 'POST' })
}

export function getPublicListenUrl(songId, purpose) {
  return request(`/public/songs/${songId}/listen-url/${purpose}`)
}

export function getPublicLibrary(params = {}) {
  const q = new URLSearchParams()
  if (params.offset) q.set('offset', params.offset)
  if (params.limit) q.set('limit', params.limit)
  return request(`/public/songs?${q}`)
}

export function rateSong(songId, score) {
  return request(`/public/songs/${songId}/rate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ score }),
  })
}

export function reportSong(songId, reason) {
  return request(`/public/songs/${songId}/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  })
}

export function redeemCoupon(code) {
  return request('/coupons/redeem', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  })
}

export function getPlans() {
  return request('/subscriptions/plans')
}

export function subscribe(plan, couponCode) {
  const body = { plan }
  if (couponCode) body.coupon_code = couponCode
  return request('/subscriptions/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function getSettings() {
  return request('/settings')
}

export function updateSettings(data) {
  return request('/settings', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function toggleTier() {
  return request('/settings/toggle-tier', { method: 'POST' })
}

export function deleteAccount() {
  return request('/settings/delete-account', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirm: true }),
  })
}

export function changePassword(currentPassword, newPassword) {
  return request('/settings/change-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  })
}

export function getQuota() {
  return request('/quota')
}

export function getAdminStats() {
  return request('/admin/stats')
}

export function getAdminUsers(offset = 0, limit = 50) {
  return request(`/admin/users?offset=${offset}&limit=${limit}`)
}

export function getAdminSongs(offset = 0, limit = 50) {
  return request(`/admin/all-songs?offset=${offset}&limit=${limit}`)
}

export function blockUser(userId) {
  return request(`/admin/users/${userId}/block`, { method: 'POST' })
}

export function unblockUser(userId) {
  return request(`/admin/users/${userId}/unblock`, { method: 'POST' })
}
