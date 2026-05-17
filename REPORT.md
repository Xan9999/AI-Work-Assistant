# Poročilo — Pogovorni RAG asistent za Nexus Consulting

## Arhitektura in kompromisi

Izbral sem **hibridni RAG**: BM25 (ključne besede) + vektorsko iskanje (semantika), združena z Reciprocal Rank Fusion, nato cross-encoder reranker in GPT za generiranje.

Nobena metoda sama ne zadostuje za posvetovalni korpus. BM25 zanesljivo najde eksaktna imena (»DataSync«, »Kova ERP«), vektorsko iskanje pa ujame odlomke o »zamudah pri migraciji«, četudi besede »zamuda« ni v dokumentu. Reranker je dodaten strošek (~3–5 s), a ocenjuje par (vprašanje, odlomek) skupaj — kar je bistveno natančnejše od posameznega rangiranja.

**Kompromisi:** Preprosto vprašanje traja ~10 s, večskočno ~35 s — vsak korak (klasifikacija, HyDE, retrieval, reranker, generiranje, zaznavanje protislovij) sekvencialno prispeva latenco. HyDE izboljša vektorski priklic, ker je hipotetični odgovor jezikovno bližje dokumentom kot surovo vprašanje, ampak doda en LLM klic na podvprašanje. Večskočna vprašanja (4 podvprašanja × 3 LLM klici) so zato najdražja. Lokalni modeli (E5 + mMiniLM, ~600 MB) eliminirajo odvisnost od interneta za iskanje, a zahtevajo ~1 GB RAM.

---

## Kaj sem med razvojem spremenil

**1. Reranker: angleški → večjezični model.** Začetni `ms-marco-MiniLM-L-6-v2` je treniran samo na angleščini — pri prvih testih na slovenskih dokumentih je sistematično nižje rangiral slovensko besedilo, tudi ko je bilo vsebinsko bolj relevantno. Zamenjal sem ga z `mmarco-mMiniLMv2-L12-H384-v1` (XLM-RoBERTa, večjezični MS MARCO). Ker gre za striktno zamenjavo vmesnika, ni bila potrebna nobena sprememba ostale kode.

**2. Večskočno iskanje brez skupnega rerankiranja.** Prvotni pipeline je zbral odlomke iz vseh podvprašanj in jih rerankal glede na *glavno* vprašanje. To je uničilo odlomke, ki odgovarjajo le enemu delu sestavljenega vprašanja — odlomek z ERP veščinami dobi nizek rerank score pri vprašanju »kdo ima ERP *in* cloud izkušnje?«, ker sam ne zadosti obema pogojema. Rezultat: Q08 je vrnil »ne vem«, čeprav je matrika znanj bila v korpusu (4/12 → 7/12). Popravek: vsako podvprašanje obdrži svojih top-k odlomkov, skupnega rerankiranja ni.

**3. Inverzni HyDE za zaznavanje protislovij.** Standardni HyDE generira plausibilen odgovor in privabi dokumente, ki se *strinjajo* z njim — za zaznavanje protislovij je to kontraproduktivno. Implementiral sem inverzni HyDE: iz prvega najdenega odlomka generiram nasprotujoč odgovor (drugačen datum, drugačna vrednost) in z njim poganjam drugi retrieval pass. To privabi dokumente, ki trdijo drugače — točno tiste, ki jih iščemo. Zaznavanje protislovij teče *pred* generiranjem odgovora in opozorilo vstavi GPT-ju direktno v kontekst, ne post-hoc za odgovor (kjer ga model ne vidi).

---

## Kje sistem odpove

**Q14 (5/12) — Atlas go-live datum (4 protislovni dokumenti v korpusu).** Sistem zazna protislovje, a v odgovoru vseeno napiše napačen datum (september namesto december 2024). Problem je pri retrieval fazi: med top-k rezultati ne pristanejo vsi štirje dokumenti z datumi hkrati. Inverzni HyDE pomaga, ampak ne zagotavlja, da najde *vse* štiri. Zaznavanje protislovij deluje samo na tem, kar retrieval vrne.

