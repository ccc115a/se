import type { Grade } from '../types'

export default function GradeTable({ grades }: { grades: Grade[] }) {
  if (grades.length === 0) return <p className="text-gray-500">目前沒有成績資料</p>
  return (
    <table className="w-full border-collapse bg-white text-sm">
      <thead>
        <tr className="bg-gray-100 text-left">
          <th className="border border-gray-300 px-3 py-2">課程代碼</th>
          <th className="border border-gray-300 px-3 py-2">課程名稱</th>
          <th className="border border-gray-300 px-3 py-2">學分</th>
          <th className="border border-gray-300 px-3 py-2">期中</th>
          <th className="border border-gray-300 px-3 py-2">期末</th>
          <th className="border border-gray-300 px-3 py-2">總分</th>
          <th className="border border-gray-300 px-3 py-2">狀態</th>
        </tr>
      </thead>
      <tbody>
        {grades.map((g) => (
          <tr key={g.course_code}>
            <td className="border border-gray-300 px-3 py-2">{g.course_code}</td>
            <td className="border border-gray-300 px-3 py-2">{g.course_name}</td>
            <td className="border border-gray-300 px-3 py-2">{g.credits}</td>
            <td className="border border-gray-300 px-3 py-2">{g.midterm_score ?? '-'}</td>
            <td className="border border-gray-300 px-3 py-2">{g.final_score ?? '-'}</td>
            <td className="border border-gray-300 px-3 py-2">{g.total_score?.toFixed(1) ?? '-'}</td>
            <td className="border border-gray-300 px-3 py-2">
              {g.is_submitted ? (
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