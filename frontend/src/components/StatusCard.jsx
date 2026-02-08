export default function StatusCard({ title, value, icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    green: 'from-green-500 to-green-600',
    emerald: 'from-emerald-500 to-emerald-600'
  }

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} text-white rounded-lg shadow-lg p-6 transform hover:scale-105 transition`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm opacity-90">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl opacity-80">{icon}</div>
      </div>
    </div>
  )
}
