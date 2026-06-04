import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input, Select, Textarea } from '../components/ui/Input'
import { Upload, ImagePlus, ArrowLeft, Info } from 'lucide-react'

const roomTags = ['Exterior', 'Kitchen', 'Bathroom', 'Bedroom', 'Living Room', 'Basement', 'Roof']

export function AddPropertyPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)

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
          Step {step} of 2 — {step === 1 ? 'Property details' : 'Upload images'}
        </p>
      </div>

      <div className="flex gap-2">
        {[1, 2].map((s) => (
          <div
            key={s}
            className={`h-1 flex-1 rounded-full ${s <= step ? 'bg-white' : 'bg-black/[0.06]'}`}
          />
        ))}
      </div>

      {step === 1 ? (
        <Card>
          <h2 className="font-medium text-black">Property Information</h2>
          <p className="mt-1 text-sm text-app-muted">
            Enter listing details. These feed the ARV model, comps search radius, and deal calculator.
          </p>
          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Input label="Street Address" placeholder="1842 Oakwood Drive" defaultValue="1842 Oakwood Drive" />
            </div>
            <Input label="City" placeholder="Austin" defaultValue="Austin" />
            <Select
              label="State"
              options={[
                { value: 'TX', label: 'Texas' },
                { value: 'CA', label: 'California' },
                { value: 'FL', label: 'Florida' },
              ]}
            />
            <Input label="ZIP Code" placeholder="78704" defaultValue="78704" />
            <Select
              label="Property Type"
              options={[
                { value: 'sfh', label: 'Single Family' },
                { value: 'duplex', label: 'Duplex' },
                { value: 'townhouse', label: 'Townhouse' },
                { value: 'multi', label: 'Multi-family' },
              ]}
            />
            <Input label="List / Asking Price ($)" type="number" placeholder="285000" defaultValue="285000" />
            <Input label="Square Footage" type="number" placeholder="1840" defaultValue="1840" />
            <Input label="Bedrooms" type="number" placeholder="3" defaultValue="3" />
            <Input label="Bathrooms" type="number" placeholder="2" defaultValue="2" />
            <Input label="Year Built" type="number" placeholder="1998" defaultValue="1998" />
            <Input label="Lot Size (sqft)" type="number" placeholder="7200" defaultValue="7200" />
            <div className="sm:col-span-2">
              <Textarea
                label="Notes (optional)"
                placeholder="Seller motivated, needs roof work, vacant property..."
                rows={3}
              />
            </div>
          </div>
          <div className="mt-8 flex justify-end">
            <Button variant="primary" onClick={() => setStep(2)}>
              Continue to images
            </Button>
          </div>
        </Card>
      ) : (
        <Card>
          <h2 className="font-medium text-black">Property Images</h2>
          <p className="mt-2 text-sm text-app-muted">
            Upload photos for AI damage detection. Minimum 5 images recommended — include exterior, kitchen,
            bathrooms, and any areas of concern.
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
            <Button variant="secondary" size="sm" className="mt-6">
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

          <div className="mt-8 flex justify-between">
            <Button variant="ghost" onClick={() => setStep(1)}>
              Back
            </Button>
            <Button variant="primary" onClick={() => navigate('/dashboard/properties/p1')}>
              Run Analysis
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
