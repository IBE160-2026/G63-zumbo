# Testoversikt

*Laget 26. november 2026 fra `backend/tests/` på `main` (commit `ac6c5ee`).*

Oversikten har én linje per testfunksjon, gruppert etter modulen i appen som testes. Det er 529 testfunksjoner i 29 filer. En parametrisert test (`@pytest.mark.parametrize`) står som én linje, selv om pytest kjører den flere ganger.

**Merking:**

- ⚠️ **Kan ikke feile på grunn av appen.** Testen sjekker bare kode eller oppsett i selve testfila, ikke koden i `backend/`. Den feiler ikke uansett hva som endres i appen.
- ◦ **Kan nesten ikke feile.** Testen sjekker en fast verdi, en fil som ikke endres (som fixturene) eller testoppsettet. Den feiler bare hvis noen endrer akkurat den verdien eller fila. Slike tester kan være nyttige som vakter, men de tester ikke logikk.

Alle andre tester kjører koden i appen og kan feile hvis den endres.

Ingen tester er uten `assert` eller `pytest.raises`.

## begreper (`backend/begreper.py`)

`test_begreper.py`

- `test_alle_sju_begrepene_finnes`: De sju begrepene finnes, i riktig rekkefølge.
- `test_hver_tekst_har_høyst_tre_setninger`: Hver forklaring har én til tre setninger.
- ⚠️ `test_setningstellingen`: Hjelpefunksjonen `setninger` i testfila teller setninger riktig. Den tester ikke appen.
- `test_nøklene_er_unike_og_gyldige_som_html_id`: Nøklene er unike og kan brukes som `id` i HTML.
- `test_varselets_begrep_finnes`: Begrepet «For tynt datagrunnlag» finnes.
- `test_overvåkingstype_nevner_klinisk_praksis_og_fyrtårnsystemet`: Forklaringen av overvåkingstype nevner vanlig klinisk praksis og fyrtårnsystemet.
- `test_test_og_positiv_prøve_sier_at_samme_person_kan_telles_flere_ganger`: Forklaringen av test sier at samme person kan telles flere ganger.
- `test_begreper_importerer_bare_standardbiblioteket`: `begreper.py` importerer bare fra Pythons standardbibliotek.

## config (`backend/config.py`)

`test_config.py`

- `test_cache_dir_vinner`: `CACHE_DIR` bestemmer cachemappen når den er satt.
- `test_vercel_gir_tmp`: På Vercel ligger cachen i `/tmp/fhi-helsedata-cache`.
- `test_vercel_teller_også_med_tom_verdi`: `VERCEL` med tom verdi regnes også som Vercel.
- `test_lokalt_gir_cache_i_reporoten`: Lokalt ligger cachen i `.cache` i reporoten.
- `test_tom_cache_dir_regnes_som_ikke_satt`: `CACHE_DIR` med bare mellomrom regnes som ikke satt.
- `test_relativ_cache_dir_regnes_fra_reporoten`: En relativ `CACHE_DIR` regnes fra reporoten.
- `test_cache_dir_med_tilde`: `~` i `CACHE_DIR` blir hjemmemappen.
- ◦ `test_cache_i_reporoten_er_i_gitignore`: `.cache/` står i `.gitignore`.
- `test_uten_nøkkel_og_modell`: Uten nøkkel og modell er nøkkelen tom og modellen Haiku.
- `test_tomme_verdier_fra_env_example_regnes_som_ikke_satt`: Tomme verdier kopiert fra `.env.example` regnes som ikke satt.
- `test_verdier_med_bare_mellomrom_regnes_som_ikke_satt`: Verdier med bare mellomrom regnes som ikke satt.
- `test_tomme_verdier_i_env_fil_regnes_som_ikke_satt`: Tomme verdier i en `.env`-fil regnes som ikke satt.
- `test_nøkkel_og_modell_leses`: Nøkkel og modell leses fra miljøet.
- `test_nøkkelen_vises_ikke_i_repr`: KI-nøkkelen vises ikke når innstillingene skrives ut.
- `test_env_fil_lastes_bare_uten_miljø`: `.env`-fila leses bare når verdien ikke står i miljøet, og den endrer ikke `os.environ`.
- `test_uten_env_fil_brukes_standardverdiene`: Uten `.env`-fil brukes standardverdiene.
- `test_import_av_config_laster_ikke_env`: Å importere `config` leser ikke `.env`.
- `test_ingen_dotenv_kall_utenfor_funksjoner`: `dotenv` kalles bare inne i funksjoner.
- `test_bare_config_leser_miljøvariabler`: Bare `config.py` leser miljøvariabler.

## domene (`backend/domene.py`)

`test_domene.py`

- `test_virus_til_tabell`: Influensa, RSV og SARS-CoV-2 hører til tabell 724, 729 og 731.
- `test_sju_aldersgrupper_med_alle_først_og_uten_ukjent`: Det er sju aldersgrupper med «Alle» først og uten «Ukjent».
- `test_aldersgruppekodene_finnes_hos_fhi`: Aldersgruppekodene finnes i FHIs dimensjonsliste.
- `test_mal_1_finnes`: Bare mal 1 finnes, med riktig tittel.
- `test_listene_kan_ikke_endres`: De faste listene kan ikke endres mens appen kjører.
- `test_usikker_ved_færre_enn_30_tester`: En uke er usikker ved færre enn 30 tester (29 er usikker, 30 er ikke).
- `test_skjult_antall_tester_er_usikker_og_manglende`: Skjult antall tester gir en usikker og manglende uke uten andel.
- `test_skjult_antall_positive_er_manglende_men_ikke_usikker`: Skjult antall positive gir en manglende uke som ikke er usikker.
- `test_begge_skjult`: Uke med begge tall skjult er manglende og uten andel.
- `test_andel_stemmer_med_fhi`: Andelen for uke 40 stemmer med FHIs `pos_rate`.
- `test_andel_følger_tallene_etter_replace`: Andelen regnes på nytt når tallene byttes ut.
- `test_null_positive_gir_andel_null_ikke_none`: 0 positive gir andel 0, ikke «mangler».
- `test_null_tester_gir_ingen_andel_men_er_ikke_manglende`: 0 tester gir ingen andel, men uka er usikker og ikke manglende.
- `test_uker_som_ikke_finnes_avvises`: Uker som ikke finnes, for eksempel uke 0, avvises.
- `test_uke_53_godtas_når_året_har_den`: Uke 53 godtas i år som har den.
- `test_negative_tall_avvises`: Negative antall avvises.
- `test_flere_positive_enn_tester_gir_andel_over_100_og_usikker_uke`: Flere positive enn tester gir andel over 100 % og usikker uke.
- `test_like_mange_positive_som_tester_er_ikke_usikker`: Like mange positive som tester gir 100 % og er ikke usikker.
- `test_flere_positive_enn_tester_er_usann_uten_tall`: «Flere positive enn tester» er usann når et av tallene mangler.
- `test_null_tester_og_positive_over_null_er_flere_positive_enn_tester`: 0 tester og positive over 0 regnes som flere positive enn tester.
- `test_utvalg_har_alle_som_standard_og_finner_tabellen`: Et utvalg har «alle» som standard aldersgruppe og finner riktig tabell.
- `test_dataserie_lagrer_ukene_som_tuple`: En dataserie lagrer ukene som en tuple.
- `test_regelutslag`: Et regelutslag har regel og tekst, og ugyldige utslag avvises.
- `test_kildehenvisning`: Kildehenvisningen for hver tabell har FHIs ordlyd og tabellnavn.
- `test_kildehenvisning_avviser_ukjent_tabell_og_tid_uten_tidssone`: Kildehenvisning avviser ukjent tabell og tid uten tidssone.
- `test_domene_importerer_bare_standardbiblioteket`: `domene.py` importerer bare fra standardbiblioteket.
- `test_gyldige_parametre_gir_utvalg`: Gyldige parametre gir et utvalg.
- `test_alle_virus_og_aldersgrupper_godtas`: Alle kombinasjoner av virus og aldersgruppe godtas.
- `test_manglende_alder_gir_alle_aldersgrupper`: Manglende eller tom alder gir «Alle aldersgrupper».
- `test_gyldige_sesonger_kan_være_en_hvilken_som_helst_iterable`: Lista over gyldige sesonger kan være en hvilken som helst iterable.
- `test_hvert_ugyldige_felt_gir_norsk_melding`: Hvert ugyldige felt gir én norsk melding som begynner med «Velg».
- `test_ukjent_alder_godtas_ikke`: Aldersgruppen «ukjent» godtas ikke.
- `test_alle_feil_samles_i_én_melding_i_fast_rekkefølge`: Alle feil samles i én melding i fast rekkefølge.
- `test_sesonger_med_feil_format_eller_dubletter_hoppes_over`: Sesonger med feil format eller dubletter hoppes over.
- `test_gyldige_sesonger_kan_ikke_være_én_tekst`: Lista over sesonger kan ikke være én tekst.
- `test_ingen_gyldige_sesonger`: Uten sesonger å velge kommer en egen melding.
- ◦ `test_feilen_er_en_valueerror`: `UgyldigUtvalg` er en `ValueError`.
- `test_manipulert_verdi_avvises_og_vises_ikke`: Manipulerte verdier avvises og vises ikke i meldingen.
- `test_meldingene_har_ingen_fhi_koder`: Feilmeldingene inneholder ingen FHI-koder.
- `test_nøkkel_eksempel`: Nøkkelen for et utvalg ser ut som `mal1-influensa-2025-2026-80pluss`.
- `test_nøkkel_har_bare_trygge_tegn`: Nøklene har bare trygge tegn for filnavn.
- `test_nøkkel_er_lik_for_like_utvalg`: Like utvalg gir lik nøkkel.
- `test_nøkkel_er_ulik_for_ulike_utvalg`: Ulike utvalg gir ulike nøkler.
- `test_nøkkel_avviser_utvalg_som_ikke_er_gyldige`: Ugyldige utvalg får ingen nøkkel.

