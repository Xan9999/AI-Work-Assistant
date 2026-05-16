# Izredni sestanek — DataSync produkcijski incident

**Datum:** 2024-08-03, 14:00  
**Format:** Zoom (urgentno sklican)  
**Projekt:** DSYNC-2024-INT

## Prisotni

- Sara Petric (PM + data inženir, Nexus)
- Janez Novak (razvijalec, Nexus)
- Franc Vidic (CTO, DataSync d.o.o.)

## Opis incidenta

Dne 2024-08-03 ob 09:47 je pipeline za sinhronizacijo podatkov iz Salesforce prenehal delovati. 

**Simptomi**: 0 zapisov procesiranih od 09:47 dalje, naraščajoča čakalna vrsta (Redis), alarmi na Grafani.

**Vzrok (ugotovljeno ob 13:20)**: Salesforce je brez predhodnega opozorila spremenil strukturo API odgovora za objekt `Contact` — polje `Phone` je bilo preimenovano v `MobilePhone` za Enterprise tier. To je pokvarilo deserializacijo.

Tveganje R01 iz registra (API spremembe Salesforce) se je uresničilo.

## Časovnica incidenta

| Čas | Dogodek |
|-----|---------|
| 09:47 | Pipeline se ustavi |
| 10:05 | Grafana alert — Sara Petric opazi |
| 10:30 | Janez Novak začne debugging |
| 13:20 | Vzrok identificiran |
| 14:00 | Ta sestanek |
| 14:45 | Fix deployiran v produkcijo |
| 15:10 | Pipeline obnovljen, zaostala vrsta procesirana |

## Vpliv

- 5 ur 3 minute downtime
- ~47.000 zapisov v zaostanku — vse procesirane do 16:00
- Ni trajne izgube podatkov

## Korektivni ukrepi

1. Implementirati schema validation ob zagonu pipeline (ne samo ob spremembi kode)
2. Salesforce API verzioniranje — zakleniti na specifično API verzijo (v58.0)
3. Alerting na strukturo odgovora, ne samo na volumen
4. Vzpostaviti Salesforce developer forum monitoring za opozorila o sprememba

## Post-mortem dokument

Sara Petric bo do 2024-08-07 napisala popoln post-mortem.
