import { useState } from 'react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import SchemaInput from '../components/SchemaInput'
import { analyze } from '../lib/api'

export default function Analyze() {
  const [prevSchema, setPrevSchema] = useState([])
  const [currSchema, setCurrSchema] = useState([])
  const [downstream, setDownstream] = useState(5)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await analyze({
        previous_schema: prevSchema,
        current_schema: currSchema,
        downstream_model_count: downstream,
      })
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
        <h1 className="text-2xl font-bold text-white">Analyze Drift</h1>
        <p className="mt-1 text-sm text-slate-400">
          Provide previous and current schemas to detect drift events, impact, and repair SQL.
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

        <button
          type="submit"
          disabled={loading || prevSchema.length === 0 || currSchema.length === 0}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 text-sm font-semibold text-white hover:bg-blue-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <Spinner />}
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Impact Score</p>
              <p className="mt-1 text-3xl font-bold text-white">{result.impact_score}</p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Risk Level</p>
              <p className="mt-1">
                <Badge variant={result.risk}>{result.risk.toUpperCase()}</Badge>
              </p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Recommendation</p>
              <p className="mt-1 text-sm text-slate-200 font-medium">
                {result.action_recommendation?.replace(/_/g, ' ')}
              </p>
            </Card>
          </div>

          {result.events?.length > 0 && (
            <Card title="Drift Events">
              <div className="divide-y divide-slate-800">
                {result.events.map((ev, i) => (
                  <div key={i} className="py-3 first:pt-0 last:pb-0 flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-200">{ev.kind.replace(/_/g, ' ')}</p>
                      <p className="text-sm text-slate-400 mt-0.5">{ev.detail}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant={ev.severity}>{ev.severity}</Badge>
                      {ev.confidence != null && (
                        <span className="text-xs text-slate-500">{Math.round(ev.confidence * 100)}%</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {result.patch_sql && (
            <Card title="Patch SQL">
              <pre className="text-sm text-cyan-300 font-mono whitespace-pre-wrap bg-slate-950 rounded-lg p-4 overflow-x-auto">
                {result.patch_sql}
              </pre>
            </Card>
          )}

          {result.pr_body && (
            <Card title="PR Body Preview">
              <pre className="text-sm text-slate-300 whitespace-pre-wrap">{result.pr_body}</pre>
            </Card>
          )}

          {result.recommendation_reasons?.length > 0 && (
            <Card title="Recommendation Reasons">
              <ul className="space-y-1.5">
                {result.recommendation_reasons.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-blue-400 shrink-0" />
                    {r}
                  </li>
                ))}
              </ul>
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
