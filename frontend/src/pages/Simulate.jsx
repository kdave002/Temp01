import { useState } from 'react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import SchemaInput from '../components/SchemaInput'
import { simulate } from '../lib/api'

const BREAKAGE_COLOR = {
  non_breaking: 'low',
  potentially_breaking: 'medium',
  likely_breaking: 'high',
}

export default function Simulate() {
  const [prevSchema, setPrevSchema] = useState([])
  const [currSchema, setCurrSchema] = useState([])
  const [downstream, setDownstream] = useState(5)
  const [useBaselines, setUseBaselines] = useState(false)
  const [baselines, setBaselines] = useState({
    incidents_per_month: 10,
    mean_time_to_detect_hours: 2,
    mean_time_to_resolve_hours: 4,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const payload = {
        previous_schema: prevSchema,
        current_schema: currSchema,
        downstream_model_count: downstream,
      }
      if (useBaselines) {
        payload.metric_baselines = baselines
      }
      const data = await simulate(payload)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-white">Simulate Impact</h1>
        <p className="mt-1 text-sm text-slate-400">
          Predict breakage class and repair path before deploying schema changes.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SchemaInput label="Previous Schema" value="" onChange={setPrevSchema} />
          <SchemaInput label="Current Schema" value="" onChange={setCurrSchema} />
        </div>

        <div className="max-w-xs">
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Downstream Model Count
          </label>
          <input
            type="number"
            min={0}
            max={10000}
            value={downstream}
            onChange={(e) => setDownstream(Number(e.target.value))}
            className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={useBaselines}
              onChange={(e) => setUseBaselines(e.target.checked)}
              className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500/50"
            />
            Include metric baselines
          </label>

          {useBaselines && (
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Incidents / month</label>
                <input
                  type="number"
                  min={0}
                  value={baselines.incidents_per_month}
                  onChange={(e) =>
                    setBaselines({ ...baselines, incidents_per_month: Number(e.target.value) })
                  }
                  className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">MTTD (hours)</label>
                <input
                  type="number"
                  min={0}
                  step={0.5}
                  value={baselines.mean_time_to_detect_hours}
                  onChange={(e) =>
                    setBaselines({ ...baselines, mean_time_to_detect_hours: Number(e.target.value) })
                  }
                  className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">MTTR (hours)</label>
                <input
                  type="number"
                  min={0}
                  step={0.5}
                  value={baselines.mean_time_to_resolve_hours}
                  onChange={(e) =>
                    setBaselines({ ...baselines, mean_time_to_resolve_hours: Number(e.target.value) })
                  }
                  className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
              </div>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || prevSchema.length === 0 || currSchema.length === 0}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-600 text-sm font-semibold text-white hover:bg-cyan-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <Spinner />}
          {loading ? 'Simulating...' : 'Simulate'}
        </button>
      </form>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Breakage Class</p>
              <p className="mt-2">
                <Badge variant={BREAKAGE_COLOR[result.predicted_breakage_class] || 'info'}>
                  {result.predicted_breakage_class?.replace(/_/g, ' ')}
                </Badge>
              </p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Repair Path</p>
              <p className="mt-1 text-sm text-slate-200 font-medium">{result.expected_repair_path}</p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Confidence</p>
              <p className="mt-1 text-2xl font-bold text-white">
                {Math.round(result.confidence_score * 100)}%
              </p>
              <Badge variant={
                result.confidence_band === 'high' ? 'low' :
                result.confidence_band === 'low' ? 'high' : 'medium'
              }>
                {result.confidence_band}
              </Badge>
            </Card>
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Range</p>
              <p className="mt-1 text-sm text-slate-200">
                {Math.round(result.confidence_range?.min * 100)}% – {Math.round(result.confidence_range?.max * 100)}%
              </p>
            </Card>
          </div>

          {result.summary && (
            <Card title="Summary">
              <p className="text-sm text-slate-300 leading-relaxed">{result.summary}</p>
            </Card>
          )}
        </div>
      )}
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
