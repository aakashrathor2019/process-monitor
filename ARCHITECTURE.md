# Architecture Overview

## Goals
- Collect running processes with parent–child relationships, CPU, memory, hostname, timestamp.
- Store snapshots via Django REST backend.
- Display latest snapshot per host in an interactive, collapsible tree.

## Components
- **Agent** → Python/EXE using `psutil`, sends JSON via REST
- **Backend** → Django + DRF + SQLite, validates API key, stores Machine/Snapshot/Process
- **Frontend** → HTML + JS, shows interactive process tree

## Flow
Agent → `/api/v1/ingest`  
→ Backend validates + stores → SQLite  
→ Frontend calls `/api/v1/hosts` and `/api/v1/snapshots/latest`  
→ Renders process tree with search/expand/auto-refresh

## Data Model
- **Machine**
  - hostname (unique), api_key, last_seen
- **Snapshot**
  - machine (FK), collected_at, created_at
- **Process**
  - snapshot (FK), pid, ppid, name, cpu_percent, mem_rss, mem_vms

## Design Choices
- Bulk insert processes per snapshot
- Simple API key per host
- SQLite for demo (swap to Postgres in prod)