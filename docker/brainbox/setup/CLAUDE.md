# Developer Container

This is a containerized development environment with Claude Code.
You have access to the GitHub CLI (`gh`) for GitHub operations.
The environment includes Python, Node.js, Go, and Rust toolchains.

## Skills

Reference skills are available at `~/.claude/skills/`. Read the relevant SKILL.md when working on tasks in these domains:

### Infrastructure / Cloud
- `~/.claude/skills/aws-patterns/SKILL.md` — AWS service patterns (Lambda, S3, EC2, VPC)
- `~/.claude/skills/azure-resource-discovery/SKILL.md` — Azure resource dependency tracing
- `~/.claude/skills/terraform-patterns/SKILL.md` — Terraform infrastructure as code
- `~/.claude/skills/kubernetes-patterns/SKILL.md` — Kubernetes deployment and cluster management
- `~/.claude/skills/docker-patterns/SKILL.md` — Containerization best practices
- `~/.claude/skills/observability-patterns/SKILL.md` — Metrics, logs, traces (Prometheus, Grafana)
- `~/.claude/skills/database-migration-patterns/SKILL.md` — Database schema migrations
- `~/.claude/skills/n8n-patterns/SKILL.md` — Workflow automation with n8n
- `~/.claude/skills/qdrant-patterns/SKILL.md` — Vector database storage and semantic retrieval

## Network Policy — Read-Only HTTP Access

This container blocks **arbitrary HTTP write operations** while allowing git and GitHub workflows.

**Allowed:**
- `WebFetch` — GET-only, safe for reading APIs and web pages
- `WebSearch` — search queries
- `mcp__brave-search__*` — web search
- `mcp__github__*` — all GitHub MCP tools (read and write)
- `mcp__qdrant__*` — vector DB operations
- `git push` / `git pull` — full git remote access
- `gh` CLI — all commands (create PRs, issues, etc.)
- `curl` / `wget` GET requests (no `-d`, `--data`, `-X POST`)

**Blocked (hard deny, no override):**
- `curl -X POST/PUT/DELETE/PATCH` or `curl -d/--data/--form`
- `wget --post-data/--post-file`
- `httpie POST/PUT/DELETE/PATCH`
- `requests.post()` / `httpx.post()` and similar Python HTTP write calls
- `mcp__playwright__click`, `fill`, `type`, `submit`, and other page interaction tools

Do NOT attempt to bypass these restrictions. If a task requires raw HTTP writes (outside of git/GitHub), inform the user that this container blocks arbitrary HTTP write operations.

### Development
- `~/.claude/skills/agent-builder/SKILL.md` — Build specialized sub-agents
- `~/.claude/skills/workflow-builder/SKILL.md` — Multi-step automation workflows
- `~/.claude/skills/router-builder/SKILL.md` — Intent routers for task distribution
- `~/.claude/skills/mcp-server-builder/SKILL.md` — Build MCP servers
- `~/.claude/skills/workspace-builder/SKILL.md` — Development workspace setup
- `~/.claude/skills/project-onboarding/SKILL.md` — Project onboarding and configuration
- `~/.claude/skills/task-decomposition/SKILL.md` — Break down complex tasks
- `~/.claude/skills/analysis-patterns/SKILL.md` — Data analysis and troubleshooting
- `~/.claude/skills/rag-builder/SKILL.md` — RAG systems with vector databases
- `~/.claude/skills/rag-wrapper/SKILL.md` — Wrap agents with RAG context
