# Zapisnik sestanka — Kick-off: ERP integracija, Kova d.o.o.

**Datum:** 2024-01-15  
**Lokacija:** Prostori Nexus Consulting, Ljubljana  
**Projekt:** Kova ERP Integration  
**Koda projekta:** KOVA-2024-ERP  

## Prisotni

| Ime | Vloga | Organizacija |
|-----|-------|-------------|
| Ana Kovač | Vodja projekta | Nexus Consulting |
| Tomaž Kržič | Rešitveni arhitekt | Nexus Consulting |
| Maja Horvat | ERP specialist | Nexus Consulting |
| Janez Novak | Razvijalec | Nexus Consulting |
| Gregor Mlakar | IT direktor | Kova d.o.o. |
| Petra Sajovic | Vodja poslovnih procesov | Kova d.o.o. |

## Agenda

1. Predstavitev projektne ekipe
2. Pregled obsega projekta
3. Tehnična arhitektura — uvod
4. Časovni plan in mejniki
5. Komunikacijski protokol
6. Tveganja — prvi pregled

## Povzetek razprave

### 1. Obseg projekta

Naročnik Kova d.o.o. ima trenutno v uporabi zastarel ERP sistem (Microsoft Dynamics NAV 2016). Cilj projekta je migracija na SAP S/4HANA 2023, vključno z integracijo naslednjih modulov:
- Finance in kontroling (FI/CO)
- Upravljanje zalog (MM)
- Prodaja in distribucija (SD)
- Osnovna sredstva (AA)

Gregor Mlakar je poudaril, da je ključna zahteva **ohranitev zgodovinskih podatkov** od leta 2015 dalje. Ocenjena količina podatkov: ~2,4 TB.

### 2. Predlagana arhitektura

Tomaž Kržič je predstavil predlagano arhitekturo:
- SAP S/4HANA bo nameščen on-premise na strežnikih naročnika
- Integracija z obstoječim e-commerce sistemom (Magento 2) prek SAP Integration Suite
- Vmesnik za obstoječi WMS sistem (Manhattan Associates) ostaja — custom API adapter
- Podatkovna migracija: orodje SAP LTMC (Legacy Transfer and Migration Cockpit)

Maja Horvat je opozorila na možne težave z mapiranjem kontnega plana iz NAV v SAP — potrebna bo ročna validacija vsaj 30% kontov.

### 3. Časovni plan

| Faza | Opis | Začetek | Konec |
|------|------|---------|-------|
| 1 | Blueprint & as-is analiza | 2024-01-22 | 2024-03-01 |
| 2 | Konfiguracija in razvoj | 2024-03-04 | 2024-06-30 |
| 3 | Testiranje (UAT) | 2024-07-01 | 2024-08-31 |
| 4 | Go-live priprava | 2024-09-01 | 2024-09-30 |
| 5 | Go-live | 2024-10-01 | — |

**Dogovorjen go-live datum: 1. oktober 2024.**

### 4. Tveganja

- Migracija podatkov iz NAV je kompleksna — Janez Novak je ocenil 3–4 tedne samo za čiščenje podatkov
- Odvisnost od dostopnosti ključnih uporabnikov na strani Kova (Petra Sajovic potrdi razpoložljivost)
- Licenciranje SAP — naročnik mora do 1. februarja potrditi nakup licenc

## Sklepi in akcije

| Akcija | Odgovorna oseba | Rok |
|--------|----------------|-----|
| Priprava projektne listine | Ana Kovač | 2024-01-22 |
| Dostop do NAV za analizo podatkov | Gregor Mlakar | 2024-01-19 |
| Potrditev SAP licenc | Petra Sajovic | 2024-02-01 |
| Arhitekturni dokument v1 | Tomaž Kržič | 2024-01-31 |
| Analiza kontnega plana | Maja Horvat | 2024-02-15 |

## Naslednji sestanek

Datum: 2024-01-29, 10:00  
Tema: Pregled as-is procesov, dostop do testnih sistemov
