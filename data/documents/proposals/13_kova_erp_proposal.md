# Projektna ponudba — Implementacija SAP S/4HANA
## Nexus Consulting d.o.o. → Kova d.o.o.

**Datum ponudbe:** 2023-11-28  
**Veljavnost ponudbe:** do 2024-01-31  
**Referenčna številka:** NCX-2023-KOVA-001  
**Verzija:** 1.2

---

## 1. Povzetek

Nexus Consulting d.o.o. predlaga implementacijo sistema SAP S/4HANA 2023 za Kova d.o.o. kot zamenjavo za obstoječi Microsoft Dynamics NAV 2016. Projekt bo trajal 9 mesecev in bo izvedeni v petih fazah.

Nexus Consulting ima bogate izkušnje z implementacijami SAP — v zadnjih 5 letih smo uspešno implementirali SAP pri 4 naročnikih v regiji. Naša SAP certificirana ekipa vključuje Majo Horvat (SAP FI/CO), ki ima več kot 8 let izkušenj z SAP implementacijami.

---

## 2. Obseg projekta

### 2.1 Vključeni moduli SAP S/4HANA

| Modul | Opis | Obseg konfiguracije |
|-------|------|---------------------|
| FI — Finance | Glavna knjiga, terjatve, obveznosti | Polna implementacija |
| CO — Kontroling | Stroškovna mesta, interni nalogi | Osnovna konfiguracija |
| MM — Material Management | Nabava, zalog | Polna implementacija |
| SD — Sales & Distribution | Prodajni nalogi, dostava, fakturiranje | Polna implementacija |
| AA — Asset Accounting | Osnovna sredstva, amortizacija | Polna implementacija |
| PM — Plant Maintenance | Vzdrževanje opreme | Ni v obsegu |
| HR — Human Resources | Kadri, obračun plač | Ni v obsegu |

### 2.2 Integracije

- **Magento 2 (e-commerce)**: Sinhronizacija naročil, artiklov in zalog med Magento in SAP SD/MM. Implementirano prek custom Python middleware (alternativa SAP Integration Suite).
- **Manhattan Associates WMS**: Ohranjanje obstoječega WMS sistema, integracija prek SAP standardnega vmesnika IDoc/BAPI.
- **Banka (SEPA)**: Avtomatski uvoz bančnih izpiskov prek SAP Multi-Bank Connectivity.

### 2.3 Podatkovna migracija

Migracija podatkov iz Microsoft Dynamics NAV 2016:
- Kontni plan in saldi (zadnjih 5 let)
- Partnerji (stranke in dobavitelji, ~1.200 zapisov)
- Artikli in cenike (~8.500 artiklov)
- Osnovna sredstva in amortizacijski plani
- Odprti dokumenti (naročila, računi)

Orodje: SAP LTMC (Legacy Transfer and Migration Cockpit).

---

## 3. Projektna ekipa Nexus

| Ime | Vloga | % angažiranosti |
|-----|-------|-----------------|
| Ana Kovač | Vodja projekta | 50% |
| Tomaž Kržič | Rešitveni arhitekt | 30% |
| Maja Horvat | SAP specialist (FI/CO/MM/SD) | 100% |
| Janez Novak | Razvijalec (integracije, ABAP) | 60% |
| Rok Bajt | Poslovni analitik | 40% |

---

## 4. Časovni plan

| Faza | Opis | Trajanje | Predvideni konec |
|------|------|---------|-----------------|
| 1 | Blueprint in as-is analiza | 6 tednov | 2024-03-01 |
| 2 | Realizacija (konfiguracija + razvoj) | 16 tednov | 2024-06-30 |
| 3 | Testiranje (integracijsko + UAT) | 8 tednov | 2024-08-31 |
| 4 | Go-live priprava in cut-over | 4 tedne | 2024-09-30 |
| 5 | Go-live in hiper-care (4 tedne) | 4 tedne | 2024-10-31 |

**Predvideni go-live: 1. oktober 2024**

---

## 5. Finančna ponudba

### 5.1 Storitve Nexus Consulting

| Storitev | Enota | Količina | Cena/enoto | Skupaj |
|---------|-------|---------|------------|--------|
| Projektno vodenje | uro | 320 | 110 € | 35.200 € |
| SAP konfiguracija (Maja Horvat) | uro | 640 | 130 € | 83.200 € |
| Razvoj integracij (Janez Novak) | uro | 380 | 115 € | 43.700 € |
| Poslovna analiza | uro | 240 | 100 € | 24.000 € |
| Arhitektura | uro | 180 | 120 € | 21.600 € |
| Izobraževanje uporabnikov | dan | 8 | 1.200 € | 9.600 € |
| **Storitve skupaj** | | | | **217.300 €** |

### 5.2 Licence in infrastruktura (informativno — Kova nabavi direktno)

| Postavka | Ocenjena cena |
|---------|--------------|
| SAP S/4HANA licence (named users, 25) | ~85.000 € |
| SAP S/4HANA Annual Maintenance (22%) | ~18.700 €/leto |
| Strežniška oprema (HPE ProLiant) | ~28.000 € |

*Navedene cene so informativne — Kova d.o.o. se pogaja direktno z SAP in HPE.*

### 5.3 Skupna vrednost storitev Nexus

**Vrednost pogodbe: 217.300 € brez DDV**

Plačilni pogoji:
- 25% ob podpisu pogodbe (54.325 €)
- 25% ob zaključku Blueprint faze
- 25% ob zaključku UAT
- 25% ob go-live

---

## 6. Pogoji in izključitve

- Ponudba ne vključuje SAP PM in HR modulov
- Spremembe obsega zahtevajo pisno spremembo pogodbe
- Naročnik zagotovi dostop do testnega SAP sistema v 2 tednih od podpisa
- Nexus ni odgovoren za zamude, ki jih povzroči naročnik (hardver, licence, dostop)
- Ponudba veljavna do 31. januarja 2024

---

## 7. Reference

- **Merkur IT** (2023): Sistemska modernizacija, uspešno zaključeno
- **Helios d.o.o.** (2022): BI implementacija, uspešno zaključeno
- **Nova Logistics** (2023): Salesforce CRM implementacija

---

*Nexus Consulting d.o.o., Dunajska 22, 1000 Ljubljana*  
*Kontakt: Ana Kovač, ana.kovac@nexus-consulting.si, +386 41 123 456*
