# Poročilo — RAG asistent za Nexus Consulting

## Izbrana arhitektura in kompromisi

Sistem uporablja hibridno iskanje: BM25 (ključne besede) + vektorsko iskanje (semantika), združeno z Reciprocal Rank Fusion, nato pa še cross-encoder reranker, ki vrednoti pare (poizvedba, odlomek) skupaj. Povrh tega sta implementirana HyDE (generiranje hipotetičnega odgovora pred iskanjem) in razširitev odlomkov s sosedi (sentence-window overlap).

**Zakaj ta pristop:** Nobena metoda sama ne zadostuje. BM25 dobro deluje pri iskanju eksaktnih imen in kratic (npr. "DataSync", "Atlas"), vektorsko iskanje pa ujame semantično sorodne odlomke, tudi če ne vsebujejo istih besed. Reranker nato iz 20 kandidatov izbere 5 najboljših z natančnejšim primerjanjem — je počasnejši, a bistveno bolj precizen. HyDE izboljša vektorsko iskanje, ker je hipotetični odgovor ("Atlas je šel v produkcijo decembra 2024") jezikovno bližje dokumentom kot surovo vprašanje ("Kdaj je šel Atlas v produkcijo?").

**Kompromisi:** Vsak korak doda latenco. Preprosta poizvedba traja ~10 s, večskočna (~35 s) pa zahteva 4–8 zaporednih klicev na LLM. Sistem je tudi drag pri evalvaciji — vsako vprašanje porabi žetone za klasifikacijo, HyDE, iskanje in oceno sodnika.

---

## Kaj sem med razvojem spremenil

**1. Reranker: angleški → večjezični model.**
Začel sem z `ms-marco-MiniLM-L-6-v2`, ki je treniran izključno na angleških podatkih. Ko sem pognal prve teste s slovenskimi dokumenti, sem opazil, da reranker slabo rangira slovensko besedilo. Zamenjal sem ga z `mmarco-mMiniLMv2-L12-H384-v1` (XLM-RoBERTa, treniran na večjezičnem MS MARCO), ki brez težav obdeluje slovenščino.

**2. Dodal HyDE in sentence-window overlap — nista bila v začetnem načrtu.**
Začetni načrt je predvideval samo BM25 + vektorsko iskanje + reranker. Med razvojem sem ugotovil, da kratki odlomki pogosto "odrežejo" odgovor ravno na meji — ključna informacija je v sosednjem kosu. Sentence-window overlap to reši brez ponovne vektorizacije. HyDE sem dodal, ker sem opazil, da so vprašanja stilistično drugačna od dokumentov, kar znižuje vektorski priklic.

**3. Shranjevanje modelov lokalno namesto iz HuggingFace predpomnilnika.**
Sprva so se modeli nalagali iz sistemskega predpomnilnika. Ker je predpomnilnik nezanesljiv (antivirusni programi, čiščenje diska, nova naprava), sem dodal `download_models.py`, ki modele enkrat shrani v `data/models/` znotraj projekta. Nalaganje zdaj vedno deluje brez internetne povezave ali skrbi za pot predpomnilnika.

---

## Kje sistem odpove

**Q08 (4/12) — večskočno vprašanje o članih ekipe z izkušnjami pri ERP in oblaku.**
Sistem je pravilno razstavil vprašanje na podvprašanja, a GPT je iz pridobljenih odlomkov generiral napačna imena. Vzrok: informacije so razpršene po tabelah v dveh različnih matricah znanj, razrezi odlomkov pa so prerezali vrstice tabel ločeno od glav stolpcev, zato model ni mogel pravilno brati vrednosti. **Ta napaka je bila odpravljena** — glejte razdelek spodaj.

**Q14 (6/12) — kdaj je projekt Atlas šel v produkcijo (protislovni dokumenti).**
Sistem je vrnil datum iz najvidnejšega dokumenta (memo o go-live) brez opomnika, da ga tri drugi dokumenti izpodbijajo. Protislovje je v korpusu eksplicitno zasnovano (štirje različni datumi), a sistem ga ni zaznal, ker iskanje vrne "najboljše" odlomke, ki si med seboj tipično strinjajo. Delno odpravljena z zaznavanjem protislovij — glejte razdelek spodaj.

**Q15 (5/12) → Q15 (6/12) — spretnosti Janeza Novaka (razlika med matriko 2023 in 2024).**
Sistem je odgovoril z eno vrednostjo, ne da bi omenil, da se med letoma razlikuje. Po implementaciji zaznavanja protislovij sistem zdaj zazna in opozori na razliko med matrikama. Ocena CH se je izboljšala iz 0 na 2.

---

## Implementirana izboljšava: atomarni tabelarični odlomki

