const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

const TOKEN_KEY = 'offmarketstream_token'

/** Uploaded photos are served by the API; in local dev the API is on another port, so make them absolute. */
const API_ORIGIN = /^https?:\/\//.test(API_BASE) ? new URL(API_BASE).origin : ''
export function assetUrl(url: string): string {
  if (!url) return url
  return url.startsWith('/api/') && API_ORIGIN ? `${API_ORIGIN}${url}` : url
}

function normalizeProperty(p: ApiProperty): ApiProperty {
  return {
    ...p,
    imageUrl: assetUrl(p.imageUrl),
    galleryImages: (p.galleryImages ?? []).map(assetUrl),
    photoAnalyses: (p.photoAnalyses ?? []).map((ph) => ({ ...ph, url: assetUrl(ph.url) })),
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

/** FastAPI validation errors come as a list; turn them into one readable sentence. */
function formatDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d: { loc?: (string | number)[]; msg?: string }) => {
        const field = String(d.loc?.[d.loc.length - 1] ?? '').replace(/_/g, ' ')
        return field ? `${field}: ${d.msg}` : d.msg
      })
      .join('; ')
  }
  return JSON.stringify(detail)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const data = await res.json()
      detail = data.detail || detail
    } catch {
      /* ignore */
    }
    throw new Error(formatDetail(detail))
  }
  if (res.status === 204) return undefined as T
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/pdf')) {
    return (await res.blob()) as T
  }
  return res.json() as Promise<T>
}

export type ApiUser = {
  id: string
  name: string
  email: string
  role: 'investor' | 'agent' | 'admin' | string
  status?: string
}

export type ApiProperty = {
  id: string
  address: string
  city: string
  state: string
  zip_code?: string
  type: string
  listPrice: number
  sqft: number
  beds: number
  baths: number
  status: 'analyzing' | 'complete' | 'draft' | string
  imageUrl: string
  galleryImages?: string[]
  rehabCost: number
  arv: number
  monthlyRent: number
  profit: number
  roi: number
  maxOffer: number
  strategy: 'flip' | 'rent' | 'hold' | 'wholesale' | string
  rankScore: number
  damages: ApiDamage[]
  comps: { id: string; address: string; salePrice: number; distance: number; sqft: number; soldDate: string }[]
  neighborhood: {
    medianPrice: number | null
    medianRent: number | null
    crimeIndex: number | null
    schoolRating: number | null
    appreciation: number | null
  }
  analysisLog?: string[]
  imageRooms?: string[]
  photoAnalyses?: ApiPhotoAnalysis[]
  rehabItems?: { label: string; category: string; severity: string; detail: string; cost: number }[]
  valuation?: {
    asIsValue?: number
    asIsSource?: string
    repairsValue?: number
    rentcastAvm?: number | null
    rentSource?: string
    neighborhoodSources?: Record<string, string>
    rehabNote?: string
  }
  warnings?: string[]
  createdAt: string
}

/** Box in 0-1 image coordinates: [x1, y1, x2, y2] */
export type Box = [number, number, number, number]

export type ApiDamage = {
  type: string
  severity: 'low' | 'medium' | 'high'
  score: number | null
  room: string
  category?: string
  source?: 'ai' | 'yolo' | 'ai+yolo' | 'legacy' | string
  imageIndex?: number | null
  areaSqft?: number | null
  description?: string
  box?: Box | null
  yoloBox?: Box | null
}

export type ApiPhotoAnalysis = {
  index: number
  url: string
  status: 'assessed' | 'not_property' | 'not_assessed' | 'missing' | string
  isPropertyPhoto: boolean
  scene: string
  room: string
  roomSource: 'user' | 'ai' | 'none' | string
  aiRoom: string | null
  aiRoomConfidence: number | null
  summary: string
  findings: ApiDamage[]
  yoloBoxes: { category: string; yoloClass: string; confidence: number; box: Box }[]
  rejectedDetections: { yoloClass: string; confidence: number; box: Box; reason: string }[]
  aiUsed: boolean
  aiCached: boolean
  aiNote: string
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  login: (email: string, password: string) =>
    request<{ access_token: string; user: ApiUser }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: { name: string; email: string; password: string; role?: string }) =>
    request<{ access_token: string; user: ApiUser }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  me: () => request<ApiUser>('/auth/me'),
  stats: () =>
    request<{ totalProperties: number; avgRoi: number; totalProfit: number; activeAnalyses: number }>(
      '/dashboard/stats',
    ),
  properties: () => request<ApiProperty[]>('/properties').then((ps) => ps.map(normalizeProperty)),
  property: (id: string) => request<ApiProperty>(`/properties/${id}`).then(normalizeProperty),
  deleteProperty: (id: string) =>
    request<void>(`/properties/${id}`, {
      method: 'DELETE',
    }),
  createProperty: (body: Record<string, unknown>) =>
    request<{ property: ApiProperty; stages: string[] }>('/properties', {
      method: 'POST',
      body: JSON.stringify(body),
    }).then((r) => ({ ...r, property: normalizeProperty(r.property) })),
  setPhotoRooms: (id: string, imageRooms: string[]) =>
    request<{ property: ApiProperty; stages: string[] }>(`/properties/${id}/photo-rooms`, {
      method: 'PUT',
      body: JSON.stringify({ image_rooms: imageRooms }),
    }).then((r) => ({ ...r, property: normalizeProperty(r.property) })),
  uploadPropertyImages: async (files: File[]) => {
    const fd = new FormData()
    files.forEach((f) => fd.append('files', f))
    const headers = new Headers()
    const token = getToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
    const res = await fetch(`${API_BASE}/uploads/property-images`, { method: 'POST', body: fd, headers })
    if (!res.ok) {
      let detail = `Upload failed (${res.status})`
      try {
        const data = await res.json()
        detail = data.detail || detail
      } catch {
        /* ignore */
      }
      throw new Error(formatDetail(detail))
    }
    return res.json() as Promise<{ batchId: string; images: { url: string; name: string }[] }>
  },
  analyze: (id: string) =>
    request<{ property: ApiProperty; stages: string[] }>(`/properties/${id}/analyze`, { method: 'POST' }).then(
      (r) => ({ ...r, property: normalizeProperty(r.property) }),
    ),
  rankings: () => request<ApiProperty[]>('/rankings').then((ps) => ps.map(normalizeProperty)),
  adminUsers: () => request<ApiUser[]>('/admin/users'),
  reportUrl: (id: string) => `${API_BASE}/properties/${id}/report.pdf`,
  downloadReport: async (id: string) => {
    const blob = await request<Blob>(`/properties/${id}/report.pdf`)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `OffmarketStream-report-${id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  },
}
