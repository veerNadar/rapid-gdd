import { useEffect, useState } from 'react'
import { describeApiError, getMetrics } from '../api/client'
import type { CallType, MetricsSummary } from '../api/types'
import { SECTION_LABELS } from '../sectionLabels'
import { card } from '../styles'

const CALL_TYPE_LABELS: Record<CallType, string> = {
  section_generation: 'Section Generation',
  review_parse: 'Review Parse',
  critique: 'Critique',
}

function pct(value: number): string {
  return `${Math.round(value * 100)}%`
}

function ms(value: number | null): string {
  return value === null ? '—' : `${Math.round(value)} ms`
}

export default function Metrics() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getMetrics()
      .then(setMetrics)
      .catch((err) => setError(describeApiError(err, 'Failed to load metrics')))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Metrics</h1>
      <p className="mt-1 text-sm text-slate-500">
        Gemini call volume, success rate, latency, and token usage. We're on the free tier —
        no real cost, but calls are tracked against the daily request limit.
      </p>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="mt-8 text-sm text-slate-400">Loading…</p>
      ) : metrics ? (
        <>
          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className={card}>
              <p className="text-xs text-slate-500">Total calls</p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {metrics.total_calls}
              </p>
            </div>
            <div className={card}>
              <p className="text-xs text-slate-500">Tokens in / out</p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {metrics.total_tokens_in} / {metrics.total_tokens_out}
              </p>
            </div>
            <div className={card}>
              <p className="text-xs text-slate-500">Total tokens</p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {metrics.total_tokens_total}
              </p>
            </div>
            <div className={card}>
              <p className="text-xs text-slate-500">Calls today</p>
              <p className="mt-1 text-2xl font-semibold text-slate-900">
                {metrics.calls_today}
                <span className="text-sm font-normal text-slate-400">
                  /{metrics.free_tier_daily_limit}
                </span>
              </p>
            </div>
          </div>

          <div className={`${card} mt-4`}>
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Free-tier daily requests used</span>
              <span>
                {metrics.calls_today} / {metrics.free_tier_daily_limit}
              </span>
            </div>
            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className={`h-full rounded-full ${
                  (metrics.free_tier_usage_pct ?? 0) >= 1 ? 'bg-red-500' : 'bg-indigo-600'
                }`}
                style={{
                  width: `${Math.min(100, Math.round((metrics.free_tier_usage_pct ?? 0) * 100))}%`,
                }}
              />
            </div>
          </div>

          <h2 className="mt-8 text-sm font-semibold text-slate-800">By Call Type</h2>
          <div className="mt-2 overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs text-slate-500">
                <tr>
                  <th className="px-3 py-2 font-medium">Call type</th>
                  <th className="px-3 py-2 font-medium">Total</th>
                  <th className="px-3 py-2 font-medium">Success rate</th>
                  <th className="px-3 py-2 font-medium">Avg latency</th>
                </tr>
              </thead>
              <tbody>
                {metrics.by_call_type.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-3 text-slate-400 italic">
                      No calls recorded yet.
                    </td>
                  </tr>
                ) : (
                  metrics.by_call_type.map((row) => (
                    <tr key={row.call_type} className="border-t border-slate-100">
                      <td className="px-3 py-2">{CALL_TYPE_LABELS[row.call_type]}</td>
                      <td className="px-3 py-2">
                        {row.total_calls} ({row.successful} ok, {row.failed} failed)
                      </td>
                      <td className="px-3 py-2">{pct(row.success_rate)}</td>
                      <td className="px-3 py-2">{ms(row.avg_latency_ms)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <h2 className="mt-8 text-sm font-semibold text-slate-800">By Section Type</h2>
          <div className="mt-2 overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs text-slate-500">
                <tr>
                  <th className="px-3 py-2 font-medium">Section</th>
                  <th className="px-3 py-2 font-medium">Total</th>
                  <th className="px-3 py-2 font-medium">Success rate</th>
                  <th className="px-3 py-2 font-medium">Avg latency</th>
                </tr>
              </thead>
              <tbody>
                {metrics.by_section_type.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-3 text-slate-400 italic">
                      No calls recorded yet.
                    </td>
                  </tr>
                ) : (
                  metrics.by_section_type.map((row) => (
                    <tr key={row.section_type} className="border-t border-slate-100">
                      <td className="px-3 py-2">{SECTION_LABELS[row.section_type]}</td>
                      <td className="px-3 py-2">
                        {row.total_calls} ({row.successful} ok, {row.failed} failed)
                      </td>
                      <td className="px-3 py-2">{pct(row.success_rate)}</td>
                      <td className="px-3 py-2">{ms(row.avg_latency_ms)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </div>
  )
}
