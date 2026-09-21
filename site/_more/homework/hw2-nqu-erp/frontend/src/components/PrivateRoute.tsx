import { Navigate, Outlet } from 'react-router-dom'
import { getUser, isLoggedIn } from '../api/client'
import { ROLE_HOME } from '../roles'
import type { LoginResponse, Role } from '../types'

export default function PrivateRoute({ roles }: { roles?: Role[] }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />

  if (roles) {
    const user = getUser<LoginResponse>()
    if (!user || !roles.includes(user.role)) {
      return <Navigate to={user ? ROLE_HOME[user.role] : '/login'} replace />
    }
  }

  return <Outlet />
}