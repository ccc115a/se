import { useEffect, useState } from 'react'
import { api, getErrorMessage } from '../api/client'
import GradeTable from '../components/GradeTable'
import type { Grade } from '../types'

export default function MyGrades() {
  const [grades, setGrades] = useState<Grade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<Grade[]>('/students/me/grades')
      .then((res) => setGrades(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-4 text-xl font-bold">我的成績</h1>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      <GradeTable grades={grades} />
    </div>
  )
}