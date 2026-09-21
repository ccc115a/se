import { useEffect, useState } from 'react'
import { api, getErrorMessage } from '../api/client'
import WeeklySchedule from '../components/WeeklySchedule'
import type { ScheduleItem } from '../types'

export default function MySchedule() {
  const [items, setItems] = useState<ScheduleItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<ScheduleItem[]>('/students/me/schedule')
      .then((res) => setItems(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-4 text-xl font-bold">我的課表</h1>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      <WeeklySchedule items={items} />
    </div>
  )
}