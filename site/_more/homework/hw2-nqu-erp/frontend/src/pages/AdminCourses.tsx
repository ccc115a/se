import { useEffect, useState } from 'react'
import { api, getErrorMessage } from '../api/client'
import CourseForm, { type CourseFormValues } from '../components/CourseForm'
import type { ApiMessage, Course, Department, TeacherOption } from '../types'

export default function AdminCourses() {
  const [courses, setCourses] = useState<Course[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [teachers, setTeachers] = useState<TeacherOption[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [editing, setEditing] = useState<Course | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')

  const refresh = async () => {
    const [courseRes, deptRes, teacherRes] = await Promise.all([
      api.get<Course[]>('/courses'),
      api.get<Department[]>('/admin/departments'),
      api.get<TeacherOption[]>('/admin/teachers'),
    ])
    setCourses(courseRes.data)
    setDepartments(deptRes.data)
    setTeachers(teacherRes.data)
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const saveCourse = async (values: CourseFormValues) => {
    setError('')
    setInfo('')
    setSubmitting(true)
    try {
      const url = editing ? `/admin/courses/${editing.course_id}` : '/admin/courses'
      const { data } = editing ? await api.put<ApiMessage>(url, values) : await api.post<ApiMessage>(url, values)
      if (data.success) setInfo(data.message)
      else setError(data.message)
      setEditing(null)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  const deleteCourse = async (course: Course) => {
    if (!window.confirm(`確定刪除課程 ${course.course_name}（${course.course_code}）？`)) return
    setError('')
    setInfo('')
    setDeleting(true)
    try {
      const { data } = await api.delete<ApiMessage>(`/admin/courses/${course.course_id}`)
      if (data.success) setInfo(data.message)
      else setError(data.message)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-4 text-xl font-bold">課程管理</h1>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      {info && <p className="mb-4 rounded bg-green-50 px-3 py-2 text-sm text-green-700">{info}</p>}

      <div className="mb-6">
        <h2 className="mb-2 text-sm font-semibold text-gray-600">
          {editing ? `編輯課程 ${editing.course_name}` : '開設新課程'}
        </h2>
        <CourseForm
          departments={departments}
          teachers={teachers}
          onSubmit={saveCourse}
          submitting={submitting}
          initial={editing ? { course_code: editing.course_code, academic_year: 113, semester: 1, course_name: editing.course_name, teacher_id: editing.teacher_id, credits: editing.credits, capacity: editing.capacity, dept_id: editing.dept_id } : null}
        />
        {editing && (
          <button
            className="mt-2 rounded px-3 py-1 text-sm text-gray-600 hover:bg-gray-100"
            onClick={() => {
              setEditing(null)
              setError('')
            }}
          >
            取消編輯
          </button>
        )}
      </div>

      <h2 className="mb-2 text-sm font-semibold text-gray-600">課程列表（{courses.length} 門）</h2>
      <div className="space-y-3">
        {courses.map((c) => (
          <div key={c.course_id} className="rounded-lg border bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-semibold">
                  {c.course_name}
                  <span className="ml-2 text-sm text-gray-500">[{c.course_code}]</span>
                </div>
                <div className="text-sm text-gray-600">
                  {c.dept_name} · 教師：{c.teacher_name} · 學分：{c.credits} · 名額：{c.enrolled_count}/{c.capacity}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-500"
                  onClick={() => {
                    setEditing(c)
                    setError('')
                  }}
                >
                  編輯
                </button>
                <button
                  className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-500 disabled:opacity-50"
                  onClick={() => deleteCourse(c)}
                  disabled={deleting}
                >
                  刪除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}