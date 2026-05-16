# Zapisnik zaključnega sestanka — Projekt Helios BI

**Datum:** 2022-09-14  
**Projekt:** HELIOS-2022-BI  
**Status:** ZAKLJUČEN

## Prisotni

- Tomaž Kržič (PM + arhitekt, Nexus)
- Sara Petric (data engineer, Nexus)
- Rok Bajt (BA, Nexus)
- Igor Babič (direktor, Helios d.o.o.)
- Katja Žnidar (analitičarka, Helios d.o.o.)

## Povzetek projekta

Implementacija Tableau Server in podatkovnega skladišča (DWH) na osnovi Microsoft SQL Server 2019.

Trajanje: april 2022 – september 2022 (6 mesecev, planirano 5).

Zamuda 1 mesec — vzrok: naročnik je spremenil zahteve glede KPI metrik v 3. fazi.

## Izvedeno

- DWH z zvezdno shemo: 8 fact tabel, 24 dimenzij
- ETL pipelines (SSIS) za 5 virov podatkov (ERP, CRM, Excel uvozi, spletna analitika, ročni vnosi)
- 12 Tableau dashboardov
- Usposabljanje 15 uporabnikov

## Ugotovitve

**Pozitivno:**
- Sara Petric: ETL pipelines so zanesljivi — 30 dnevni monitoring po go-live brez napake
- Naročnik zadovoljen z Tableau — Igor Babič: "Prvič vidimo podatke v realnem času"

**Negativno:**
- SQL Server 2019 licenca je bila dražja, kot je naročnik pričakoval — prihodnjič bolj natančna predkalkulacija
- Ročni Excel uvozi so problematični — priporočeno, da naročnik v letu 2023 nadgradi na avtomatski API priklop

## Zaključni status

Projekt je bil uradno prevzet. Naročnik podpisal acceptance report 2022-09-10.

Znesek projekta: 68.000 € (brez DDV).

## Orodja in tehnologije

- Tableau Server 2022.1 (on-premise)
- Microsoft SQL Server 2019
- SSIS (SQL Server Integration Services)
- Power Query za transformacije

*Opomba: Tableau Server 2022.1 licenca poteče 2024-06-30 — naročnik mora podaljšati ali nadgraditi.*