## fhi (`backend/fhi.py`)

### Henting – `test_fhi_hent.py`

- `test_hent_gir_det_rå_svaret_fra_fixturen`: `hent` gir FHIs svar uendret, med ett kall.
- `test_forespørselen_har_riktig_tabell_og_filtre`: Forespørselen til tabell 724 har riktige filtre og ber om json-stat2.
- `test_valgt_aldersgruppe_og_ukene_frem_til_siste_publiserte_uke`: Forespørselen har valgt aldersgruppe og ukene til siste publiserte uke.
- `test_ukekoden_har_to_sifre_og_liten_w`: Ukekoden skrives som `2027-w01`.
- `test_forespørsel_som_ikke_kan_lages_gir_valueerror`: En forespørsel som ikke kan lages, gir `ValueError`.
- `test_forespørsel_for_tabell_uten_faste_filtre_gir_valueerror`: En tabell uten faste filtre gir `ValueError`.
- `test_hent_dimensjoner_med_egen_funksjon`: Dimensjonslisten hentes med egen funksjon og gir siste publiserte uke.
- `test_tidsgrensen_er_10_sekunder`: Kallet har tidsgrense på 10 sekunder.
- `test_egen_klient_brukes_og_får_tidsgrensen`: En klient som sendes inn, brukes og får tidsgrensen.
- `test_tidsavbrudd_og_nettverksfeil`: Tidsavbrudd og nettverksfeil gir `FhiUtilgjengelig`.
- `test_http_feil`: HTTP-feil (4xx og 5xx) gir `FhiUtilgjengelig`.
- `test_ugyldig_svar`: Svar som ikke er et JSON-objekt, gir `FhiUtilgjengelig`.
- `test_lukket_klient_gir_fhiutilgjengelig`: En lukket klient gir `FhiUtilgjengelig`.
- `test_hele_kallet_gir_opp_etter_tidsgrensen`: Hele kallet gir opp etter den totale tidsgrensen.
- ◦ `test_total_tidsgrense_er_10_sekunder`: Konstanten for total tidsgrense er 10.
- `test_hodene_ber_om_json`: Kallet sender `Accept`, `Content-Type` og `User-Agent`.
- `test_dimensjonslisten_gir_også_fhiutilgjengelig`: Feil ved henting av dimensjonslisten gir også `FhiUtilgjengelig`.
- ◦ `test_fhiutilgjengelig_er_ikke_en_valueerror`: `FhiUtilgjengelig` er ikke en `ValueError`.
- `test_bare_fhi_py_kaller_fhi`: Bare `fhi.py` har FHIs adresse.
- `test_bare_fhi_py_importerer_httpx`: Bare `fhi.py` importerer `httpx`.
- `test_rsv_hentes_fra_tabell_729_med_rsvtype_og_nonstl`: RSV hentes fra tabell 729 med `rsvtype` A+B og vanlig klinisk praksis.
- `test_rsv_svar_fra_feil_tabell_gir_fhiutilgjengelig`: Et RSV-svar fra feil tabell gir `FhiUtilgjengelig`.
- `test_dimensjonslisten_for_729`: Dimensjonslisten for 729 gir siste uke og sesonger.
- `test_sars_cov_2_hentes_fra_tabell_731_uten_typedimensjon`: SARS-CoV-2 hentes fra tabell 731 uten typedimensjon.
- `test_sars_cov_2_svar_med_typedimensjon_gir_fhiutilgjengelig`: Et SARS-CoV-2-svar med typedimensjon gir `FhiUtilgjengelig`.
- `test_dimensjonslisten_for_731`: Dimensjonslisten for 731 gir siste uke og sesonger.

### Tolking – `test_fhi_tolk.py`

- `test_én_uke_per_forventet_uke_i_sesongen`: Tolkingen gir én uke per uke i sesongen (33).
- `test_tre_uker_stemmer_med_fixturen`: Tre utvalgte uker har samme tall som fixturen.
- `test_andelen_stemmer_med_fhis_pos_rate_for_alle_uker`: Andelen stemmer med FHIs `pos_rate` for alle uker.
- `test_fixturen_har_ingen_manglende_eller_usikre_uker`: De ekte tallene gir ingen manglende eller usikre uker.
- `test_uten_siste_publiserte_uke_brukes_høyeste_uke_i_svaret`: Uten siste publiserte uke brukes høyeste uke i svaret.
- `test_sesongen_som_pågår_stopper_ved_siste_publiserte_uke`: En sesong som pågår, stopper ved siste publiserte uke.
- `test_uker_i_svaret_etter_siste_publiserte_uke_forsvinner_ikke`: Uker i svaret etter siste publiserte uke blir ikke borte.
- `test_siste_publiserte_uke_fra_dimensjonslisten`: Siste publiserte uke leses fra dimensjonslisten.
- `test_sesonglisten_fra_dimensjonslisten`: Sesonglisten leses fra dimensjonslisten.
- `test_sesonger_bare_fra_uke_40_til_uke_20`: Bare uke 40–20 gir en sesong.
- `test_siste_publiserte_uke_tar_høyeste_uke_også_uten_rekkefølge`: Siste uke er den høyeste, også når lista ikke er sortert.
- `test_ugyldig_dimensjonsliste`: En ugyldig dimensjonsliste gir `ValueError`.
- `test_dimensjonsliste_uten_noen_sesong_gir_valueerror`: En dimensjonsliste uten sesonger gir `ValueError`.
- `test_skjulte_verdier_og_manglende_uke_blir_none`: Skjulte verdier og manglende uker blir `None`, ikke 0.
- `test_ingen_skjult_verdi_blir_null`: Ingen skjult verdi blir gjort om til 0.
- `test_konstruert_svar_frem_til_siste_publiserte_uke`: Et konstruert svar fylles ut med manglende uker frem til siste publiserte uke.
- `test_verdiene_kan_være_et_objekt_med_plass_og_verdi`: Verdiene kan komme som et objekt med plass og verdi.
- `test_rekkefølgen_på_dimensjonene_følger_id`: Tolkingen følger rekkefølgen i `id`, ikke en fast rekkefølge.
- `test_ugyldig_svar_gir_valueerror`: Et ugyldig svar gir `ValueError`.
- `test_ugyldig_antall_gir_valueerror`: Antall som ikke er gyldige heltall, gir `ValueError`.
- `test_heltall_skrevet_som_desimaltall_godtas`: Heltall skrevet som desimaltall (`250.0`) godtas.
- `test_svar_for_feil_sesong_gir_valueerror`: Et svar for feil sesong gir `ValueError`.
- `test_svar_med_en_uke_utenfor_sesongen_gir_valueerror`: Én uke utenfor sesongen gir `ValueError`.
- `test_plassene_i_index_brukes_ikke_rekkefølgen_på_nøklene`: Tolkingen bruker plassene i `index`, ikke rekkefølgen på nøklene.
- `test_ugyldige_plasser_i_index_gir_valueerror`: Ugyldige plasser i `index` gir `ValueError`.
- `test_samme_uke_to_ganger_gir_valueerror`: Samme uke to ganger gir `ValueError`.
- `test_flere_aldersgrupper_i_svaret_gir_valueerror`: Flere aldersgrupper i svaret gir `ValueError`.
- `test_svar_uten_et_fast_filter_gir_valueerror`: Et svar uten et av de faste filtrene gir `ValueError`.
- `test_flere_positive_enn_tester_gjennom_tolk`: Flere positive enn tester gir andel over 100 % og usikker uke også gjennom tolkingen.
- `test_andre_tabeller_kan_ikke_tolkes_ennå`: Andre tabeller kan ikke tolkes.
- `test_fhi_importerer_ikke_andre_skallmoduler`: `fhi.py` importerer bare `domene` og `sesong` fra appen.
- `test_alle_andre_funksjoner_enn_skallet_er_rene`: Alle funksjoner unntatt henting er rene (ingen nett, filer eller klokke).
- `test_rsv_fixturen_gir_én_uke_per_uke_i_sesongen`: RSV-tallene gir én uke per uke i sesongen.
- `test_rsv_tre_uker_stemmer_med_fixturen`: Tre RSV-uker har samme tall som fixturen.
- ◦ `test_rsv_dimensjonslisten_har_samme_uker_som_724`: RSV-fixturen har samme siste uke og sesonger som 724-fixturen. Sammenligner bare to fixturer.
- `test_svar_fra_724_tolket_som_rsv_gir_valueerror`: Et svar fra 724 tolket som RSV gir `ValueError`.
- `test_svar_fra_729_tolket_som_influensa_gir_valueerror`: Et svar fra 729 tolket som influensa gir `ValueError`.
- `test_rsv_svar_med_annen_rsvtype_gir_valueerror`: Et RSV-svar med annen `rsvtype` gir `ValueError`.
- `test_sars_cov_2_fixturen_gir_én_uke_per_uke_i_sesongen`: SARS-CoV-2-tallene gir én uke per uke i sesongen.
- `test_sars_cov_2_tre_uker_stemmer_med_fixturen`: Tre SARS-CoV-2-uker har samme tall som fixturen.
- ◦ `test_sars_cov_2_dimensjonslisten_har_samme_uker_som_724`: SARS-CoV-2-fixturen har samme siste uke og sesonger som 724-fixturen. Sammenligner bare to fixturer.
- `test_svar_med_typedimensjon_tolket_som_sars_cov_2_gir_valueerror`: Et svar med typedimensjon tolket som SARS-CoV-2 gir `ValueError`.
- `test_svar_fra_731_tolket_som_annet_virus_gir_valueerror`: Et svar fra 731 tolket som annet virus gir `ValueError`.
- `test_sars_cov_2_svar_med_annen_overvåkingstype_gir_valueerror`: Et SARS-CoV-2-svar med annen overvåkingstype gir `ValueError`.
- `test_alle_tabellene_i_virus_har_faste_filtre`: Alle tabellene i `VIRUS` har faste filtre.

