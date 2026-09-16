export default function ComplaintSection({ title, children }) {
  return (
    <section className="space-y-3">
      <div className="border-b border-slate-200 pb-2">
        <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">{children}</div>
    </section>
  )
}
