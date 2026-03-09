import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Card from '../components/Card'
import Badge from '../components/Badge'
import { healthCheck, pilotReadiness } from '../lib/api'

export default function Dashboard() {
  const [health, setHealth] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    healthCheck()
      .then(setHealth)
      .catch((e) => setError(e.message))

    pilotReadiness({
      data_owner_identified: true,
      repo_access_configured: true,
      ci_green: true,
      rollback_plan_defined: false,
      oncall_contact_set: false,
    })
      .then(setReadiness)
      .catch(() => {})
  }, [])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">
          Monitor schema drift and system health at a glance.
        </p>
      </header>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          Backend unreachable: {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Service Status"
          value={health ? 'Online' : error ? 'Offline' : '...'}
          color={health ? 'text-emerald-400' : error ? 'text-red-400' : 'text-slate-400'}
        />
        <StatCard
          label="Repo Configured"
          value={health?.repo_configured ? 'Yes' : 'No'}
          color={health?.repo_configured ? 'text-emerald-400' : 'text-amber-400'}
        />
        <StatCard
          label="Pilot Readiness"
          value={readiness ? `${readiness.readiness_score}%` : '—'}
          color={
            readiness?.status === 'ready'
              ? 'text-emerald-400'
              : readiness?.status === 'ready_with_risks'
              ? 'text-amber-400'
              : 'text-slate-400'
          }
        />
        <StatCard
          label="Readiness Status"
          value={readiness ? readiness.status.replace(/_/g, ' ') : '—'}
          color="text-slate-300"
        />
      </div>

      {readiness?.missing_items?.length > 0 && (
        <Card title="Missing Readiness Items">
          <ul className="space-y-2">
            {readiness.missing_items.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-amber-400 shrink-0" />
                {item}
              </li>
            ))}
          </ul>
          {readiness.recommendation && (
            <p className="mt-4 text-sm text-slate-400 italic">{readiness.recommendation}</p>
          )}
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickAction
          to="/analyze"
          title="Analyze Drift"
          description="Detect schema changes and generate repair patches."
          color="from-blue-600 to-blue-500"
        />
        <QuickAction
          to="/simulate"
          title="Simulate Impact"
          description="Predict breakage class before deploying changes."
          color="from-cyan-600 to-cyan-500"
        />
        <QuickAction
          to="/roi"
          title="Calculate ROI"
          description="Estimate time and cost savings from automation."
          color="from-emerald-600 to-emerald-500"
        />
      </div>
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <Card>
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${color}`}>{value}</p>
    </Card>
  )
}

function QuickAction({ to, title, description, color }) {
  return (
    <Link
      to={to}
      className="group block rounded-xl border border-slate-800 bg-slate-900/60 p-5 transition hover:border-slate-700"
    >
      <div className={`inline-flex rounded-lg bg-gradient-to-r ${color} px-3 py-1.5 text-xs font-semibold text-white mb-3`}>
        {title}
      </div>
      <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">
        {description}
      </p>
    </Link>
  )
}
