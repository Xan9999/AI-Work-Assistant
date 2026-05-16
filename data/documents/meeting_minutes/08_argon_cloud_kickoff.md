# Zapisnik — Kick-off: Argon Cloud Migration (Azure)

**Datum:** 2024-02-19  
**Lokacija:** Zoom  
**Projekt:** ARGON-2024-AZURE  

## Prisotni

- Luka Zupan (vodja tehničnega dela, Nexus)
- Tomaž Kržič (arhitekt, Nexus)
- Ana Kovač (PM, Nexus)
- Dejan Pregelj (IT direktor, Argon d.o.o.)
- Vesna Hočevar (sistemska administratorka, Argon d.o.o.)

## Obseg projekta

Argon d.o.o. migrira celotno infrastrukturo iz lastnega podatkovnega centra v Microsoft Azure (region West Europe — Amsterdam). Razlog: pogodba za datacenter poteče junij 2024, podaljšanje predrago.

### Inventar za migracijo

| Sistem | Tehnologija | Kritičnost | Ciljna platforma |
|--------|------------|------------|-----------------|
| ERP (Navision) | Windows Server 2019 | Visoka | Azure VM (lift & shift) |
| Spletna stran | Apache/PHP | Nizka | Azure App Service |
| Email server | Exchange 2016 | Visoka | Microsoft 365 (migracija) |
| File server | Windows Server, SMB | Srednja | Azure Files |
| Backup sistem | Veeam | — | Azure Backup |
| Baza podatkov | SQL Server 2019 | Visoka | Azure SQL Managed Instance |

Skupaj ~18 TB podatkov.

## Ključne omejitve

1. **Trdi rok**: Migracija mora biti zaključena do **2024-05-31** (datacenter pogodba poteče)
2. Argon d.o.o. nima Azure izkušenj — potrebno usposabljanje internega IT
3. Exchange → M365 migracija: Vesna Hočevar je opravila uvodni tečaj, bo vodila ta del

## Arhitektura

Tomaž Kržič predlaga:
- **Lift & shift** za ERP in SQL Server (ni časa za refaktoring pred rokom)
- **PaaS** za spletno stran (App Service — enostavno, stroškovno učinkovito)
- **SaaS** za email (M365 — Microsoft direktna migracija)

Luka Zupan: Azure DevOps za pipeline, Terraform za infrastrukturo.

## Tveganja

- 18 TB podatkov — migracija bo trajala 3–5 dni ob dovolj široki pasovni širini
- Exchange → M365 je kompleksno, priporočamo Microsoft FastTrack
- Datacenter rok je absoluten — ni manevrskega prostora

## Plan

| Faza | Opis | Rok |
|------|------|-----|
| 1 | Postavitev Azure landing zone | 2024-03-08 |
| 2 | Migracija nekritičnih sistemov | 2024-03-31 |
| 3 | M365 email migracija | 2024-04-15 |
| 4 | Migracija ERP in SQL | 2024-05-10 |
| 5 | Testiranje in cut-over | 2024-05-25 |

**Go-live: 2024-05-31 (trdi rok)**
