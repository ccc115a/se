export type Role = 'STUDENT' | 'TEACHER' | 'ADMIN'

export interface LoginResponse {
  token: string
  user_id: number
  username: string
  full_name: string
  role: Role
}

export interface ScheduleInfo {
  day_of_week: number
  start_period: number
  end_period: number
  location: string
}

export interface Course {
  course_id: number
  course_code: string
  course_name: string
  teacher_id: number
  teacher_name: string
  credits: number
  capacity: number
  enrolled_count: number
  dept_id: number
  dept_name: string
  schedules: ScheduleInfo[]
}

export interface ScheduleItem {
  course_code: string
  course_name: string
  teacher_name: string
  day_of_week: number
  start_period: number
  end_period: number
  location: string
}

export interface Grade {
  course_code: string
  course_name: string
  credits: number
  midterm_score: number | null
  final_score: number | null
  total_score: number | null
  is_submitted: boolean
}

export interface ApiMessage {
  success: boolean
  message: string
}

export interface RosterItem {
  enrollment_id: number
  student_id: number
  student_number: string
  full_name: string
  midterm_score: number | null
  final_score: number | null
  total_score: number | null
  is_submitted: boolean
}

export interface AdminUser {
  user_id: number
  username: string
  full_name: string
  role: Role
  dept_id: number
  dept_name: string
  email: string
}

export interface TeacherOption {
  user_id: number
  username: string
  full_name: string
  dept_name: string
}

export interface Department {
  dept_id: number
  dept_code: string
  dept_name: string
}