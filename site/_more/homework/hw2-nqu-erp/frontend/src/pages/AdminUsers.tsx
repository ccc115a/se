import { useEffect, useMemo, useState } from 'react'
import { api, getErrorMessage } from '../api/client'
import UserForm, { type UserFormValues } from '../components/UserForm'
import type { AdminUser, ApiMessage, Department } from '../types'

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [editing, setEditing] = useState<AdminUser | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')

  const refresh = async () => {
    const [userRes, deptRes] = await Promise.all([api.get<AdminUser[]>('/admin/users'), api.get<Department[]>('/admin/departments')])
    setUsers(userRes.data)
    setDepartments(deptRes.data)
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim()
    if (!q) return users
    return users.filter((u) => u.username.includes(q) || u.full_name.includes(q) || u.role.includes(q))
  }, [users, search])

  const saveUser = async (values: UserFormValues) => {
    setError('')
    setInfo('')
    setSubmitting(true)
    try {
      const url = editing ? `/admin/users/${editing.user_id}` : '/admin/users'
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

  const deleteUser = async (user: AdminUser) => {
    if (!window.confirm(`確定刪除帳號 ${user.username}（${user.full_name}）？`)) return
    setError('')
    setInfo('')
    setDeleting(true)
    try {
      const { data } = await api.delete<ApiMessage>(`/admin/users/${user.user_id}`)
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
      <h1 className="mb-1 text-xl font-bold">帳號管理</h1>
      <p className="mb-4 text-sm text-gray-500">共 {filtered.length} 筆帳號</p>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      {info && <p className="mb-4 rounded bg-green-50 px-3 py-2 text-sm text-green-700">{info}</p>}

      <div className="mb-6">
        <h2 className="mb-2 text-sm font-semibold text-gray-600">
          {editing ? `編輯帳號 ${editing.username}` : '新增帳號'}
        </h2>
        <UserForm
          departments={departments}
          onSubmit={saveUser}
          submitting={submitting}
          initial={editing ? { username: editing.username, password: '', full_name: editing.full_name, role: editing.role, dept_id: editing.dept_id, email: editing.email } : null}
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

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-600">帳號列表</h2>
        <input
          className="w-64 rounded border px-3 py-2 text-sm"
          placeholder="搜尋帳號 / 姓名 / 角色"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <table className="w-full border-collapse bg-white text-sm">
        <thead>
          <tr className="bg-gray-100 text-left">
            <th className="border border-gray-300 px-3 py-2">帳號</th>
            <th className="border border-gray-300 px-3 py-2">姓名</th>
            <th className="border border-gray-300 px-3 py-2">角色</th>
            <th className="border border-gray-300 px-3 py-2">科系</th>
            <th className="border border-gray-300 px-3 py-2">Email</th>
            <th className="border border-gray-300 px-3 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((u) => (
            <tr key={u.user_id}>
              <td className="border border-gray-300 px-3 py-2">{u.username}</td>
              <td className="border border-gray-300 px-3 py-2">{u.full_name}</td>
              <td className="border border-gray-300 px-3 py-2">{u.role}</td>
              <td className="border border-gray-300 px-3 py-2">{u.dept_name}</td>
              <td className="border border-gray-300 px-3 py-2">{u.email}</td>
              <td className="border border-gray-300 px-3 py-2">
                <button
                  className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-500"
                  onClick={() => {
                    setEditing(u)
                    setError('')
                  }}
                >
                  編輯
                </button>{' '}
                <button
                  className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-500 disabled:opacity-50"
                  onClick={() => deleteUser(u)}
                  disabled={deleting}
                >
                  刪除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}