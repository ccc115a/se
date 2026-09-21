import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, getErrorMessage } from '../api/client'
import RosterTable, { type DraftGrade } from '../components/RosterTable'
import type { ApiMessage, RosterItem } from '../types'

export default function TeacherGradeEntry() {
  const { courseId } = useParams()
  const [roster, setRoster] = useState<RosterItem[]>([])
  const [drafts, setDrafts] = useState<DraftGrade[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')

  const load = async () => {
    const res = await api.get<RosterItem[]>(`/teachers/me/courses/${courseId}/students`)
    setRoster(res.data)
  }

  useEffect(() => {
    load()
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId])

  const save = async () => {
    setError('')
    setInfo('')
    if (drafts.length === 0) {
      setError('請先輸入要儲存的成績')
      return
    }
    setSaving(true)
    try {
      const { data } = await api.put<ApiMessage>('/grades/batch', {
        course_id: Number(courseId),
        grades: drafts,
      })
      if (data.success) setInfo(data.message)
      else setError(data.message)
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  const submit = async () => {
    setConfirmOpen(false)
    setError('')
    setInfo('')
    setSaving(true)
    try {
      const { data } = await api.post<ApiMessage>('/grades/submit', { course_id: Number(courseId) })
      if (data.success) setInfo(data.message)
      else setError(data.message)
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8">載入中...</div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link to="/teacher/courses" className="mb-3 inline-block text-sm text-blue-700 hover:underline">
        ← 返回授課清單
      </Link>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">成績登錄</h1>
        <div className="flex gap-2">
          <button
            className="rounded bg-blue-700 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
            onClick={save}
            disabled={saving}
          >
            {saving ? '處理中...' : '儲存成績'}
          </button>
          <button
            className="rounded bg-amber-500 px-4 py-2 text-white hover:bg-amber-400 disabled:opacity-50"
            onClick={() => setConfirmOpen(true)}
            disabled={saving}
          >
            鎖定送交
          </button>
        </div>
      </div>
      {error && <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
      {info && <p className="mb-4 rounded bg-green-50 px-3 py-2 text-sm text-green-700">{info}</p>}
      <RosterTable roster={roster} onDraftChange={setDrafts} />

      {confirmOpen && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/40" onClick={() => setConfirmOpen(false)}>
          <div className="w-96 rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h2 className="mb-2 text-lg font-bold">確認鎖定送交？</h2>
            <p className="mb-4 text-sm text-gray-600">鎖定後成績將無法修改，確定要送交嗎？</p>
            <div className="flex justify-end gap-2">
              <button className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-100" onClick={() => setConfirmOpen(false)}>
                取消
              </button>
              <button className="rounded bg-amber-500 px-4 py-2 text-white hover:bg-amber-400" onClick={submit}>
                確認送交
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}