# Tehnično poročilo — Naučene lekcije: Cloud migracije
## Nexus Consulting — interno poročilo

**Datum:** 2024-07-01  
**Avtor:** Luka Zupan, Tomaž Kržič  
**Osnova:** Projekti Atlas (AWS) in Argon (Azure)

---

## 1. Namen

To poročilo združuje tehnične izkušnje iz dveh cloud migracij, ki jih je Nexus Consulting izvedel v 2024:
- **ATLAS-2023-CLOUD**: Migracija Atlas d.o.o. na AWS eu-central-1
- **ARGON-2024-AZURE**: Migracija Argon d.o.o. na Azure West Europe

Namen: standardizirati pristop za prihodnje projekte.

---

## 2. Skupne ugotovitve (AWS in Azure)

### 2.1 Lift & shift je pogosto prava odločitev

**Na Atlasu** smo začeli z ambicijoznim načrtom re-arhitekture .NET servisov. Zamuda je prisilila kompromis: lift & shift v Windows containers. Rezultat je bil hitrejši in enako zanesljiv.

**Na Argonu** je bil ERP (Navision) lift & shift edina realna opcija glede na trdi rok (datacenter pogodba).

**Priporoča se**: Za projekte z omejenimi roki privzeti lift & shift. Re-arhitekturo načrtovati kot ločeno fazo po stabilizaciji v oblaku.

### 2.2 Terraform je obvezen

Oba projekta sta bila izvedena z Terraform za infrastrukturo. Prednosti:
- Ponovljiva deployment (dev → staging → prod brez ročnih klikov)
- Git historia za infrastrukturne spremembe
- Hitro obnovitev po incident (Argon: cel VNet obnoviti v 12 min)

**Priporoča se**: Terraform od prvega dne. Brez izjem.

### 2.3 Assessment pred migracijo prihrani čas

Atlas: nismo naredili formalnega workload assessment → napačna sizing dveh EC2 (premajhna, povečali po 2 tednih).

Argon: Uporabili smo Azure Migrate Assessment → sizing bil točen ±10%.

**Priporoča se**: Azure Migrate ali AWS Migration Evaluator za vsak projekt pred začetkom.

---

## 3. AWS-specifične ugotovitve

### 3.1 Windows containers na ECS so problematični

Na Atlasu smo 2 .NET Framework 4.5 servisa namestili v Windows containers na ECS. Težave:
- Windows container image je velik (15 GB+) — dolgi deployment časi
- AWS ne podpira Windows Fargate (samo EC2 launch type za Windows)
- Cena EC2 Windows nodeov je ~40% višja od Linux

**Priporoča se**: Če je Windows containers neizogibno, načrtovati EC2 (ne ECS Fargate). Bolje je prioritizirati migrацijo na .NET 8 (Linux).

### 3.2 RDS Multi-AZ je nujen za produkcijo

Na Atlasu: testno okolje je imelo Single-AZ RDS. Med testno migracijo je prišlo do AZ outage (redko, a se zgodi) — 47 minut downtime.

**Priporoča se**: Multi-AZ za vsako produkcijsko bazo brez izjeme.

### 3.3 CloudFront pospeši SEA/APAC dostop

Atlas ima ~15% prometa iz Azije. Po aktivaciji CloudFront: latenca iz Singapore 340ms → 45ms.

---

## 4. Azure-specifične ugotovitve

### 4.1 Azure SQL Managed Instance je odlična rešitev

Na Argonu smo migrirali SQL Server 2019 → Azure SQL Managed Instance (General Purpose). Brez sprememb v aplikacijah — 100% kompatibilnost. Performance primerljiva z on-prem. Backup in patch management avtomatski.

**Priporoča se**: Azure SQL MI pred SQL Server na VM, razen če je potreben specifičen feature ki ga MI ne podpira.

### 4.2 Azure Files latenca

Za file server smo izbrali Azure Files Premium (SMB). Pri nekaterih desktop operacijah (odpiranje Word dokumentov) je latenca opazno višja od on-prem NFS (~80ms vs ~5ms).

**Priporoča se**: Za heavy SMB workloade, razmisliti o Azure NetApp Files ali hibridnem pristopu (Azure File Sync + on-prem cache).

### 4.3 Exchange → M365 je kompleksnejše, kot pričakovano

Argon: Exchange 2016 → M365. Težave z legacy distribution groups, shared mailboxes, in public folders. 2 nabiralnika z okvarjenimi PST.

**Priporoča se**: Načrtovati 2–3 tedne samo za Exchange → M365, ne glede na število nabiralnikov. Obravnavati kot ločen projekt.

---

## 5. Primerjava AWS vs Azure za prihodnje projekte

| Kriterij | AWS | Azure |
|---------|-----|-------|
| Nexus expertise | Višja (Luka: 4x AWS cert) | Srednja (Luka: 1x Azure cert) |
| Windows workloadi | Dobra | Odlična (native Microsoft) |
| Primerno za Microsoft-centric naročnike | Manj | Bolj |
| Cena za Linux workloade | Ugodnejša | Podobna |
| Dokumentacija | Obsežna, kompleksna | Dobra |
| SLA za compute | 99.99% | 99.99% |

**Priporoča se**: AWS za naročnike brez Microsoft ekosistema, Azure za Microsoft-centric naročnike (Office 365, AD, SQL Server).

---

## 6. Standardni checklist za cloud migracije

- [ ] Workload assessment (AWS Migration Evaluator / Azure Migrate)
- [ ] GDPR/podatkovni suverenitet pregled — EU regija potrjena
- [ ] Terraform repository vzpostaviti pred prvim deployment
- [ ] Multi-AZ za vse produkcijske baze
- [ ] WAF od prvega dne
- [ ] Cut-over okno: sobota med 02:00 in 06:00 (ne petek zvečer)
- [ ] Rollback plan dokumentiran in testiran
- [ ] Hiper-care obdobje min. 4 tedne po go-live
