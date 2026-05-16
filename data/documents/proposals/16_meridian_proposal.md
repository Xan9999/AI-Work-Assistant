# Projektna ponudba — Spletna platforma
## Nexus Consulting d.o.o. → Meridian d.o.o.

**Datum:** 2024-01-22  
**Referenčna številka:** NCX-2024-MERIDIAN-001  

---

## 1. Povzetek

Meridian d.o.o. potrebuje novo spletno platformo za upravljanje naročnin in distribucijo digitalnih vsebin. Obstoječa platforma (Joomla 3, PHP 5.6) je zastarela in ne podpira novih poslovnih modelov.

**Predlagana rešitev**: Django REST Framework (Python) backend + React 18 frontend, oblak AWS.

**Vrednost pogodbe: 68.000 € brez DDV. Trajanje: 6 mesecev.**

---

## 2. Funkcionalne zahteve

### Mora imeti (MVP)
- Sistem za upravljanje naročnin (mesečne, letne)
- Integracija Stripe plačil
- Upravljanje vsebine (CMS za uredništvo)
- Sistem vlog (bralec, naročnik, urednik, admin)
- PDF generiranje poročil
- REST API za mobilno aplikacijo (iOS + Android, razvijata zunanji razvijalci)

### Lepo bi imelo (post-MVP)
- Napredne analitike in dashboardi
- A/B testiranje vsebine
- Večjezičnost (SL + EN)

---

## 3. Tehnična arhitektura

### Backend
- Python 3.12, Django 5.0, Django REST Framework
- PostgreSQL 16
- Celery + Redis za asinhrono procesiranje (PDF, emaili)
- JWT autentikacija

### Frontend
- React 18, TypeScript
- Tailwind CSS
- React Query za state management

### Infrastruktura (AWS)
- ECS Fargate za Django in Celery workers
- RDS PostgreSQL (db.t3.medium)
- S3 za statične datoteke in medije
- CloudFront CDN
- SES za transakcijske emaile

---

## 4. Ekipa in časovni plan

| Faza | Opis | Trajanje |
|------|------|---------|
| 1 | Arhitektura, setup, auth | 3 tedne |
| 2 | Core funkcionalnosti (naročnine, Stripe) | 6 tednov |
| 3 | CMS modul | 4 tedne |
| 4 | API za mobilno | 4 tedne |
| 5 | PDF, analitike | 3 tedne |
| 6 | QA, load test, go-live | 4 tedne |

**Skupaj: 24 tednov (~6 mesecev). Predvideni go-live: september 2024.**

### Ekipa

| Ime | Vloga |
|-----|-------|
| Tomaž Kržič | Arhitekt + PM |
| Janez Novak | Backend developer |
| Nina Vidmar | Frontend developer |

---

## 5. Finančna ponudba

| Storitev | Ure | Cena/uro | Skupaj |
|---------|-----|---------|-------|
| Arhitektura + PM (Tomaž) | 200 | 120 € | 24.000 € |
| Backend razvoj (Janez) | 280 | 115 € | 32.200 € |
| Frontend razvoj (Nina) | 100 | 100 € | 10.000 € |
| QA in testiranje | 20 | 90 € | 1.800 € |
| **Skupaj** | | | **68.000 €** |

Plačilni pogoji: 30% ob podpisu, 40% ob zaključku faze 4, 30% ob go-live.
