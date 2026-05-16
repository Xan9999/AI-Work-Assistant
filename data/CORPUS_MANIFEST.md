# Corpus Manifest — Nexus Consulting Document Corpus

**Total documents:** 33  
**Company:** Nexus Consulting d.o.o. (IT consulting, Ljubljana)  
**Languages:** Slovenian (primary), some English sections

---

## Document Index

### Meeting Minutes (12 documents)

| File | Description | Date | Key topics | Has table |
|------|-------------|------|-----------|-----------|
| 01_kova_erp_kickoff.md | Kick-off: Kova ERP project | 2024-01-15 | SAP S/4HANA, go-live Oct 2024, project scope | Yes |
| 02_atlas_cloud_weekly_march.md | Atlas weekly sync | 2024-03-12 | .NET migration, go-live revision Q3 2024 | No |
| 03_atlas_steering_committee.md | Atlas steering committee | 2024-05-07 | Budget status, go-live revised Dec 2024 | Yes |
| 04_merkur_retrospective.md | Merkur project retrospective | 2023-11-08 | PHP migration lessons, PostgreSQL | No |
| 05_internal_resource_planning.md | Internal Q1 2024 planning | 2024-01-08 | Team allocation, over-allocation Janez | Yes |
| 06_meridian_sprint_review.md | Meridian Sprint 4 review | 2024-06-03 | PDF performance, API progress | No |
| 07_datasync_risk_review.md | DataSync risk review | 2024-04-22 | GDPR, Salesforce licence risk | Yes |
| 08_argon_cloud_kickoff.md | Argon Azure migration kick-off | 2024-02-19 | Azure, hard deadline May 31 2024 | Yes |
| 09_helios_closeout.md | Helios BI close-out | 2022-09-14 | Tableau, DWH, project closure | No |
| 10_kova_erp_architecture_review.md | Kova architecture review | 2024-03-05 | Go-live revised Q1 2025 ⚠️ contradicts #01 | No |
| 11_datasync_incident.md | DataSync production incident | 2024-08-03 | Salesforce field rename, 5h downtime | Yes |
| 12_nova_logistics_crm_kickoff.md | Nova Logistics CRM kick-off | 2023-03-06 | Salesforce Sales Cloud, SAP B1 | Yes |

### Proposals and Project Reports (10 documents)

| File | Description | Date | Key topics | Has table |
|------|-------------|------|-----------|-----------|
| 13_kova_erp_proposal.md | Kova ERP proposal | 2023-11-28 | SAP S/4HANA, 217,300 EUR, go-live Oct 2024 | Yes |
| 14_atlas_cloud_proposal.md | Atlas AWS migration proposal | 2023-08-15 | AWS, 142,000 EUR, go-live Q2 2024 ⚠️ | Yes |
| 15_merkur_final_report.md | Merkur final project report | 2023-11-15 | PHP 8.2, PostgreSQL, completed | Yes |
| 16_meridian_proposal.md | Meridian web platform proposal | 2024-01-22 | Django, React, 68,000 EUR, go-live Sep 2024 | Yes |
| 17_helios_bi_report_2022.md | Helios BI report (2022) ⚠️ OUTDATED | 2022-09-20 | Tableau Server 2022.1, SSIS, outdated info | Yes |
| 18_argon_cloud_final_report.md | Argon Azure migration final report | 2024-06-10 | Azure, completed on time, lessons | Yes |
| 19_datasync_proposal.md | DataSync integration proposal | 2024-03-18 | Salesforce+SAP B1, 56,000 EUR | Yes |
| 20_nova_logistics_crm_report.md | Nova Logistics mid-project report | 2023-07-15 | Salesforce, SAP B1 integration, data quality | Yes |
| 21_techgroup_erp_proposal.md | TechGroup ERP proposal (rejected) | 2024-02-05 | ERP comparison, BC recommended, rejected | Yes |
| 22_meridian_midproject_report.md | Meridian mid-project report | 2024-06-10 | Sprint 4, 1-2 weeks behind, go-live Sep 2024 | No |

### Technical Reports and Specifications (11 documents)

| File | Description | Date | Key topics | Has table |
|------|-------------|------|-----------|-----------|
| 23_sap_erp_tech_spec.md | SAP S/4HANA technical spec | 2024-03-15 | Server config, HANA, migration, licenses | Yes |
| 24_aws_atlas_architecture.md | AWS Atlas architecture spec | 2024-04-08 | VPC, EC2, RDS, security, costs | Yes |
| 25_team_skills_matrix_2024.md | Team skills matrix 2024 ✓ CURRENT | 2024-01-10 | All team members, all technologies, certs | Yes |
| 26_team_skills_matrix_2023.md | Team skills matrix 2023 ⚠️ OUTDATED | 2023-01-15 | Older skill levels, fewer certs | Yes |
| 27_cloud_migration_lessons_learned.md | Cloud migration lessons (AWS+Azure) | 2024-07-01 | Lessons from Atlas+Argon, recommendations | Yes |
| 28_datasync_api_spec.md | DataSync API specification | 2024-06-15 | FastAPI, endpoints, GDPR, monitoring | Yes |
| 29_erp_vendor_comparison.md | ERP vendor comparison | 2024-01-20 | SAP vs BC vs Odoo, TCO, recommendations | Yes |
| 30_meridian_tech_spec.md | Meridian technical specification | 2024-04-10 | Django, React, AWS, security | Yes |
| 31_datasync_postmortem.md | DataSync incident post-mortem | 2024-08-07 | Root cause, 5h downtime, fixes | Yes |
| 32_nexus_standard_stack_2024.txt | Nexus standard tech stack | 2024-02-01 | Python, Django, AWS, Terraform defaults | No |
| 33_atlas_go_live_memo.txt | Atlas go-live confirmation memo | 2024-11-28 | Go-live Dec 15 2024 confirmed ⚠️ | No |

---

## Engineered Noise

### Contradictions (for evaluation)
- **Atlas go-live date**: Q2 2024 (proposal) → Q3 2024 (Mar meeting) → Dec 2024 (May steering) → Dec 15 2024 (Nov memo)
- **Kova go-live date**: Oct 1 2024 (kick-off) → Q1 2025 (architecture review)
- **Janez Novak skills**: Different scores in 2023 vs 2024 matrix

### Outdated documents
- `17_helios_bi_report_2022.md` — 2022, Tableau 2022.1 EOL warning, outdated recommendations
- `26_team_skills_matrix_2023.md` — superseded by 2024 version

### Documents with no answer in corpus (for hallucination testing)
- CEO of any client company
- Nexus Consulting annual revenue
- Penetration test results
- Number of employees at any client
- Personal salary information

---

## Key Entities

**Nexus team**: Ana Kovač (PM), Luka Zupan (DevOps/AWS), Janez Novak (developer), Tomaž Kržič (architect), Maja Horvat (SAP/ERP), Sara Petric (data), Nina Vidmar (frontend), Rok Bajt (BA)

**Clients**: Kova d.o.o. (ERP), Atlas d.o.o. (AWS cloud), Merkur IT (modernization), Meridian d.o.o. (web platform), Helios d.o.o. (BI), DataSync d.o.o. (integration), Argon d.o.o. (Azure cloud), Nova Logistics d.o.o. (CRM), TechGroup d.o.o. (ERP evaluation — rejected)