Med analizo napak Q08 sem ugotovil, da razrez dokumentov na odlomke loči naslov podrazdelka (`### 2.1 Cloud platforme`) od tabele, ki mu sledi — ob meji odlomka glava stolpcev ostane v enem kosu, vrstice podatkov pa v naslednjem. GPT brez glav stolpcev ne more pravilno interpretirati vrednosti.

Popravek: v `src/ingest.py` sem dodal funkcijo `_atomic_blocks()`, ki pri razrezu dolgih razdelkov najprej združi vsak `### podnaslov` z blokom, ki mu neposredno sledi (tabelo). Šele nato se izvaja seštevanje velikosti odlomkov. Na ta način nobena tabela ni nikoli ločena od svojih glav stolpcev, četudi presega ciljno velikost odlomka. Indeksa sta bila po spremembi znova zgrajena.

---

## Implementirana izboljšava: večskočno iskanje brez skupnega rerankiranja

Izvirni večskočni pipeline je za vsako podvprašanje poklical `search(sub_q)` (interno: BM25 + vektorsko iskanje + RRF + reranker glede na `sub_q`), nato pa vse pridobljene odlomke **znova rerankal glede na glavno vprašanje**. Ta drugi reranking je ubil odlomke, ki odgovarjajo le enemu delu večdelnega vprašanja — npr. odlomek z oblačnimi veščinami ekipe dobi nizek score pri vprašanju "kdo ima tako ERP **kot** oblačne izkušnje?", ker en odlomek ne more odgovoriti na oba dela hkrati. Rezultat: Q08 je vrnil "ne morem odgovoriti", čeprav so matrike znanj bile v korpusu.

Popravek v `src/rag.py`: skupni reranking je odstranjen. Namesto tega ohranimo top-5 odlomkov na podvprašanje (že renkani glede na podvprašanje) in neposredno združimo rezultate. Za presojo koristnosti konteksta zdaj upoštevamo najboljši score iz faze podvprašanj, ne finalnih odlomkov.

Dodatno: reranker `predict()` zdaj kliče z `batch_size=4` (namesto privzetih 32), kar prepreči zrušitev z "out of memory" pri zaporednem vrednotenju 15 vprašanj.

**Vpliv:** multi-hop 77.1 % → 81.2 %, simple search 90.3 % → 94.4 %.

---

## Implementirana izboljšava: zaznavanje protislovij

Pred generiranjem odgovora sistem požene **dodatni retrieval** brez HyDE, da zbere širok nabor odlomkov o temi. Razlog za odsotnost HyDE: pri prvotnem iskanju HyDE usmeri vektorsko iskanje k dokumentom, ki potrjujejo določen odgovor. Za zaznavanje protislovij pa želimo pokritost teme neodvisno od vsebine odgovora.

Zbrane odlomke GPT pregleda z vprašanjem: *"Ali kateri par odlomkov navaja eksplicitno drugačno vrednost za isto dejstvo?"* Prompt je omejen na prava protislovja (različni datumi, različne številke) in ne sproži za dopolnilne informacije ali različni vlogi (npr. CEO vs IT direktor). Če je protislovje zaznano, se opozorilo vstavi **v kontekst pred generiranjem odgovora** — GPT tako razreši protislovje eksplicitno znotraj odgovora, namesto da dobi post-hoc prilepljeno opozorilo, ki ga ne upošteva.

**Nadgradnja za večskočne poizvedbe:** pri večskočnih vprašanjih je bil prvotni broad retrieval narejen z originalnim sestavljenim vprašanjem. To je problem, ker reranker odlomek o ERP veščinah oceni slabo pri vprašanju "kdo ima ERP *in* cloud izkušnje?" — en odlomek ne more odgovoriti na oba dela hkrati. Popravek: broad retrieval za zaznavanje protislovij se zdaj izvaja ločeno za vsako podvprašanje (po `CONTRADICTION_CHECK_K // n` odlomkov na podvprašanje), rezultati pa se združijo. Reranker vsako podtemo oceni v svojem kontekstu.

**Rezultati po implementaciji:**
- Neodgovorljiva vprašanja: 75 % → **100 %** (popravek SC — ko ni dokumentov, ni kaj citirati; to ni napaka citiranja)
- Q15 CH: 0 → 2 (protislovje med matrikama 2023/2024 je zaznano)
- Q14 CH: ostaja 0 — glejte razdelek spodaj
- **Skupaj: 80.0 % → 83.3 %**

---

## Implementirana izboljšava: adaptivno število vrnjenih odlomkov

Analiza napak je pokazala dva vzorca, kjer privzeti `k=5` sistematično vrne premalo odlomkov:

