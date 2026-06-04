import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input, Select } from '../components/ui/Input'
import { Settings, Database, Cpu, Globe, Shield } from 'lucide-react'

export function AdminSettingsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-black">System Settings</h1>
        <p className="mt-1 text-sm text-app-muted">
          Configure integrations, defaults, and platform behavior
        </p>
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        <Shield className="mt-0.5 h-4 w-4 shrink-0" />
        Admin-only configuration panel. Changes here would affect all users in production.
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black/[0.04]">
              <Database className="h-5 w-5 text-app-subtle" />
            </div>
            <div>
              <h2 className="font-medium text-black">Database</h2>
              <p className="text-sm text-app-muted">PostgreSQL connection</p>
            </div>
          </div>
          <div className="mt-6 space-y-4">
            <Input label="Host" defaultValue="localhost:5432" />
            <Input label="Database name" defaultValue="propiq_db" />
            <Input label="Connection pool size" type="number" defaultValue="10" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black/[0.04]">
              <Cpu className="h-5 w-5 text-app-subtle" />
            </div>
            <div>
              <h2 className="font-medium text-black">ML / CV Services</h2>
              <p className="text-sm text-app-muted">Inference endpoints</p>
            </div>
          </div>
          <div className="mt-6 space-y-4">
            <Input label="CV Service URL" defaultValue="http://localhost:8001/detect" />
            <Input label="ML Service URL" defaultValue="http://localhost:8002/predict" />
            <Select
              label="CV model version"
              options={[
                { value: 'v1', label: 'DamageNet v1.0' },
                { value: 'v2', label: 'DamageNet v2.0 (beta)' },
              ]}
            />
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black/[0.04]">
              <Globe className="h-5 w-5 text-app-subtle" />
            </div>
            <div>
              <h2 className="font-medium text-black">Market Data API</h2>
              <p className="text-sm text-app-muted">Comps and neighborhood feeds</p>
            </div>
          </div>
          <div className="mt-6 space-y-4">
            <Input label="API Key" type="password" defaultValue="••••••••••••" />
            <Input label="Comps search radius (miles)" type="number" defaultValue="0.5" />
            <Select
              label="Default market region"
              options={[
                { value: 'tx', label: 'Texas' },
                { value: 'ca', label: 'California' },
                { value: 'fl', label: 'Florida' },
              ]}
            />
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black/[0.04]">
              <Settings className="h-5 w-5 text-app-subtle" />
            </div>
            <div>
              <h2 className="font-medium text-black">Analysis Defaults</h2>
              <p className="text-sm text-app-muted">Deal calculation parameters</p>
            </div>
          </div>
          <div className="mt-6 space-y-4">
            <Input label="Default closing costs (%)" type="number" defaultValue="3" />
            <Input label="Default holding period (months)" type="number" defaultValue="6" />
            <Input label="Min ROI threshold (%)" type="number" defaultValue="15" />
            <Input label="Max rehab % of ARV" type="number" defaultValue="30" />
          </div>
        </Card>
      </div>

      <div className="flex justify-end gap-3">
        <Button variant="ghost">Reset to defaults</Button>
        <Button variant="primary">Save changes</Button>
      </div>
    </div>
  )
}
