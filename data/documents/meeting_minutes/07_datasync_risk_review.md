# Sestanek pregleda tveganj — DataSync projekt

**Datum:** 2024-04-22  
**Projekt:** DATASYNC-2024  
**Koda:** DSYNC-2024-INT

## Prisotni

- Sara Petric (PM + data arhitekt, Nexus)
- Rok Bajt (BA, Nexus)
- Tomaž Kržič (arhitekt, Nexus) — svetovalec
- Franc Vidic (CTO, DataSync d.o.o.)
- Mojca Stare (IT arhitekt, DataSync d.o.o.)

## Register tveganj

| ID | Tveganje | Verjetnost | Vpliv | Ukrep |
|----|---------|------------|-------|-------|
| R01 | API spremembe pri viru podatkov (Salesforce) | Srednja | Visok | Verzioniranje API, monitoring |
| R02 | Volumen podatkov preseže oceno (>10M zapisov/dan) | Nizka | Visok | Load testing v fazi 2 |
| R03 | Regulatorno tveganje (GDPR - osebni podatki v toku) | Visoka | Kritičen | DPO pregled pred go-live |
| R04 | Odvisnost od Salesforce licence (DataSync nima Enterprise) | Visoka | Visok | DataSync nabavi licenco do maja |
| R05 | Zamuda pri dostavi podatkovnih shem s strani naročnika | Srednja | Srednji | Eskalacija po 5 delovnih dneh |

## Razprava o R03 — GDPR

Tomaž Kržič je opozoril: tok podatkov vključuje e-mail naslove in telefonske številke strank. To so osebni podatki po GDPR. Potrebna je:
1. Ocena učinkov (DPIA)
2. Podpisana pogodba o obdelavi podatkov (DPA) med DataSync d.o.o. in Nexus
3. Podatki se ne smejo shranjevati v staging okolju brez šifriranja

Franc Vidic potrdi, da bo njihov DPO (Nataša Obreza) kontaktiral Nexus do konca tedna.

## Razprava o R04 — Salesforce licenca

Mojca Stare: "Salesforce Enterprise licenca stane ~45.000 € letno. Management še ni odobril." Brez te licence API klicov ni mogoče izvajati v zahtevanem obsegu.

Sara Petric: "Brez potrditve o licenci do 2024-05-10 bomo morali projekt ustaviti ali spremeniti arhitekturo."

## Sklepi

- DataSync management mora do 2024-05-10 potrditi nakup Salesforce Enterprise licence (R04)
- DPO pregled GDPR tveganj do 2024-05-15 (R03)
- Sara Petric pripravi load test plan do 2024-04-30 (R02)
