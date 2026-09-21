import type { Role } from './types'

export const ROLE_HOME: Record<Role, string> = {
  STUDENT: '/courses',
  TEACHER: '/teacher/courses',
  ADMIN: '/admin/users',
}