### Fixturene – `test_fhi_fixturer.py`

Alle testene her sjekker de lagrede svarene fra FHI i `tests/fixtures/fhi/`, ikke koden i appen.

- ◦ `test_fixturen_har_cacheformatet`: Hver fixtur har feltene `hentet` og `svar`, med tid i UTC.
- ◦ `test_dataene_er_json_stat2`: Datasvaret er json-stat2.
- ◦ `test_dataene_har_uke_2025_w40`: Datasvaret har uke 2025-w40 med de kjente tallene.
- ◦ `test_dataene_er_utvalget_fra_storyen`: Datasvaret har utvalget fra story 1.3.
- ◦ `test_dataene_har_alle_ukene_i_sesongen`: Datasvaret har alle 33 ukene.
- ◦ `test_verdiene_følger_id_og_size`: Antall verdier stemmer med `id` og `size`.
- ◦ `test_rsv_dataene_er_utvalget_fra_storyen`: RSV-svaret har utvalget fra story 6.1.
- ◦ `test_sars_cov_2_dataene_er_utvalget_fra_storyen`: SARS-CoV-2-svaret har utvalget fra story 6.2.

## sesong (`backend/sesong.py`)

`test_sesong.py`

- `test_sesong_2026_2027_har_uke_53_som_vanlig_uke`: Sesongen 2026/2027 har uke 53 og 34 uker.
- `test_sesong_2020_2021_har_også_uke_53`: Sesongen 2020/2021 har også uke 53.
- `test_første_sesong_2024_2025`: Sesongen 2024/2025 går fra uke 40 til uke 20, 33 uker.
- `test_sesong_uten_uke_53`: Sesongen 2025/2026 har ikke uke 53.
- `test_ukene_følger_hverandre_uten_hull`: Ukene i en sesong følger hverandre uten hull.
- `test_sesongstart_er_uke_40`: Sesongen starter i uke 40.
- `test_sesongen_som_pågår_stopper_ved_siste_publiserte_uke`: En sesong som pågår, stopper ved siste publiserte uke.
- `test_siste_publiserte_uke_før_sesongstart_gir_ingen_uker`: Siste publiserte uke før sesongstart gir ingen uker.
- `test_ugyldig_sesong_avvises`: Ugyldige sesongnavn avvises.
- `test_uke_som_ikke_finnes_avvises`: Uker som ikke finnes, avvises.
- `test_uke_må_være_heltall`: Uka må være heltall.
- `test_siste_publiserte_uke_kan_være_en_liste`: Siste publiserte uke kan være en liste.
- `test_samme_sesongregel_som_utvalg`: `sesong` og `domene` godtar de samme sesongnavnene.
- `test_startår_og_navn`: Startår og sesongnavn regnes riktig begge veier.
- `test_sesonger_fra_dato`: Sesonglisten ut fra dato starter med 2024/2025 og har ingen hull.
- `test_ny_sesong_starter_mandag_i_uke_40_i_norsk_tid`: En ny sesong starter mandag i uke 40, norsk tid.
- `test_sesonger_fra_dato_før_første_sesong`: En dato før første sesong gir bare 2024/2025.
- `test_sesonger_fra_dato_krever_tidssone`: En dato uten tidssone avvises.
- `test_grensen_på_24_timer`: Tall er utdatert etter 24 timer.
- `test_tidssonen_spiller_ingen_rolle_for_grensen`: Tidssonen påvirker ikke 24-timersgrensen.
- `test_grensen_over_skifte_til_og_fra_sommertid`: 24-timersgrensen holder når sommertid starter og slutter.
- `test_hentet_frem_i_tid`: Et hentetidspunkt frem i tid regnes riktig.
- `test_er_utdatert_krever_tidssone`: `er_utdatert` krever tidssone.
- `test_sesong_importerer_bare_det_den_trenger`: `sesong.py` importerer bare `datetime`, `zoneinfo` og `domene`.
- `test_sesong_bruker_ikke_klokka_eller_filer`: `sesong.py` bruker ikke klokka eller filer.

## mellomlager (`backend/mellomlager.py`)

`test_mellomlager.py`

- `test_lagre_og_lese_svar`: Et lagret svar kan leses igjen.
- `test_filen_heter_etter_utvalg_noekkel`: Fila heter etter nøkkelen for utvalget.
- `test_filformatet_er_som_fixturene`: Fila har samme format som fixturene.
- `test_fixturene_kan_leses_som_cachefiler`: Fixturene kan leses som cachefiler.
- `test_lagre_og_lese_dimensjoner`: Dimensjonslisten lagres og leses per tabell.
- `test_hentet_lagres_i_utc_og_leses_med_tidssone`: Hentetidspunktet lagres i UTC og leses med tidssone.
- `test_ny_lagring_erstatter_den_gamle`: En ny lagring erstatter den gamle.
- `test_ulike_utvalg_har_hver_sin_fil`: Ulike utvalg har hver sin fil.
- `test_norske_tegn_bevares`: Æ, ø og å bevares.
- `test_skriving_går_via_midlertidig_fil_og_os_replace`: Skrivingen går via en midlertidig fil og `os.replace`.
- `test_feil_under_skriving_beholder_den_gamle_fila`: Feil under skriving beholder den gamle fila.
- `test_fil_som_mangler_gir_none`: En fil som mangler, gir `None`.
- `test_ødelagt_fil_regnes_som_ikke_funnet`: En ødelagt fil regnes som ikke funnet.
- `test_mappe_i_stedet_for_fil_regnes_som_ikke_funnet`: En mappe i stedet for en fil regnes som ikke funnet.
- `test_fil_uten_lesetilgang_regnes_som_ikke_funnet`: En fil uten lesetilgang regnes som ikke funnet.
- `test_hentet_uten_tidssone_avvises`: Et hentetidspunkt uten tidssone avvises, og ingenting lagres.
- `test_svar_må_være_et_objekt`: Svaret må være et objekt.
- `test_ukjent_tabell_avvises`: Ukjente tabellnumre avvises.
- `test_manipulert_utvalg_gir_ikke_filnavn`: Et manipulert utvalg gir ikke et filnavn.
- `test_bare_mellomlager_skriver_filer`: Bare `mellomlager.py` skriver filer.
- `test_lagre_og_lese_forklaring`: En KI-forklaring lagres og leses med tidspunkt, modell og tekst.
- `test_forklaringen_ligger_i_ki_mappen_med_tre_felt`: Forklaringen ligger i `ki/` med tre felt.
- `test_forklaring_som_mangler_gir_none`: En forklaring som mangler, gir `None`.
- `test_ødelagt_forklaring_regnes_som_ikke_funnet`: En ødelagt forklaring regnes som ikke funnet.
- `test_ugyldig_forklaringsnøkkel_avvises`: Ugyldige forklaringsnøkler avvises.
- `test_ugyldig_forklaring_lagres_ikke`: En ugyldig forklaring lagres ikke.
- `test_laget_uten_tidssone_avvises`: Et tidspunkt uten tidssone avvises.
- `test_forklaringen_skrives_atomisk`: Forklaringen skrives atomisk og den gamle beholdes ved feil.

