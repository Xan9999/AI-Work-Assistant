# Zaključno poročilo — Argon Azure Cloud Migration
## Projekt: ARGON-2024-AZURE

**Datum:** 2024-06-10  
**Status:** ZAKLJUČEN  
**Acceptance report:** podpisan 2024-06-05

---

## 1. Povzetek

Nexus Consulting je uspešno migriral celotno IT infrastrukturo Argon d.o.o. iz lastnega podatkovnega centra v Microsoft Azure (West Europe – Amsterdam) v roku in okviru proračuna.

Ključno: trdi rok 2024-05-31 (datum poteka datacenter pogodbe) je bil izpolnjen.

| Metrika | Planirano | Dejansko |
|---------|-----------|---------|
| Go-live datum | 2024-05-31 | 2024-05-30 (1 dan prej!) |
| Skupni strošek Nexus storitev | 48.000 € | 51.200 € |
| Prekoračitev | — | +3.200 € (odobreno s change order) |
| Downtime pri cut-over | < 4 ure | 3 ure 20 min |

---

## 2. Migrirani sistemi

| Sistem | Iz | V | Strategija | Status |
|--------|----|----|-----------|--------|
| ERP (Navision) | On-prem WS 2019 | Azure VM (D4s v3) | Lift & shift | ✓ |
| Spletna stran | Apache/PHP | Azure App Service | Re-platform | ✓ |
| Email | Exchange 2016 | Microsoft 365 E3 | SaaS migracija | ✓ |
| File server | Windows SMB | Azure Files Premium | Lift & shift | ✓ |
| Backup | Veeam | Azure Backup | Replace | ✓ |
| SQL baza | SQL Server 2019 | Azure SQL MI GP | Managed PaaS | ✓ |

Skupaj migrirano: 18,4 TB podatkov.

---

## 3. Exchange → M365 migracija

Najtežji del projekta. Vesna Hočevar (Argon) je vodila ta del s podporo Luka Zupan.

- 47 nabiralnikov, skupaj 380 GB
- Migracija trajala 4 dni (vikend 11.–14. april)
- 2 nabiralnika z okvarjenimi PST datotekami — ročna obnovitev
- Microsoft FastTrack podpora ni bila dostopna za obseg (< 150 sedežev) — rešeno brez

---

## 4. Naučene lekcije

### Kaj je šlo dobro
- **Terraform** za infrastrukturo: popolnoma ponovljiva konfiguracija, nič ročnih klikov
- **Phased migracija**: nekritični sistemi prvi, ERP zadnji — minimizirali tveganje
- **Azure Migrate Assessment**: natančno ocenil Azure VM velikosti (±10% od dejanskih)

### Kaj bi naredili drugače
- **Exchange 2016 je bil starejši kot pričakovano** — 2 tedna več za migration planning
- **Azure Files latenca**: za nekatere nalog SMB operacije opazno počasnejše od on-prem NFS. Priporočamo Azure NetApp Files za naslednji projekt z heavy file I/O.
- **Cut-over v petek zvečer ni idealen**: čeprav je uspelo, priporoča se sobota zgodaj zjutraj (manj stresa za ekipo)

---

## 5. Ekipa

| Ime | Vloga |
|-----|-------|
| Ana Kovač | PM |
| Luka Zupan | Azure DevOps, infrastruktura |
| Tomaž Kržič | Arhitekt |
| Nina Vidmar | Podpora pri App Service migraciji |

---

## 6. Post-migracija stroški Azure (mesečno)

| Storitev | Mesečni strošek |
|---------|----------------|
| Azure VM (2x D4s v3) | 520 € |
| Azure SQL MI (General Purpose) | 890 € |
| Azure Files Premium (5 TB) | 210 € |
| App Service (P2v3) | 145 € |
| M365 E3 (47 licenc) | 1.034 € |
| Backup, monitoring, ostalo | 180 € |
| **Skupaj mesečno** | **2.979 €** |

*Opomba: M365 strošek je bil prej del ločene pogodbe z Microsoft partnerjem.*
