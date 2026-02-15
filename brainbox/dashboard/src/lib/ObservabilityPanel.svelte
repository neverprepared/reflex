<script>
  import { onMount, onDestroy } from 'svelte';
  import { fetchLangfuseHealth, fetchSessions, fetchSessionSummary, connectSSE } from './api.js';
  import TraceTimeline from './TraceTimeline.svelte';
  import ToolBreakdown from './ToolBreakdown.svelte';

  let health = $state({ healthy: false, mode: 'off' });
  let sessions = $state([]);
  let summaries = $state([]);
  let selectedSession = $state('');
  let eventSource = null;

  const DOCKER_EVENTS = ['create', 'start', 'stop', 'die', 'destroy'];

  async function refreshHealth() {
    try {
      health = await fetchLangfuseHealth();
    } catch { health = { healthy: false, mode: 'unknown' }; }
  }

  async function refreshSessions() {
    try {
      const all = await fetchSessions();
      sessions = all.filter(s => s.active);
    } catch { /* noop */ }
  }

  async function refreshSummaries() {
    try {
      const results = await Promise.all(
        activeSessions.map(name =>
          fetchSessionSummary(name).catch(() => ({
            session_id: name,
            total_traces: 0,
            total_observations: 0,
            error_count: 0,
            tool_counts: {},
          }))
        )
      );
      summaries = results;
    } catch { /* noop */ }
  }

  onMount(() => {
    refreshHealth();
    refreshSessions();
    eventSource = connectSSE((data) => {
      if (DOCKER_EVENTS.includes(data)) {
        refreshSessions();
      }
    });
  });

  onDestroy(() => {
    if (eventSource) eventSource.close();
  });

  let activeSessions = $derived(sessions.map(s => s.session_name));

  // Re-fetch summaries when sessions change
  $effect(() => {
    if (activeSessions.length > 0) {
      refreshSummaries();
    } else {
      summaries = [];
    }
  });

  let totalTraces = $derived(summaries.reduce((n, s) => n + (s.total_traces || 0), 0));
  let totalErrors = $derived(summaries.reduce((n, s) => n + (s.error_count || 0), 0));
  let activeCount = $derived(activeSessions.length);
</script>

<header>
  <h1><span class="accent">observability</span></h1>
  {#if activeSessions.length > 0}
    <div class="session-filter">
      <select bind:value={selectedSession}>
        <option value="">All sessions</option>
        {#each activeSessions as name (name)}
          <option value={name}>{name}</option>
        {/each}
      </select>
    </div>
  {/if}
</header>

<div class="stats">
  <div class="stat-card" class:stat-healthy={health.healthy} class:stat-unhealthy={!health.healthy}>
    <div class="stat-label">LangFuse</div>
    <div class="stat-value">{health.healthy ? 'Connected' : 'Offline'}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Traces</div>
    <div class="stat-value">{totalTraces}</div>
  </div>
  <div class="stat-card" class:stat-errors={totalErrors > 0}>
    <div class="stat-label">Errors</div>
    <div class="stat-value">{totalErrors}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Active Sessions</div>
    <div class="stat-value stat-sessions">{activeCount}</div>
  </div>
</div>

<div class="widgets">
  <TraceTimeline sessions={activeSessions} {selectedSession} />
  <ToolBreakdown sessions={selectedSession ? [selectedSession] : activeSessions} />
</div>

<style>
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  h1 {
    font-size: 22px;
    font-weight: 600;
    color: #e2e8f0;
  }
  .accent { color: #f59e0b; }

  .session-filter select {
    background: #111827;
    border: 1px solid #1e293b;
    color: #e2e8f0;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
  }
  .session-filter select:focus {
    outline: none;
    border-color: #f59e0b;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }
  @media (max-width: 600px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
  }
  .stat-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px 20px;
  }
  .stat-label {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
  }
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #e2e8f0;
  }
  .stat-healthy .stat-value { color: #10b981; font-size: 20px; }
  .stat-unhealthy .stat-value { color: #ef4444; font-size: 20px; }
  .stat-errors .stat-value { color: #ef4444; }
  .stat-sessions { color: #10b981; }

  .widgets {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  @media (max-width: 900px) {
    .widgets { grid-template-columns: 1fr; }
  }
</style>
