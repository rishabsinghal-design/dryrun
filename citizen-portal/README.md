# Citizen Service Portal

A unified, accessible web portal enabling citizens to discover, apply for, and track government services online.

## Architecture

Modular monolith with service-oriented decomposition (see HLD §1):

```
citizen-portal/
├── apps/
│   ├── citizen-web/        # Next.js 14 SSR citizen-facing portal
│   └── admin-web/          # Next.js 14 SSR admin portal
├── services/
│   ├── identity/           # Auth, registration, MFA, SAML SSO
│   ├── catalogue/          # Service catalogue CRUD + search
│   ├── application/        # Forms, drafts, submissions, status lifecycle
│   ├── document/           # Upload, ClamAV scan, object storage
│   ├── notification/       # Async email/SMS dispatch
│   ├── audit/              # Append-only audit log
│   ├── reporting/          # Aggregated metrics + Redis cache
│   └── dept-adapter/       # Departmental case-mgmt REST adapters
├── packages/
│   └── shared/             # Shared types, error codes, utilities
├── db/
│   └── migrations/         # Flyway versioned SQL migrations
├── infra/                  # Terraform + Helm (cloud-agnostic stubs)
└── docker-compose.yml      # Local development stack
```

## Quick Start

```bash
cp .env.example .env
docker compose up -d
# Citizen portal: http://localhost:3000
# Admin portal:   http://localhost:3001
# API Gateway:    http://localhost:8080
```

## Tech Stack

| Layer | Technology |
|---|---|
| Citizen & Admin UI | Next.js 14, TypeScript, Tailwind CSS |
| Backend services | Node.js 20, Express 4, TypeScript |
| Database | PostgreSQL 15 |
| Cache / Sessions | Redis 7 |
| Message queue | RabbitMQ 3.12 |
| Object storage | S3-compatible (MinIO for local dev) |
| Virus scanning | ClamAV (sidecar) |
| Migrations | Flyway |
| CI/CD | GitHub Actions |
