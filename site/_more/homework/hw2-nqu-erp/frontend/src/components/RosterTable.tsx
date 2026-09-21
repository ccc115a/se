import { useState } from 'react'
import type { RosterItem } from '../types'

export interface DraftGrade {
  enrollment_id: number
  midterm_score: number | null
  final_score: number | null
}

interface Props {
  roster: RosterItem[]
  onDraftChange?: (drafts: DraftGrade[]) => void
}

export default function RosterTable({ roster, onDraftChange }: Props) {
  const [drafts, setDrafts] = useState<Record<string, string>>({})

  const handleChange = (enrollmentId: number, field: 'midterm' | 'final', value: string) => {
    const next = { ...drafts, [`${enrollmentId}:${field}`]: value }
    setDrafts(next)
    onDraftChange?.(toDrafts(roster, next))
  }

  if (roster.length === 0) return <p className="text-gray-500">此課程目前沒有選課學生</p>

  return (
    <table className="w-full border-collapse bg-white text-sm">
      <thead>
        <tr className="bg-gray-100 text-left">
          <th className="border border-gray-300 px-3 py-2">學號</th>
          <th className="border border-gray-300 px-3 py-2">姓名</th>
          <th className="border border-gray-300 px-3 py-2">期中</th>
          <th className="border border-gray-300 px-3 py-2">期末</th>
          <th className="border border-gray-300 px-3 py-2">總分</th>
          <th className="border border-gray-300 px-3 py-2">狀態</th>
        </tr>
      </thead>
      <tbody>
        {roster.map((r) => (
          <tr key={r.enrollment_id}>
            <td className="border border-gray-300 px-3 py-2">{r.student_number}</td>
            <td className="border border-gray-300 px-3 py-2">{r.full_name}</td>
            <td className="border border-gray-300 px-3 py-2">
              <input
                className="w-20 rounded border px-2 py-1 text-sm"
                type="number"
                min={0}
                max={100}
                step={0.01}
                disabled={r.is_submitted}
                aria-label={`期中考 ${r.student_number}`}
                placeholder={r.midterm_score?.toString() ?? ''}
                value={drafts[`${r.enrollment_id}:midterm`] ?? ''}
                onChange={(e) => handleChange(r.enrollment_id, 'midterm', e.target.value)}
              />
            </td>
            <td className="border border-gray-300 px-3 py-2">
              <input
                className="w-20 rounded border px-2 py-1 text-sm"
                type="number"
                min={0}
                max={100}
                step={0.01}
                disabled={r.is_submitted}
                aria-label={`期末考 ${r.student_number}`}
                placeholder={r.final_score?.toString() ?? ''}
                value={drafts[`${r.enrollment_id}:final`] ?? ''}
                onChange={(e) => handleChange(r.enrollment_id, 'final', e.target.value)}
              />
            </td>
            <td className="border border-gray-300 px-3 py-2">{r.total_score?.toFixed(1) ?? '-'}</td>
            <td className="border border-gray-300 px-3 py-2">
              {r.is_submitted ? (
                <span className="rounded bg-green-100 px-2 py-0.5 text-green-700">已送交</span>
              ) : (
                <span className="rounded bg-gray-100 px-2 py-0.5 text-gray-600">未送交</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function toDrafts(roster: RosterItem[], drafts: Record<string, string>): DraftGrade[] {
  return roster
    .filter((r) => !r.is_submitted)
    .map((r) => {
      const mid = drafts[`${r.enrollment_id}:midterm`]
      const fin = drafts[`${r.enrollment_id}:final`]
      const padMid = mid !== undefined && mid.trim() !== ''
      const padFinal = fin !== undefined && fin.trim() !== ''
      if (!padMid && !padFinal) return null
      return {
        enrollment_id: r.enrollment_id,
        midterm_score: padMid ? Number(mid) : r.midterm_score,
        final_score: padFinal ? Number(fin) : r.final_score,
      }
    })
    .filter((e): e is DraftGrade => e !== null)
}