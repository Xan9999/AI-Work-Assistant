# Zapisnik retrospektive — Projekt Merkur IT Modernizacija

**Datum:** 2023-11-08  
**Format:** Zoom  
**Projekt:** MERKUR-2023-MOD (zaključen)  

## Prisotni

- Ana Kovač (PM, Nexus)
- Janez Novak (razvijalec, Nexus)
- Sara Petric (data engineer, Nexus)
- Nina Vidmar (junior developer, Nexus)
- Rok Bajt (BA, Nexus)
- Andrej Čuk (CTO, Merkur IT)

## Kaj je šlo dobro

- **Podatkovna migracija** je bila izvedena brez izgube podatkov. Sara Petric je pohvaljena za natančne validacijske skripte.
- **Komunikacija z naročnikom** — tedenski status emaili so bili dobro sprejeti.
- **CI/CD pipeline** — Janez Novak je vzpostavil popolnoma avtomatiziran pipeline, ki ga bo naročnik lahko vzdrževal sam.
- Projekt zaključen v roku (zamuda samo 2 tedna pri UAT fazi).

## Kaj bi naredili drugače

- **Zahteve zbrane prepozno**: Analiza zahtev je trajala 3 tedne predolgo. Rok Bajt predlaga template za zahteve za naslednje projekte.
- **Testno okolje**: Naročnik ni imel testnega okolja pripravljenega ob začetku razvojne faze — 2-tedenski zastoj.
- **Dokumentacija**: Nina Vidmar opozori, da je bila koda slabo dokumentirana med razvojem; dokumentacijo so morali pisati retroaktivno.

## Tehnične ugotovitve

- Prehod iz PHP 7.2 na PHP 8.2 je povzročil 14 breaking changes — priporočljivo je zagotoviti daljše prehodno testno obdobje pri naslednjih migracijah verzij.
- PostgreSQL 15 performance je bila bistveno boljša od MySQL 5.7, ki ga je naročnik imel prej (~3x hitrejše kompleksne poizvedbe).
- Docker Compose v produkciji ni primeren za večji promet — priporočljivo Kubernetes ali vsaj Docker Swarm.

## Naučene lekcije za naslednje projekte

1. Vedno zahtevati pripravljeno testno okolje PRED začetkom razvoja
2. Uvesti "definition of done" ki vključuje dokumentacijo
3. Analiza breaking changes pred vsakim večjim upgrade-om verzije
4. Za naslednji projekt z Merkur IT se dogovoriti za fiksni support retainer (3 mesece post go-live)

## Zaključek projekta

Projekt MERKUR-2023-MOD je uradno zaključen. Naročnik je podpisal acceptance report 2023-10-31.
