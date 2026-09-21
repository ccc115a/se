import { Link, useNavigate } from 'react-router-dom'
import { getUser, isLoggedIn, logout } from '../api/client'
import type { LoginResponse, Role } from '../types'

const NAV_LINKS: Record<Role, { to: string; label: string }[]> = {
  STUDENT: [
    { to: '/courses', label: '課程瀏覽' },
    { to: '/schedule', label: '我的課表' },
    { to: '/grades', label: '我的成績' },
  ],
  TEACHER: [{ to: '/teacher/courses', label: '授課清單' }],
  ADMIN: [
    { to: '/admin/users', label: '帳號管理' },
    { to: '/admin/courses', label: '課程管理' },
  ],
}

export default function Navbar() {
  const navigate = useNavigate()
  const user = getUser<LoginResponse>()

  if (!isLoggedIn() || !user) return null

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-blue-700 text-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <span className="font-bold">NQU 選課系統</span>
        <div className="flex items-center gap-4">
          {NAV_LINKS[user.role].map((l) => (
            <Link key={l.to} className="hover:underline" to={l.to}>
              {l.label}
            </Link>
          ))}
          <span className="text-sm text-blue-100">{user.full_name}</span>
          <button className="rounded bg-blue-600 px-3 py-1 text-sm hover:bg-blue-500" onClick={handleLogout}>
            登出
          </button>
        </div>
      </div>
    </nav>
  )
}