## kontrollregler (`backend/kontrollregler.py`)

`test_kontrollregler.py`

- `test_r1_slår_inn_ved_19_positive`: R1 slår inn ved 19 kjente positive.
- `test_r1_slår_ikke_inn_ved_20_positive`: R1 slår ikke inn ved 20 kjente positive.
- `test_r1_teller_ikke_skjulte_verdier_som_noe`: R1 teller ikke skjulte verdier.
- `test_r1_sier_ikke_ingen_positive_når_alle_er_skjult`: Når alle positive er skjult, sier R1 «ingen kjente positive», ikke «ingen positive». Navnet på testen er lett å lese motsatt.
- `test_r1_teller_kjente_positive_når_bare_testene_er_skjult`: R1 teller kjente positive når bare testene er skjult.
- `test_r1_setningen_bruker_de_faktiske_tallene`: Setningen i R1 bruker de faktiske tallene.
- `test_r2_slår_ikke_inn_ved_4_av_20_uker`: R2 slår ikke inn ved 4 av 20 uker med få tester.
- `test_r2_slår_inn_ved_5_av_20_uker`: R2 slår inn ved 5 av 20 uker med få tester.
- `test_r2_29_tester_teller_og_30_teller_ikke`: 29 tester teller i R2, 30 gjør det ikke.
- `test_r2_teller_ikke_skjult_antall_tester`: R2 teller ikke uker med skjult antall tester.
- `test_r2_teller_ikke_flere_positive_enn_tester_med_minst_30_tester`: R2 teller ikke uker med flere positive enn tester når de har minst 30 tester.
- `test_r2_teller_uke_med_0_tester`: R2 teller uker med 0 tester.
- `test_r3_slår_ikke_inn_ved_2_av_10_uker`: R3 slår ikke inn ved 2 av 10 manglende uker.
- `test_r3_slår_inn_ved_3_av_10_uker`: R3 slår inn ved 3 av 10 manglende uker.
- `test_r4_slår_inn_ved_2_uker_med_data`: R4 slår inn ved 2 uker med tall.
- `test_r4_slår_ikke_inn_ved_3_uker_med_data`: R4 slår ikke inn ved 3 uker med tall.
- `test_r4_teller_ikke_manglende_uker`: R4 teller ikke manglende uker.
- `test_r4_uke_med_0_tester_og_positive_over_0_har_tall`: En uke med 0 tester og positive over 0 har tall i R4.
- `test_r5_slår_inn_for_hele_sesongen_2024_2025`: R5 slår inn for hele sesongen 2024/2025.
- `test_r5_gjelder_bare_sesongen_2024_2025`: R5 gjelder bare 2024/2025.
- `test_r5_slår_ikke_inn_for_ekte_tall_fra_2025_2026`: R5 slår ikke inn for de ekte tallene fra 2025/2026.
- `test_r5_slår_ikke_inn_når_serien_slutter_med_uke_8_i_2025`: R5 slår ikke inn når serien slutter i uke 8 i 2025.
- `test_r5_slår_inn_når_serien_når_uke_9_i_2025`: R5 slår inn når serien når uke 9 i 2025.
- `test_r5_grensen_går_ved_uke_9_i_2025`: Grensen for R5 går ved uke 9 i 2025.
- `test_r5_teller_også_manglende_uker`: R5 teller også manglende uker.
- `test_ingen_utslag_gir_tom_liste`: Uten utslag blir lista tom.
- `test_utslagene_kommer_i_rekkefølge`: Utslagene kommer i rekkefølgen R1 til R5.
- `test_tom_serie_gir_r1_og_r4`: En tom serie gir R1 og R4.
- `test_ekte_tall_fra_2025_2026_gir_ingen_varsel`: De ekte tallene fra 2025/2026 gir ingen varsel.
- `test_kontrollregler_importerer_bare_domene_og_standardbiblioteket`: `kontrollregler.py` importerer bare `domene` og standardbiblioteket.

## ki og prompten (`backend/ki.py`, `backend/prompts/`)

### `test_ki.py`

- `test_med_nøkkel_gir_forklaringen_fra_claude`: Med nøkkel kommer forklaringen fra Claude, med ett kall.
- `test_uten_nøkkel_kalles_ikke_claude`: Uten nøkkel kalles ikke Claude.
- `test_tom_nøkkel_i_miljøet_gir_mangler_nøkkel`: En tom nøkkel i miljøet gir «mangler nøkkel».
- `test_feil_fra_claude_eller_nettet_gir_ki_feil`: Feil fra Claude eller nettet gir `KiFeil`.
- `test_feil_når_klienten_lages_gir_ki_feil`: Feil når klienten lages, gir `KiFeil`.
- `test_svar_som_ikke_kan_brukes_gir_ki_feil`: Svar som ikke kan brukes, gir `KiFeil`.
- `test_feilen_logges_uten_nøkkelen`: Feilen logges uten nøkkelen.
- `test_klienten_lages_med_eksplisitt_nøkkel`: Klienten lages med nøkkelen fra innstillingene.
- `test_klienten_har_tidsgrense_og_lukkes`: Klienten har tidsgrense og antall forsøk, og lukkes etterpå.
- `test_kallet_har_lengde_og_innsats`: Kallet har maks antall tokens og lav innsats.
- `test_standardmodellen_er_haiku`: Standardmodellen er Haiku.
- `test_modellen_kan_overstyres_med_anthropic_model`: Modellen kan overstyres med `ANTHROPIC_MODEL`.
- `test_uten_ny_klient_brukes_anthropic`: Uten egen klient brukes Anthropic-klienten.
- `test_claude_får_den_utfylte_prompten`: Claude får den utfylte prompten.
- `test_prompten_har_ukene_slik_de_står_i_tabellen`: Prompten har ukene skrevet som i tabellen.
- `test_prompten_har_skjulte_og_manglende_tall_skrevet_tydelig`: Prompten skriver skjulte og manglende tall med ord.
- `test_prompten_har_regelutslag_og_kilde`: Prompten har regelutslag, tabell og hentetidspunkt.
- `test_uten_regelutslag_er_feltet_tomt`: Uten regelutslag er feltet tomt.
- `test_prompten_har_ingen_ufylte_plassholdere`: Prompten har ingen ufylte plassholdere.
- `test_kilden_er_den_samme_som_under_grafen`: Kilden i prompten er den samme som under grafen.
- `test_kilde_står_ikke_to_ganger`: «Kilde:» står bare én gang, til slutt.
- `test_ukelinje`: Hver ukelinje skrives riktig for vanlige, skjulte og manglende tall.
- `test_bare_ki_py_importerer_anthropic`: Bare `ki.py` importerer `anthropic`.
- `test_ki_importerer_bare_det_arkitekturen_tillater`: `ki.py` importerer bare modulene arkitekturen tillater.
- `test_nøkkelen_er_sha256_av_kanonisk_json`: Nøkkelen er SHA-256 av utvalg, uker, regelutslag, prompt, ukeformat og modell.
- `test_samme_tall_gir_samme_nøkkel_også_med_nytt_hentetidspunkt`: Samme tall gir samme nøkkel også med nytt hentetidspunkt.
- `test_endrede_tall_gir_ny_nøkkel`: Endrede tall gir ny nøkkel.
- `test_annet_utvalg_gir_ny_nøkkel`: Et annet utvalg gir ny nøkkel.
- `test_endrede_regelutslag_gir_ny_nøkkel`: Endrede regelutslag gir ny nøkkel.
- `test_annen_modell_gir_ny_nøkkel`: En annen modell gir ny nøkkel.
- `test_endret_prompt_gir_ny_nøkkel`: En endret prompt gir ny nøkkel.
- `test_nytt_ukeformat_gir_ny_nøkkel`: Et nytt ukeformat gir ny nøkkel.
- `test_nøkkelen_er_64_heksadesimale_tegn`: Nøkkelen er 64 heksadesimale tegn.

