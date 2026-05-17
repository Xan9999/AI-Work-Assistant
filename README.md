# Pogovorni RAG asistent — Nexus Consulting

Prototip internega pogovornega asistenta za IT svetovalno podjetje. Odgovarja na vprašanja nad 33 sintetičnimi dokumenti (zapisniki sestankov, projektne ponudbe, tehnična poročila) z natančnim sklicevanjem na vir, zaznavanjem protislovij med dokumenti in podporo za vprašanja, ki zahtevajo združevanje informacij iz več virov.

**Evalvacijski rezultat (LLM-as-judge, 30 vprašanj):** 81.7 % (angleščina) · 80.6 % (slovenščina)

---

## Zahteve

- Python 3.10+
- OpenAI API ključ (`gpt-4o-mini` ali novejši)
- ~1 GB RAM, ~600 MB prostora na disku (modeli)

---

## Namestitev

**1. Namesti odvisnosti**
```bash
pip install -r requirements.txt
```

**2. Nastavi API ključ**

Ustvari `.env` v korenu projekta:
```
CHATGPT_API_KEY=sk-...
CHATGPT_MODEL=gpt-4o-mini
```

**3. Prenesi modele lokalno** *(enkrat)*
```bash
python src/download_models.py
```
Modeli se shranijo v `data/models/` — zagoni brez interneta delujejo.

**4. Indeksiraj dokumente** *(enkrat ali ob spremembi dokumentov)*
```bash
python src/ingest.py
```

**5. Zaženi asistenta**
```bash
python src/cli.py
```

---

## Uporaba CLI

```
Nexus Consulting RAG Assistant
Vnesi vprašanje ali ukaz:
  /history   — prikaži zgodovino pogovora
  /clear     — počisti zgodovino
  /quit      — izhod

> Kateri projekti so vključevali migracijo na oblak in kaj smo se naučili?
> Kdo iz ekipe ima izkušnje tako z ERP kot z AWS?
> Kdaj je projekt Atlas šel v produkcijo?
```

Asistent navede vir za vsak odgovor (dokument + razdelek) in eksplicitno opozori, kadar dokumenti vsebujejo nasprotujoče si informacije.

---

## Evalvacija

**Angleška vprašanja (15):**
```bash
python eval/evaluate.py
```

**Slovenska vprašanja (15):**
```bash
python eval/evaluate.py \
  --questions eval/questions_sl.json \
  --results   eval/results_sl.json \
  --report    eval/report_sl.md
```

| Argument | Privzeto | Opis |
|---|---|---|
| `--questions` | `eval/questions.json` | Vhodni nabor vprašanj (JSON) |
| `--results` | `eval/results.json` | Izhod: ocene po vprašanjih (JSON) |
| `--report` | `eval/report.md` | Izhod: poročilo (Markdown) |

Evalvacija pokriva 4 tipe vprašanj: enostavno iskanje, večskočno, neodgovorljivo (test halucinacij), protislovno (trik vprašanja). Sodnik je GPT-4o-mini z ocenjevalnimi kriteriji faktična pravilnost, citiranje virov, ravnanje z negotovostjo in zaznavanje protislovij (vsak 0–3).

---

## Arhitektura

```
Vprašanje
    │
    ▼
Razširitev kratkih sledilnih vprašanj (pogovorna zgodovina)
    │
    ▼
Klasifikacija: simple / multi_hop
    │
    ├── simple ──────────────────────────────────────────┐
    │                                                    │
    ▼                                                    ▼
HyDE (hipotetični odgovor)              Razgradnja na 2–4 podvprašanj
    │                                       │  (za vsako: HyDE + retrieval)
    ▼                                       ▼
BM25(poizvedba) + vektor(HyDE)      BM25 + vektor na podvprašanje
    │                                       │  (reranker ocenjuje glede na
    │                                       │   podvprašanje — ne glavno)
    └──────────────────┬────────────────────┘
                       ▼
                  RRF fuzija
                       │
                       ▼
            Cross-encoder reranker
            (adaptivni k: 5 / 8 / 10
             glede na tip poizvedbe)
                       │
                       ▼
       Razširitev s sosednjimi odlomki
                       │
                       ▼
    Zaznavanje protislovij — 2 retrieval passa:
      1. brez HyDE (široka pokritost teme)
      2. inverzni HyDE (privabi nasprotujoče dokumente)
                       │
                       ▼
    Generiranje odgovora (GPT) — z opozorilom
    o protislovju vstavljenim v kontekst
                       │
                       ▼
                 Končni odgovor
```

---

## Struktura projekta

```
AI-Work-Assistant/
├── src/
│   ├── ingest.py          # Razrez dokumentov, BM25 + ChromaDB indeksiranje
│   ├── retrieval.py       # HybridRetriever: BM25 + vektor + RRF + reranker
│   ├── rag.py             # RAGAssistant: klasifikacija, HyDE, multi-hop, protislovja
│   ├── cli.py             # Interaktivni CLI
│   └── download_models.py # Enkratni prenos modelov v data/models/
├── eval/
│   ├── questions.json     # 15 vprašanj (angleščina)
│   ├── questions_sl.json  # 15 vprašanj (slovenščina)
│   ├── results.json       # Rezultati evalvacije (angleščina)
│   ├── results_sl.json    # Rezultati evalvacije (slovenščina)
│   └── evaluate.py        # LLM-as-judge evalvacija
├── data/
│   ├── documents/         # 33 sintetičnih dokumentov (Markdown + TXT)
│   ├── CORPUS_MANIFEST.md # Popis dokumentov in zasnovanih napak
│   ├── models/            # Lokalno shranjeni modeli (ni v git)
│   ├── bm25_index.pkl     # BM25 indeks (ni v git)
│   └── chroma_db/         # ChromaDB vektorski indeks (ni v git)
├── REPORT.md              # Arhitekturno poročilo
├── .env                   # API ključi (ni v git)
└── requirements.txt
```

---

## Modeli

| Vloga | Model | Lokacija |
|---|---|---|
| Vektorizacija | `intfloat/multilingual-e5-base` | `data/models/` |
| Reranker | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | `data/models/` |
| Generiranje / evalvacija | `gpt-4o-mini` (nastavljivo) | OpenAI API |

Embedding in reranker sta večjezična — podpirata slovenščino in angleščino brez ločenih modelov.

---

## Korpus dokumentov

33 sintetičnih dokumentov podjetja Nexus Consulting d.o.o. (IT svetovanje):

| Tip | Število | Primeri |
|---|---|---|
| Zapisniki sestankov | 12 | kick-off, retrospektiva, steering committee |
| Projektne ponudbe in poročila | 10 | SAP ERP, cloud migracija, BI implementacija |
| Tehnična poročila | 11 | matrika kompetenc, tehnična specifikacija, lessons learned |

Dokumenti vsebujejo zasnovane napake: 4 dokumenti z različnimi datumi go-live za isti projekt (Q14), matriki kompetenc za leti 2023 in 2024 z različnimi vrednostmi (Q15/SL14), ter nekateri dokumenti s podatki, ki niso v korpusu (test halucinacij).
