import { useState } from 'react'

function simulateLocally({ currentReviewHours, targetReviewHours, currentCIMinutes, targetCIMinutes, prsPerMonth, hourlyRate }) {
  const contextSwitchCost = (23 / 60)
  const currentCost = prsPerMonth * (
    contextSwitchCost +
    (currentReviewHours * 0.3) +
    (currentCIMinutes / 60)
  ) * hourlyRate

  const improvedCost = prsPerMonth * (
    contextSwitchCost +
    (targetReviewHours * 0.3) +
    (targetCIMinutes / 60)
  ) * hourlyRate

  return {
    savedDollars: Math.round(currentCost - improvedCost),
    savedHours: Math.round((currentCost - improvedCost) / hourlyRate)
  }
}

export default function WhatIfSimulator({ currentData, prsPerMonth, hourlyRate }) {
  const currentReview = Math.round(currentData.prMetrics.avgTimeToFirstReview)
  const currentCI = Math.round(currentData.ciMetrics?.avgDurationMinutes || 15)

  const [targetReview, setTargetReview] = useState(Math.max(currentReview - 4, 1))
  const [targetCI, setTargetCI] = useState(Math.max(currentCI - 5, 1))

  const savings = simulateLocally({
    currentReviewHours: currentReview,
    targetReviewHours: targetReview,
    currentCIMinutes: currentCI,
    targetCIMinutes: targetCI,
    prsPerMonth: Math.max(prsPerMonth, 1),
    hourlyRate
  })

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mt-6">
      <h3 className="text-xl font-bold mb-1">What-If Simulator</h3>
      <p className="text-gray-400 text-sm mb-6">Drag the sliders to see how much your team would recover.</p>

      <div className="mb-6">
        <div className="flex justify-between text-sm mb-1">
          <span>Avg time to first review</span>
          <span className="text-yellow-400">{targetReview}h <span className="text-gray-500">(currently {currentReview}h)</span></span>
        </div>
        <input type="range" min={1} max={currentReview} value={targetReview}
          onChange={e => setTargetReview(+e.target.value)}
          className="w-full accent-yellow-400" />
      </div>

      <div className="mb-8">
        <div className="flex justify-between text-sm mb-1">
          <span>Avg CI run duration</span>
          <span className="text-blue-400">{targetCI} min <span className="text-gray-500">(currently {currentCI} min)</span></span>
        </div>
        <input type="range" min={1} max={currentCI} value={targetCI}
          onChange={e => setTargetCI(+e.target.value)}
          className="w-full accent-blue-400" />
      </div>

      <div className="bg-green-950 border border-green-700 rounded-lg p-4 text-center">
        <p className="text-green-400 text-sm uppercase tracking-widest mb-1">Monthly Savings</p>
        <p className="text-4xl font-black text-green-400">${savings.savedDollars.toLocaleString()}</p>
        <p className="text-gray-400 text-sm mt-1">{savings.savedHours} developer-hours recovered / month</p>
      </div>
    </div>
  )
}