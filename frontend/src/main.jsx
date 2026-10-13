import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = '/api';

// ── API helpers ────────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── Utility components ─────────────────────────────────────────────────────

function Badge({ value, className }) {
  return <span className={`badge badge-${(value || '').toLowerCase().replace('_', '-')}`}>{value}</span>;
}

function StatCard({ label, value, icon, color }) {
  return (
    <div className={`stat-card stat-card--${color}`}>
      <div className="stat-card__icon">{icon}</div>
      <div className="stat-card__body">
        <span className="stat-card__value">{value}</span>
        <span className="stat-card__label">{label}</span>
      </div>
    </div>
  );
}

function EmptyState({ message }) {
  return <div className="empty-state"><span>📭</span><p>{message}</p></div>;
}

function Spinner() {
  return <div className="spinner" aria-label="Loading" />;
}

function Alert({ type, message, onDismiss }) {
  if (!message) return null;
  return (
    <div className={`alert alert--${type}`} role="alert">
      <span>{type === 'error' ? '⚠️' : '✅'} {message}</span>
      {onDismiss && <button className="alert__close" onClick={onDismiss}>×</button>}
    </div>
  );
}

// ── Deployment Form ────────────────────────────────────────────────────────

function DeploymentForm({ onCreated, onClose }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    const f = new FormData(e.currentTarget);
    try {
      await apiFetch('/deployments', {
        method: 'POST',
        body: JSON.stringify({
          service_name: f.get('service_name'),
          version: f.get('version'),
          status: f.get('status'),
          deployed_by: f.get('deployed_by'),
          notes: f.get('notes'),
        }),
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onSubmit={handleSubmit} onClick={e => e.stopPropagation()}>
        <div className="modal__header">
          <div>
            <p className="eyebrow">NEW DEPLOYMENT</p>
            <h2>Record a Deployment</h2>
          </div>
          <button type="button" className="btn-icon" onClick={onClose} aria-label="Close">×</button>
        </div>
        {error && <Alert type="error" message={error} />}
        <label>Service Name *
          <input name="service_name" required placeholder="e.g. payment-service" maxLength={200} />
        </label>
        <label>Version *
          <input name="version" required placeholder="e.g. v1.2.3" maxLength={100} />
        </label>
        <div className="form-row">
          <label>Status
            <select name="status">
              <option value="PENDING">Pending</option>
              <option value="RUNNING">Running</option>
              <option value="SUCCESS">Success</option>
              <option value="FAILED">Failed</option>
              <option value="ROLLED_BACK">Rolled Back</option>
            </select>
          </label>
          <label>Deployed By
            <input name="deployed_by" placeholder="ci-pipeline" />
          </label>
        </div>
        <label>Notes
          <textarea name="notes" placeholder="Deployment notes…" rows={3} />
        </label>
        <button className="btn btn--primary btn--full" disabled={loading}>
          {loading ? 'Saving…' : 'Create Deployment'}
        </button>
      </form>
    </div>
  );
}

// ── Incident Form ──────────────────────────────────────────────────────────

function IncidentForm({ onCreated, onClose }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    const f = new FormData(e.currentTarget);
    try {
      await apiFetch('/incidents', {
        method: 'POST',
        body: JSON.stringify({
          title: f.get('title'),
          description: f.get('description'),
          severity: f.get('severity'),
          affected_service: f.get('affected_service'),
          owner: f.get('owner'),
        }),
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onSubmit={handleSubmit} onClick={e => e.stopPropagation()}>
        <div className="modal__header">
          <div>
            <p className="eyebrow">NEW INCIDENT</p>
            <h2>Report an Incident</h2>
          </div>
          <button type="button" className="btn-icon" onClick={onClose}>×</button>
        </div>
        {error && <Alert type="error" message={error} />}
        <label>Title *
          <input name="title" required placeholder="e.g. Database connection timeout" maxLength={200} />
        </label>
        <label>Description
          <textarea name="description" placeholder="What's happening?" rows={3} />
        </label>
        <div className="form-row">
          <label>Severity
            <select name="severity">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </label>
          <label>Affected Service
            <input name="affected_service" placeholder="e.g. orders-api" />
          </label>
        </div>
        <label>Owner
          <input name="owner" placeholder="ops-team" />
        </label>
        <button className="btn btn--primary btn--full" disabled={loading}>
          {loading ? 'Saving…' : 'Report Incident'}
        </button>
      </form>
    </div>
  );
}

// ── Deployments View ───────────────────────────────────────────────────────

function DeploymentsView() {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [success, setSuccess] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const qs = statusFilter ? `?status=${statusFilter}&page_size=50` : '?page_size=50';
      const res = await apiFetch(`/deployments${qs}`);
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => { load(); }, [load]);

  async function advanceStatus(dep) {
    const next = { PENDING: 'RUNNING', RUNNING: 'SUCCESS', SUCCESS: 'ROLLED_BACK', FAILED: 'ROLLED_BACK', ROLLED_BACK: 'PENDING' };
    try {
      await apiFetch(`/deployments/${dep.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: next[dep.status] || 'PENDING' }),
      });
      setSuccess(`Deployment ${dep.service_name} updated`);
      setTimeout(() => setSuccess(''), 3000);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const statuses = ['', 'PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'ROLLED_BACK'];

  return (
    <section className="view">
      <div className="view__header">
        <div>
          <p className="eyebrow">OPERATIONS / DEPLOYMENTS</p>
          <h1>Deployments</h1>
          <p className="muted">Track service releases across all environments</p>
        </div>
        <button className="btn btn--primary" id="new-deployment-btn" onClick={() => setShowForm(true)}>＋ New Deployment</button>
      </div>

      <div className="filter-bar">
        {statuses.map(s => (
          <button key={s || 'ALL'} id={`filter-dep-${s || 'all'}`}
            className={`filter-btn ${statusFilter === s ? 'active' : ''}`}
            onClick={() => setStatusFilter(s)}>
            {s || 'All'}
          </button>
        ))}
      </div>

      {success && <Alert type="success" message={success} onDismiss={() => setSuccess('')} />}
      {error && <Alert type="error" message={error} onDismiss={() => setError('')} />}

      {loading ? <Spinner /> : data.items.length === 0 ? (
        <EmptyState message="No deployments found. Create your first deployment." />
      ) : (
        <div className="table-wrap">
          <table id="deployments-table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Version</th>
                <th>Status</th>
                <th>Deployed By</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map(dep => (
                <tr key={dep.id}>
                  <td><strong>{dep.service_name}</strong></td>
                  <td><code>{dep.version}</code></td>
                  <td><Badge value={dep.status} /></td>
                  <td>{dep.deployed_by}</td>
                  <td>{new Date(dep.created_at).toLocaleString()}</td>
                  <td>
                    <button className="btn-icon" title="Advance status" onClick={() => advanceStatus(dep)}>↻</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="table-meta">Showing {data.items.length} of {data.total} deployments</p>
        </div>
      )}

      {showForm && <DeploymentForm onCreated={load} onClose={() => setShowForm(false)} />}
    </section>
  );
}

// ── Incidents View ─────────────────────────────────────────────────────────

function IncidentsView() {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [success, setSuccess] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/incidents?page_size=50');
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function resolve(inc) {
    try {
      await apiFetch(`/incidents/${inc.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'RESOLVED' }),
      });
      setSuccess(`Incident "${inc.title}" resolved`);
      setTimeout(() => setSuccess(''), 3000);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="view">
      <div className="view__header">
        <div>
          <p className="eyebrow">OPERATIONS / INCIDENTS</p>
          <h1>Incidents</h1>
          <p className="muted">Track and resolve operational incidents</p>
        </div>
        <button className="btn btn--primary btn--danger" id="new-incident-btn" onClick={() => setShowForm(true)}>🚨 Report Incident</button>
      </div>

      {success && <Alert type="success" message={success} onDismiss={() => setSuccess('')} />}
      {error && <Alert type="error" message={error} onDismiss={() => setError('')} />}

      {loading ? <Spinner /> : data.items.length === 0 ? (
        <EmptyState message="No incidents. All systems operational ✅" />
      ) : (
        <div className="table-wrap">
          <table id="incidents-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Affected Service</th>
                <th>Owner</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map(inc => (
                <tr key={inc.id} className={inc.severity === 'CRITICAL' ? 'row--critical' : ''}>
                  <td><strong>{inc.title}</strong><br /><small className="muted">{inc.description}</small></td>
                  <td><Badge value={inc.severity} /></td>
                  <td><Badge value={inc.status} /></td>
                  <td>{inc.affected_service || '—'}</td>
                  <td>{inc.owner}</td>
                  <td>{new Date(inc.created_at).toLocaleString()}</td>
                  <td>
                    {inc.status !== 'RESOLVED' && inc.status !== 'CLOSED' && (
                      <button className="btn btn--sm btn--success" onClick={() => resolve(inc)}>Resolve</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="table-meta">Showing {data.items.length} of {data.total} incidents</p>
        </div>
      )}

      {showForm && <IncidentForm onCreated={load} onClose={() => setShowForm(false)} />}
    </section>
  );
}

// ── Dashboard View ─────────────────────────────────────────────────────────

function DashboardView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    apiFetch('/stats').then(setStats).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="view"><Spinner /></div>;

  return (
    <section className="view">
      <div className="view__header">
        <div>
          <p className="eyebrow">WORKSPACE / OVERVIEW</p>
          <h1>Operations Dashboard</h1>
          <p className="muted">Real-time status of your deployment pipeline and incidents</p>
        </div>
      </div>

      {error && <Alert type="error" message={`Backend unavailable: ${error}. Start the backend and PostgreSQL, then refresh.`} />}

      <h2 className="section-title">Deployments</h2>
      <div className="stats-grid">
        <StatCard label="Total Deployments" value={stats?.deployments?.total ?? 0} icon="🚀" color="blue" />
        <StatCard label="Successful" value={stats?.deployments?.success ?? 0} icon="✅" color="green" />
        <StatCard label="Running" value={stats?.deployments?.running ?? 0} icon="⚡" color="yellow" />
        <StatCard label="Failed" value={stats?.deployments?.failed ?? 0} icon="❌" color="red" />
      </div>

      <h2 className="section-title">Incidents</h2>
      <div className="stats-grid">
        <StatCard label="Total Incidents" value={stats?.incidents?.total ?? 0} icon="🚨" color="red" />
        <StatCard label="Open" value={stats?.incidents?.open ?? 0} icon="🔴" color="red" />
        <StatCard label="Investigating" value={stats?.incidents?.investigating ?? 0} icon="🔍" color="yellow" />
        <StatCard label="Resolved" value={stats?.incidents?.resolved ?? 0} icon="✅" color="green" />
      </div>

      <div className="pipeline-banner">
        <p className="eyebrow">CI/CD PIPELINE</p>
        <div className="pipeline-steps">
          {['Code', 'Test', 'Build', 'Scan', 'Push', 'Deploy'].map((step, i) => (
            <React.Fragment key={step}>
              <span className="pipeline-step pipeline-step--done">{step}</span>
              {i < 5 && <span className="pipeline-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── App Shell ──────────────────────────────────────────────────────────────

function App() {
  const [view, setView] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '▦' },
    { id: 'deployments', label: 'Deployments', icon: '🚀' },
    { id: 'incidents', label: 'Incidents', icon: '🚨' },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <div className="brand-mark">OP</div>
          <div>
            <strong>OpsPulse</strong>
            <small>Reliability Platform</small>
          </div>
        </div>
        <nav className="sidebar__nav">
          {navItems.map(item => (
            <button key={item.id} id={`nav-${item.id}`}
              className={`nav-item ${view === item.id ? 'active' : ''}`}
              onClick={() => setView(item.id)}>
              <span className="nav-item__icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar__footer">
          <div className="sidebar__profile">
            <div className="avatar">NR</div>
            <div>
              <strong>Monika Bhardwaj</strong>
              <small>SRE Engineer</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        {view === 'dashboard' && <DashboardView />}
        {view === 'deployments' && <DeploymentsView />}
        {view === 'incidents' && <IncidentsView />}
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
