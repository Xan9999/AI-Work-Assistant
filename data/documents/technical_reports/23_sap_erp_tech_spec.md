# Tehnična specifikacija — SAP S/4HANA arhitektura
## Projekt: KOVA-2024-ERP | Dokument: TECH-SPEC-001

**Verzija:** 2.1  
**Datum:** 2024-03-15  
**Avtor:** Tomaž Kržič  
**Status:** ODOBREN

---

## 1. Pregled arhitekture

SAP S/4HANA bo nameščen on-premise na infrastrukturi naročnika Kova d.o.o. v njihovem podatkovnem centru v Ljubljani.

### 1.1 Strežniška konfiguracija

| Komponenta | Specifikacija | Količina |
|-----------|--------------|---------|
| SAP aplikacijski strežnik | HPE ProLiant DL380 Gen10, 2x Xeon Gold 6230, 512 GB RAM, 4x 1.92 TB SSD | 2 |
| SAP HANA DB strežnik | HPE ProLiant DL560 Gen10, 4x Xeon Gold 6230, 1.5 TB RAM, 8x 3.84 TB NVMe | 1 |
| Backup strežnik | HPE ProLiant DL360 Gen10, 2x Xeon Silver 4214, 128 GB RAM | 1 |
| SAN storage | HPE MSA 2060 SAN, 48x 3.84 TB SSD, skupaj 184 TB bruto | 1 |

### 1.2 Omrežna arhitektura

```
Internet
   ↓
Palo Alto Firewall (DMZ)
   ↓
Core switch (Cisco Catalyst 9300)
   ├── SAP App Server 1 (10.10.1.11)
   ├── SAP App Server 2 (10.10.1.12)
   ├── HANA DB Server  (10.10.1.20) — izoliran VLAN
   └── Backup Server   (10.10.1.30)
```

---

## 2. SAP S/4HANA konfiguracija

### 2.1 Sistem krajina (System Landscape)

| Sistem | SID | Namen | Verzija |
|--------|-----|-------|---------|
| Development | D01 | Razvoj in konfiguracija | S/4HANA 2023 |
| Quality | Q01 | Testiranje (UAT) | S/4HANA 2023 |
| Production | P01 | Produkcija | S/4HANA 2023 |

Transportni sistem: CTS (Change and Transport System) — D01 → Q01 → P01.

### 2.2 SAP HANA konfiguracija

| Parameter | Vrednost |
|---------|---------|
| HANA verzija | SAP HANA 2.0 SPS 07 |
| Način delovanja | Scale-up (single node) |
| Način replikacije | System Replication (sinhrono, Q01 kot DR) |
| Backup strategija | Dnevni full backup + log backup vsake 30 min |
| Backup cilj | HPE MSA SAN + off-site (Veeam + cloud) |
| RPO | 30 minut |
| RTO | 2 uri |

### 2.3 Licenčna konfiguracija

| Tip licence | Število | Letni strošek (ocena) |
|------------|---------|----------------------|
| SAP S/4HANA Professional User | 15 | ~45.000 € |
| SAP S/4HANA Limited Professional | 30 | ~27.000 € |
| SAP S/4HANA Employee User | 50 | ~12.500 € |
| **Skupaj** | **95** | **~84.500 €/leto** |

---

## 3. Integracijska arhitektura

### 3.1 Magento 2 integracija

Namesto SAP Integration Suite (predrago) je implementiran **custom Python middleware**.

| Komponenta | Opis |
|-----------|------|
| Runtime | Python 3.12, FastAPI |
| Deployment | Docker na ločenem Linux strežniku |
| Protokol SF→SAP | BAPI klici prek pyrfc knjižnice |
| Protokol SAP→Magento | Magento REST API (OAuth 2.0) |
| Sinhronizacija naročil | Real-time webhook iz Magento |
| Sinhronizacija zalog | Batch, vsake 15 minut |
| Error handling | Dead letter queue v PostgreSQL |

**Opozorilo**: Custom middleware pomeni, da Nexus ali Kova IT mora vzdrževati to kodo. Priporočamo vsaj 2x letno varnostni pregled in posodobitev odvisnosti.

### 3.2 Manhattan Associates WMS

Integracija prek SAP standardnega IDocs vmesnika:
- MBGMCR01 — Gibanje zalog (WMS → SAP)
- WMMBXY — Nalog za skladiščenje (SAP → WMS)
- WHSCON — Potrditev uskladiščenja

---

## 4. Varnost

### 4.1 SAP avtorizacijski koncept

Vloge:

| Vloga | Opis | Število uporabnikov |
|-------|------|---------------------|
| Z_FI_ACCOUNTANT | Knjiženje v FI | 8 |
| Z_FI_READONLY | Branje FI | 15 |
| Z_MM_PURCHASING | Nabava | 6 |
| Z_SD_SALES | Prodaja | 20 |
| Z_BASIS_ADMIN | Sistemski administrator | 3 |
| Z_SUPERUSER | Polni dostop (samo produkcija!) | 2 |

### 4.2 Omrežna varnost

- SAP GUI dostop samo iz internega omrežja (VPN za remote)
- SAP Web Dispatcher v DMZ za fiori/web dostop
- TLS 1.3 za vse zunanjo komunikacijo
- Revizijska sled: vse transakcije v SAP beležene

---

## 5. Podatkovna migracija — tehnični postopek

### 5.1 Orodje: SAP LTMC

LTMC (Legacy Transfer and Migration Cockpit) bo uporabljen za strukturirano migracijo:

| Predmet migracije | LTMC Migration Object | Rok validacije |
|------------------|-----------------------|---------------|
| Kontni plan | G/L Account | 2024-05-01 |
| Stranke | Business Partner (Customer) | 2024-05-15 |
| Dobavitelji | Business Partner (Vendor) | 2024-05-15 |
| Artikli | Material Master | 2024-06-01 |
| Osnovna sredstva | Fixed Asset | 2024-06-15 |
| Odprti saldi | G/L Open Items | 2024-08-01 |

### 5.2 Čiščenje podatkov

Janez Novak bo razvil Python skripte za predpripravo podatkov iz NAV:
- Deduplikacija partnerjev (~340 duplikatov identificiranih)
- Normalizacija davčnih številk
- Validacija IBAN računov
- Maping NAV kontov → SAP kontov (ročna validacija Maja Horvat)

Ocenjen čas čiščenja: **6 tednov** (januari 2024 ocena: 3–4 tedne — povečano po analizi kakovosti).
