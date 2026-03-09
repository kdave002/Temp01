import { useState } from 'react'

const PLACEHOLDER = `user_id,INT64
email,STRING
created_at,TIMESTAMP`;

export default function SchemaInput({ label, value, onChange }) {
  const [raw, setRaw] = useState(value || '')

  function handleChange(text) {
    setRaw(text)
    const columns = text
      .split('\n')
      .map(line => line.trim())
      .filter(Boolean)
      .map(line => {
        const [name, ...rest] = line.split(',')
        return { name: name?.trim(), type: rest.join(',').trim() }
      })
      .filter(c => c.name && c.type)
    onChange(columns)
  }

  return (
    <div>
      <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
      <textarea
        rows={6}
        className="w-full rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200 px-3 py-2 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 placeholder-slate-500"
        placeholder={PLACEHOLDER}
        value={raw}
        onChange={(e) => handleChange(e.target.value)}
      />
      <p className="mt-1 text-xs text-slate-500">One column per line: name,TYPE</p>
    </div>
  )
}
