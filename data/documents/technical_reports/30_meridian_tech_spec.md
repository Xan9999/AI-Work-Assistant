# Tehnična specifikacija — Meridian Web Platform
## Projekt: MERIDIAN-2024-WEB | Dokument: TECH-001

**Verzija:** 1.2  
**Datum:** 2024-04-10  
**Avtor:** Tomaž Kržič, Janez Novak

---

## 1. Pregled

Meridian Web Platform je Django/React spletna aplikacija za upravljanje digitalnih naročnin in distribucijo vsebin.

---

## 2. Backend arhitektura

### 2.1 Stack

| Komponenta | Tehnologija | Verzija |
|-----------|------------|---------|
| Programski jezik | Python | 3.12 |
| Web framework | Django | 5.0 |
| REST API | Django REST Framework | 3.15 |
| Avtentikacija | SimpleJWT | 5.3 |
| Async tasking | Celery | 5.4 |
| Message broker | Redis | 7.2 |
| Podatkovna baza | PostgreSQL | 16 |
| PDF generiranje | WeasyPrint | 61.0 |
| Email | SendGrid API | — |
| Plačila | Stripe API v3 | — |

### 2.2 Django aplikacije

```
meridian/
  ├── accounts/      # Uporabniki, vloge, JWT
  ├── subscriptions/ # Naročnine, plan management
  ├── content/       # CMS, kategorije, objave
  ├── payments/      # Stripe integracija
  ├── reports/       # PDF generiranje (async)
  ├── api/           # DRF router, verzioniranje
  └── core/          # Skupne utilities
```

### 2.3 Celery tasks

| Task | Queue | Prioriteta | Timeout |
|------|-------|-----------|---------|
| generate_pdf_report | pdf | Visoka | 120s |
| send_welcome_email | email | Nizka | 30s |
| send_invoice_email | email | Visoka | 30s |
| expire_subscriptions | scheduled | — | 60s |
| sync_stripe_invoices | stripe | Nizka | 180s |

---

## 3. Frontend arhitektura

### 3.1 Stack

| Komponenta | Tehnologija | Verzija |
|-----------|------------|---------|
| Framework | React | 18.3 |
| Jezik | TypeScript | 5.4 |
| Build tool | Vite | 5.2 |
| CSS framework | Tailwind CSS | 3.4 |
| State management | React Query (TanStack) | 5.0 |
| Routing | React Router | 6.23 |
| Form handling | React Hook Form | 7.51 |
| HTTP client | Axios | 1.7 |

---

## 4. AWS infrastruktura

### 4.1 Compute

| Komponenta | Storitev | Konfiguracija |
|-----------|---------|--------------|
| Django API | ECS Fargate | 1 vCPU, 2 GB, 2 taski |
| Celery workers | ECS Fargate | 0.5 vCPU, 1 GB, 2 taski |
| React frontend | S3 + CloudFront | — |

### 4.2 Podatkovna baza

| Storitev | Konfiguracija | Multi-AZ |
|---------|--------------|---------|
| RDS PostgreSQL 16 | db.t3.medium | Da |
| ElastiCache Redis 7 | cache.t3.micro | Ne (dev/staging) / Da (prod) |

### 4.3 Ostala infrastruktura

| Storitev | Namen |
|---------|-------|
| S3 | Mediji (slike, PDF-ji) |
| CloudFront | CDN za S3 medije in React app |
| SES | Transakcijski emaili |
| ACM | SSL certifikat (*.meridian.si) |
| Route 53 | DNS |

---

## 5. Varnost

| Aspekt | Implementacija |
|--------|---------------|
| Avtentikacija | JWT (access 15 min, refresh 7 dni) |
| CORS | Samo meridian.si in api.meridian.si |
| Rate limiting | 100 req/min per user (DRF throttle) |
| SQL injection | Django ORM (parameterized) |
| XSS | Django CSRF, React escaping |
| Plačilni podatki | Stripe elements (ne shranjujemo kartic) |
| GDPR | Brisanje računa izbriše osebne podatke v 30 dneh |

---

## 6. API verzioniranje

API je verzioniran prek URL prefixov:
- `/api/v1/` — aktualna verzija (v razvoju)
- `/api/v2/` — planirana za post-MVP (večjezičnost)

Mobilna aplikacija (zunanji razvijalci) bo konsumirala `/api/v1/`.

---

## 7. Performance cilje

| Metrika | Cilj |
|--------|------|
| API response time (P95) | < 200ms |
| PDF generiranje | < 10s (async) |
| Stran load time (LCP) | < 2.5s |
| Uptime SLA | 99.9% |
| Concurrent users | 500 (load test cilj) |
