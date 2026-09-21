import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, getErrorMessage } from '../api/client'
import type { Course } from '../types'

export default function TeacherCourses() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get<Course[]>('/teachers/me/courses')
      .then((res) => setCourses(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-4 text-xl font-bold">我的授課清單</h1>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      <div className="space-y-3">
        {courses.map((c) => (
          <div key={c.course_id} className="flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm">
            <div>
              <div className="font-semibold">
                {c.course_name}
                <span className="ml-2 text-sm text-gray-500">[{c.course_code}]</span>
              </div>
              <div className="text-sm text-gray-600">
                學分：{c.credits} · 修課人數：{c.enrolled_count}/{c.capacity}
              </div>
              <div className="mt-1 text-sm text-gray-500">
                {c.schedules.length > 0
                  ? c.schedules
                      .map((s) => `週${s.day_of_week} 第 ${s.start_period}~${s.end_period} 節 ${s.location}`)
                      .join(' / ')
                  : '時段未定'}
              </div>
            </div>
            <Link
              to={`/teacher/courses/${c.course_id}`}
              className="rounded bg-blue-700 px-4 py-2 text-white hover:bg-blue-600"
            >
              登錄成績
            </Link>
          </div>
        ))}
        {courses.length === 0 && <p className="text-gray-500">目前沒有授課課程</p>}
      </div>
    </div>
  )
}