**Q08 / SL07 (7/12, 9/12) — branje matričnih tabel.** Kompetencne matrike so razdeljene po odlomkih — en kos pokrije 2–3 vrstice tabele. Za vprašanje »kateri člani imajo score ≥ 3 pri Dockerju« je treba primerjati vrednosti iz *vseh* vrstic naenkrat. Adaptivno povečanje k (na 8–10 za matrična vprašanja) delno pomaga, pri mejnih primerih pa sistem preskočil kakšno vrstico.

**SL04 (9/12) — korenski vzrok incidenta DataSync.** Dokument ima sekcijo »Opis incidenta« (kaj se je zgodilo) in ločeno sekcijo »Analiza vzrokov« (zakaj). Retrieval vrne opis, ker se semantično bolje ujema z vprašanjem »kaj je bil vzrok?« Odgovor je vsebinsko koheren, a faktično napačen — kar je ena nevarnejših vrst napak, ker sodnik brez poznavanja dokumenta ne zazna razlike.

---

## Kaj bi naredil drugače z enim tednom

**Agentni RAG namesto fiksnega pipeline-a.** Trenutni sistem ima nespremenljivo zaporedje korakov: klasificiraj → razgradi → retrieval → reranker → generiraj. Agent z orodji (npr. `search(query)`, `get_document(name)`, `filter_by_date(after, before)`, `compare(doc_a, doc_b)`) bi sam odločil, kaj in v kakšnem vrstnem redu poizvedati. Za Q14 bi agent eksplicitno poiskal vse dokumente, ki omenjajo »Atlas« in vsebujejo datum, ter jih primerjal — namesto da upa, da bodo vsi pristali v top-k. Za SL04 bi po »Opis incidenta« samodejno poiskal »Analiza vzrokov« v istem dokumentu. Agentni pristop ne odpravi le teh dveh točkovnih napak — odpre možnost za iterativno iskanje, kjer agent ugotovi, da ima premalo konteksta, in poizve še enkrat z drugačno strategijo.

**Ekstrakcija entitet in relacij v grafno bazo.** Ob ingestion fazi bi z LLM-jem iz vsakega dokumenta ekstrahiral entitete (projekti, osebe, datumi, tehnologije) in relacije (»Luka Zupan je delal na Atlasu«, »atlas_proposal.md nadomešča atlas_weekly_march.md«) ter jih shranil v Neo4j ali networkx graf. Retrieval bi kombiniral vektorsko iskanje z grafnim obhodom — vprašanje »kaj se je Nexus naučil pri cloud migracijah?« bi sprožilo iskanje vozlišča »cloud migracija«, od tam pa sledilo robovom do projektov, lekcij in oseb. To bi rešilo revizijske verige (Q14), matrična vprašanja (Q08, SL07) in multi-hop poizvedbe strukturalno, ne s povečevanjem k. Pristop je znan kot GraphRAG in je trenutno aktivno področje razvoja.

---

## Kako sem uporabljal AI asistente

Celoten projekt sem razvil z **Claude Code** (CLI orodje). Konkretno:

- **Sintetični dokumenti:** 33 dokumentov je napisal Claude po mojih specifikacijah — tipi dokumentov, dolžine, vgrajene napake, protislovni datumi. Brez tega bi pripravo korpusa porabila cel dan.
- **Koda:** opisal sem arhitekturno odločitev (npr. »odpravi skupni reranking pri multi-hop«), Claude je implementiral, jaz sem pregledal in primerjal z evalvacijskimi rezultati.
- **Kje me je AI zavedel:** pri prvem predlogu za zaznavanje protislovij je Claude implementiral post-hoc opozorilo — prilepljeno za odgovor, kjer ga GPT v naslednjem klicu ni videl in ni popravil napačnega odgovora. To sem opazil šele pri analizi Q14. Šele ko sem pojasnil problem (GPT ne vidi svojega prejšnjega odgovora), je Claude predlagal pravilno rešitev: premik zaznavanja *pred* generiranje.
- **Meje:** arhitekturne odločitve (inverzni HyDE, per-sub-question reranking) sem sprejel sam na podlagi analize evalvacijskih napak. Claude je predlagal opcije in implementiral izbrano, nikoli pa ni sam identificiral vzroka napake — to je zahtevalo ročno branje rezultatov.

**Evalvacijski rezultat (LLM-as-judge, 4 kriteriji × 0–3):** 81.7 % na angleškem nizu (147/180), 80.6 % na slovenskem nizu (145/180), skupaj **81.1 %** na 30 vprašanjih.
