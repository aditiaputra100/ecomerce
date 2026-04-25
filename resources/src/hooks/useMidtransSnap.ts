import { useCallback, useEffect, useState } from 'react'
import { SNAP_SCRIPT_URL } from '../config'
import { fetchMidtransClientKey } from '../services'

declare global {
  interface Window {
    snap?: {
      pay: (
        token: string,
        callbacks?: {
          onSuccess?: (result: unknown) => void
          onPending?: (result: unknown) => void
          onError?: (error: unknown) => void
          onClose?: () => void
        },
      ) => void
    }
  }
}

export function useMidtransSnap() {
  const [clientKey, setClientKey] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    fetchMidtransClientKey()
      .then((res) => setClientKey(res.clientKey))
      .catch(() => setClientKey(null))
  }, [])

  useEffect(() => {
    if (!clientKey) return
    const scriptId = 'midtrans-snap'
    if (document.getElementById(scriptId)) {
      queueMicrotask(() => setReady(true))
      return
    }

    const script = document.createElement('script')
    script.id = scriptId
    script.src = SNAP_SCRIPT_URL
    script.dataset.clientKey = clientKey
    script.onload = () => setReady(true)
    script.onerror = () => setReady(false)
    document.body.appendChild(script)

    return () => {
      // keep script for reuse
    }
  }, [clientKey])

  const pay = useCallback(
    (token: string, callbacks?: Parameters<NonNullable<typeof window.snap>['pay']>[1]) => {
      if (!ready || !window.snap) {
        throw new Error('Midtrans Snap not ready')
      }
      window.snap.pay(token, callbacks)
    },
    [ready],
  )

  return { ready, clientKey, pay }
}
