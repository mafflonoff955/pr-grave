import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function ReviewerHeatmap({ reviewerLoad }) {
  const data = Object.entries(reviewerLoad)
    .map(([name, stats]) => ({ name, ...stats }))
    .sort((a, b) => b.reviewed - a.reviewed)
    .slice(0, 15)

  const max = Math.max(...data.map(d => d.reviewed))

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mt-6">
      <h3 className="text-xl font-bold mb-1">Reviewer Load</h3>
      <p className="text-gray-400 text-sm mb-4">Are reviews bottlenecked on a few people?</p>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} layout="vertical">
          <XAxis type="number" stroke="#555" />
          <YAxis type="category" dataKey="name" width={100} stroke="#555" tick={{ fill: '#ccc', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: '#1a1a1a', border: '1px solid #444' }}
            formatter={(val) => [`${val} reviews`, 'Reviews done']}
          />
          <Bar dataKey="reviewed" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.reviewed === max ? '#ef4444' : '#6366f1'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {data[0]?.reviewed > (data[1]?.reviewed || 0) * 2 && (
        <p className="text-red-400 text-sm mt-3">
          <strong>{data[0].name}</strong> is doing {Math.round(data[0].reviewed / data.reduce((a, b) => a + b.reviewed, 0) * 100)}% of all reviews. Single point of failure.
        </p>
      )}
    </div>
  )
}