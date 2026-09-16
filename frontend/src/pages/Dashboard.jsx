import Header from '../components/Header'
import ComplaintForm from '../components/ComplaintForm'
import AICopilot from '../components/AICopilot'

export default function Dashboard() {
  return (
    <div className="flex min-h-dvh flex-col bg-slate-100 text-slate-900 lg:h-dvh lg:overflow-hidden">
      <Header />

      <main className="mx-auto flex min-h-0 w-full max-w-7xl flex-1 flex-col px-4 py-3 sm:px-6 lg:overflow-hidden">
        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[1.2fr_1fr] lg:overflow-hidden">
          {/* Left: independent scroll for long form */}
          <div className="min-h-[65vh] lg:min-h-0 lg:h-full lg:overflow-hidden">
            <ComplaintForm />
          </div>

          {/* Right: natural overflow — scrollbar only when needed */}
          <div className="min-h-[65vh] lg:min-h-0 lg:h-full lg:overflow-hidden">
            <AICopilot />
          </div>
        </div>
      </main>
    </div>
  )
}
