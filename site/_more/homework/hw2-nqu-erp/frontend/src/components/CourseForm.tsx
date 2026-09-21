import { FormEvent, useEffect, useState } from 'react'
import type { Department, TeacherOption } from '../types'

export interface CourseFormValues {
  course_code: string
  academic_year: number
  semester: number
  course_name: string
  teacher_id: number
  credits: number
  capacity: number
  dept_id: number
}

interface Props {
  departments: Department[]
  teachers: TeacherOption[]
  onSubmit: (values: CourseFormValues) => void
  submitting?: boolean
  initial?: CourseFormValues | null
}

export default function CourseForm({ departments, teachers, onSubmit, submitting = false, initial = null }: Props) {
  const [courseCode, setCourseCode] = useState(initial?.course_code ?? '')
  const [courseName, setCourseName] = useState(initial?.course_name ?? '')
  const [deptId, setDeptId] = useState(initial?.dept_id ?? departments[0]?.dept_id ?? 1)
  const [teacherId, setTeacherId] = useState(initial?.teacher_id ?? teachers[0]?.user_id ?? 1)
  const [credits, setCredits] = useState(initial?.credits ?? 3)
  const [capacity, setCapacity] = useState(initial?.capacity ?? 40)

  useEffect(() => {
    setCourseCode(initial?.course_code ?? '')
    setCourseName(initial?.course_name ?? '')
    setDeptId(initial?.dept_id ?? departments[0]?.dept_id ?? 1)
    setTeacherId(initial?.teacher_id ?? teachers[0]?.user_id ?? 1)
    setCredits(initial?.credits ?? 3)
    setCapacity(initial?.capacity ?? 40)
  }, [initial, departments, teachers])

  const editing = Boolean(initial)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit({
      course_code: courseCode,
      academic_year: 113,
      semester: 1,
      course_name: courseName,
      teacher_id: teacherId,
      credits,
      capacity,
      dept_id: deptId,
    })
    if (!editing) {
      setCourseCode('')
      setCourseName('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border bg-white p-4 shadow-sm">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm text-gray-600">課程代碼</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            value={courseCode}
            onChange={(e) => setCourseCode(e.target.value)}
            placeholder="如 CSIE301"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">課程名稱</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="課程名稱"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">科系</label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={deptId}
            onChange={(e) => setDeptId(Number(e.target.value))}
          >
            {departments.map((d) => (
              <option key={d.dept_id} value={d.dept_id}>
                {d.dept_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">授課教師</label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={teacherId}
            onChange={(e) => setTeacherId(Number(e.target.value))}
          >
            {teachers.map((t) => (
              <option key={t.user_id} value={t.user_id}>
                {t.full_name}（{t.username}）
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">學分</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            type="number"
            min={1}
            max={6}
            value={credits}
            onChange={(e) => setCredits(Number(e.target.value))}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">名額上限</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            type="number"
            min={1}
            max={200}
            value={capacity}
            onChange={(e) => setCapacity(Number(e.target.value))}
            required
          />
        </div>
      </div>
      <button
        className="rounded bg-blue-700 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
        disabled={submitting}
      >
        {submitting ? '儲存中...' : editing ? '儲存修改' : '建立課程'}
      </button>
    </form>
  )
}