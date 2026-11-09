import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input, Select, Textarea } from '../components/ui/Input'
import { Upload, ImagePlus, ArrowLeft, Info, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

const roomTags = ['Exterior', 'Kitchen', 'Bathroom', 'Bedroom', 'Living Room', 'Basement', 'Roof']

export function AddPropertyPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stages, setStages] = useState<string[]>([])
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

  const runAnalysis = async () => {
    setLoading(true)
    setError('')
    setStages(['Uploading property…', 'Queuing CV scan…'])
    try {
      const res = await api.createProperty({
        ...form,
        list_price: Number(form.list_price),
        sqft: Number(form.sqft),
        beds: Number(form.beds),
        baths: Number(form.baths),
        year_built: Number(form.year_built) || null,
        lot_size: Number(form.lot_size) || null,
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
            Upload photos for AI damage detection. For the demo, you can run analysis without files — the CV engine
            will simulate a professional scan from property attributes.
          </p>

          <div className="mt-4 flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            CV model detects: roof wear, water stains, cracks, peeling paint, HVAC aging, and foundation issues.
          </div>

          <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-black/10 bg-app-elevated px-6 py-16 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-black/[0.04]">
              <Upload className="h-6 w-6 text-app-subtle" />
            </div>
            <p className="mt-4 font-medium text-black">Drag and drop images here</p>
            <p className="mt-1 text-sm text-app-muted">PNG, JPG up to 10MB each · Max 20 images</p>
            <Button variant="secondary" size="sm" className="mt-6" type="button">
              <ImagePlus className="h-4 w-4" />
              Browse files
            </Button>
          </div>

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
