# API tehnična specifikacija — DataSync Integration Engine
## Projekt: DSYNC-2024-INT | Dokument: API-SPEC-001

**Verzija:** 1.3  
**Datum:** 2024-06-15  
**Avtor:** Sara Petric, Janez Novak

---

## 1. Pregled

DataSync Integration Engine je Python (FastAPI) servis, ki posreduje podatke med Salesforce in SAP Business One v realnem času in batch načinu.

### Komponente

```
Salesforce
    ↓ Webhook / Polling
Integration Engine (FastAPI)
    ↓
Redis Streams (message queue)
    ↓
SAP B1 Service Layer (REST)
    ↓
Audit Log (PostgreSQL)
```

---

## 2. API endpointi

### 2.1 Webhook endpointi (SF → Engine)

| Endpoint | Metoda | Opis | Rate limit |
|----------|--------|------|-----------|
| `/webhooks/sf/account` | POST | Nova/posodobljena stranka iz SF | 100/min |
| `/webhooks/sf/contact` | POST | Nov/posodobljen kontakt iz SF | 100/min |
| `/webhooks/sf/opportunity` | POST | Priložnost → naročilo | 50/min |
| `/webhooks/sf/opportunity/closed` | POST | Zaključena priložnost → SAP naročilo | 50/min |
| `/health` | GET | Health check | — |
| `/metrics` | GET | Prometheus metrics | — |

### 2.2 Batch endpointi (SAP B1 → SF)

| Endpoint | Metoda | Opis | Urnik |
|----------|--------|------|-------|
| `/batch/inventory` | POST | Sinhronizacija zaloge SAP→SF | Vsake 15 min |
| `/batch/pricelist` | POST | Sinhronizacija cenika SAP→SF | Dnevno 02:00 |
| `/batch/invoice-status` | POST | Status računov SAP→SF | 4x dnevno |

---

## 3. Podatkovni modeli

### 3.1 Salesforce Account → SAP Business One Business Partner

| SF polje | SAP B1 polje | Tip | Transformacija |
|---------|-------------|-----|---------------|
| Id | U_SF_ID (UDF) | String | 1:1 |
| Name | CardName | String | 1:1 |
| BillingStreet | MailAddressRow1 | String | 1:1 |
| BillingCity | MailCity | String | 1:1 |
| BillingCountryCode | MailCountry | String | ISO 3166 → SAP koda |
| Phone | Phone1 | String | Normalizacija formata |
| AnnualRevenue | — | — | Ne sinhronizira |
| TaxId (custom) | FederalTaxID | String | 1:1 |

### 3.2 SAP B1 Item → Salesforce Product2

| SAP B1 polje | SF polje | Tip | Transformacija |
|-------------|---------|-----|---------------|
| ItemCode | ProductCode | String | 1:1 |
| ItemName | Name | String | 1:1 |
| ItemsGroupCode | Family | String | Lookup tabela |
| OnHand | Quantity_c (custom) | Decimal | Seštevek po skladiščih |
| PriceList[1].Price | UnitPrice | Decimal | EUR privzeto |
| U_SF_ID | ExternalId | String | Za upsert |

---

## 4. Error handling

### 4.1 Retry politika

| Scenarij | Retry | Backoff | Dead letter |
|---------|-------|---------|------------|
| SF API timeout | 3x | Exponential (1s, 2s, 4s) | Da |
| SAP B1 API 429 (rate limit) | 5x | Fixed 60s | Da |
| SAP B1 API 500 | 3x | Exponential | Da |
| Validacijska napaka | 0x | — | Da (z opisom) |
| Network error | 5x | Exponential | Da |

### 4.2 Dead letter queue

Neuspešni dogodki se shranijo v PostgreSQL tabelo `dlq_events`:

```sql
CREATE TABLE dlq_events (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type   VARCHAR(50) NOT NULL,
    payload      JSONB NOT NULL,
    error_msg    TEXT,
    retry_count  INT DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ,
    resolved_by  VARCHAR(100)
);
```

---

## 5. GDPR in varnost

### 5.1 Osebni podatki v toku

Tok vsebuje osebne podatke (ime, email, telefon). Ukrepi:

| Ukrep | Implementacija |
|-------|---------------|
| Šifriranje v tranzitu | TLS 1.3 za vse API klice |
| Šifriranje v mirovanju | PostgreSQL + Redis šifriranje (AES-256) |
| Minimizacija podatkov | Ne shranjujemo AnnualRevenue in podobnih poslovnih polj |
| Audit log retencija | 90 dni (po DPA pogodbi) |
| Anonimizacija v testih | Test environment nima realnih podatkov |

### 5.2 Avtentikacija

- Salesforce: OAuth 2.0 JWT Bearer Flow (ne username/password)
- SAP B1 Service Layer: Session token z 30-min življenjsko dobo, auto-refresh
- Webhook avtentikacija: HMAC-SHA256 podpis (Salesforce signing secret)

---

## 6. Monitoring

| Metrika | Alert prag | Akcija |
|--------|-----------|--------|
| Events processed/min < 10 | 5 min | PagerDuty alert Sara Petric |
| Error rate > 5% | 2 min | PagerDuty alert |
| DLQ size > 100 | Takoj | Slack #alerts |
| SAP B1 response time > 5s | 10 min | Email alert |
| Redis memory > 80% | — | CloudWatch alarm |

Incident z 2024-08-03 (Salesforce field rename) je privedel do dodajanja:
- Schema validation ob zagonu (ne samo pri spremembi kode)
- Alert na strukturo SF odgovora
