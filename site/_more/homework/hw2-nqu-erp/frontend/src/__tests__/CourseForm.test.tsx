import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import CourseForm, { type CourseFormValues } from '../components/CourseForm'
import type { Department, TeacherOption } from '../types'

const departments: Department[] = [
  { dept_id: 1, dept_code: 'CSIE', dept_name: '資訊工程學系' },
  { dept_id: 2, dept_code: 'EE', dept_name: '電機工程學系' },
]

const teachers: TeacherOption[] = [
  { user_id: 1, username: 'T001', full_name: '王大明', dept_name: '資訊工程學系' },
  { user_id: 3, username: 'T003', full_name: '張志偉', dept_name: '電機工程學系' },
]

describe('CourseForm', () => {
  it('renders department and teacher options', () => {
    render(<CourseForm departments={departments} teachers={teachers} onSubmit={() => {}} />)
    expect(screen.getByText('資訊工程學系')).toBeInTheDocument()
    expect(screen.getByText('王大明（T001）')).toBeInTheDocument()
    expect(screen.getByText('張志偉（T003）')).toBeInTheDocument()
  })

  it('submits course values with defaults', () => {
    const onSubmit = vi.fn()
    render(<CourseForm departments={departments} teachers={teachers} onSubmit={onSubmit} />)

    fireEvent.change(screen.getByPlaceholderText('如 CSIE301'), { target: { value: 'CSIE501' } })
    fireEvent.change(screen.getByPlaceholderText('課程名稱'), { target: { value: '人工智慧' } })
    fireEvent.click(screen.getByRole('button', { name: '建立課程' }))

    const values: CourseFormValues = onSubmit.mock.calls[0][0]
    expect(values.course_code).toBe('CSIE501')
    expect(values.course_name).toBe('人工智慧')
    expect(values.credits).toBe(3)
    expect(values.capacity).toBe(40)
    expect(values.academic_year).toBe(113)
    expect(values.semester).toBe(1)
    expect(values.dept_id).toBe(1)
    expect(values.teacher_id).toBe(1)
  })

  it('shows submitting state label', () => {
    render(<CourseForm departments={departments} teachers={teachers} onSubmit={() => {}} submitting />)
    expect(screen.getByRole('button', { name: '儲存中...' })).toBeDisabled()
  })

  it('edit mode prefills values and submits them', () => {
    const onSubmit = vi.fn()
    render(
      <CourseForm
        departments={departments}
        teachers={teachers}
        onSubmit={onSubmit}
        initial={{ course_code: 'TEST101', academic_year: 113, semester: 1, course_name: '測試課程改名', teacher_id: 3, credits: 4, capacity: 60, dept_id: 2 }}
      />,
    )

    expect(screen.getByRole('button', { name: '儲存修改' })).toBeInTheDocument()

    const codeInput = screen.getByPlaceholderText('如 CSIE301') as HTMLInputElement
    expect(codeInput.value).toBe('TEST101')
    const nameInput = screen.getByPlaceholderText('課程名稱') as HTMLInputElement
    expect(nameInput.value).toBe('測試課程改名')

    fireEvent.click(screen.getByRole('button', { name: '儲存修改' }))

    const values: CourseFormValues = onSubmit.mock.calls[0][0]
    expect(values.course_code).toBe('TEST101')
    expect(values.course_name).toBe('測試課程改名')
    expect(values.credits).toBe(4)
    expect(values.capacity).toBe(60)
    expect(values.dept_id).toBe(2)
    expect(values.teacher_id).toBe(3)
  })
})