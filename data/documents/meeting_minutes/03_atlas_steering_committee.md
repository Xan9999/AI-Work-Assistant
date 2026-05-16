# Zapisnik — Steering Committee: Atlas Cloud Migration

**Datum:** 2024-05-07  
**Format:** On-site, Atlas d.o.o. sejna soba  
**Projekt:** ATLAS-2023-CLOUD  

## Prisotni

- Ana Kovač — PM, Nexus Consulting
- Tomaž Kržič — Arhitekt, Nexus Consulting
- Mitja Ferlan — IT Manager, Atlas d.o.o.
- Bojan Rus — COO, Atlas d.o.o.
- Sandra Leban — CFO, Atlas d.o.o.

## Namen sestanka

Četrtletni pregled statusa projekta za vodstvo Atlas d.o.o. Pregled napredka, stroškov in revidiranega časovnega plana.

## Status projekta

Ana Kovač je predstavila dashboard:

- **Dokončano:** Infrastruktura (100%), migracija 5/7 aplikacij (71%), testiranje QA okolja (80%)
- **V teku:** Migracija zadnjih 2 aplikacij (.NET legacy), performance testiranje
- **Ni začeto:** Produkcijska migracija, cut-over plan

### Stroški

| Postavka | Planirano | Porabljeno | Preostalo |
|----------|-----------|------------|-----------|
| Nexus storitve | 142.000 € | 98.400 € | 43.600 € |
| AWS infrastruktura | 28.000 € | 19.200 € | 8.800 € |
| Licence in orodja | 12.000 € | 11.800 € | 200 € |
| **Skupaj** | **182.000 €** | **129.400 €** | **52.600 €** |

Projekt je **v okviru proračuna**.

### Revidirani časovni plan

Tomaž Kržič je pojasnil zamudo pri dveh legacy .NET aplikacijah. Odločitev: obe aplikaciji bosta migrirani v Windows containers na EC2, brez refaktoringa na .NET 8. To pospeši zaključek za ~6 tednov.

**Novi predvideni go-live: december 2024.**

Bojan Rus je izrazil zaskrbljenost — originalni plan je predvideval zaključek do junija 2024. Ana Kovač je pojasnila vzroke zamude (tehnična kompleksnost legacy .NET, WAF odobritve).

Sandra Leban je vprašala o vplivu zamude na AWS stroške — Luka Zupan (ni prisoten, pisno poročilo) ocenjuje +3.200 € za podaljšano vzporedno delovanje obeh okolij.

## Sklepi

1. Vodstvo Atlas d.o.o. sprejme revidirani plan z go-live december 2024
2. Nexus pripravi pisno spremembo pogodbe (change order) za podaljšanje projekta
3. Naslednji steering committee: september 2024

## Opomba projektnega managerja

Ana Kovač po sestanku: "Glede na potek bomo najverjetneje zaključili med novembrom in januarjem — december je optimistična ocena."
