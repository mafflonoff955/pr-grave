export default function ScanProgress() {
  return (
    <div className="text-center py-12">
      <div className="inline-block animate-spin text-4xl mb-4">💀</div>
      <p className="text-gray-400">Scanning repository...</p>
      <p className="text-gray-500 text-sm mt-2">This may take a moment for large repos</p>
    </div>
  )
}