# Mid-project poročilo — Meridian Web Platform
## Projekt: MERIDIAN-2024-WEB | Sprint 4 zaključen

**Datum:** 2024-06-10  
**Status:** V teku — RUMENA (blaga zamuda)

---

## 1. Povzetek

Projekt je v drugi polovici. Napredek je dober, a 1–2 tedna za planom. Go-live september 2024 je še dosegljiv, a bo zahteval disciplino.

---

## 2. Kaj je dokončano (Sprint 1–4)

- Kompletna infrastruktura AWS (ECS Fargate, RDS, S3, CloudFront)
- Autentikacija in sistem vlog
- Upravljanje naročnin (Stripe integracija)
- CMS modul (osnoven)
- REST API: 18 od 24 endpointov

---

## 3. Spremembe glede na originalno ponudbo

### 3.1 PDF generiranje — arhitekturna sprememba

Originalna ponudba: sinhrono generiranje PDF v Django viewu.  
Dejansko implementirano: asinhrono (Celery + Redis) po zahtevi naročnika (performance issue identificiran v Sprint 4).

**Vpliv na strošek**: +8 ur razvoja Janez Novak (v okviru varnostnega rezervata v pogodbi).

### 3.2 Go-live datum

**Originalna ponudba: september 2024.**  
**Aktualni plan: september 2024** — ostaja, a je bolj tesno.

Zakaj zamuda: mobilni API endpointi so bili kompleksnejši od ocene (+ 1 teden). Blaž Tratnik (UX) je zamudil z redesign feedbackom za 5 dni.

### 3.3 Večjezičnost

Naročnik (Klara Šimc) je 2024-05-15 prosila za slovensko lokalizacijo (i18n). To je bilo v originalni ponudbi označeno kot "post-MVP".

**Sklep**: i18n bo implementiran, a SAMO za slovenščino in angleščino, v Sprintu 6 (zadnji sprint). Ni change order — Tomaž Kržič je ocenil, da je Django i18n dovolj standardna da jo Janez Novak naredi v 20 urah brez prekoračitve.

---

## 4. Finančni status

| Faza | Planirano | Status |
|------|-----------|--------|
| Podpis (30%) | 20.400 € | ✓ Prejeto |
| Faza 4 milestone (40%) | 27.200 € | Čaka zaključek Sprint 5 |
| Go-live (30%) | 20.400 € | Čaka go-live |
| **Skupaj** | **68.000 €** | |

---

## 5. Tveganja

| Tveganje | Verjetnost | Ukrep |
|---------|------------|-------|
| Go-live zamuda (okt namesto sep) | Srednja | Sprint 6 scope lockdown |
| Load test odkrije performance issue | Nizka | Planiran load test Sprint 5 |
| Naročnik zahteva nove funkcije | Visoka | Formalni change order proces |
