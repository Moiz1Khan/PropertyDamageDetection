const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

const TOKEN_KEY = 'offmarketstream_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
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
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
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
  damages: { type: string; severity: 'low' | 'medium' | 'high'; score: number; room: string }[]
  comps: { id: string; address: string; salePrice: number; distance: number; sqft: number; soldDate: string }[]
  neighborhood: {
    medianPrice: number
    medianRent: number
    crimeIndex: number
    schoolRating: number
    appreciation: number
  }
  analysisLog?: string[]
  createdAt: string
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
  properties: () => request<ApiProperty[]>('/properties'),
  property: (id: string) => request<ApiProperty>(`/properties/${id}`),
  createProperty: (body: Record<string, unknown>) =>
    request<{ property: ApiProperty; stages: string[] }>('/properties', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
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
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    }
    return res.json() as Promise<{ batchId: string; images: { url: string; name: string }[] }>
  },
  analyze: (id: string) =>
    request<{ property: ApiProperty; stages: string[] }>(`/properties/${id}/analyze`, { method: 'POST' }),
  rankings: () => request<ApiProperty[]>('/rankings'),
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
