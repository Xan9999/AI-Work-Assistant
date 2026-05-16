# Zapisnik tedenskega sestanka — Atlas cloud migracija

**Datum:** 2024-03-12  
**Format:** Hibridno (Zoom + pisarna)  
**Projekt:** Atlas Cloud Migration  
**Koda projekta:** ATLAS-2023-CLOUD  

## Prisotni

- Ana Kovač (PM, Nexus) — on-site
- Luka Zupan (DevOps, Nexus) — on-site
- Janez Novak (razvijalec, Nexus) — remote
- Mitja Ferlan (IT manager, Atlas d.o.o.) — on-site
- Urška Brence (sistemska administratorka, Atlas d.o.o.) — remote

## Status posameznih komponent

### Infrastruktura (Luka Zupan)

VPC in subnet struktura je postavljena v eu-central-1 (Frankfurt). Terraform koda je v repozitoriju, CI/CD pipeline za infrastrukturo deluje.

Izvedeni:
- 3x EC2 t3.large za aplikacijski sloj
- RDS PostgreSQL 15.2 (Multi-AZ)
- S3 bucketi za statične datoteke in backupe
- CloudFront distribucija za CDN

V teku:
- Konfiguracija WAF pravil — 60% dokončano
- VPN connection med on-premise in AWS VPC — čaka na Urška stran (firewall pravila)

### Migracija aplikacij (Janez Novak)

Containerizacija 3 od 7 servisov je dokončana. Preostali 4 servisi imajo legacy odvisnosti (stari .NET Framework 4.5), ki zahtevajo refaktoring ali Windows containers.

Janez predlaga: 2 servisa migrirati na .NET 8, 2 pa pustiti kot Windows containers začasno.

Mitja Ferlan potrdi, da je to sprejemljivo za začetno fazo.

### Podatkovna baza (skupaj)

Testna migracija PostgreSQL izvedena v testnem okolju — čas migracije: 4h 23min za 890 GB podatkov. V produkciji bo migracija izvedena med vikendom z downtime oknom 6–8 ur.

## Tveganja in blokade

1. **WAF pravila** — Urška potrebuje odobritev od IT varnostnega oddelka Atlas d.o.o. za odprtje portov. Rok: 2024-03-15.
2. **Windows containers** — Luka opozori, da EKS za Windows nods stane ~40% več. Alternativa: EC2 brez Kubernetes za ta 2 servisa.
3. **SSL certifikati** — obstoječi certifikati od DigiCert potečejo 2024-05-01. Prehod na AWS Certificate Manager planiran.

## Časovni plan — update

Originalni plan predvideval go-live **Q2 2024 (junij 2024)**. Glede na zamudo pri containerizaciji in WAF odobritvi, Ana Kovač predlaga revizijo na **Q3 2024 (september 2024)**.

Mitja Ferlan se strinja — bo obvestil management Atlas d.o.o.

## Sklepi

| Akcija | Odgovorna oseba | Rok |
|--------|----------------|-----|
| Odprtje firewall portov za VPN | Urška Brence | 2024-03-15 |
| Refaktoring plan za .NET servise | Janez Novak | 2024-03-19 |
| Kalkulacija stroškov Windows nodes vs EC2 | Luka Zupan | 2024-03-14 |
| Obvestilo managementu o zamudi | Mitja Ferlan | 2024-03-13 |

## Naslednji sestanek

Datum: 2024-03-19, 09:30
