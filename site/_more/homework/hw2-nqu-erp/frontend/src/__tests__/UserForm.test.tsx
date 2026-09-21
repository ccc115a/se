import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import UserForm, { type UserFormValues } from '../components/UserForm'
import type { Department } from '../types'

const departments: Department[] = [
  { dept_id: 1, dept_code: 'CSIE', dept_name: '資訊工程學系' },
  { dept_id: 2, dept_code: 'EE', dept_name: '電機工程學系' },
]

describe('UserForm', () => {
  it('renders role and department selects', () => {
    render(<UserForm departments={departments} onSubmit={() => {}} />)
    expect(screen.getByText('學生')).toBeInTheDocument()
    expect(screen.getByText('資訊工程學系')).toBeInTheDocument()
  })

  it('submits entered values with current dept and role', () => {
    const onSubmit = vi.fn()
    render(<UserForm departments={departments} onSubmit={onSubmit} />)

    fireEvent.change(screen.getByPlaceholderText('學號 / 帳號'), { target: { value: 'S100' } })
    fireEvent.change(screen.getByPlaceholderText('姓名'), { target: { value: '測試人員' } })
    fireEvent.change(screen.getByPlaceholderText('密碼'), { target: { value: 'pw1234' } })
    fireEvent.change(screen.getByPlaceholderText('email'), { target: { value: 's100@nqu.edu.tw' } })
    fireEvent.click(screen.getByRole('button', { name: '建立帳號' }))

    const values: UserFormValues = onSubmit.mock.calls[0][0]
    expect(values.username).toBe('S100')
    expect(values.full_name).toBe('測試人員')
    expect(values.role).toBe('STUDENT')
    expect(values.dept_id).toBe(1)
    expect(values.email).toBe('s100@nqu.edu.tw')
  })

  it('shows submitting state label', () => {
    render(<UserForm departments={departments} onSubmit={() => {}} submitting />)
    expect(screen.getByRole('button', { name: '儲存中...' })).toBeDisabled()
  })

  it('edit mode prefills values, locks username, password optional', () => {
    const onSubmit = vi.fn()
    render(
      <UserForm
        departments={departments}
        onSubmit={onSubmit}
        initial={{ username: 'S099', password: '', full_name: '測試改名', role: 'TEACHER', dept_id: 2, email: 's099@nqu.edu.tw' }}
      />,
    )

    expect(screen.getByRole('button', { name: '儲存修改' })).toBeInTheDocument()
    const usernameInput = screen.getByPlaceholderText('學號 / 帳號') as HTMLInputElement
    expect(usernameInput).toBeDisabled()
    expect(usernameInput.value).toBe('S099')

    fireEvent.change(screen.getByPlaceholderText('姓名'), { target: { value: '再度改名' } })
    fireEvent.click(screen.getByRole('button', { name: '儲存修改' }))

    const values: UserFormValues = onSubmit.mock.calls[0][0]
    expect(values.full_name).toBe('再度改名')
    expect(values.role).toBe('TEACHER')
    expect(values.dept_id).toBe(2)
    expect(values.email).toBe('s099@nqu.edu.tw')
  })
})