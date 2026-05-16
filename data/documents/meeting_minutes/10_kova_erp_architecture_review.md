# Arhitekturni pregled — Kova ERP projekt

**Datum:** 2024-03-05  
**Projekt:** KOVA-2024-ERP

## Prisotni

- Tomaž Kržič (arhitekt, Nexus)
- Maja Horvat (ERP specialist, Nexus)
- Janez Novak (razvijalec, Nexus)
- Gregor Mlakar (IT direktor, Kova d.o.o.)

## Namen

Pregled arhitekturnih odločitev po zaključku Blueprint faze.

## Ključne odločitve

### 1. Namestitev

**Odločitev**: SAP S/4HANA ostane on-premise (ne cloud).

Razlog: Gregor Mlakar je po internih posvetovanjih potrdil, da varnostna politika Kova d.o.o. prepoveduje shranjevanje poslovnih podatkov zunaj lastnih prostorov. SAP RISE (cloud) odpade.

Konfiguracija strežnika: 2x HPE ProLiant DL380 Gen10, 512GB RAM, SSD RAID.

### 2. Integracija z e-commerce

Namesto SAP Integration Suite (kot predlagano na kick-offu) bo uporabljen **custom middleware** v Pythonu, ker:
- SAP Integration Suite letna licenca: ~18.000 € — predrago za obseg integracij
- Magento → SAP integracija je standardna, obstajajo open-source konektorji
- Janez Novak ocenjuje razvoj custom vmesnika: 3–4 tedne

Tomaž Kržič opozori: custom middleware pomeni večje vzdrževalno breme dolgoročno. Sprejeto tveganje.

### 3. Podatkovna migracija

Orodje: SAP LTMC (ostaja kot na kick-offu).

**Sprememba**: Janez Novak je po analizi NAV podatkov ugotovil, da je kakovost podatkov slabša, kot pričakovano — ocena čiščenja se podaljša na 6 tednov (prej 3–4).

### 4. Go-live datum

Zaradi podaljšanja časa za čiščenje podatkov in spremembe arhitekture integracije:

**Revidirani go-live: Q1 2025 (januar ali februar 2025).**

*Opomba: To je v nasprotju z zapisnikom kick-off sestanka (01.10.2024) — datum je bil uradno revidiran.*

Gregor Mlakar bo obvestil vodstvo Kova d.o.o.

## Odprta vprašanja

- Verzija Magento: Kova ima Magento 2.4.3 — konec podpore december 2023. Priporočena nadgradnja na 2.4.7 preden začnemo integracijo.
- Hardware naročilo: Gregor Mlakar mora naročiti strežnike do 2024-03-15 (dobavni rok 6 tednov).
