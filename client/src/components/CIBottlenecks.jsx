import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function CIBottlenecks({ ciMetrics }) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mt-6">
      <h3 className="text-xl font-bold mb-1">CI/CD Bottlenecks</h3>
      <p className="text-gray-400 text-sm mb-4">Average build duration per workflow</p>

      <div className="flex gap-6 mb-6">
        <div className="text-center">
          <p className="text-3xl font-bold text-orange-400">{Math.round(ciMetrics.avgDurationMinutes)} min</p>
          <p className="text-gray-500 text-xs">avg build time</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold text-red-400">{Math.round(ciMetrics.failureRate)}%</p>
          <p className="text-gray-500 text-xs">failure rate</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold text-gray-300">{ciMetrics.totalRuns}</p>
          <p className="text-gray-500 text-xs">runs analyzed</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={ciMetrics.workflows.slice(0, 8)}>
          <XAxis dataKey="name" stroke="#555" tick={{ fill: '#999', fontSize: 11 }} />
          <YAxis stroke="#555" tick={{ fill: '#999' }} />
          <Tooltip
            contentStyle={{ background: '#1a1a1a', border: '1px solid #444' }}
            formatter={(val) => [`${Math.round(val)} min`, 'Avg duration']}
          />
          <Bar dataKey="avgDurationMinutes" fill="#f97316" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}