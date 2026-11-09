import { useEffect, useState } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import { FileText, Download, Calendar, FileCheck } from 'lucide-react'
import { formatCurrency, formatPercent } from '../data/mockData'
import { api, type ApiProperty } from '../lib/api'

export function ReportsPage() {
  const [reports, setReports] = useState<ApiProperty[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  useEffect(() => {
    api
      .properties()
      .then((props) => setReports(props.filter((p) => p.status === 'complete')))
      .finally(() => setLoading(false))
  }, [])

  const download = async (id: string) => {
    setBusyId(id)
    try {
      await api.downloadReport(id)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-black">Reports</h1>
        <p className="mt-1 text-sm text-app-muted">
          PDF investment summary reports for completed analyses · {reports.length} available
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: 'Total reports', value: String(reports.length) },
          { label: 'This month', value: String(reports.length) },
          { label: 'Format', value: 'PDF' },
        ].map(({ label, value }) => (
          <Card key={label} padding="sm">
            <p className="text-xs text-app-muted">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-black">{value}</p>
          </Card>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-app-muted">Loading reports…</p>
      ) : (
        <div className="grid gap-4">
          {reports.map((p) => (
            <Card key={p.id} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-black/[0.04]">
                  <FileText className="h-5 w-5 text-app-subtle" />
                </div>
                <div>
                  <p className="font-medium text-black">Investment Summary — {p.address}</p>
                  <p className="mt-1 text-sm text-app-muted">
                    {p.city}, {p.state} · ROI {formatPercent(p.roi)} · Profit {formatCurrency(p.profit)}
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-app-muted">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      Generated {p.createdAt}
                    </span>
                    <span className="flex items-center gap-1">
                      <FileCheck className="h-3 w-3" />
                      1 page · PDF
                    </span>
                  </div>
                  <div className="mt-2">
                    <StatusBadge status="complete" />
                  </div>
                </div>
              </div>
              <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full sm:w-auto"
                  onClick={() => download(p.id)}
                  disabled={busyId === p.id}
                >
                  <Download className="h-4 w-4" />
                  {busyId === p.id ? 'Preparing…' : 'Download PDF'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
