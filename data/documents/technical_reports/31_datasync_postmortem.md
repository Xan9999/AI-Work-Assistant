# Post-mortem poročilo — DataSync produkcijski incident
## Incident ID: DSYNC-INC-2024-001

**Datum incidenta:** 2024-08-03  
**Datum poročila:** 2024-08-07  
**Avtor:** Sara Petric  
**Status:** ZAKLJUČEN — korektivni ukrepi implementirani

---

## 1. Povzetek

Dne 2024-08-03 med 09:47 in 15:10 je DataSync Integration Engine prenehal procesirati podatke. Vzrok: Salesforce je brez predhodnega opozorila preimensoval polje `Phone` v `MobilePhone` za objekt Contact v Enterprise tieru. To je pokvarilo deserializacijo v Python modelu.

**Skupen downtime**: 5 ur 23 minut  
**Izguba podatkov**: Nič (vsi eventi so bili v Redis čakalni vrsti)  
**Vpliv na poslovanje**: Zamuda pri sinhronizaciji ~47.000 kontakt posodobitev

---

## 2. Časovnica

| Čas | Dogodek |
|-----|---------|
| 09:47:03 | Zadnji uspešno procesiran event |
| 09:47:04 | Začetek napak: `KeyError: 'Phone'` v Pydantic modelu |
| 09:47:04 | Redis čakalna vrsta začne naraščati |
| 10:05:22 | Grafana alert: "Events processed/min < 10" |
| 10:05:45 | Sara Petric prejme PagerDuty alert |
| 10:30:00 | Janez Novak začne debugging |
| 11:15:00 | Pregledani Salesforce release notes — ničesar relevantnega (napaka: niso iskali v Enterprise changelogs) |
| 13:20:00 | Vzrok identificiran: `MobilePhone` vs `Phone` |
| 14:00:00 | Izredni sestanek |
| 14:45:00 | Fix deployiran (dodano field mapping + fallback) |
| 15:10:00 | Pipeline obnovljen, čakalna vrsta procesirana |

---

## 3. Analiza vzroka (5 Why)

**Simptom**: Pipeline se ustavi z `KeyError: 'Phone'`

**Why 1**: Pydantic model zahteva polje `Phone` ki ga ni v payloadu.  
**Why 2**: Salesforce je preimenoval `Phone` → `MobilePhone` za Enterprise tier.  
**Why 3**: Nismo bili obveščeni o spremembi.  
**Why 4**: Nismo subscribirali Salesforce Enterprise release notes (samo splošne).  
**Why 5**: V fazi tveganj (R01) smo identificirali API spremembe kot tveganje, a nismo implementirali schema validation ki bi to odkrilo prej.

**Korenski vzrok**: Odsotnost schema validation pri vstopu payloada — napaka se ni odkrila dokler ni prišlo do dejanske napake pri procesiranju.

---

## 4. Korektivni ukrepi

| Ukrep | Odgovorna oseba | Rok | Status |
|-------|----------------|-----|--------|
| Schema validation ob zagonu (ne samo ob kodi) | Janez Novak | 2024-08-10 | ✓ Implementirano |
| Zakleniti Salesforce API verzijo na v58.0 | Janez Novak | 2024-08-10 | ✓ Implementirano |
| Alert na nepričakovana polja v SF odgovoru | Sara Petric | 2024-08-12 | ✓ Implementirano |
| Salesforce Enterprise changelog monitoring | Sara Petric | 2024-08-15 | ✓ Implementirano |
| Graceful degradation za neznana polja | Janez Novak | 2024-08-20 | ✓ Implementirano |

### Sprememba kode — field mapping

```python
# Prej (krhko):
contact_phone = sf_contact["Phone"]

# Po (robustno):
contact_phone = (
    sf_contact.get("Phone") or 
    sf_contact.get("MobilePhone") or 
    sf_contact.get("HomePhone")
)
```

---

## 5. Naučene lekcije

1. **Schema validation mora biti proaktivna** — ne čakati na napako pri procesiranju
2. **Zunanja API odvisnost = tveganje** — vse field access mora biti defensiven (`.get()` ne `[]`)
3. **Salesforce Enterprise in Standard tier imata različne field strukture** — tega nismo vedeli
4. **Monitoring mora vključevati strukturne anomalije** — ne samo volumetric metrike

---

## 6. Komunikacija z naročnikom

Sara Petric je Franc Vidic (CTO, DataSync) obvestila ob 10:15 z emailom. Ob 14:00 je bil izredni sestanek. Naročnik je bil razumljiv — downtime je bil sprejemljiv glede na naravo incidenta.

*DataSync je zahteval brezplačno implementacijo schema validation — Nexus je to odobril kot goodwill gesture.*