### `test_prompt.py`

- `test_prompten_har_nøyaktig_de_fire_plassholderne`: Promptfila har nøyaktig de fire plassholderne.
- `test_prompten_kan_fylles_ut_med_format`: Prompten kan fylles ut med `format` uten krøllparenteser igjen.
- ◦ `test_prompten_ber_om_norsk_og_høyst_120_ord`: Promptteksten ber om norsk og høyst 120 ord.
- ◦ `test_prompten_ber_ki_en_ikke_nevne_hentetidspunktet`: Promptteksten ber KI-en ikke nevne hentetidspunktet.

## formatering (`backend/formatering.py`)

`test_formatering.py`

- `test_tabellen_bruker_de_samme_funksjonene_som_prompten`: Tabellen og prompten bruker de samme formateringsfunksjonene.
- `test_kildetekst_er_den_samme_som_under_grafen`: Kildeteksten er den samme som under grafen.
- `test_formatering_importerer_bare_domene_og_standardbiblioteket`: `formatering.py` importerer bare `domene` og standardbiblioteket.

## tjeneste (`backend/tjeneste.py`)

### `test_tjeneste.py`

- `test_ferske_lagrede_tall_brukes_uten_kall_til_fhi`: Ferske lagrede tall brukes uten kall til FHI.
- `test_utdaterte_tall_hentes_på_nytt_og_lagres`: Utdaterte tall hentes på nytt og lagres.
- `test_uten_lagrede_tall_hentes_tall_frem_til_siste_publiserte_uke`: Uten lagrede tall hentes tall frem til siste publiserte uke.
- `test_svaret_har_serie_regelutslag_og_kilde`: Svaret har dataserie, regelutslag og kilde.
- `test_fersk_dimensjonsliste_hentes_ikke_på_nytt`: En fersk dimensjonsliste hentes ikke på nytt.
- `test_fhi_nede_gir_sist_lagrede_tall_med_kontrollregler`: Når FHI er nede, vises sist lagrede tall med kontrollregler.
- `test_data_feiler_etter_at_dimensjonslisten_er_hentet`: Feil i datakallet etter dimensjonslisten gir sist lagrede tall.
- `test_fhi_nede_uten_lagrede_tall_gir_melding`: FHI nede uten lagrede tall gir en melding, og feilen logges.
- `test_lagret_fil_som_ikke_kan_tolkes_regnes_som_manglende`: En lagret fil som ikke kan tolkes, regnes som manglende.
- `test_meldingene_har_ingen_fhi_koder`: Meldingene har ingen FHI-koder.
- `test_lagring_som_feiler_gir_likevel_tall`: Tallene vises selv om lagringen feiler.
- `test_rsv_hentes_fra_729_med_729_sin_dimensjonsliste`: RSV hentes fra 729 med dimensjonslisten til 729.
- `test_rsv_kilde_er_tabell_729`: Kilden for RSV er tabell 729.
- `test_siste_publiserte_uke_for_rsv_kommer_fra_729`: Siste publiserte uke for RSV kommer fra 729.
- `test_lagret_729_liste_brukes_uten_kall`: En lagret liste for 729 brukes uten kall.
- `test_sesonglisten_kommer_fortsatt_fra_724`: Sesonglisten kommer fortsatt fra 724.
- `test_rsv_fhi_nede_venter_ikke_på_729_rett_etter_feil_på_724`: Rett etter en feil på 724 prøver ikke RSV 729 også.
- `test_tvungen_henting_for_rsv_henter_729_selv_om_alt_er_ferskt`: Tvungen henting for RSV henter 729 selv om alt er ferskt.
- `test_rsv_venter_ikke_på_724_listen_som_hentes_samtidig`: RSV venter ikke på 724-lista som hentes samtidig.
- `test_rsv_svar_fra_feil_tabell_gir_fhi_nede`: Et RSV-svar fra feil tabell gir «FHI nede» og lagres ikke.
- `test_sesong_uten_publiserte_uker_gir_melding_uten_datakall`: En sesong uten publiserte uker gir en melding uten datakall.
- `test_sesonger_fra_fhi_lagres`: Sesonglisten fra FHI lagres.
- `test_fhis_liste_vinner_over_reserven_i_uke_40`: FHIs sesongliste vinner over reservelista i uke 40.
- `test_fhi_nede_gir_lagret_sesongliste_selv_om_den_er_gammel`: Når FHI er nede, brukes den lagrede sesonglisten selv om den er gammel.
- `test_fhi_nede_uten_brukbar_liste_gir_reserven`: Uten brukbar lagret liste brukes reservelista.
- `test_lagret_liste_uten_uker_hentes_på_nytt`: En lagret liste uten uker hentes på nytt.
- `test_gammel_dimensjonsliste_hentes_på_nytt_når_fhi_svarer`: En gammel dimensjonsliste hentes på nytt når FHI svarer.
- `test_to_samtidige_kall_deler_ett_kall_til_fhi`: To samtidige kall deler ett kall til FHI.
- `test_to_samtidige_kall_deler_ett_kall_også_når_fhi_er_nede`: To samtidige kall deler ett kall også når FHI er nede.
- `test_samtidige_sesongkall_deler_ett_kall_til_fhi`: Samtidige kall etter sesonglisten deler ett kall.
- `test_feil_i_jobben_gis_videre_og_nøkkelen_frigis`: En feil i en delt jobb gis videre, og nøkkelen kan brukes igjen.
- `test_dimensjonslisten_hentes_ikke_på_nytt_rett_etter_feil`: Dimensjonslisten hentes ikke på nytt rett etter en feil.
- `test_dimensjonslisten_prøves_igjen_etter_pausen`: Dimensjonslisten prøves igjen etter pausen.
- `test_sars_cov_2_hentes_fra_731_med_731_sin_dimensjonsliste`: SARS-CoV-2 hentes fra 731 med dimensjonslisten til 731.
- `test_sars_cov_2_kilde_er_tabell_731`: Kilden for SARS-CoV-2 er tabell 731.
- `test_siste_publiserte_uke_for_sars_cov_2_kommer_fra_731`: Siste publiserte uke for SARS-CoV-2 kommer fra 731.

### `test_tjeneste_forklaring.py`

- `test_forklaringen_lagres_med_laget_modell_og_tekst`: KI-forklaringen lagres med tidspunkt, modell og tekst.
- `test_samme_tall_bruker_lagret_tekst_uten_å_kalle_claude`: Samme tall bruker lagret tekst uten å kalle Claude.
- `test_endrede_tall_gir_nytt_kall_og_ny_fil`: Endrede tall gir nytt kall og ny fil.
- `test_endrede_regelutslag_gir_nytt_kall`: Endrede regelutslag gir nytt kall.
- `test_endret_prompt_gir_nytt_kall`: En endret prompt gir nytt kall.
- `test_endret_modell_gir_nytt_kall`: En endret modell gir nytt kall.
- `test_ki_feil_lagres_ikke_og_neste_kall_prøver_igjen`: En KI-feil lagres ikke, og neste kall prøver igjen.
- `test_ubrukelig_svar_lagres_ikke`: Et ubrukelig svar lagres ikke.
- `test_mangler_nøkkel_lagres_ikke_og_kaller_ikke_claude`: Uten nøkkel lagres ingenting, og Claude kalles ikke.
- `test_uten_nøkkel_brukes_heller_ikke_lagret_forklaring`: Uten nøkkel brukes heller ikke en lagret forklaring.
- `test_uten_tall_kalles_ikke_claude`: Uten tall kalles ikke Claude.
- `test_forklaringen_vises_selv_om_den_ikke_kan_lagres`: Forklaringen vises selv om den ikke kan lagres.
- `test_forklaringen_vises_selv_med_nå_uten_tidssone`: Forklaringen vises selv med et tidspunkt uten tidssone, men lagres ikke.
- `test_lagret_forklaring_logges`: Bruk av lagret forklaring logges.
- `test_ødelagt_lagret_forklaring_gir_nytt_kall`: En ødelagt lagret forklaring gir nytt kall og ny lagring.
- `test_prompt_som_ikke_kan_leses_gir_ki_feil`: En prompt som ikke kan leses, gir `KiFeil` uten kall.
- `test_samtidige_kall_for_samme_tall_deler_ett_kall_til_claude`: Samtidige kall for samme tall deler ett kall til Claude.

