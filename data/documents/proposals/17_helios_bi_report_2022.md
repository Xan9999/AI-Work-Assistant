# Projektno poročilo — Helios BI implementacija
## Projekt: HELIOS-2022-BI | ZASTARELO POROČILO

**Datum poročila:** 2022-09-20  
**OPOZORILO: To poročilo je iz leta 2022 in vsebuje zastarele informacije glede licenc in tehnologije.**

---

## 1. Projektni povzetek

Nexus Consulting je za Helios d.o.o. implementiral Business Intelligence rešitev na osnovi Tableau Server in Microsoft SQL Server 2019 DWH.

Projekt je bil uspešno zaključen in prevzet septembra 2022.

Vrednost projekta: 68.000 € (brez DDV).

---

## 2. Implementirana rešitev

### Podatkovno skladišče

Zvezdna shema z naslednjimi tabelami:

| Tabela | Tip | Število zapisov (ob go-live) |
|--------|-----|------------------------------|
| fact_prodaja | Fact | 2.840.000 |
| fact_nabava | Fact | 890.000 |
| fact_zalog | Fact | 450.000 |
| fact_financni_tok | Fact | 1.200.000 |
| dim_stranka | Dimenzija | 12.400 |
| dim_artikel | Dimenzija | 8.500 |
| dim_cas | Dimenzija | 3.650 |
| dim_lokacija | Dimenzija | 48 |

### ETL Pipelines (SSIS)

| Pipeline | Vir | Frekvenca | Trajanje |
|---------|-----|-----------|---------|
| ERP_extract | SAP B1 | Nočno | ~45 min |
| CRM_extract | Salesforce | 4x dnevno | ~8 min |
| Excel_import | SharePoint | Ročno | ~2 min |
| Web_analytics | Google Analytics API | Dnevno | ~12 min |
| Manual_data | Excel upload | Ad-hoc | — |

### Dashboardi

12 Tableau dashboardov:
1. Executive summary (CEO)
2. Prodajni KPI (direktor prodaje)
3. Zalog analiza (logistika)
4. Finančni pregled (CFO)
5–12. Operativni dashboardi po oddelkih

---

## 3. Tehnična konfiguracija

**Tableau Server 2022.1** — nameščen on-premise na Windows Server 2019.

Licenca: Tableau Creator × 5, Tableau Explorer × 10, Tableau Viewer × 25.

*OPOMBA (zastarelo): Tableau Server 2022.1 bo dosegel konec življenjske dobe. Naročnik mora pred junijem 2024 nadgraditi na novejšo verzijo ali migrirati na Tableau Cloud.*

**SQL Server 2019** — Standard Edition. 
*OPOMBA (zastarelo): SQL Server 2019 Standard ima omejitev 24 jeder in 128 GB RAM. Ob rasti podatkov bo potrebna nadgradnja na Enterprise.*

---

## 4. Ekipa

| Ime | Vloga |
|-----|-------|
| Tomaž Kržič | PM + Arhitekt |
| Sara Petric | Data engineer (ETL, DWH modeliranje) |
| Rok Bajt | BA (zahteve, KPI definicije) |

---

## 5. Priporočila za naslednje korake (2022 perspektiva)

1. V 2023 avtomatizirati Excel uvoz z direktnim API priklopom
2. Razmisliti o nadgradnji Tableau licenc na Tableau Cloud (2023/2024)
3. Vzpostaviti monitoring ETL pipeline z alarmiranjem
4. Razširiti DWH z HR podatki (plače, prisotnost)

*Vsa priporočila so bila dana v kontekstu leta 2022. Nekatera so morda že izvedena ali zastarela.*