1. **Matrična vprašanja** — vrednost je presek vrstice (oseba) in stolpca (veščina); en odlomek pokrije le del tabele, zato je potrebnih več odlomkov za celotno sliko.
2. **Enumeracijska vprašanja** — vprašanja tipa "kateri projekti / kateri člani" zahtevajo pokritost celotnega korpusa, ne le najboljšega zadetka.

Popravek v `src/retrieval.py`: `search()` pregleda poizvedbo in avtomatsko poveča `k`:
- Besede iz `ENUM_KEYWORDS` (kateri, which, seznam, list, vsi, all, projekti, člani…) → `k = max(k, 10)`
- Besede iz `MATRIX_KEYWORDS` (ocena, kompetenca, matrika, certifikat, skill, rating…) → `k = max(k, 8)`
- Ostale poizvedbe → `k` nespremenjen

Enumeracijska pravila imajo prednost pred matričnimi. Ker se `k` poveča samo pri rerankerju (ne pri BM25 ali vektorskem iskanju), dodaten strošek je minimalen.

---

## Implementirana izboljšava: navodila za razreševanje protislovij in izčrpnost

Analiza evalvacijskih napak je pokazala dva vzorca napačnih odgovorov, ki jih ni povzročal pomanjkljiv retrieval, temveč pomanjkljiva navodila za generiranje:

**Datumska protislovja (Q14):** sistem je zaznal protislovje med dokumenti, a GPT je v odgovoru obdržal datum iz prvega najdenega dokumenta (september 2024) namesto datuma iz najnovejšega dokumenta (december 2024). Problem ni bil v iskanju, temveč v odsotnosti eksplicitnega pravila za razreševanje.

**Nepopolna enumeracija (Q09, Q10, SL09):** vprašanja kot "kateri projekti so presegli rok?" so dobila odgovor z 1–2 projekti namesto vseh, ker GPT ni imel navodila, da mora pregledati vse vire.

Popravek v `SYSTEM_PROMPT` (`src/rag.py`):
- **Pravilo 4:** pri protislovnih datumih ali vrednostih za isto entiteto izberi vrednost iz **najnovejšega dokumenta** kot merodajno in naštej vse verzije kronološko. Brez tihe izbire ene verzije.
- **Pravilo 7:** za vprašanja z "kateri projekti / kateri člani / seznam vseh X" mora biti odgovor **izčrpen** — preglej vse vire in vključi vsako ujemajočo entiteto, ne le najprominentnejše.

---

## Kaj bi naredil drugače z več časa

Prioriteta bi bila **popolno razreševanje revizijskih protislovij** (Q14 CH ostaja 0): kljub implementiranemu pravilu 4 v system promptu sistem še vedno ne razloži vseh štirih datumskih revizij v enem odgovoru. Problem je v retrieval fazi — ne vsi štirje dokumenti z datumi pristanejo med top-k rezultati hkrati. Rešitev bi bila eksplicitna detekcija "revizijske verige": pri vprašanjih o datumih za isti projekt zberi odlomke iz vseh dokumentov, ki omenjajo projekt in datum, ne le tistih z najvišjim rerank score.

Druga prioriteta: **vzporedni HyDE klici** z `asyncio` za večskočne poizvedbe — 4 podvprašanja bi se obdelala hkrati, kar bi latenco zmanjšalo s ~35 s na ~15 s.

---

## Kako sem uporabljal AI asistente

Celoten projekt sem razvil z **Claude Code** (CLI orodje). Konkretno:

- **Generiranje dokumentov**: Vseh 33 sintetičnih dokumentov je napisal Claude na podlagi opisa podjetja in navodil za zasnovane napake (protislovni datumi, razlike v matrikah). Sam sem določil strukturo in vrste dokumentov, Claude pa je napisal vsebino.
- **Pisanje kode**: Vsa koda (`ingest.py`, `retrieval.py`, `rag.py`, `cli.py`, `evaluate.py`) je nastala v pogovoru s Claude Code. Opisal sem, kaj želim (npr. "dodaj HyDE in sentence-window overlap"), Claude je predlagal implementacijo, jaz sem jo pregledal in odobril.
- **Razhroščevanje**: Ko je sistem ob zagonu sesul (segmentation fault), sem Claude Code prosil za koračno izolacijo — vsak komponento posebej. Skupaj sva ugotovila, da je sesutje prehodne narave (verjetno pritisk na pomnilnik), ne napaka v kodi.
- **Meje uporabe**: Arhitekturne odločitve (kateri reranker, zakaj HyDE, kateri kompromisi) so bile skupne — Claude je predlagal možnosti z argumenti, jaz sem izbral. Evalvacijske rezultate in analizo napak sem interpretiral sam, Claude je le formatiral tabele.