### `test_tjeneste_tving.py`

- `test_uten_tving_brukes_de_ferske_tallene`: Uten tvang brukes de ferske tallene.
- `test_tving_henter_fra_fhi_selv_om_tallene_er_ferske`: Med tvang hentes tallene fra FHI selv om de er ferske.
- `test_tving_lagrer_med_nytt_hentetidspunkt`: Tvungen henting lagrer med nytt hentetidspunkt.
- `test_tving_henter_også_dimensjonslisten`: Tvungen henting henter også dimensjonslisten.
- `test_tving_når_fhi_er_nede_gir_sist_lagrede_tall`: Tvungen henting når FHI er nede, gir sist lagrede tall.
- `test_tving_prøver_fhi_igjen_rett_etter_en_feil`: Tvungen henting prøver FHI igjen rett etter en feil.
- `test_tving_uten_lagrede_tall_og_fhi_nede_gir_melding`: Tvungen henting uten lagrede tall og med FHI nede gir en melding.
- `test_pausen_etter_feil_gjelder_også_datakallet`: Pausen etter en feil gjelder også datakallet.
- `test_tvunget_kall_blir_ikke_med_på_et_vanlig_kall`: Et tvunget kall deler ikke kall med et vanlig kall.
- `test_samtidige_tvungne_kall_deler_ett_kall_til_fhi`: Samtidige tvungne kall deler ett kall til FHI.

## web (`backend/web.py`, maler, CSS og JavaScript)

### Resultatsiden og skjemaet – `test_web.py`

- `test_resultatsiden_har_skjema_med_skjult_mal_og_virus`: Resultatsiden har et skjema med skjult mal og virus.
- `test_overskriften_viser_viruset`: Overskriften og sidetittelen viser viruset.
- `test_ugyldig_virus_viser_melding_og_lenke_uten_skjema`: Et ugyldig virus gir melding og lenke til forsiden, uten skjema.
- `test_sesongene_med_siste_som_standard`: Sesongene vises med den siste valgt.
- `test_alle_aldersgrupper_er_standard`: «Alle aldersgrupper» er valgt som standard, og «Ukjent» vises ikke.
- `test_synlige_felt_har_label`: Synlige felt har `label`.
- `test_siden_er_norsk_uten_fhi_koder`: Sidene er på norsk og har ingen FHI-koder.
- `test_ugyldig_utvalg_gir_melding_og_ingen_henting`: Et ugyldig utvalg gir melding og ingen henting.
- `test_melding_viser_ikke_verdien_brukeren_sendte`: Meldingen viser ikke verdien brukeren sendte.
- `test_gyldig_utvalg_henter_tall`: Et gyldig utvalg henter tall.
- `test_resultatsiden_uten_valg_sender_til_forsiden`: Resultatsiden uten valg sender til forsiden (303).
- `test_parametre_med_mellomrom_avvises_av_domene`: Parametre med mellomrom avvises.
- `test_valgene_er_forhåndsvalgt_etter_innsending`: Valgene er forhåndsvalgt etter innsending.
- `test_ukjente_valg_viser_standardvalget`: Ukjente valg viser standardvalget i skjemaet.
- `test_nytt_utvalg_fra_skjemaet_gjelder_samme_virus`: Et nytt utvalg fra skjemaet gjelder samme virus.
- `test_skjemaet_vises_når_fhi_er_nede`: Skjemaet vises når FHI er nede.
- `test_fhi_nede_gir_melding_og_ett_kall_per_side`: FHI nede gir melding og bare ett kall per side.
- `test_rsv_viser_tall_og_kilde_for_729`: RSV-siden viser tall og kilde fra 729.
- `test_sars_cov_2_viser_tall_og_kilde_for_731`: SARS-CoV-2-siden viser tall og kilde fra 731.
- `test_innstillingene_leses_en_gang_ved_oppstart`: Innstillingene leses én gang ved oppstart.
- `test_bare_web_kaller_les_innstillinger`: Bare `web.py` kaller `les_innstillinger`.
- `test_appen_bruker_les_innstillinger_fra_config`: Appen bruker `les_innstillinger` fra `config`.

### Forsiden – `test_web_forside.py`

- `test_forsiden_har_overskrift_intro_og_tre_kort`: Forsiden har overskrift, introtekst og tre kort.
- `test_kortene_står_i_rekkefølge_med_lenke_til_sesongen_som_pågår`: Kortene står i rekkefølge og lenker til sesongen som pågår.
- `test_kortet_viser_andelen_i_siste_uke_med_andel`: Hvert kort viser andelen i siste uke med andel.
- `test_forsiden_og_resultatsiden_deler_mellomlageret`: Forsiden og resultatsiden deler mellomlageret.
- `test_forsiden_er_uten_fhi_koder`: Forsiden har ingen FHI-koder.
- `test_chatbotteksten_står_på_forsiden_og_ikke_på_resultatsiden`: Chatbot-teksten står på forsiden og ikke på resultatsiden.
- `test_resultatsiden_har_lenken_tilbake`: Resultatsiden har lenke tilbake over overskriften.
- `test_kortlenken_åpner_resultatsiden`: Lenken på kortet åpner resultatsiden.
- `test_siste_uke_med_andel_hopper_over_uker_uten_andel`: Siste uke med andel hopper over uker uten andel.
- `test_kortet_sier_fra_om_usikker_uke`: Kortet sier fra om usikker uke.
- `test_forsiden_sier_fra_om_usikker_uke_i_tekst`: Forsiden skriver «usikker uke» i teksten.
- `test_kortet_med_sikker_uke_sier_ikke_usikker`: Et kort med sikker uke sier ikke «usikker».
- `test_fhi_nede_med_lagrede_tall_viser_dem_med_dato`: FHI nede med lagrede tall viser dem med dato.
- `test_fhi_nede_uten_lagrede_tall_gir_tekst_og_lenke`: FHI nede uten lagrede tall gir tekst og lenke.
- `test_fhi_nede_gir_ett_kall_på_forsiden`: FHI nede gir bare ett kall på forsiden.
- `test_feil_når_kortet_lages_gir_tekst_og_ikke_500`: En feil i ett kort gir tekst, ikke feilside.
- `test_kort_uten_uke_med_andel_gir_tekst`: Et kort uten uke med andel gir tekst og lenke.
- `test_forsiden_uten_uke_med_andel_gir_tekst_og_lenke`: Forsiden uten uke med andel gir tekst og lenke.
- `test_uventet_feil_i_ett_kort_gir_tekst_og_ikke_500`: En uventet feil i ett kort gir tekst, ikke feilside.
- `test_forsiden_kaller_ikke_ki`: Forsiden kaller ikke KI-en.
- `test_gamle_adresser_sendes_videre_med_301`: Gamle adresser sendes videre til `/resultat` med 301.
- `test_forside_uten_valg_sendes_ikke_videre`: Forsiden uten valg sendes ikke videre.
- `test_ugyldig_valg_gir_melding_og_lenke_uten_henting`: Et ugyldig valg gir melding og lenke uten henting.
- `test_hent_nyeste_sender_til_resultatsiden`: «Hent nyeste» sender til resultatsiden.

### Tabellen – `test_web_tabell.py`

