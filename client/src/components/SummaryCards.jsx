function Card({ label, value, unit, severity }) {
  const colors = { ok: 'border-green-800', warn: 'border-yellow-700', critical: 'border-red-700' }
  const textColors = { ok: 'text-green-400', warn: 'text-yellow-400', critical: 'text-red-400' }
  return (
    <div className={`bg-gray-900 border ${colors[severity]} rounded-xl p-4`}>
      <p className="text-gray-400 text-xs uppercase tracking-widest mb-2">{label}</p>
      <p className={`text-3xl font-bold ${textColors[severity]}`}>{value}<span className="text-base font-normal text-gray-500 ml-1">{unit}</span></p>
    </div>
  )
}

export default function SummaryCards({ metrics, ciMetrics }) {
  const reviewSeverity = metrics.avgTimeToFirstReview < 4 ? 'ok' : metrics.avgTimeToFirstReview < 12 ? 'warn' : 'critical'
  const mergeSeverity = metrics.avgTimeToMerge < 24 ? 'ok' : metrics.avgTimeToMerge < 72 ? 'warn' : 'critical'
  const largePRSeverity = metrics.largePRs < 5 ? 'ok' : metrics.largePRs < 15 ? 'warn' : 'critical'

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
      <Card label="Avg Time to First Review" value={Math.round(metrics.avgTimeToFirstReview)} unit="hrs" severity={reviewSeverity} />
      <Card label="Avg Time to Merge" value={Math.round(metrics.avgTimeToMerge)} unit="hrs" severity={mergeSeverity} />
      <Card label="Large PRs (500+ lines)" value={metrics.largePRs} unit="PRs" severity={largePRSeverity} />
      {ciMetrics && <Card label="CI Failure Rate" value={Math.round(ciMetrics.failureRate)} unit="%" severity={ciMetrics.failureRate < 10 ? 'ok' : ciMetrics.failureRate < 25 ? 'warn' : 'critical'} />}
    </div>
  )
}