import { Badge } from '../ui/Badge'
import type { ApiDamage, ApiPhotoAnalysis, Box } from '../../lib/api'
import { ROOM_OPTIONS } from '../../lib/rooms'

const severityVariant = { low: 'success', medium: 'warning', high: 'danger' } as const
const severityColor = { low: '#10b981', medium: '#f59e0b', high: '#ef4444' }

function BoxOverlay({ box, n, color }: { box: Box; n: number; color: string }) {
  const [x1, y1, x2, y2] = box
  return (
    <div
      className="pointer-events-none absolute rounded-md border-2"
      style={{
        left: `${x1 * 100}%`,
        top: `${y1 * 100}%`,
        width: `${(x2 - x1) * 100}%`,
        height: `${(y2 - y1) * 100}%`,
        borderColor: color,
        boxShadow: '0 0 0 1px rgba(0,0,0,0.35)',
      }}
    >
      <span
        className="absolute -left-0.5 -top-5 rounded px-1.5 text-[11px] font-semibold leading-5 text-white"
        style={{ backgroundColor: color }}
      >
        {n}
      </span>
    </div>
  )
}

function roomHint(photo: ApiPhotoAnalysis): string {
  if (photo.roomSource === 'user') return 'Room set by you'
  if (photo.roomSource === 'ai')
    return `Room detected automatically (${Math.round((photo.aiRoomConfidence ?? 0) * 100)}% sure)`
  if (photo.aiUsed) return "Couldn't tell the room from this photo — pick one"
  return 'Pick the room for this photo'
}

function FindingRow({ d, n }: { d: ApiDamage; n: number }) {
  return (
    <div className="flex gap-3 rounded-xl border border-black/[0.06] bg-app-elevated px-3 py-2.5">
      <span
        className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded text-[11px] font-semibold text-white"
        style={{ backgroundColor: severityColor[d.severity] }}
      >
        {n}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-medium text-black">{d.type}</p>
          <Badge variant={severityVariant[d.severity]}>{d.severity}</Badge>
          {d.score != null && (
            <span className="text-xs text-app-muted">{Math.round(d.score * 100)}% confidence</span>
          )}
          {d.areaSqft ? <span className="text-xs text-app-muted">~{d.areaSqft} sqft</span> : null}
        </div>
        {d.description && <p className="mt-1 text-xs text-app-muted">{d.description}</p>}
      </div>
    </div>
  )
}

export function PhotoInspection({
  photo,
  roomValue,
  onRoomChange,
  disabled,
}: {
  photo: ApiPhotoAnalysis
  roomValue: string
  onRoomChange: (room: string) => void
  disabled?: boolean
}) {
  const findings = photo.findings ?? []
  return (
    <div className="grid gap-4 rounded-2xl border border-black/[0.06] p-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] sm:p-4">
      <div className="relative self-start overflow-hidden rounded-xl bg-black/[0.03]">
        <img src={photo.url} alt={`Photo ${photo.index + 1}`} className="block h-auto w-full" />
        {findings.map((d, i) => {
          const box = d.box ?? d.yoloBox
          return box ? <BoxOverlay key={i} box={box} n={i + 1} color={severityColor[d.severity]} /> : null
        })}
      </div>

      <div className="min-w-0 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium text-black">Photo {photo.index + 1}</p>
          {photo.status === 'not_property' && <Badge variant="danger">Not a property photo</Badge>}
          {photo.status === 'not_assessed' && <Badge variant="warning">Not assessed</Badge>}
          {photo.status === 'missing' && <Badge variant="danger">File missing</Badge>}
          {photo.status === 'assessed' && (
            <Badge variant={findings.length ? 'warning' : 'success'}>
              {findings.length ? `${findings.length} issue(s)` : 'No damage found'}
            </Badge>
          )}
        </div>

        <label className="block">
          <span className="text-xs text-app-muted">{roomHint(photo)}</span>
          <select
            className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm text-black disabled:opacity-60"
            value={roomValue}
            disabled={disabled}
            onChange={(e) => onRoomChange(e.target.value)}
          >
            <option value="">
              {photo.roomSource === 'ai' ? `Auto-detect (${photo.room})` : 'Auto-detect'}
            </option>
            {ROOM_OPTIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>

        {photo.summary && <p className="text-sm text-app-subtle">{photo.summary}</p>}

        <div className="space-y-2">
          {findings.map((d, i) => (
            <FindingRow key={i} d={d} n={i + 1} />
          ))}
        </div>

        {photo.rejectedDetections?.length > 0 && (
          <p className="text-xs text-app-muted">
            Filtered out {photo.rejectedDetections.length} false detection(s):{' '}
            {photo.rejectedDetections.map((r) => `"${r.yoloClass}" — ${r.reason}`).join('; ')}
          </p>
        )}
        {photo.aiNote && !photo.aiUsed && <p className="text-xs text-amber-700">{photo.aiNote}</p>}
      </div>
    </div>
  )
}
