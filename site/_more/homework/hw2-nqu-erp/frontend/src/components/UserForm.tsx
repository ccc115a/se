import { FormEvent, useEffect, useState } from 'react'
import type { Department, Role } from '../types'

export interface UserFormValues {
  username: string
  password: string
  full_name: string
  role: Role
  dept_id: number
  email: string
}

interface Props {
  departments: Department[]
  onSubmit: (values: UserFormValues) => void
  submitting?: boolean
  initial?: UserFormValues | null
}

export default function UserForm({ departments, onSubmit, submitting = false, initial = null }: Props) {
  const [username, setUsername] = useState(initial?.username ?? '')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState(initial?.full_name ?? '')
  const [role, setRole] = useState<Role>(initial?.role ?? 'STUDENT')
  const [deptId, setDeptId] = useState(initial?.dept_id ?? departments[0]?.dept_id ?? 1)
  const [email, setEmail] = useState(initial?.email ?? '')

  useEffect(() => {
    setUsername(initial?.username ?? '')
    setPassword('')
    setFullName(initial?.full_name ?? '')
    setRole(initial?.role ?? 'STUDENT')
    setDeptId(initial?.dept_id ?? departments[0]?.dept_id ?? 1)
    setEmail(initial?.email ?? '')
  }, [initial, departments])

  const editing = Boolean(initial)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit({ username, password, full_name: fullName, role, dept_id: deptId, email })
    if (!editing) {
      setUsername('')
      setPassword('')
      setFullName('')
      setEmail('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border bg-white p-4 shadow-sm">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm text-gray-600">帳號</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm disabled:bg-gray-100"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="學號 / 帳號"
            required
            disabled={editing}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">姓名</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="姓名"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">密碼</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={editing ? '留空表示不修改' : '密碼'}
            required={!editing}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">角色</label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
          >
            <option value="STUDENT">學生</option>
            <option value="TEACHER">教師</option>
            <option value="ADMIN">管理員</option>
          </select>
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
          <label className="mb-1 block text-sm text-gray-600">Email</label>
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email"
            required
          />
        </div>
      </div>
      <button
        className="rounded bg-blue-700 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
        disabled={submitting}
      >
        {submitting ? '儲存中...' : editing ? '儲存修改' : '建立帳號'}
      </button>
    </form>
  )
}