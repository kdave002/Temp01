export default function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur ${className}`}>
      {title && (
        <div className="px-5 py-4 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  )
}
