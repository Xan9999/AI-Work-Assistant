# Zapisnik — Kick-off: Nova Logistics CRM implementacija

**Datum:** 2023-03-06  
**Format:** On-site, Nova Logistics, Maribor  
**Projekt:** NOVA-2023-CRM

## Prisotni

- Rok Bajt (PM + BA, Nexus)
- Janez Novak (razvijalec, Nexus)
- Nina Vidmar (junior developer, Nexus)
- Aleksander Petek (direktor prodaje, Nova Logistics d.o.o.)
- Tanja Sušnik (IT vodja, Nova Logistics d.o.o.)

## Obseg

Implementacija Salesforce Sales Cloud za prodajno ekipo Nova Logistics (22 prodajnikov). Vključuje:
- Konfiguracija Salesforce objektov (Account, Contact, Opportunity, Lead)
- Integracija z obstoječim ERP (SAP B1)
- Migracija podatkov iz Excel/Access baz
- Usposabljanje 22 uporabnikov

## Zahteve naročnika

Aleksander Petek: "Naša ekipa dela 70% v terenu. Mobilni dostop je prioriteta #1. Poročila morajo biti dostopna na telefonu."

Rok Bajt ugotavlja, da Salesforce Mobile app pokriva to zahtevo nativno.

## Tehnična ocena

Tanja Sušnik: SAP Business One verzija 9.3 (zastarela — podpora konča 2025). Integracija z Salesforce bo zahtevala custom razvoj.

Janez Novak ocenjuje SAP B1 → Salesforce integracija: 4–5 tednov razvoja, API-first pristop.

## Tveganja

- Kakovost podatkov v Excelu/Accessu — Rok Bajt zahteva vzorec podatkov pred podpisom pogodbe
- SAP B1 verzija 9.3 — priporoča nadgradnjo na 10.0 pred integracijo (Nova Logistics to upošteva)
- Sprememba upravljanja (22 prodajnikov, navajeni na Excel) — potreben sprememba management plan

## Časovni plan

| Faza | Opis | Trajanje |
|------|------|---------|
| 1 | Konfiguracija Salesforce | 3 tedne |
| 2 | SAP B1 integracija | 5 tednov |
| 3 | Migracija podatkov | 2 tedni |
| 4 | UAT + usposabljanje | 3 tedni |

**Skupaj: ~13 tednov. Predviden go-live: junij 2023.**

## Naslednji korak

Rok Bajt pošlje pogodbo do 2023-03-10. Nova Logistics potrdi do 2023-03-17.
