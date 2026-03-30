import SummaryCards from './SummaryCards'
import ReviewerHeatmap from './ReviewerHeatmap'
import CIBottlenecks from './CIBottlenecks'
import WhatIfSimulator from './WhatIfSimulator'

export default function Dashboard({ data, onReset }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">{data.repo}</h2>
          <p className="text-gray-400 text-sm">{data.prsAnalyzed} PRs analyzed · {data.prsLastMonth} merged last month</p>
        </div>
        <button onClick={onReset} className="text-sm text-gray-500 hover:text-white">New Scan</button>
      </div>

      {/* The big number — most important, shown first */}
      <div className="bg-red-950 border border-red-800 rounded-xl p-6 mb-6 text-center">
        <p className="text-gray-400 text-sm uppercase tracking-widest mb-2">Estimated Cost of DX Friction / Month</p>
        <p className="text-6xl font-black text-red-400">
          ${data.costAnalysis.totalWastedDollarsPerMonth.toLocaleString()}
        </p>
        <p className="text-gray-500 mt-2">{data.costAnalysis.totalWastedHoursPerMonth} developer-hours lost</p>
      </div>

      <SummaryCards metrics={data.prMetrics} ciMetrics={data.ciMetrics} />
      <ReviewerHeatmap reviewerLoad={data.prMetrics.reviewerLoad} />
      {data.ciMetrics && <CIBottlenecks ciMetrics={data.ciMetrics} />}
      <WhatIfSimulator
        currentData={data}
        prsPerMonth={data.prsLastMonth}
        hourlyRate={75}
      />
    </div>
  )
}