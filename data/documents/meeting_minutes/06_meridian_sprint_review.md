# Sprint Review — Meridian Web Platform, Sprint 4

**Datum:** 2024-06-03  
**Projekt:** MERIDIAN-2024-WEB  
**Sprint:** 4 (od 6 načrtovanih)

## Prisotni

- Tomaž Kržič (PM/arhitekt, Nexus)
- Nina Vidmar (razvijalec, Nexus)
- Janez Novak (razvijalec, Nexus)
- Klara Šimc (product owner, Meridian d.o.o.)
- Blaž Tratnik (UX designer, Meridian d.o.o.)

## Demonstracija

Nina Vidmar je demonstrirala:
- Modul za upravljanje vsebine (CMS) — funkcionalen, čaka UX review
- Sistem za uporabniške vloge in pravice — implementiran, unit testi pokrivajo 94%
- REST API za mobilno aplikacijo — 18 od 24 endpointov dokončanih

Janez Novak je demonstriral:
- Integracija z payment gateway Stripe — uspešno testirana v sandbox okolju
- PDF generiranje poročil — deluje, a je prepočasno (8 sec za kompleksen report)

## Sprint 4 velocity

Načrtovano story points: 48  
Dokončano: 41  
Nedokončano (preneseno v Sprint 5): 7

## Problemi

**PDF performance**: Janez Novak ocenjuje, da je problem v sinhroni generaciji. Predlog: asinhrona generacija z background workerjem (Celery/Redis). Klara Šimc to sprejme — dodata v Sprint 5.

**Mobile API**: 6 endpointov za "advanced search" funkcionalnost je kompleksnejše, kot je bilo ocenjeno. Prestavitev na Sprint 5 in Sprint 6.

## Feedback naročnika

Klara Šimc: "Napredek je dober, CMS je točno to kar smo si zamišljali. Stripe integracija nas veseli. Zaskrbljeni smo glede PDF performansa — naši uporabniki generirajo do 50 reportov dnevno."

Blaž Tratnik: "Vmesnik izgleda dobro, manjšo redesign UX bomo poslali do petka."

## Plan Sprint 5

- Celery/Redis za async PDF
- Preostalih 6 API endpointov
- UX popravki po Blaž feedbacku
- Load testing (Nina)

## Status projekta

Projekt je **1 teden za planom**. Go-live ostaja **september 2024** — dosegljivo z minimalnim obsegom Sprint 6.
