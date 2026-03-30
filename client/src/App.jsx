import { useState } from 'react'
import RepoInput from './components/RepoInput'
import ScanProgress from './components/ScanProgress'
import Dashboard from './components/Dashboard'

export default function App() {
  const [status, setStatus] = useState('idle') // idle | scanning | done | error
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  async function handleScan({ repoUrl, teamSize, hourlyRate }) {
    setStatus('scanning')
    setError(null)
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoUrl, teamSize, hourlyRate })
      })
      const body = await res.json()
      if (!res.ok) throw new Error(body.detail || body.error || 'Unknown error')
      const json = await res.json()
      setData(json)
      setStatus('done')
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-red-400">PR Graveyard</h1>
        <p className="text-gray-400 mt-1">X-Ray your GitHub repository. See what's killing your team's velocity.</p>
      </header>

      {status === 'idle' && <RepoInput onScan={handleScan} />}
      {status === 'scanning' && <ScanProgress />}
      {status === 'error' && (
        <div>
          <p className="text-red-400">Error: {error}</p>
          <button onClick={() => setStatus('idle')} className="mt-4 px-4 py-2 bg-gray-800 rounded hover:bg-gray-700">Try Again</button>
        </div>
      )}
      {status === 'done' && data && (
        <Dashboard data={data} onReset={() => setStatus('idle')} />
      )}
    </div>
  )
}