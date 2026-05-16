# Projektna ponudba — Migracija v oblak (AWS)
## Nexus Consulting d.o.o. → Atlas d.o.o.

**Datum ponudbe:** 2023-08-15  
**Veljavnost:** do 2023-10-15  
**Referenčna številka:** NCX-2023-ATLAS-001  

---

## 1. Povzetek

Atlas d.o.o. želi migrirati svoje IT sisteme iz lastne strežniške sobe v javni oblak. Nexus Consulting predlaga migrацijo na AWS (Amazon Web Services) z regijo eu-central-1 (Frankfurt).

Projekt bo trajal 12 mesecev in vključuje migracijo 7 aplikacij, 3 podatkovnih baz in celotne mrežne infrastrukture.

**Skupna vrednost storitev Nexus: 142.000 € brez DDV**

---

## 2. Zakaj AWS

Nexus Consulting priporoča AWS pred Azure in Google Cloud iz naslednjih razlogov:

| Kriterij | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Ekipa Nexus ima certificirane strokovnjake | Da (3x) | Ne | Ne |
| Prisotnost v EU (Frankfurt) | Da | Da | Da |
| Ekosistem orodij (DevOps) | Odličen | Dober | Dober |
| Stroški za predviden workload | Najugodnejši* | +12% | +8% |
| Podpora za Windows workloade | Odlična | Odlična | Osnovna |

*Ocena na podlagi AWS Pricing Calculator za predvideni workload.

---

## 3. Obseg migracije

### Aplikacije

| Aplikacija | Trenutna platforma | Ciljna platforma | Strategija |
|-----------|-------------------|-----------------|-----------|
| ERP (Dynamics 365) | On-premise | EC2 + RDS | Lift & shift |
| Web portal | IIS / .NET | Elastic Beanstalk | Re-platform |
| API gateway | Custom Node.js | API Gateway + Lambda | Re-architect |
| Document management | FileNet on-prem | S3 + Lambda | Re-architect |
| Reporting (SSRS) | SQL Server 2017 | RDS + QuickSight | Replace |
| Legacy CRM | Access/VBA | EC2 (maintain) | Lift & shift |
| Intranet | SharePoint 2016 | SharePoint Online | Replace |

### Podatkovne baze

| Baza | Trenutno | Cilj | Metoda |
|------|---------|------|--------|
| Glavna baza (SQL Server) | On-premise, 890 GB | RDS SQL Server Multi-AZ | AWS DMS |
| Dokumenti (MongoDB) | On-premise, 120 GB | DocumentDB | mongodump/restore |
| Archiv (PostgreSQL) | On-premise, 2.1 TB | RDS PostgreSQL | AWS DMS |

---

## 4. Arhitektura

```
Internet → Route 53 → CloudFront (CDN)
                           ↓
                    Application Load Balancer
                           ↓
         ┌─────────────────────────────────────┐
         │           VPC (10.0.0.0/16)         │
         │  Public subnet: NAT GW, Bastion     │
         │  Private subnet: EC2, ECS           │
         │  Data subnet: RDS, ElastiCache      │
         └─────────────────────────────────────┘
```

---

## 5. Časovni plan in stroški

### Faze

| Faza | Opis | Trajanje | Nexus storitve |
|------|------|---------|---------------|
| 1 | Landing zone, VPC, IAM | 3 tedne | 18.000 € |
| 2 | Migracija nekritičnih aplikacij | 8 tednov | 32.000 € |
| 3 | Migracija podatkovnih baz | 6 tednov | 28.000 € |
| 4 | Migracija kritičnih aplikacij | 8 tednov | 38.000 € |
| 5 | Testiranje, cut-over, hiper-care | 4 tedne | 26.000 € |
| **Skupaj** | | **29 tednov** | **142.000 €** |

**Predvideni go-live: junij 2024 (Q2 2024)**

### Ocenjeni AWS stroški (mesečno, po migraciji)

| Storitev | Mesečni strošek |
|---------|----------------|
| EC2 (5x t3.large, 2x t3.xlarge) | 820 € |
| RDS Multi-AZ (db.r5.large) | 480 € |
| S3 (5 TB) | 115 € |
| CloudFront | 80 € |
| Data transfer | 120 € |
| Ostalo (Route53, WAF, monitoring) | 185 € |
| **Skupaj mesečno** | **1.800 €** |

Primerjava: Trenutni strošek lastne strežniške sobe = ~2.400 €/mesec (energija, hlajenje, amortizacija, IT admin).

**Prihranek: ~600 €/mesec oz. 7.200 €/leto.**

---

## 6. Ekipa Nexus za projekt

| Ime | Vloga | Certifikati |
|-----|-------|------------|
| Ana Kovač | PM | PMP |
| Luka Zupan | DevOps inženir | AWS Solutions Architect Associate, AWS DevOps Professional |
| Janez Novak | Razvijalec | — |
| Tomaž Kržič | Arhitekt | AWS Solutions Architect Professional (v pripravi) |

---

## 7. Garancije in SLA

- Dostopnost produkcijskega okolja: 99.9% (SLA AWS + naša arhitektura)
- RPO (Recovery Point Objective): 1 ura
- RTO (Recovery Time Objective): 4 ure
- Hiper-care podpora po go-live: 4 tedne (vključeno)

---

*Nexus Consulting d.o.o. | Dunajska 22, 1000 Ljubljana*
