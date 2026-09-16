export default function ChatMessage({ role, content }) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[90%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${
          isUser
            ? 'bg-teal-700 text-white'
            : 'border border-slate-200 bg-slate-50 text-slate-700'
        }`}
      >
        {!isUser && (
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            Assistant
          </p>
        )}
        <p className="break-words whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}