- `test_tall_har_mellomrom_som_tusenskille`: Tall har mellomrom som tusenskille.
- `test_skjult_tall_vises_som_skjult_ikke_0`: Et skjult tall vises som «skjult», ikke 0.
- `test_andel_med_en_desimal_og_komma`: Andelen har én desimal og komma.
- `test_andel_som_mangler_vises_som_mangler`: En andel som mangler, vises som «mangler».
- `test_uke_vises_som_uke_og_nummer`: Uka vises som «uke 50».
- `test_tidspunkt_i_norsk_tid`: Tidspunktet vises i norsk tid.
- `test_tabellen_har_kolonnene_og_en_rad_per_uke`: Tabellen har de fire kolonnene og én rad per uke.
- `test_lagrede_tall_vises_uten_kall_til_fhi`: Lagrede tall vises uten kall til FHI.
- `test_skjulte_verdier_vises_som_skjult_og_mangler`: Skjulte verdier vises som «skjult» og «mangler».
- `test_uke_med_0_tester_viser_kan_ikke_regnes_ut`: En uke med 0 tester viser «kan ikke regnes ut».
- `test_andelstekst`: Andelsteksten er riktig for vanlige, skjulte og manglende tall.
- `test_usikre_uker_har_tegn_og_fotnote`: Usikre uker har stjerne og fotnote.
- `test_flere_positive_enn_tester_har_egen_fotnote`: Flere positive enn tester har egen fotnote (†).
- `test_ingen_fotnoter_uten_usikre_uker`: Uten usikre uker er det ingen fotnoter.
- `test_kildehenvisning_under_tabellen`: Kildehenvisningen står under tabellen.
- `test_nye_tall_har_hentetidspunktet_nå`: Nye tall har hentetidspunktet nå.
- `test_fhi_nede_med_lagrede_tall_viser_dem_med_dato`: FHI nede med lagrede tall viser dem med dato.
- `test_fhi_nede_uten_lagrede_tall_gir_ingen_tabell`: FHI nede uten lagrede tall gir ingen tabell.
- `test_tabellen_står_i_html_fra_serveren`: Tabellen lages på serveren, ikke med JavaScript.
- `test_tabellen_har_utvalget_som_tittel_og_kan_rulles_med_tastatur`: Tabellen har utvalget som tittel og kan rulles med tastaturet.
- `test_utvalgstekst_med_aldersgruppe`: Utvalgsteksten tar med aldersgruppen.
- `test_bare_stjerne_uten_kors_når_ingen_uke_har_flere_positive`: Bare stjerne, ikke kors, når ingen uke har flere positive enn tester.
- `test_tegnene_er_skjult_for_skjermlesere_i_radoverskriften`: Stjerne og kors er skjult for skjermlesere.
- `test_uke_med_0_tester_og_positive_har_fotnote_men_ingen_andel`: En uke med 0 tester og positive over 0 har fotnote, men ingen andel.
- `test_sist_lagrede_står_over_tabellen_og_bare_når_fhi_er_nede`: «Sist lagrede tall» står over tabellen, og bare når FHI er nede.
- `test_prompten_har_de_samme_tallene_som_tabellen`: Prompten har de samme tallene som tabellen.

### Grafen – `test_web_graf.py`

- `test_jsonblokken_har_samme_tall_som_tabellen`: Grafdataene har de samme tallene som tabellen.
- `test_jsonblokken_med_ekte_tall`: Grafdataene for de ekte tallene starter riktig.
- `test_akseteksten_står_i_malen`: Aksetekstene står i malen.
- `test_manglende_uker_er_null`: Manglende uker er `null` i grafen, ikke 0.
- `test_usikre_uker_er_markert_også_flere_positive_enn_tester`: Usikre uker er markert, også uker med flere positive enn tester.
- `test_grafen_har_forklaring_av_markeringen`: Grafen forklarer markeringene.
- `test_forklaringen_vises_også_uten_usikre_uker`: Forklaringen vises også uten usikre uker.
- `test_app_js_gir_usikre_uker_åpen_sirkel`: `app.js` gir usikre uker åpen sirkel og brudd for manglende uker.
- `test_grafen_har_tittel_med_utvalget`: Grafen har utvalget som tittel.
- `test_alternativtekst_med_utvalg_og_hovedtrekk`: Alternativteksten har utvalget og hovedtrekkene.
- `test_alternativtekst_nevner_usikre_uker`: Alternativteksten nevner usikre uker.
- `test_alternativtekst_teller_bare_tegnede_sirkler_og_brudd`: Alternativteksten teller bare sirkler og brudd som faktisk tegnes.
- `test_alternativtekst_når_siste_uke_er_høyest`: Alternativteksten når siste uke er høyest.
- `test_ingen_graf_uten_andeler`: Uten andeler vises tabell, men ingen graf.
- `test_alternativtekst_uten_andeler`: Alternativteksten uten andeler sier det.
- `test_chart_js_fra_jsdelivr_med_fast_versjon_og_integrity`: Chart.js hentes med fast versjon og `integrity`.
- `test_bare_egen_javascript_i_app_js`: All egen JavaScript ligger i `app.js`.
- `test_bare_app_js_uten_tall`: Uten tall lastes bare `app.js`.
- `test_app_js_serveres`: `app.js` serveres.
- `test_jsonblokken_er_trygg_inne_i_script`: Grafdataene kan ikke bryte ut av `<script>`.
- `test_app_js_kobler_graf_og_tabell`: `app.js` kobler graf og tabell.
- `test_app_js_verktøytips_med_tester_positive_og_andel`: Verktøytipset viser tester, positive og andel.
- `test_app_js_mindre_punkter_på_smale_skjermer`: Punktene blir mindre på smale skjermer.

### Varselet – `test_web_varsel.py`

- `test_varsel_med_r1_og_r5_samtidig`: Varselet viser R1 og R5 samtidig.
- `test_varsel_har_ikon_og_overskrift`: Varselet har ikon og overskrift.
- `test_varselet_står_over_grafen_og_tabellen`: Varselet står over grafen og tabellen.
- `test_varsel_med_ekte_regel_r5_fra_lagrede_tall`: Lagrede tall fra 2024/2025 gir varsel med R5.
- `test_varsel_med_ekte_regel_r1_fra_lagrede_tall`: Lagrede tall med få positive gir varsel med R1.
- `test_varsel_også_med_sist_lagrede_tall`: Varselet vises også med sist lagrede tall.
- `test_varselet_lenker_til_forklaringen_av_tynt_datagrunnlag`: Varselet lenker til forklaringen av «For tynt datagrunnlag».
- `test_ingen_varsel_uten_regelutslag`: Uten regelutslag vises ikke noe varsel.
- `test_ingen_varsel_uten_utvalg`: Uten gyldig utvalg vises ikke noe varsel.
- `test_ingen_varsel_ved_ugyldig_utvalg`: Ved ugyldig utvalg vises ikke noe varsel.
- `test_ingen_varsel_når_det_ikke_finnes_tall`: Uten tall vises ikke noe varsel.

### Begrepsforklaringene – `test_web_begreper.py`

- `test_siden_viser_alle_sju_forklaringene_ordrett`: Siden viser alle sju forklaringene ordrett.
- `test_forklaringene_er_lukket_og_bruker_details_og_summary`: Forklaringene er lukket og bruker `details` og `summary`.
- `test_forklaringene_vises_også_uten_utvalg`: Forklaringene vises også uten utvalg.
- `test_forklaringene_står_under_tabellen_og_kilden`: Forklaringene står under tabellen og kilden.

### KI-forklaringen på siden – `test_web_forklaring.py`

- `test_siden_har_området_med_aria_live_og_ventetekst`: Siden har et område med `aria-live` og ventetekst.
- `test_området_peker_på_forklaringen_med_samme_parametre`: Området peker på forklaringen med samme parametre.
- `test_feilteksten_står_i_malen`: Feilteksten står i malen.
- `test_områdets_overskrift_og_plass_etter_begrepene`: Området har overskrift og står etter begrepene.
- `test_uten_javascript_sier_siden_det`: Uten JavaScript sier siden at forklaringen krever det.
- `test_siden_kaller_ikke_claude`: Siden kaller ikke Claude.
- `test_siden_kaller_ikke_ki`: Siden kaller ikke KI-funksjonene.
- `test_uten_tall_vises_ikke_området`: Uten tall vises ikke området.
- `test_uten_tall_fra_fhi_vises_ikke_området`: Uten tall fra FHI vises ikke området.
- `test_med_lagrede_tall_vises_siden_uten_fhi_og_uten_ki`: Med lagrede tall vises siden uten å vente på FHI eller KI.
- `test_app_js_henter_fragmentet_og_bruker_feilteksten`: `app.js` henter forklaringen og bruker feilteksten.
- `test_fragmentet_har_forklaringen_merket_skrevet_av_ki`: Forklaringen er merket «Skrevet av KI».
- `test_fragmentet_har_kildehenvisningen`: Forklaringen har kildehenvisning.
- `test_kildehenvisningen_er_den_samme_som_under_tabellen`: Kildehenvisningen ved forklaringen er den samme som under tabellen.
- `test_avsnitt_i_forklaringen_blir_egne_avsnitt`: Avsnitt i forklaringen blir egne avsnitt.
- `test_teksten_fra_claude_escapes`: HTML i teksten fra Claude vises som tekst.
- `test_fragmentet_lagres_ikke_av_nettleseren`: Nettleseren lagrer ikke forklaringen (`no-store`).
- `test_uten_nøkkel_sier_fragmentet_at_nøkkel_trengs`: Uten nøkkel sier forklaringsfeltet at nøkkel trengs.
- `test_uten_nøkkel_brukes_ikke_en_lagret_forklaring`: Uten nøkkel brukes ikke en lagret forklaring.
- `test_ved_kifeil_gir_fragmentet_feilteksten`: Ved KI-feil vises feilteksten.
- `test_feilteksten_er_den_samme_i_fragmentet_og_på_siden`: Feilteksten er den samme i forklaringen og på siden.
- `test_uten_tall_gir_fragmentet_feilteksten`: Uten tall vises feilteksten, og Claude kalles ikke.
- `test_ugyldig_utvalg_gir_400`: Et ugyldig utvalg gir 400, og Claude kalles ikke.
- `test_forklaringsadresse_lager_samme_parametre_som_skjemaet`: Adressen til forklaringen har samme parametre som skjemaet.

