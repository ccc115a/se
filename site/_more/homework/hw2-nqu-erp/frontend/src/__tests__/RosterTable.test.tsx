import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import RosterTable, { toDrafts } from '../components/RosterTable'
import type { RosterItem } from '../types'

const roster: RosterItem[] = [
  {
    enrollment_id: 1,
    student_id: 11,
    student_number: '11303001',
    full_name: '陳小明',
    midterm_score: 80,
    final_score: 90,
    total_score: 86,
    is_submitted: true,
  },
  {
    enrollment_id: 2,
    student_id: 12,
    student_number: '11303002',
    full_name: '林小華',
    midterm_score: null,
    final_score: null,
    total_score: null,
    is_submitted: false,
  },
]

describe('RosterTable', () => {
  it('renders student rows with scores', () => {
    render(<RosterTable roster={roster} />)
    expect(screen.getByText('11303001')).toBeInTheDocument()
    expect(screen.getByText('陳小明')).toBeInTheDocument()
    expect(screen.getByText('林小華')).toBeInTheDocument()
    expect(screen.getByText('86.0')).toBeInTheDocument()
  })

  it('shows 已送交 and 未送交 tags', () => {
    render(<RosterTable roster={roster} />)
    expect(screen.getByText('已送交')).toBeInTheDocument()
    expect(screen.getByText('未送交')).toBeInTheDocument()
  })

  it('disables inputs for submitted rows', () => {
    render(<RosterTable roster={roster} />)
    const input = screen.getByLabelText('期中考 11303001')
    expect(input).toBeDisabled()
    const editable = screen.getByLabelText('期中考 11303002')
    expect(editable).not.toBeDisabled()
  })

  it('shows a message when roster is empty', () => {
    render(<RosterTable roster={[]} />)
    expect(screen.getByText('此課程目前沒有選課學生')).toBeInTheDocument()
  })

  it('emits draft entries on input change', () => {
    const onDraftChange = vi.fn()
    render(<RosterTable roster={roster} onDraftChange={onDraftChange} />)
    fireEvent.change(screen.getByLabelText('期中考 11303002'), { target: { value: '77' } })
    expect(onDraftChange).toHaveBeenCalled()
    const entries = onDraftChange.mock.calls[0][0]
    expect(entries).toEqual([{ enrollment_id: 2, midterm_score: 77, final_score: null }])
  })
})

describe('toDrafts', () => {
  const drafts = { '2:midterm': '77' }

  it('skips submitted rows and inactive blanks', () => {
    expect(toDrafts(roster, drafts)).toEqual([{ enrollment_id: 2, midterm_score: 77, final_score: null }])
  })

  it('returns an empty array when nothing typed', () => {
    expect(toDrafts(roster, {})).toEqual([])
  })
})