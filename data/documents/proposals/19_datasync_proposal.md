# Projektna ponudba — Platforma za integracijo podatkov
## Nexus Consulting d.o.o. → DataSync d.o.o.

**Datum:** 2024-03-18  
**Referenčna številka:** NCX-2024-DSYNC-001

---

## 1. Povzetek

DataSync d.o.o. potrebuje rešitev za integracijo podatkov med Salesforce CRM in internim ERP sistemom (SAP Business One). Cilj je avtomatizacija pretoka podatkov o strankah, naročilih in zalogah v realnem času.

**Vrednost ponudbe: 56.000 € brez DDV. Trajanje: 5 mesecev.**

---

## 2. Predlagana arhitektura

### Tok podatkov

```
Salesforce → Webhook/Polling → Nexus Integration Engine → SAP B1 API
                                       ↓
                               Redis Queue (buffer)
                                       ↓
                              PostgreSQL (audit log)
                                       ↓
                              Grafana (monitoring)
```

### Komponente

- **Nexus Integration Engine**: Python (FastAPI), Docker, Kubernetes
- **Message queue**: Redis Streams
- **Audit log**: PostgreSQL
- **Monitoring**: Grafana + Prometheus
- **Deployment**: AWS ECS Fargate

---

## 3. Integracijski tokovi

| Tok | Smer | Frekvenca | Volumen (ocena) |
|-----|------|-----------|----------------|
| Nove stranke | SF → SAP B1 | Real-time (webhook) | ~50/dan |
| Posodobitve strank | SF → SAP B1 | Real-time | ~200/dan |
| Naročila | SF → SAP B1 | Real-time | ~150/dan |
| Zaloge | SAP B1 → SF | Batch (15 min) | ~8.500 artiklov |
| Cenik | SAP B1 → SF | Batch (dnevno) | ~8.500 artiklov |
| Plačilni status | SAP B1 → SF | Batch (4x dnevno) | ~500 zapisov |

---

## 4. Ekipa in plan

| Faza | Opis | Trajanje | Vodja |
|------|------|---------|-------|
| 1 | Arhitektura, GDPR, DPA | 2 tedna | Tomaž Kržič |
| 2 | Core integration engine | 6 tednov | Sara Petric |
| 3 | SF → SAP B1 tokovi | 4 tedne | Sara Petric + Janez Novak |
| 4 | SAP B1 → SF tokovi | 3 tedne | Janez Novak |
| 5 | Monitoring, testiranje, go-live | 3 tedne | Sara Petric |

**PM:** Sara Petric

---

## 5. Predpogoji (naročnik zagotovi)

- Salesforce Enterprise licenca (brez tega API klici omejeni)
- SAP Business One verzija 10.0 ali novejša (Service Layer API)
- DPO podpis DPA pogodbe pred začetkom razvoja
- Testni Salesforce sandbox
- Testni SAP B1 environment

---

## 6. Cena

| Storitev | Ure | €/uro | Skupaj |
|---------|-----|-------|-------|
| Arhitektura (Tomaž) | 80 | 120 € | 9.600 € |
| Data engineering (Sara) | 220 | 110 € | 24.200 € |
| Backend razvoj (Janez) | 160 | 115 € | 18.400 € |
| BA + dokumentacija (Rok) | 36 | 100 € | 3.600 € |
| Skupaj | | | **55.800 €** |

*Zaokroženo na 56.000 € z vključenim manjšim varnostnim rezervatom.*
