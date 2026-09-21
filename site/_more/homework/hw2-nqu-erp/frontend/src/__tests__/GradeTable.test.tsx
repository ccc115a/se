import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import GradeTable from '../components/GradeTable'
import type { Grade } from '../types'

describe('GradeTable', () => {
  const grades: Grade[] = [
    {
      course_code: 'CSIE301',
      course_name: '程式設計',
      credits: 3,
      midterm_score: 80,
      final_score: 90,
      total_score: 86,
      is_submitted: true,
    },
    {
      course_code: 'EE201',
      course_name: '電路學',
      credits: 3,
      midterm_score: null,
      final_score: null,
      total_score: null,
      is_submitted: false,
    },
  ]

  it('renders course rows with scores', () => {
    render(<GradeTable grades={grades} />)
    expect(screen.getByText('程式設計')).toBeInTheDocument()
    expect(screen.getByText('CSIE301')).toBeInTheDocument()
    expect(screen.getAllByText('86.0').length).toBeGreaterThan(0)
  })

  it('shows 已送交 and 未送交 tags', () => {
    render(<GradeTable grades={grades} />)
    expect(screen.getByText('已送交')).toBeInTheDocument()
    expect(screen.getByText('未送交')).toBeInTheDocument()
  })

  it('renders placeholder for missing scores', () => {
    render(<GradeTable grades={grades} />)
    const cells = screen.getAllByText('-')
    expect(cells.length).toBe(3)
  })

  it('shows a message when empty', () => {
    render(<GradeTable grades={[]} />)
    expect(screen.getByText('目前沒有成績資料')).toBeInTheDocument()
  })
})