<script>
  import { onMount, onDestroy } from 'svelte';
  import { fetchSessionTraces } from './api.js';

  let { sessions = [], selectedSession = '' } = $props();

  let traces = $state([]);
  let timer = null;

  async function refresh() {
    try {
      if (selectedSession) {
        traces = await fetchSessionTraces(selectedSession);
      } else {
        // Fetch traces for all sessions and merge
        const all = await Promise.all(
          sessions.map(s => fetchSessionTraces(s, 20).catch(() => []))
        );
        traces = all.flat().sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || '')).slice(0, 50);
      }
    } catch { /* noop */ }
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 10000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  // Re-fetch when session changes
  $effect(() => {
    selectedSession;
    sessions;
    refresh();
  });

  function formatTime(ts) {
    if (!ts) return '';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch { return ts; }
  }

  let expandedId = $state(null);
</script>

<div class="timeline-section">
  <h3>Recent Traces</h3>
  {#if traces.length === 0}
    <p class="empty">No traces recorded</p>
  {:else}
    <div class="trace-list">
      {#each traces as t (t.id)}
        <button class="trace-row" class:expanded={expandedId === t.id} onclick={() => expandedId = expandedId === t.id ? null : t.id}>
          <span class="trace-time">{formatTime(t.timestamp)}</span>
          <span class="session-badge">{t.session_id}</span>
          <span class="trace-name">{t.name || 'trace'}</span>
          <span class="status-dot" class:error={t.status === 'error'} class:ok={t.status === 'ok'}></span>
        </button>
        {#if expandedId === t.id}
          <div class="trace-detail">
            {#if t.input}<div class="detail-block"><span class="detail-label">Input</span><pre>{t.input}</pre></div>{/if}
            {#if t.output}<div class="detail-block"><span class="detail-label">Output</span><pre>{t.output}</pre></div>{/if}
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>

<style>
  .timeline-section {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 20px;
  }
  h3 {
    font-size: 14px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
  }
  .empty { color: #475569; font-size: 14px; }
  .trace-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
    max-height: 400px;
    overflow-y: auto;
  }
  .trace-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    border: none;
    background: transparent;
    color: #e2e8f0;
    font-size: 13px;
    cursor: pointer;
    border-radius: 4px;
    text-align: left;
    width: 100%;
  }
  .trace-row:hover { background: rgba(30, 41, 59, 0.6); }
  .trace-row.expanded { background: rgba(30, 41, 59, 0.4); }
  .trace-time {
    color: #64748b;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
    font-size: 12px;
    min-width: 70px;
  }
  .session-badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
    white-space: nowrap;
  }
  .trace-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .status-dot.ok { background: #10b981; }
  .status-dot.error { background: #ef4444; }
  .trace-detail {
    padding: 8px 12px 12px 94px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .detail-block {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .detail-label {
    font-size: 10px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  pre {
    font-size: 12px;
    color: #94a3b8;
    background: rgba(15, 23, 42, 0.5);
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0;
  }
</style>
