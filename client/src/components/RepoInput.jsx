import { useState } from 'react'

export default function RepoInput({ onScan }) {
  const [repoUrl, setRepoUrl] = useState('')
  const [teamSize, setTeamSize] = useState(8)
  const [hourlyRate, setHourlyRate] = useState(75)

  return (
    <div className="max-w-xl">
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-1">GitHub Repository (e.g. facebook/react or full URL)</label>
        <input
          type="text"
          placeholder="facebook/react or https://github.com/facebook/react"
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          className="w-full bg-gray-900 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-red-400"
        />
      </div>
      <div className="flex gap-4 mb-6">
        <div className="flex-1">
          <label className="block text-sm text-gray-400 mb-1">Team size</label>
          <input type="number" value={teamSize} onChange={e => setTeamSize(+e.target.value)} min={1}
            className="w-full bg-gray-900 border border-gray-700 rounded px-4 py-2 text-white" />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-gray-400 mb-1">Avg hourly rate (USD)</label>
          <input type="number" value={hourlyRate} onChange={e => setHourlyRate(+e.target.value)} min={1}
            className="w-full bg-gray-900 border border-gray-700 rounded px-4 py-2 text-white" />
        </div>
      </div>
      <button
        onClick={() => onScan({ repoUrl, teamSize, hourlyRate })}
        disabled={!repoUrl}
        className="w-full bg-red-600 hover:bg-red-500 disabled:opacity-40 text-white font-bold py-3 rounded text-lg transition-colors"
      >
        Scan Repository
      </button>
    </div>
  )
}