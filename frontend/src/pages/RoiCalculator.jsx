import { useState } from 'react'
import Card from '../components/Card'
import { roiEstimate } from '../lib/api'

export default function RoiCalculator() {
  const [form, setForm] = useState({
    incidents_per_month: 12,
    mean_time_to_detect_hours: 2,
    mean_time_to_resolve_hours: 4,
    engineers_involved_per_incident: 2,
    hourly_engineering_cost_usd: 150,
    driftshield_adoption_rate: 0.8,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await roiEstimate(form)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fmt = (n) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(n)
  const usd = (n) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-white">ROI Calculator</h1>
        <p className="mt-1 text-sm text-slate-400">
          Estimate time and cost savings from DriftShield automation.
        </p>
      </header>

      <form onSubmit={handleSubmit}>
        <Card title="Your Current Metrics">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-5">
            <Field
              label="Incidents per month"
              value={form.incidents_per_month}
              onChange={(v) => update('incidents_per_month', v)}
              min={0}
              max={100000}
            />
            <Field
              label="Mean time to detect (hours)"
              value={form.mean_time_to_detect_hours}
              onChange={(v) => update('mean_time_to_detect_hours', v)}
              min={0}
              max={744}
              step={0.5}
            />
            <Field
              label="Mean time to resolve (hours)"
              value={form.mean_time_to_resolve_hours}
              onChange={(v) => update('mean_time_to_resolve_hours', v)}
              min={0}
              max={744}
              step={0.5}
            />
            <Field
              label="Engineers per incident"
              value={form.engineers_involved_per_incident}
              onChange={(v) => update('engineers_involved_per_incident', v)}
              min={0.1}
              max={500}
              step={0.5}
            />
            <Field
              label="Hourly cost (USD)"
              value={form.hourly_engineering_cost_usd}
              onChange={(v) => update('hourly_engineering_cost_usd', v)}
              min={1}
              max={10000}
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Adoption rate: {Math.round(form.driftshield_adoption_rate * 100)}%
              </label>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={form.driftshield_adoption_rate}
                onChange={(e) => update('driftshield_adoption_rate', Number(e.target.value))}
                className="w-full accent-blue-500"
              />
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 text-sm font-semibold text-white hover:bg-emerald-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading && <Spinner />}
              {loading ? 'Calculating...' : 'Calculate ROI'}
            </button>
          </div>
        </Card>
      </form>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <HighlightCard label="Annual Cost Saved" value={usd(result.annual_cost_saved_usd)} color="text-emerald-400" />
            <HighlightCard label="Annual Hours Saved" value={fmt(result.annual_engineering_hours_saved)} color="text-blue-400" />
            <HighlightCard label="Monthly Incidents Prevented" value={fmt(result.monthly_incidents_prevented)} color="text-cyan-400" />
            <HighlightCard label="Cost Reduction" value={`${result.monthly_cost_savings_percent.toFixed(1)}%`} color="text-amber-400" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card title="Before DriftShield">
              <dl className="space-y-3">
                <Row label="Monthly hours" value={`${fmt(result.baseline_monthly_engineering_hours)} hrs`} />
                <Row label="Monthly cost" value={usd(result.baseline_monthly_cost_usd)} />
              </dl>
            </Card>
            <Card title="With DriftShield">
              <dl className="space-y-3">
                <Row label="Monthly hours" value={`${fmt(result.projected_monthly_engineering_hours)} hrs`} />
                <Row label="Monthly cost" value={usd(result.projected_monthly_cost_usd)} />
                <Row label="Monthly savings" value={usd(result.monthly_cost_saved_usd)} highlight />
              </dl>
            </Card>
          </div>

          <Card title="Assumptions">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {Object.entries(result.assumptions).map(([key, val]) => (
                <div key={key}>
                  <p className="text-xs text-slate-500">{key.replace(/_/g, ' ')}</p>
                  <p className="text-sm font-medium text-slate-300">{typeof val === 'number' && val <= 1 ? `${(val * 100).toFixed(0)}%` : val}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

function Field({ label, value, onChange, min, max, step = 1 }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500"
      />
    </div>
  )
}

function HighlightCard({ label, value, color }) {
  return (
    <Card>
      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${color}`}>{value}</p>
    </Card>
  )
}

function Row({ label, value, highlight }) {
  return (
    <div className="flex justify-between">
      <dt className="text-sm text-slate-400">{label}</dt>
      <dd className={`text-sm font-medium ${highlight ? 'text-emerald-400' : 'text-slate-200'}`}>{value}</dd>
    </div>
  )
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}