### «Hent nyeste tall nå» – `test_web_hent_nyeste.py`

- `test_siden_sier_når_tallene_ble_hentet_og_at_fhi_publiserer_på_torsdag`: Siden sier når tallene ble hentet, og at FHI publiserer på torsdag.
- `test_knappen_sender_post_med_samme_utvalg`: Knappen sender POST med samme utvalg.
- `test_uten_tall_vises_ikke_knappen`: Uten gyldig utvalg vises ikke knappen.
- `test_app_js_deaktiverer_knappen_når_skjemaet_sendes`: `app.js` deaktiverer knappen når skjemaet sendes.
- `test_post_svarer_303_til_samme_utvalg`: POST svarer 303 til samme utvalg.
- `test_post_henter_uten_mellomlager_og_lagrer_med_nytt_hentetidspunkt`: POST henter uten mellomlager og lagrer med nytt hentetidspunkt.
- `test_post_og_omdirigering_gir_siden_med_de_nye_tallene`: POST og omdirigering gir siden med de nye tallene.
- `test_fhi_nede_gir_sist_lagrede_tall_med_dato`: FHI nede gir sist lagrede tall med dato.
- `test_fhi_nede_uten_lagrede_tall_gir_meldingen_uten_tall`: FHI nede uten lagrede tall gir meldingen uten tall.
- `test_merket_endrer_ikke_en_side_uten_tall`: Merket i adressen endrer ikke en side uten tall.
- `test_merket_gjelder_ikke_når_adressen_lastes_inn_senere`: Merket gjelder ikke når adressen lastes inn senere.
- `test_merket_gjelder_ikke_for_tall_hentet_etter_forsøket`: Merket gjelder ikke for tall hentet etter forsøket.
- `test_merket_med_ugyldig_verdi_ignoreres`: Merket med ugyldig verdi ignoreres.
- `test_data_nede_etter_dimensjonslisten_venter_ikke_på_fhi_to_ganger`: Feil i datakallet gir ikke et nytt kall til FHI på samme side.
- `test_gyldig_utvalg_uten_tall_har_knappen_og_teksten_om_torsdag`: Et gyldig utvalg uten tall har knappen og teksten om torsdag.
- `test_sars_cov_2_uten_tall_har_knappen`: SARS-CoV-2 uten tall har knappen.
- `test_ugyldig_utvalg_hentes_ikke_og_sendes_til_siden`: Et ugyldig utvalg hentes ikke og sendes til siden.
- `test_ugyldig_utvalg_gir_feilmeldingen_på_siden`: Et ugyldig utvalg gir feilmeldingen på siden.
- `test_get_til_hent_nyeste_er_ikke_lov`: GET til `/hent-nyeste` gir 405.
- `test_uendrede_tall_gir_ikke_nytt_kall_til_claude`: Uendrede tall gir ikke nytt kall til Claude.
- `test_endrede_tall_gir_ny_forklaring`: Endrede tall gir ny forklaring.

### Stil og tilgjengelighet – `test_stil.py`

- ⚠️ `test_kontrastberegningen`: Hjelpefunksjonen `kontrast` i testfila regner kontrast riktig. Den tester ikke appen.
- `test_fargene_er_fhis_palett`: Fargene i CSS er fra FHIs palett.
- `test_kontrasten_holder_grensene`: Kontrasten mellom fargeparene holder WCAG-grensene.
- `test_farger_står_bare_som_variabler_i_root`: Farger står bare som variabler i `:root`.
- `test_app_js_leser_graffargene_og_skriften_fra_variablene`: `app.js` leser graffarger og skrift fra CSS-variablene.
- `test_synlig_fokusmarkering_på_alt_som_kan_nås_med_tab`: Alt som kan nås med Tab, har synlig fokusmarkering.
- `test_smal_skjerm_uten_vannrett_rulling`: Smale skjermer får ikke vannrett rulling.
- `test_skriftene_ligger_lokalt_med_lisens`: Skriftene ligger lokalt med lisens, ikke hos Google.
- `test_overskrifter_i_fraunces_og_tekst_i_poppins`: Overskrifter er i Fraunces og tekst i Poppins.
- `test_alle_skjemafelt_har_label`: Alle skjemafelt har `label`.
- `test_skriftfilene_serveres`: Skriftfilene serveres.
- `test_avsenderlinjen_og_ingen_logo`: Bunnen har avsenderlinjen og ingen logo.
- `test_justering_står_rett_under_hentetidspunktet`: Teksten om justering står rett under hentetidspunktet.
- `test_justering_vises_ikke_uten_tall`: Teksten om justering vises ikke uten tall.
- ◦ `test_varselets_overskrift_er_uendret`: Overskriften i varselet står i malen.
- `test_chatbotteksten_står_nederst_på_forsiden`: Chatbot-teksten står nederst på forsiden.
- `test_chatbotteksten_står_ikke_på_resultatsiden`: Chatbot-teksten står ikke på resultatsiden.
- `test_kortene_står_i_rutenett_og_er_én_lenke`: Kortene står i rutenett, og hvert kort er én lenke.
- `test_varselet_er_rosa_med_ramme_og_ikon_i_rød_1`: Varselet er rosa med ramme og ikon i FHIs Rød 1.
- `test_markert_rad_er_ikke_bare_farge`: En markert rad vises med mer enn farge.

## Skriptet for demo (`backend/scripts/vis_forklaring.py`)

`test_vis_forklaring.py`

- `test_falsk_claude_gir_den_lagrede_forklaringen`: Den falske Claude-klienten gir den lagrede forklaringen.
- `test_falsk_claude_kan_feile`: Den falske klienten kan gi `KiFeil`.
- `test_ukjent_utfall_stopper_skriptet`: Et ukjent utfall stopper skriptet med en melding.
- ◦ `test_demoen_bruker_ikke_den_vanlige_porten`: Demoen bruker ikke port 8000.
- `test_main_starter_appen_med_riktig_utfall`: Skriptet starter appen med riktig utfall og uten å skrive i cachen.

## Prosjektoppsett (ingen modul i appen)

### `test_gitignore.py`

- `test_nøkler_og_cache_er_ignorert`: `.env`, `.env.local` og `.cache/` er ignorert av git.
- `test_env_example_er_ikke_ignorert`: `.env.example` er ikke ignorert.
- `test_nøkler_og_cache_er_ikke_sjekket_inn`: Ingen nøkkel- eller cachefiler er sjekket inn.
- ◦ `test_env_example_har_nøklene`: `.env.example` har `ANTHROPIC_API_KEY` og `ANTHROPIC_MODEL`.

### `test_nettsperre.py`

Disse testene sjekker testoppsettet i `pyproject.toml` (sperren mot nett), ikke appen.

- ◦ `test_socket_blir_stoppet`: En socket mot nettet stoppes.
- ◦ `test_httpx_kall_blir_stoppet`: Et `httpx`-kall stoppes.
- ◦ `test_respx_virker_med_sperren_på`: `respx` virker selv om sperren er på.
- ◦ `test_lokal_socketpair_er_tillatt`: Lokale sockets er tillatt.

### `test_readme.py`

- ◦ `test_readme_nevner_kommandoen`: README nevner kommandoene for å installere, teste og kjøre ruff.
- ◦ `test_readme_har_oppstartskommandoen`: README har kommandoen for å starte appen.
- ◦ `test_readme_sier_at_env_er_valgfri`: README sier at `.env` er valgfri.
- ◦ `test_readme_forklarer_hvordan_nøkkelen_settes_i_env`: README forklarer hvordan nøkkelen settes.

### `test_fixturemapper.py`

- ◦ `test_fixturemappe_finnes`: Mappene `fhi`, `ki` og `konstruert` finnes under `tests/fixtures`.

## Sammendrag av merkingen

- ⚠️ **2 tester** kan ikke feile på grunn av appen: `test_setningstellingen` og `test_kontrastberegningen`. Begge tester en hjelpefunksjon i selve testfila. De er likevel nyttige, fordi andre tester bruker hjelpefunksjonene.
- ◦ **28 tester** kan nesten ikke feile. De sjekker fixturene, README, `.env.example`, testoppsettet eller en fast verdi (for eksempel at tidsgrensen er 10 sekunder).
- Resten, 499 tester, kjører koden i appen.
