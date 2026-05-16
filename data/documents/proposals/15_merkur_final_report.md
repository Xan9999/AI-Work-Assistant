# Zaključno projektno poročilo — Merkur IT Modernizacija
## Projekt: MERKUR-2023-MOD

**Datum poročila:** 2023-11-15  
**Status projekta:** ZAKLJUČEN  
**Acceptance report podpisan:** 2023-10-31

---

## 1. Povzetek projekta

Nexus Consulting je za Merkur IT d.o.o. izvedel modernizacijo spletne platforme — prehod z monolitne PHP 7.2 aplikacije na moderno mikrostoritveno arhitekturo v PHP 8.2 z React frontendom.

| | Planirano | Dejansko |
|---|---|---|
| Trajanje | 7 mesecev | 7,5 meseca |
| Vrednost pogodbe | 94.000 € | 94.000 € (brez sprememb) |
| Go-live | 2023-09-30 | 2023-10-14 |
| Zadovoljstvo naročnika | — | 8.5/10 |

---

## 2. Izvedene spremembe

### 2.1 Backend

- Migracija PHP 7.2 → PHP 8.2 (14 breaking changes razrešenih)
- Refaktoring monolita na 6 mikrostoritev:
  - auth-service
  - product-service
  - order-service
  - notification-service
  - search-service
  - admin-service
- Prehod MySQL 5.7 → PostgreSQL 15 (performance gain ~3x na kompleksnih poizvedbah)
- Redis za caching in session management
- RabbitMQ za asinhrono komunikacijo med storitvami

### 2.2 Frontend

- Nov React 18 frontend (zamenjava za jQuery/Bootstrap 3 spaghetti)
- TypeScript (stroga tipizacija)
- Vite za bundling

### 2.3 Infrastruktura

- Docker Compose za development
- Kubernetes (k3s) za produkcijo na lastnih strežnikih Merkur IT
- CI/CD: GitHub Actions → Argo CD
- Monitoring: Prometheus + Grafana

### 2.4 Podatkovna migracija

- 4,2 GB podatkov migrirano iz MySQL v PostgreSQL
- 0 izgubljenih zapisov
- Validacijske skripte Sara Petric (432 kontrolnih točk)

---

## 3. Izzivi in rešitve

| Izziv | Rešitev |
|-------|---------|
| PHP 8.2 breaking changes | Sistematičen pregled vsake funkcije z PHPStan level 8 |
| MySQL → PostgreSQL razlike (DATE, NULL handling) | Obsežni migracijski testi, ročna validacija |
| Docker Compose v produkciji (ni skalabilno) | Preklop na k3s Kubernetes |
| Počasna UAT (naročnik ni imel testne ekipe) | Nexus zagotovil 2 testni scenariji na dan, naročnik odobril |

---

## 4. Naučene lekcije (za Nexus interno)

1. **Zahtevaj testno okolje pred začetkom**: 2 tedna zastoja ker Merkur IT ni imel testnih strežnikov.
2. **PHP verzijska migracija je podcenjena**: 14 breaking changes — naslednjič plan 1 teden samo za analizo breaking changes.
3. **k3s je odlična rešitev** za manjše naročnike, ki hočejo Kubernetes brez stroška managed platforme.
4. **PostgreSQL vs MySQL**: Pri vsakem novem projektu privzeto priporoči PostgreSQL.

---

## 5. Ekipa projekta

| Ime | Vloga | Prispevek |
|-----|-------|-----------|
| Ana Kovač | PM | Projektno vodenje, komunikacija z naročnikom |
| Janez Novak | Lead developer | PHP 8.2 migracija, mikrostoritve |
| Nina Vidmar | Frontend developer | React 18, TypeScript |
| Sara Petric | Data engineer | PostgreSQL migracija, validacija |
| Rok Bajt | BA | Zahteve, UAT koordinacija |

---

## 6. Post-projektna podpora

Merkur IT ima 3-mesečni support retainer (november 2023 – januar 2024), vrednost: 4.500 €/mesec.

Po zaključku retainerja je priporočena vzpostavitev internega DevOps inženirja pri naročniku.
