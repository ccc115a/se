import { AxiosError, AxiosHeaders } from 'axios'
import { describe, expect, it } from 'vitest'
import { getErrorMessage } from '../api/client'

describe('getErrorMessage', () => {
  it('extracts Chinese error message from backend response', () => {
    const err = new AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      { headers: new AxiosHeaders(), method: 'get' } as never,
      null,
      {
        status: 401,
        statusText: 'Unauthorized',
        headers: {},
        data: { error: '帳號或密碼錯誤' },
        config: {} as never,
      },
    )
    expect(getErrorMessage(err)).toBe('帳號或密碼錯誤')
  })

  it('falls back to a generic message when no payload', () => {
    const err = new AxiosError('Network Error', 'ERR_NETWORK')
    expect(getErrorMessage(err)).toBe('發生錯誤，請稍後再試')
  })

  it('falls back for non-axios errors', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('發生錯誤，請稍後再試')
  })
})