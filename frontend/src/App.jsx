import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL
  || (import.meta.env.DEV ? 'http://127.0.0.1:8010/api/disagreements/' : '')

function App() {
  const [org, setOrg] = useState('ORG-A')
  const [reason, setReason] = useState('')
  const [sortDescending, setSortDescending] = useState(false)
  const [rows, setRows] = useState([])
  const [error, setError] = useState(
    API_URL ? '' : 'API endpoint is not configured. Set VITE_API_URL for this deployment.',
  )

  useEffect(() => {
    if (!API_URL) return

    const params = new URLSearchParams({ org, sort: `${sortDescending ? '-' : ''}value` })
    if (reason) params.set('reason', reason)
    fetch(`${API_URL}?${params}`)
      .then((response) => {
        if (!response.ok) throw new Error(`API returned ${response.status}`)
        return response.json()
      })
      .then((data) => {
        setRows(data.rows || [])
        setError('')
      })
      .catch(() => {
        setRows([])
        setError('Could not load disagreements. Make sure the Django API is running.')
      })
  }, [org, reason, sortDescending])

  const reasons = useMemo(
    () => [...new Set(rows.map((row) => row.reason))].sort(),
    [rows],
  )

  return (
    <main className="app">
      <header>
        <div>
          <p className="eyebrow">DealerOS reconciliation</p>
          <h1>System disagreements</h1>
        </div>
        <div className="filters">
          <label>
            Organization
            <select value={org} onChange={(event) => setOrg(event.target.value)}>
              <option value="ORG-A">ORG-A</option>
              <option value="ORG-B">ORG-B</option>
            </select>
          </label>
          <label>
            Reason
            <select value={reason} onChange={(event) => setReason(event.target.value)}>
              <option value="">All reasons</option>
              {reasons.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
        </div>
      </header>

      {error && <p className="message error">{error}</p>}
      {!error && rows.length === 0 && <p className="message">No disagreements found.</p>}

      {rows.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Reason</th>
                <th>Record ID</th>
                <th>Location</th>
                <th
                  className="sortable"
                  onClick={() => setSortDescending((current) => !current)}
                >
                  System A value {sortDescending ? '↓' : '↑'}
                </th>
                <th>System B value</th>
                <th>Difference</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.record_id}-${row.reason}-${index}`}>
                  <td><span className="reason">{row.reason}</span></td>
                  <td>{row.record_id}</td>
                  <td>{row.location || '—'}</td>
                  <td>{row.a_value || '—'}</td>
                  <td>{row.b_value || '—'}</td>
                  <td>{row.difference || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}

export default App
