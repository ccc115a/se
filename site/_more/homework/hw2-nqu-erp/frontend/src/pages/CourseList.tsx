import { useEffect, useMemo, useState } from 'react'
import { api, getErrorMessage } from '../api/client'
import type { ApiMessage, Course, ScheduleItem } from '../types'

export default function CourseList() {
  const [courses, setCourses] = useState<Course[]>([])
  const [enrolled, setEnrolled] = useState<Set<string>>(new Set())
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')

  const refresh = async () => {
    const [courseRes, scheduleRes] = await Promise.all([
      api.get<Course[]>('/courses'),
      api.get<ScheduleItem[]>('/students/me/schedule'),
    ])
    setCourses(courseRes.data)
    setEnrolled(new Set(scheduleRes.data.map((s) => s.course_code)))
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim()
    if (!q) return courses
    return courses.filter((c) => c.course_name.includes(q))
  }, [courses, search])

  const enroll = async (course: Course) => {
    setError('')
    setInfo('')
    try {
      const { data } = await api.post<ApiMessage>('/enrollments', { course_id: course.course_id })
      if (data.success) setInfo(data.message)
      else setError(data.message)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  const drop = async (course: Course) => {
    setError('')
    setInfo('')
    try {
      const { data } = await api.delete<ApiMessage>('/enrollments', { data: { course_id: course.course_id } })
      if (data.success) setInfo(data.message)
      else setError(data.message)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">課程瀏覽</h1>
        <input
          className="w-64 rounded border px-3 py-2"
          placeholder="搜尋課程名稱"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      {info && <p className="mb-4 rounded bg-green-50 px-3 py-2 text-sm text-green-700">{info}</p>}
      <div className="space-y-3">
        {filtered.map((c) => {
          const isEnrolled = enrolled.has(c.course_code)
          const full = c.enrolled_count >= c.capacity
          return (
            <div key={c.course_id} className="rounded-lg border bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold">
                    {c.course_name}
                    <span className="ml-2 text-sm text-gray-500">[{c.course_code}]</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    教師：{c.teacher_name} · 學分：{c.credits} · 名額：{c.enrolled_count}/{c.capacity}
                  </div>
                  <div className="mt-1 text-sm text-gray-500">
                    {c.schedules.length > 0
                      ? c.schedules
                          .map((s) => `週${s.day_of_week} 第 ${s.start_period}~${s.end_period} 節 ${s.location}`)
                          .join(' / ')
                      : '時段未定'}
                  </div>
                </div>
                {isEnrolled ? (
                  <button
                    className="rounded bg-amber-500 px-4 py-2 text-white hover:bg-amber-400"
                    onClick={() => drop(c)}
                  >
                    退選
                  </button>
                ) : (
                  <button
                    className="rounded bg-blue-700 px-4 py-2 text-white hover:bg-blue-600 disabled:bg-gray-300"
                    onClick={() => enroll(c)}
                    disabled={full}
                  >
                    {full ? '已額滿' : '加選'}
                  </button>
                )}
              </div>
            </div>
          )
        })}
        {filtered.length === 0 && <p className="text-gray-500">沒有符合條件的課程</p>}
      </div>
    </div>
  )
}