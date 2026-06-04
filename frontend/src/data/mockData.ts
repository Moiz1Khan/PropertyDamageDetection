export type PropertyStatus = 'analyzing' | 'complete' | 'draft'
export type Strategy = 'flip' | 'rent' | 'hold' | 'wholesale'
export type UserRole = 'investor' | 'agent' | 'admin'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  avatar?: string
}

export interface DamageDetection {
  type: string
  severity: 'low' | 'medium' | 'high'
  score: number
  room: string
}

export interface CompProperty {
  id: string
  address: string
  salePrice: number
  distance: number
  sqft: number
  soldDate: string
}

export interface Property {
  id: string
  address: string
  city: string
  state: string
  type: string
  listPrice: number
  sqft: number
  beds: number
  baths: number
  status: PropertyStatus
  imageUrl: string
  rehabCost: number
  arv: number
  monthlyRent: number
  profit: number
  roi: number
  maxOffer: number
  strategy: Strategy
  rankScore: number
  damages: DamageDetection[]
  comps: CompProperty[]
  neighborhood: {
    medianPrice: number
    medianRent: number
    crimeIndex: number
    schoolRating: number
    appreciation: number
  }
  createdAt: string
}

export const currentUser: User = {
  id: 'u1',
  name: 'Alex Morgan',
  email: 'alex@investor.com',
  role: 'investor',
}

export const mockProperties: Property[] = [
  {
    id: 'p1',
    address: '1842 Oakwood Drive',
    city: 'Austin',
    state: 'TX',
    type: 'Single Family',
    listPrice: 285000,
    sqft: 1840,
    beds: 3,
    baths: 2,
    status: 'complete',
    imageUrl: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80',
    rehabCost: 42000,
    arv: 395000,
    monthlyRent: 2450,
    profit: 68000,
    roi: 23.8,
    maxOffer: 298000,
    strategy: 'flip',
    rankScore: 92,
    damages: [
      { type: 'Roof wear', severity: 'medium', score: 0.72, room: 'Exterior' },
      { type: 'Water stain', severity: 'low', score: 0.34, room: 'Kitchen' },
      { type: 'Cracked tile', severity: 'low', score: 0.28, room: 'Bathroom' },
    ],
    comps: [
      { id: 'c1', address: '1820 Oakwood Dr', salePrice: 388000, distance: 0.1, sqft: 1780, soldDate: '2025-11-12' },
      { id: 'c2', address: '1901 Maple Lane', salePrice: 402000, distance: 0.3, sqft: 1920, soldDate: '2025-10-28' },
      { id: 'c3', address: '1755 Cedar Ave', salePrice: 375000, distance: 0.5, sqft: 1810, soldDate: '2025-09-15' },
    ],
    neighborhood: { medianPrice: 372000, medianRent: 2380, crimeIndex: 22, schoolRating: 8.2, appreciation: 4.8 },
    createdAt: '2026-03-01',
  },
  {
    id: 'p2',
    address: '729 Riverside Blvd',
    city: 'Austin',
    state: 'TX',
    type: 'Duplex',
    listPrice: 410000,
    sqft: 2200,
    beds: 4,
    baths: 3,
    status: 'complete',
    imageUrl: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
    rehabCost: 55000,
    arv: 520000,
    monthlyRent: 3200,
    profit: 55000,
    roi: 18.2,
    maxOffer: 412000,
    strategy: 'rent',
    rankScore: 85,
    damages: [
      { type: 'HVAC aging', severity: 'medium', score: 0.65, room: 'Utility' },
      { type: 'Peeling paint', severity: 'low', score: 0.22, room: 'Living Room' },
    ],
    comps: [
      { id: 'c4', address: '701 Riverside Blvd', salePrice: 505000, distance: 0.2, sqft: 2150, soldDate: '2026-01-08' },
      { id: 'c5', address: '812 River Rd', salePrice: 498000, distance: 0.4, sqft: 2280, soldDate: '2025-12-20' },
    ],
    neighborhood: { medianPrice: 445000, medianRent: 3050, crimeIndex: 18, schoolRating: 7.8, appreciation: 5.2 },
    createdAt: '2026-02-18',
  },
  {
    id: 'p3',
    address: '3301 Highland Park',
    city: 'Dallas',
    state: 'TX',
    type: 'Single Family',
    listPrice: 195000,
    sqft: 1420,
    beds: 3,
    baths: 1,
    status: 'analyzing',
    imageUrl: 'https://images.unsplash.com/photo-1605276374101-dee2ffb0f962?w=800&q=80',
    rehabCost: 38000,
    arv: 268000,
    monthlyRent: 1850,
    profit: 35000,
    roi: 17.9,
    maxOffer: 188000,
    strategy: 'flip',
    rankScore: 78,
    damages: [
      { type: 'Foundation crack', severity: 'high', score: 0.88, room: 'Basement' },
      { type: 'Outdated wiring', severity: 'medium', score: 0.58, room: 'Whole house' },
    ],
    comps: [
      { id: 'c6', address: '3288 Highland Park', salePrice: 262000, distance: 0.1, sqft: 1380, soldDate: '2026-02-01' },
    ],
    neighborhood: { medianPrice: 248000, medianRent: 1720, crimeIndex: 35, schoolRating: 6.5, appreciation: 3.1 },
    createdAt: '2026-03-10',
  },
  {
    id: 'p4',
    address: '512 Commerce St',
    city: 'Houston',
    state: 'TX',
    type: 'Townhouse',
    listPrice: 320000,
    sqft: 1680,
    beds: 3,
    baths: 2.5,
    status: 'complete',
    imageUrl: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',
    rehabCost: 28000,
    arv: 378000,
    monthlyRent: 2100,
    profit: 30000,
    roi: 14.5,
    maxOffer: 315000,
    strategy: 'hold',
    rankScore: 71,
    damages: [
      { type: 'Minor drywall', severity: 'low', score: 0.18, room: 'Bedroom' },
    ],
    comps: [
      { id: 'c7', address: '498 Commerce St', salePrice: 365000, distance: 0.2, sqft: 1650, soldDate: '2025-11-30' },
    ],
    neighborhood: { medianPrice: 340000, medianRent: 2050, crimeIndex: 28, schoolRating: 7.2, appreciation: 3.9 },
    createdAt: '2026-01-25',
  },
]

export const dashboardStats = {
  totalProperties: 12,
  avgRoi: 19.4,
  totalProfit: 248000,
  activeAnalyses: 2,
}

export const formatCurrency = (n: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)

export const formatPercent = (n: number) => `${n.toFixed(1)}%`

export const strategyLabels: Record<Strategy, string> = {
  flip: 'Fix & Flip',
  rent: 'Buy & Hold (Rental)',
  hold: 'Long-term Hold',
  wholesale: 'Wholesale',
}

export const adminUsers = [
  { id: 'u1', name: 'Alex Morgan', email: 'alex@investor.com', role: 'Investor', status: 'Active', joined: '2025-08-12' },
  { id: 'u2', name: 'Sarah Chen', email: 'sarah@agent.com', role: 'Agent', status: 'Active', joined: '2025-09-03' },
  { id: 'u3', name: 'Mike Torres', email: 'mike@investor.com', role: 'Investor', status: 'Active', joined: '2025-10-21' },
  { id: 'u4', name: 'Admin User', email: 'admin@propiq.com', role: 'Admin', status: 'Active', joined: '2025-06-01' },
  { id: 'u5', name: 'James Wright', email: 'james@lender.com', role: 'Lender', status: 'Pending', joined: '2026-02-28' },
]
