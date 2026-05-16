# Tehnična specifikacija — AWS arhitektura
## Projekt: ATLAS-2023-CLOUD | Dokument: ARCH-001

**Verzija:** 1.4  
**Datum:** 2024-04-08  
**Avtor:** Luka Zupan, Tomaž Kržič  
**Status:** ODOBREN (po steering committee 2024-05-07)

---

## 1. Pregled arhitekture

Atlas d.o.o. bo migriral v AWS regijo **eu-central-1 (Frankfurt)**. Vse podatke ostajajo znotraj EU (GDPR skladnost).

### 1.1 VPC dizajn

```
VPC: 10.0.0.0/16

Public subnets (2 AZ):
  10.0.1.0/24  (eu-central-1a) — NAT Gateway, ALB
  10.0.2.0/24  (eu-central-1b) — NAT Gateway, ALB

Private subnets (2 AZ):
  10.0.11.0/24 (eu-central-1a) — EC2, ECS
  10.0.12.0/24 (eu-central-1b) — EC2, ECS

Data subnets (2 AZ):
  10.0.21.0/24 (eu-central-1a) — RDS, ElastiCache
  10.0.22.0/24 (eu-central-1b) — RDS, ElastiCache
```

---

## 2. Compute konfiguracija

### 2.1 EC2 instance

| Aplikacija | Instance type | OS | AZ | Cena/mesec |
|-----------|--------------|-----|-----|-----------|
| App Server 1 (ERP) | t3.large | Windows 2019 | eu-central-1a | 186 € |
| App Server 2 (ERP) | t3.large | Windows 2019 | eu-central-1b | 186 € |
| Legacy CRM | t3.medium | Windows 2019 | eu-central-1a | 93 € |
| Legacy CRM (standby) | t3.medium | Windows 2019 | eu-central-1b | 93 € |
| Bastion Host | t3.micro | Amazon Linux 2023 | eu-central-1a | 9 € |

*Windows .NET legacy servisi so na EC2 (ne ECS) ker EKS Windows nodes so ~40% dražji.*

### 2.2 ECS Fargate (containerized apps)

| Servis | CPU | RAM | Replike | Cena/mesec |
|--------|-----|-----|---------|-----------|
| web-portal | 0.5 vCPU | 1 GB | 2 | 28 € |
| api-gateway | 1 vCPU | 2 GB | 2 | 56 € |
| document-service | 0.5 vCPU | 1 GB | 1 | 14 € |

---

## 3. Database konfiguracija

### 3.1 RDS PostgreSQL (glavna baza)

| Parameter | Vrednost |
|---------|---------|
| Engine | PostgreSQL 15.2 |
| Instance | db.r5.large (2 vCPU, 16 GB RAM) |
| Storage | 500 GB gp3, autoscaling do 2 TB |
| Multi-AZ | Da (eu-central-1a + 1b) |
| Backup | Avtomatski, 35 dni retencija |
| Šifriranje | AES-256 (AWS KMS) |
| Performance Insights | Vklopljeno |
| Cena/mesec | ~480 € |

### 3.2 DocumentDB (MongoDB kompatibilno)

| Parameter | Vrednost |
|---------|---------|
| Engine | Amazon DocumentDB 6.0 |
| Instance | db.r5.large (primary) + 1 replica |
| Storage | 120 GB, autoscaling |
| Cena/mesec | ~220 € |

---

## 4. Storage

| Storitev | Namen | Kapaciteta | Cena/mesec |
|---------|-------|------------|-----------|
| S3 (Standard) | Statične datoteke, mediji | 800 GB | 18 € |
| S3 (Glacier IR) | Arhivski dokumenti | 4 TB | 52 € |
| EFS | Shared filesystem za ECS | 50 GB | 15 € |

---

## 5. Security konfiguracija

### 5.1 IAM

- Principi least privilege za vse EC2/ECS vloge
- AWS Organizations SCPs za preprečevanje izhoda podatkov iz eu-central-1
- MFA obvezno za vse IAM user accounts
- AWS SSO za konzolni dostop

### 5.2 WAF pravila

| Pravilo | Akcija |
|---------|--------|
| AWS managed rules (Common) | Block |
| SQL injection detection | Block |
| XSS detection | Block |
| Rate limiting (>500 req/5min na IP) | Block |
| Geo-block (ne-EU) | Count (za monitoring) |

### 5.3 Monitoring

- CloudWatch Logs: vse aplikacijske loge
- CloudWatch Alarms: CPU >80%, RDS storage >80%, ALB 5xx >1%
- AWS Config: compliance monitoring
- CloudTrail: audit log vseh API klicev

---

## 6. Disaster Recovery

| Metrika | Cilj | Implementacija |
|---------|------|---------------|
| RPO | 1 ura | RDS automated backup + log shipping |
| RTO | 4 ure | Runbook dokumentiran, letna vaja |
| Backup retencija | 35 dni | RDS + S3 lifecycle |
| DR region | eu-west-1 (Irska) | S3 Cross-Region Replication za kritične podatke |

---

## 7. Ocenjeni mesečni stroški (po migraciji)

| Storitev | Mesečni strošek |
|---------|----------------|
| EC2 (5 instanc) | 567 € |
| ECS Fargate | 98 € |
| RDS PostgreSQL Multi-AZ | 480 € |
| DocumentDB | 220 € |
| S3 + EFS | 85 € |
| CloudFront | 80 € |
| WAF | 45 € |
| Data transfer (out) | 120 € |
| CloudWatch, CloudTrail | 35 € |
| **Skupaj** | **1.730 €** |
