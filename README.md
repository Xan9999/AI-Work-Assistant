# Pogovorni asistent za interna dokumenta — Nexus Consulting

Hibridni RAG asistent (BM25 + vektorsko iskanje + reranker), ki odgovarja na vprašanja o internih dokumentih podjetja Nexus Consulting d.o.o. Podpira slovenščino, večskočne poizvedbe, zaznavanje protislovij in pogovorno zgodovino.

---

## Zahteve

- Python 3.10+
- OpenAI API ključ (`gpt-4o-mini` ali drugo GPT-4 serijo)
- ~1 GB RAM, ~600 MB prostor na disku (za modele)

---

## Namestitev

**1. Namesti odvisnosti**
```bash
pip install -r requirements.txt
```

**2. Nastavi okoljske spremenljivke**

Ustvari datoteko `.env` v korenu projekta:
```
CHATGPT_API_KEY=sk-...
CHATGPT_MODEL=gpt-4o-mini
```

**3. Prenesi modele lokalno**
```bash
python src/download_models.py
```
Modeli se shranijo v `data/models/` in se ne prenašajo ob vsakem zagonu.

**4. Indeksiraj dokumente**
```bash
python src/ingest.py
```
Zgradi BM25 indeks (`data/bm25_index.pkl`) in ChromaDB vektorski indeks (`data/chroma_db/`).

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

> Katere certifikate ima Luka Zupan?
```

Asistent odgovori z odlomki iz dokumentov, navedenimi viri in opozorili, če dokumenti vsebujejo nasprotujoče si informacije.

---

## Evalvacija

**Privzeti nabor 15 vprašanj (angleščina):**
```bash
python eval/evaluate.py
```

**Kontrolni nabor 15 vprašanj v slovenščini:**
```bash
python eval/evaluate.py \
  --questions eval/questions_sl.json \
  --results eval/results_sl.json \
  --report eval/report_sl.md
```

**Argumenti:**
| Argument | Privzeto | Opis |
|----------|----------|------|
| `--questions` | `eval/questions.json` | Pot do JSON datoteke z vprašanji |
| `--results` | `eval/results.json` | Izhod: rezultati po vprašanjih (JSON) |
| `--report` | `eval/report.md` | Izhod: človeško berljivo poročilo (Markdown) |

Evalvacija uporablja GPT-4o-mini kot sodnika (LLM-as-judge) in ocenjuje 4 kriterije: faktično pravilnost, citiranje virov, ravnanje z negotovostjo in zaznavanje protislovij.

---

## Struktura projekta

```
AI-Work-Assistant/
├── src/
│   ├── ingest.py          # Razrez dokumentov, BM25 + ChromaDB indeksiranje
│   ├── retrieval.py       # HybridRetriever: BM25 + vektorsko + RRF + reranker
│   ├── rag.py             # RAGAssistant: klasifikacija, HyDE, večskočno iskanje
│   ├── cli.py             # Interaktivni CLI
│   └── download_models.py # Enkratni prenos modelov v data/models/
├── eval/
│   ├── questions.json     # 15 evalvacijskih vprašanj (angleščina)
│   ├── questions_sl.json  # 15 kontrolnih vprašanj (slovenščina)
│   └── evaluate.py        # LLM-as-judge evalvacija
├── data/
│   ├── documents/         # 33 sintetičnih dokumentov (Markdown)
│   ├── models/            # Lokalno shranjeni modeli (ni v git)
│   ├── bm25_index.pkl     # BM25 indeks (ni v git)
│   └── chroma_db/         # ChromaDB vektorski indeks (ni v git)
├── REPORT.md              # Arhitekturno poročilo (slovenščina)
├── .env                   # API ključi (ni v git)
└── requirements.txt
```

---

## Arhitektura

```
Vprašanje
    │
    ▼
Klasifikacija (simple / multi_hop)
    │
    ├─── simple ──────────────────────────────────┐
    │                                             │
    ▼                                             ▼
HyDE (hipotetični odgovor)            Razgradnja na 2-4 podvprašanj
    │                                     │ (za vsako: HyDE + retrieval)
    ▼                                     ▼
BM25(poizvedba) + vektor(HyDE)      BM25 + vektor na podvprašanje
    │                                     │
    └──────────────┬──────────────────────┘
                   ▼
              RRF fuzija
                   │
                   ▼
         Cross-encoder reranker
                   │
                   ▼
        Razširitev s sosednjimi odlomki
                   │
                   ▼
          Generiranje odgovora (GPT)
                   │
                   ▼
        Zaznavanje protislovij (k=10, brez HyDE)
                   │
                   ▼
               Končni odgovor
```

---

## Modeli

| Vloga | Model | Lokacija |
|-------|-------|----------|
| Vektorizacija | `intfloat/multilingual-e5-base` | `data/models/` |
| Reranker | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | `data/models/` |
| Generiranje | `gpt-4o-mini` (nastavljivo) | OpenAI API |

---

## Nabori evalvacijskih vprašanj

| Datoteka | Jezik | Vprašanj | Tipi |
|----------|-------|----------|------|
| `eval/questions.json` | angleščina | 15 | simple, multi_hop, unanswerable, trick_contradictory |
| `eval/questions_sl.json` | slovenščina | 15 | simple, multi_hop, unanswerable, trick_contradictory |
