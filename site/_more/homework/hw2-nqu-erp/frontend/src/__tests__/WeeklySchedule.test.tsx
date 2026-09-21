import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import WeeklySchedule from '../components/WeeklySchedule'
import type { ScheduleItem } from '../types'

const items: ScheduleItem[] = [
  {
    course_code: 'CSIE301',
    course_name: '程式設計',
    teacher_name: '王大明',
    day_of_week: 1,
    start_period: 1,
    end_period: 3,
    location: 'E201',
  },
  {
    course_code: 'EE201',
    course_name: '電路學',
    teacher_name: '李老師',
    day_of_week: 3,
    start_period: 4,
    end_period: 4,
    location: 'E202',
  },
]

describe('WeeklySchedule', () => {
  it('renders day headers', () => {
    render(<WeeklySchedule items={items} />)
    expect(screen.getByText('週一')).toBeInTheDocument()
    expect(screen.getByText('週五')).toBeInTheDocument()
  })

  it('renders course blocks with name, location and teacher', () => {
    render(<WeeklySchedule items={items} />)
    expect(screen.getByText('程式設計')).toBeInTheDocument()
    expect(screen.getByText('E201')).toBeInTheDocument()
    expect(screen.getByText('王大明')).toBeInTheDocument()
    expect(screen.getByText('電路學')).toBeInTheDocument()
  })

  it('renders period numbers 1 and 14', () => {
    render(<WeeklySchedule items={items} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('14')).toBeInTheDocument()
  })

  it('shows empty state when no items', () => {
    render(<WeeklySchedule items={[]} />)
    expect(screen.queryByText('程式設計')).not.toBeInTheDocument()
  })
})