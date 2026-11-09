import { useCallback, useRef, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input, Select, Textarea } from '../components/ui/Input'
import { Upload, ImagePlus, ArrowLeft, Info, Loader2, X } from 'lucide-react'
import { api } from '../lib/api'

const roomTags = ['Exterior', 'Kitchen', 'Bathroom', 'Bedroom', 'Living Room', 'Basement', 'Roof']
const MAX_FILES = 20
const MAX_MB = 10

function validateFiles(incoming: FileList | File[]): File[] {
  const list = Array.from(incoming)
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  const out: File[] = []
  for (const f of list) {
    if (!allowed.includes(f.type)) continue
    if (f.size > MAX_MB * 1024 * 1024) continue
    out.push(f)
  }
  return out.slice(0, MAX_FILES)
}

export function AddPropertyPage() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stages, setStages] = useState<string[]>([])
  const [files, setFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])
  const [form, setForm] = useState({
    address: '1842 Oakwood Drive',
    city: 'Austin',
    state: 'TX',
    zip_code: '78704',
    property_type: 'Single Family',
    list_price: 285000,
    sqft: 1840,
    beds: 3,
    baths: 2,
    year_built: 1998,
    lot_size: 7200,
    notes: '',
  })

  const update = (key: string, value: string | number) => setForm((f) => ({ ...f, [key]: value }))

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const next = validateFiles(incoming)
    if (!next.length) {
      setError('Use PNG, JPG, or WebP under 10MB each.')
      return
    }
    setError('')
    setFiles((prev) => {
      const merged = [...prev, ...next].slice(0, MAX_FILES)
      setPreviews(merged.map((f) => URL.createObjectURL(f)))
      return merged
    })
  }, [])

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const merged = prev.filter((_, i) => i !== index)
      setPreviews(merged.map((f) => URL.createObjectURL(f)))
      return merged
    })
  }

  const runAnalysis = async () => {
    setLoading(true)
    setError('')
    setStages(['Saving property details…'])
    try {
      let galleryUrls: string[] = []
      if (files.length > 0) {
        setStages((s) => [...s, `Uploading ${files.length} image(s)…`])
        const uploaded = await api.uploadPropertyImages(files)
        galleryUrls = uploaded.images.map((i) => i.url)
      }
      setStages((s) => [...s, 'Queuing CV scan…'])
      const res = await api.createProperty({
        ...form,
        list_price: Number(form.list_price),
        sqft: Number(form.sqft),
        beds: Number(form.beds),
        baths: Number(form.baths),
        year_built: Number(form.year_built) || null,
        lot_size: Number(form.lot_size) || null,
        gallery_image_urls: galleryUrls.length ? galleryUrls : undefined,
        image_url: galleryUrls[0],
        run_analysis: true,
      })
      setStages(res.stages)
      setTimeout(() => navigate(`/dashboard/properties/${res.property.id}`), 800)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed')
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <Link
          to="/dashboard/properties"
          className="mb-4 inline-flex items-center gap-2 text-sm text-app-muted hover:text-black"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to properties
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight text-black">New Property Analysis</h1>
        <p className="mt-1 text-sm text-app-muted">
          Step {step} of 2 — {step === 1 ? 'Property details' : 'Upload images & run AI'}
        </p>
      </div>

      <div className="flex gap-2">
        {[1, 2].map((s) => (
          <div key={s} className={`h-1 flex-1 rounded-full ${s <= step ? 'bg-black' : 'bg-black/[0.06]'}`} />
        ))}
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {step === 1 ? (
        <Card>
          <h2 className="font-medium text-black">Property Information</h2>
          <p className="mt-1 text-sm text-app-muted">
            Enter listing details. These feed the ARV model, comps search radius, and deal calculator.
          </p>
          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Input
                label="Street Address"
                value={form.address}
                onChange={(e) => update('address', e.target.value)}
              />
            </div>
            <Input label="City" value={form.city} onChange={(e) => update('city', e.target.value)} />
            <Select
              label="State"
              value={form.state}
              onChange={(e) => update('state', e.target.value)}
              options={[
                { value: 'TX', label: 'Texas' },
                { value: 'CA', label: 'California' },
                { value: 'FL', label: 'Florida' },
              ]}
            />
            <Input label="ZIP Code" value={form.zip_code} onChange={(e) => update('zip_code', e.target.value)} />
            <Select
              label="Property Type"
              value={form.property_type}
              onChange={(e) => update('property_type', e.target.value)}
              options={[
                { value: 'Single Family', label: 'Single Family' },
                { value: 'Duplex', label: 'Duplex' },
                { value: 'Townhouse', label: 'Townhouse' },
                { value: 'Multi-family', label: 'Multi-family' },
              ]}
            />
            <Input
              label="List / Asking Price ($)"
              type="number"
              value={form.list_price}
              onChange={(e) => update('list_price', Number(e.target.value))}
            />
            <Input
              label="Square Footage"
              type="number"
              value={form.sqft}
              onChange={(e) => update('sqft', Number(e.target.value))}
            />
            <Input
              label="Bedrooms"
              type="number"
              value={form.beds}
              onChange={(e) => update('beds', Number(e.target.value))}
            />
            <Input
              label="Bathrooms"
              type="number"
              step="0.5"
              value={form.baths}
              onChange={(e) => update('baths', Number(e.target.value))}
            />
            <Input
              label="Year Built"
              type="number"
              value={form.year_built}
              onChange={(e) => update('year_built', Number(e.target.value))}
            />
            <Input
              label="Lot Size (sqft)"
              type="number"
              value={form.lot_size}
              onChange={(e) => update('lot_size', Number(e.target.value))}
            />
            <div className="sm:col-span-2">
              <Textarea
                label="Notes (optional)"
                value={form.notes}
                onChange={(e) => update('notes', e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button variant="primary" onClick={() => setStep(2)} className="w-full sm:w-auto">
              Continue to images
            </Button>
          </div>
        </Card>
      ) : (
        <Card>
          <h2 className="font-medium text-black">Property Images</h2>
          <p className="mt-2 text-sm text-app-muted">
            Upload photos for AI damage detection. You can also run analysis without images — CV will simulate from
            property attributes.
          </p>

          <div className="mt-4 flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            CV model detects: roof wear, water stains, cracks, peeling paint, HVAC aging, and foundation issues.
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            multiple
            className="hidden"
            onChange={(e) => {
              if (e.target.files?.length) addFiles(e.target.files)
              e.target.value = ''
            }}
          />

          <div
            className="mt-6 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-black/10 bg-app-elevated px-6 py-10 text-center"
            onDragOver={(e) => {
              e.preventDefault()
              e.stopPropagation()
            }}
            onDrop={(e) => {
              e.preventDefault()
              e.stopPropagation()
              if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files)
            }}
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-black/[0.04]">
              <Upload className="h-6 w-6 text-app-subtle" />
            </div>
            <p className="mt-4 font-medium text-black">Drag and drop images here</p>
            <p className="mt-1 text-sm text-app-muted">
              PNG, JPG up to 10MB each · Max {MAX_FILES} images · {files.length} selected
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="mt-6"
              type="button"
              onClick={() => fileInputRef.current?.click()}
            >
              <ImagePlus className="h-4 w-4" />
              Browse files
            </Button>
          </div>

          {previews.length > 0 && (
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {previews.map((src, i) => (
                <div key={src} className="relative aspect-[4/3] overflow-hidden rounded-xl border border-black/10">
                  <img src={src} alt="" className="h-full w-full object-cover" />
                  <button
                    type="button"
                    className="absolute right-1 top-1 rounded-full bg-black/60 p-1 text-white hover:bg-black"
                    onClick={() => removeFile(i)}
                    aria-label="Remove image"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6">
            <p className="text-sm font-medium text-app-subtle">Tag rooms (optional)</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {roomTags.map((tag) => (
                <span
                  key={tag}
                  className="cursor-pointer rounded-full border border-black/10 px-3 py-1 text-xs text-app-subtle hover:border-black/20 hover:text-black"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {stages.length > 0 && (
            <div className="mt-6 space-y-2 rounded-2xl bg-app-elevated p-4 text-sm">
              {stages.map((s) => (
                <p key={s} className="text-app-subtle">
                  ✓ {s}
                </p>
              ))}
            </div>
          )}

          <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
            <Button variant="ghost" onClick={() => setStep(1)} className="w-full sm:w-auto" disabled={loading}>
              Back
            </Button>
            <Button variant="primary" onClick={runAnalysis} className="w-full sm:w-auto" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Running analysis…
                </>
              ) : (
                'Run Analysis'
              )}
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
