import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, getErrorMessage, saveUser } from '../api/client'
import { ROLE_HOME } from '../roles'
import type { LoginResponse } from '../types'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post<LoginResponse>('/auth/login', { username, password })
      localStorage.setItem('nqu_token', data.token)
      saveUser(data)
      navigate(ROLE_HOME[data.role])
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <form onSubmit={handleSubmit} className="w-80 space-y-4 rounded-lg border bg-white p-8 shadow">
        <h1 className="text-center text-xl font-bold">NQU 選課系統登入</h1>
        <div>
          <label className="mb-1 block text-sm text-gray-600">帳號</label>
          <input
            className="w-full rounded border px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="學號"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-600">密碼</label>
          <input
            className="w-full rounded border px-3 py-2"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="密碼"
            required
          />
        </div>
        {error && <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
        <button
          className="w-full rounded bg-blue-700 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? '登入中...' : '登入'}
        </button>
      </form>
    </div>
  )
}