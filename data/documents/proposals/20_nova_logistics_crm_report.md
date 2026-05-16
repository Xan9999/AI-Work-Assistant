# Projektno poročilo — Nova Logistics CRM (Salesforce)
## Projekt: NOVA-2023-CRM | Mid-project poročilo

**Datum:** 2023-07-15  
**Status projekta:** V teku (faza 3 od 4)

---

## 1. Status

Projekt je v tretji fazi (podatkovna migracija). Splošna ocena: **zelena** (v okviru plana in proračuna).

| Faza | Status | Opomba |
|------|--------|--------|
| 1 — Konfiguracija SF | ✓ Zaključeno | 1 teden pred planom |
| 2 — SAP B1 integracija | ✓ Zaključeno | V roku |
| 3 — Migracija podatkov | 🔄 V teku | 70% dokončano |
| 4 — UAT + usposabljanje | ⏳ Planiran avg 2023 | — |

---

## 2. Faza 2 — SAP B1 integracija (zaključena)

Integracija SAP Business One (verzija 10.0) s Salesforce Sales Cloud je zaključena.

Implementirani tokovi:
- SAP B1 Account → Salesforce Account (sinhronizacija strank)
- Salesforce Opportunity Won → SAP B1 Sales Order
- SAP B1 Invoice → Salesforce (plačilni status)

Tehnična rešitev: Python middleware (FastAPI), REST API SAP B1 Service Layer, Salesforce Connected App (OAuth 2.0).

Janez Novak opomba: "SAP B1 Service Layer je bil boljši za integracijo kot DI API — dokumentacija je bila slaba, ampak API sam soliden."

---

## 3. Faza 3 — Migracija podatkov (v teku)

### Viri podatkov

| Vir | Format | Zapisov | Status |
|-----|--------|---------|--------|
| Obstoječi CRM (Access 2010) | MDB | 4.200 strank | ✓ Migrirano |
| Excel tabele (prodajniki) | XLSX, 22 datotek | ~1.800 kontaktov | 🔄 70% |
| SAP B1 partnerji | API | 6.800 računov | ⏳ Planiran |

**Problem**: Excel datoteke prodajnikov imajo slabo kakovost podatkov — podvojene stranke, različni formati telefonskih številk, brez mail v 30% primerov. Rok Bajt dela na normalizaciji.

---

## 4. Tveganja

| Tveganje | Status |
|---------|--------|
| SAP B1 verzija 9.3 (Tanja Sušnik omenila na kick-offu) | RAZREŠENO — verzija je bila 10.0 |
| Kakovost Excel podatkov | AKTIVNO — podaljšuje migracijo za ~1 teden |
| Sprememba upravljanja (22 prodajnikov) | MITIGIRANO — Rok Bajt pripravlja trening material |

---

## 5. Finančni status

| Faza | Vrednost | Status |
|------|---------|--------|
| F1 — Konfiguracija | 18.500 € | Fakturirano |
| F2 — Integracija | 28.000 € | Fakturirano |
| F3 — Migracija | 14.000 € | V teku |
| F4 — UAT + training | 18.000 € | Čaka |
| **Skupaj** | **78.500 €** | |

---

## 6. Plan do zaključka

- 2023-07-31: Zaključek migracije (vse Excel datoteke + SAP B1)
- 2023-08-01–2023-08-25: UAT z 22 prodajniki
- 2023-08-28–2023-09-08: Usposabljanje
- **Go-live: 2023-09-11** (rahla zamuda od originalnega junij 2023 — vzrok Excel podatkovna kakovost)
