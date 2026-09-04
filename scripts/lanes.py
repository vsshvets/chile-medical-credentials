"""The 13 research lanes. One lane = one file = one owner. English out, Spanish quotes verbatim."""

SUBJECT = """
THE PERSON THIS IS FOR (every answer is judged against her situation, not the general case):
- Ukrainian citizen. Lives in Vinnytsia, Ukraine, TODAY. Has never been to Chile.
- NO Chilean residency, NO Chilean visa, NO RUT, NO ClaveUnica.
- Medical doctor. Degree from a Ukrainian medical university (Soviet/Ukrainian system).
- PhD: "кандидат медичних наук" (candidate of medical sciences).
- Academic rank: "доцент" (dotsent) = Associate Professor level. NOT a Chilean rank.
- Works at Vinnytsia National Medical University, teaching RHEUMATOLOGY to students.
- Has taught international students IN ENGLISH. Spanish level: assume none.
- She is a practising/teaching rheumatologist, i.e. she holds a Ukrainian SPECIALTY, not just a general medical degree.
- Goal: validate her credentials in Chile NOW, pre-emptively, so that later she could
  (a) teach at a Chilean medical university, and/or (b) practise as a doctor in Chile.
- Her son lives in Chile. Family reunification may be a lever; flag it, do not assume it.
"""

RULES = """
HARD EVIDENCE RULES — a violation makes the whole lane worthless:

1. EVERY claim needs at least one source with a VERBATIM quote_original copied character-for-character
   from that exact URL. Never paraphrase into quote_original. Never invent a quote. If you cannot
   produce a real verbatim quote, lower the confidence and say so in unknowns_declared instead.
2. The URL you cite must be the page the quote is actually on. A real-but-unrelated URL is the
   most common failure. If you only have a search snippet, cite the page the snippet came from and
   say "snippet only" in quote_locator.
3. date_of_content is the SOURCE's own publication/update date. If the page shows no date, write
   exactly "UNDATED". Do not guess. UNDATED is treated as stale.
4. THE STALENESS TRAP IS THE BIGGEST RISK IN THIS PROJECT. On 17 August 2026, Decreto 174/2024
   together with Ley 21.325 art. 143 changed who may recognise/revalidate foreign degrees in Chile:
   the Universidad de Chile "privativa y excluyente" monopoly ended and accredited State universities
   may now do it. Almost every blog, forum, law-firm page and even some official pages still describe
   the OLD regime. For every legal claim set regime.regime_side to PRE / POST / NEUTRAL / UNKNOWN
   relative to that date. A page with no date, or dated before 2026-08-17, cannot support a POST claim.
5. Money: Chilean fees are usually in UTM (Unidad Tributaria Mensual), which changes every month.
   Always record the UTM figure as cost_amount with cost_unit "UTM". A CLP number without its UTM
   original and its month is wrong within 30 days.
6. Distinguish "the law permits X" from "this institution actually accepts X today". They are
   different claims with different confidence. Legal empowerment does not mean an operational process exists.
7. Never smooth over an unknown. unknowns_declared and open_questions must be non-empty and honest.
   "I could not find it" is a valid, valuable result. Inventing a plausible answer is not.
8. Write claims in ENGLISH. Keep Spanish terms in Spanish inside the English sentence. Quotes stay
   verbatim in their original language.
9. Be precise about MODALITY: "must" vs "may" vs "in practice usually" vs "unknown". A modality
   error here becomes wrong advice to a real person.
10. Use live web search aggressively. Prefer: bcn.cl/leychile, diariooficial.interior.gob.cl,
   mineduc.cl, superdesalud.gob.cl, minsal.cl, eunacom.cl, cned.cl, mifuturo.cl, cnachile.cl,
   serviciomigraciones.cl, minrel.gob.cl, and the universities' own .cl domains. Blogs and
   immigration-agency pages are NEVER a source; at most they tell you what to go and verify.
"""

LANES = {
"L01": ("The legal spine of foreign-degree recognition in Chile", """
Establish the CURRENT legal framework, as of today, for recognising a foreign professional title and a
foreign academic degree in Chile.

Answer precisely:
1. Decreto 174/2024 (Ministerio de Educacion): full title, publication date in the Diario Oficial,
   and its actual ENTRY INTO FORCE date. Quote the article that sets vigencia.
2. Ley 21.325 art. 143: quote the article verbatim. What exactly does it authorise, and for whom?
3. What did DFL 3/2006 (or DFL 2/2010, Ley General de Universidades) art. 6 say before, and is that
   text still in force? Quote the current LeyChile "Texto vigente" banner date.
4. Define the THREE distinct legal acts with a legal citation for each, and say exactly what each one
   entitles the holder to do: (a) reconocimiento, (b) revalidacion, (c) convalidacion. Also mention
   homologacion if it is a distinct term in Chilean law.
5. WHICH BODIES may now perform each act? Is Universidad de Chile still the only one operating in
   practice? What is the exact eligibility test for other universities (accreditation years, level,
   state vs private)?
6. Is there a transitional regime for files opened before 17 Aug 2026?
7. Confirm or refute: there is NO Chile-Ukraine bilateral treaty on mutual recognition of degrees.
   List the countries Chile DOES have such a route with, and name the body that runs each route.
8. Does MINEDUC have ANY role for a non-treaty country like Ukraine? Answer explicitly yes or no.
"""),

"L02": ("Universidad de Chile revalidacion, operational reality for a medical degree", """
Establish the ACTUAL step-by-step process at Universidad de Chile for revalidating a foreign
MEDICAL degree (titulo de Medico Cirujano), as it operates today.

Answer precisely:
1. The complete sequence of steps, in order, with who does what.
2. The exact portal(s) used. Is it Ucampus? Give the exact URL. What can be done online and what cannot?
3. CRITICAL: can a person who is OUTSIDE CHILE, with no RUT and no ClaveUnica, open a file at all?
   If an in-person step exists (cotejo/comparison of original documents), say exactly who must appear,
   whether a mandatario/apoderado with a poder notarial can appear instead, and whether the apostilled
   originals must be physically in Santiago.
4. The examination structure for Medicina specifically: how many exams, written/oral/practical,
   subjects, pass mark, how many retakes, in what language, on what schedule.
5. The full 2026 fee schedule with each line item and what it pays for. Quote the arancel page.
   Record every fee in UTM where the source states UTM.
6. Realistic elapsed time from submission to titulo revalidado. Distinguish the regulation's maximum
   from observed real-world duration, and label which is which.
7. Are there fixed application windows/convocatorias, or is it rolling?
8. Exact contact point: office name, email, phone, address.
"""),

"L03": ("The newly-eligible State universities route", """
Since 17 August 2026 other Chilean State universities may recognise/revalidate foreign degrees.
Establish who they actually are and whether any of them is genuinely open for business.

Answer precisely:
1. The exhaustive list of Chilean STATE universities meeting the accreditation threshold in
   Decreto 174/2024 (name, accreditation years, level, accreditation expiry date, source).
2. For each: has it actually PUBLISHED a reglamento or procedure for reconocimiento/revalidacion
   since August 2026? Give the URL and date. If it has not, say so plainly.
3. Does any of them handle MEDICINE specifically, or do they exclude regulated health professions?
4. Is a revalidacion granted by, say, USACH or Universidad de Valparaiso legally equivalent nationwide
   to one granted by Universidad de Chile? Quote the legal basis.
5. Any difference in cost, exam requirements, or waiting time between them.
6. Contact emails for the ones that are operational.
DO NOT assume that legal empowerment means an operational process exists. Check each one and report
honestly, including "no published procedure found as of today".
"""),

"L04": ("EUNACOM", """
Establish exactly what EUNACOM is and what passing it does and does NOT do.

THE SINGLE HIGHEST-RISK CLAIM IN THIS PROJECT: a scouting pass claimed "passing EUNACOM automatically
revalidates a foreign medical degree". Verify or refute this against the verbatim text of Ley 20.261
and its reglamento. It may instead only authorise practice / entry to a registry, which is a very
different thing. Quote the actual article. If the two readings are both defensible, say so and present both.

Also answer:
1. Ley 20.261 and its reglamento: what does the law say EUNACOM is for, verbatim.
2. Sections: teorica and practica. Which apply to a foreign-titled doctor?
3. PREREQUISITES to sit it as a foreign graduate whose degree is NOT yet revalidated. Is revalidacion
   a prerequisite for EUNACOM, or an alternative to it? This ordering matters enormously.
4. Does she need a RUT, a visa, or Chilean residency to register for EUNACOM?
5. Registration windows and exam dates for the next 12 months. Fee. Where it is physically sat.
   Is it ever available outside Chile?
6. Language: Spanish only?
7. Pass rates for foreign-trained doctors, if published.
8. Does a pass expire?
9. For which jobs is EUNACOM legally REQUIRED: public health services, municipal primary care,
   FONASA libre eleccion, state postgraduate training, issuing medical leave certificates (licencias
   medicas — verify the reported May 2026 rule and find the actual norm). And for which is it NOT
   required: private practice? university teaching?
"""),

"L05": ("Practising: the registry, the specialty, and rheumatology", """
Establish what a foreign doctor must do BEYOND degree recognition to legally work as a doctor,
and specifically as a RHEUMATOLOGIST, in Chile.

Answer precisely:
1. Registro Nacional de Prestadores Individuales de Salud (Superintendencia de Salud): who must be in
   it, what documents it demands from a foreign-trained doctor, cost, how long, and whether it can be
   done online from abroad.
2. Is registration in the Registro required to practise privately, or only for the public system?
3. Specialty recognition: how a foreign-obtained specialty (rheumatology) is recognised in Chile.
   Cover CONACEM (Corporacion Nacional Autonoma de Certificacion de Especialidades Medicas): dossier
   required, whether an exam is involved, fee, timeline, and whether a Ukrainian specialty certificate
   is acceptable input at all. Also cover the state route via MINSAL / DS 8/2013 if it is distinct.
4. What is the role of Sociedad Chilena de Reumatologia (SOCHIRE)?
5. What can she legally do with a revalidated degree but WITHOUT specialty certification?
   Can she work as a general practitioner? In APS? On honorarios?
6. Consequences for billing: FONASA and ISAPRE — does an uncertified specialist get paid as a specialist?
7. Is there any published shortage of rheumatologists in Chile, with a number and a source?
"""),

"L06": ("Academic hiring: what a Chilean medical faculty actually requires", """
THE MOST DECISION-RELEVANT LANE. Establish whether she needs her degree revalidated AT ALL to be
hired as an academic at a Chilean medical faculty, if she does not treat patients.

Answer precisely:
1. Is there ANY national norm requiring a revalidated title to teach at a university without clinical
   practice? Verify the NEGATIVE properly — search for it, and if you cannot find one, say so and cite
   what you checked. Look at Ley 21.091, Ley 21.094 (universidades estatales), and any Contraloria dictamen.
2. Ley 18.834 (Estatuto Administrativo) art. 12: the Chilean-nationality requirement for public
   employment. Quote it. Does it bind STATE universities? What are the exceptions? Do contrata,
   honorarios, or "profesor hora" contracts escape it? This could silently block every state university.
3. The jerarquia academica ladder (Instructor / Profesor Asistente / Profesor Asociado / Profesor
   Titular). How is rank assigned to a newly hired foreigner? Is a foreign rank ever carried over?
   (Expected answer: no, each university's comision evaluates. Verify.)
4. Find at least 4 REAL published concursos academicos at Chilean medical faculties and quote their
   "requisitos" verbatim. Do they demand a revalidated Chilean title, or just "titulo profesional de
   Medico Cirujano o equivalente"? Do they require Chilean nationality or residency? Do they require
   a doctorado?
5. Do clinical teaching posts (docencia con pacientes) always additionally require revalidacion,
   EUNACOM and registry entry? Say where the line falls.
6. Spanish language: is any certificate (SIELE/DELE) ever demanded, or is it de facto?
7. Does ANY Chilean medical faculty teach in English, or run an English-track programme?
8. Published salary ranges for academic staff at state universities (they are public by transparency law).
"""),

"L07": ("Her PhD and her docent rank: what they are worth in Chile", """
Establish how a Ukrainian "кандидат медичних наук" and the rank of "доцент" map into the Chilean system.

Answer precisely:
1. Ukrainian law: the equation of кандидат наук with доктор філософії / PhD. Cite Закон України
   "Про вищу освіту" (1556-VII) and quote the relevant provision. What DOCUMENT can she obtain in
   Ukraine that officially states this equivalence, and who issues it (МОН, НАЗЯВО, ENIC-Ukraine)?
2. In Chile, who recognises a foreign ACADEMIC DEGREE (grado academico de doctor), and is that the
   same track and the same body as for a professional title? What does it cost and how long does it take?
3. Is there a real risk a Chilean evaluator grades кандидат наук as a Magister rather than a Doctor?
   Find any Chilean or ENIC-NARIC guidance on Ukrainian/post-Soviet degrees. Report honestly if none exists.
4. Is reconocimiento of the doctorado actually NEEDED to be hired as an academic, or do universities
   simply evaluate the diploma themselves? Find evidence either way from real concursos.
5. What is "доцент" in Chilean terms? It is an academic RANK/title (атестат доцента), not a degree.
   Does Chile recognise foreign academic ranks at all? (Expected: no. Verify and state it plainly.)
6. Does she gain anything from her teaching seniority and publication record in a Chilean concurso?
"""),

"L08": ("The document chain from Ukraine", """
Establish exactly which documents she needs, how each is legalised in Ukraine, and how it must be
translated for Chile. This is the practical bottleneck and it is done from Ukraine.

Answer precisely:
1. The complete document list: диплом лікаря + додаток/виписка з оцінками (transcript with hours),
   диплом кандидата наук, атестат доцента, сертифікат лікаря-спеціаліста, трудова книжка/довідка
   про стаж, паспорт. Which does Chile actually demand for (a) revalidacion of the title,
   (b) reconocimiento of the doctorado, (c) an academic job application?
2. APOSTILLE: who apostilles each document type in Ukraine right now — МОН for education documents,
   Мін'юст for civil, МОЗ for medical/specialty certificates. Current fee, current timeline, and
   whether the electronic apostille register is accepted abroad. Note any wartime changes.
3. Chile is a party to the Apostille Convention (verify, cite the Chilean law and date). Therefore
   consular legalisation should NOT be required. Verify and state it loudly — institutions still ask
   for it wrongly.
4. TRANSLATION into Spanish. Chile has NO sworn-translator (traductor jurado/publico) system, unlike
   Spain and Argentina. Verify this. So who may translate, and how is the translation certified?
   Cover the MINREL Departamento de Traducciones, notarial certification in Chile, and whether a
   translation made in Ukraine plus an apostille on the translation is accepted.
5. Must the translation be Ukrainian to Spanish directly, or is Ukrainian to English to Spanish accepted?
6. Do any documents expire (validity window) once apostilled or translated?
7. Total realistic cost and total weeks for the whole document chain, itemised.
"""),

"L09": ("Immigration, RUT, and whether she can start from Ukraine", """
Establish whether she can begin any of this from Ukraine, and what immigration status she would need
to actually take up a post.

Answer precisely:
1. Can a foreigner with only a passport, physically abroad, open a recognition/revalidation file?
   Does the university require a RUT or ClaveUnica to even register?
2. How does a non-resident foreigner obtain a RUT? Distinguish the SII "RUT for foreigners" (tax) from
   the Registro Civil RUN (identity). Can either be obtained without being in Chile, or by a mandatario?
3. Under Ley 21.325, which visa subcategories fit her: work contract, academic/researcher, family
   reunification with a son resident in Chile. Name the exact subcategoria and quote the requirement.
4. THE MOST COMMON WRONG ANSWER: can she enter as a tourist and change status inside Chile?
   Verify against Ley 21.325 and state the rule plainly.
5. Which Chilean consulate serves Ukraine right now (the embassy situation may have changed since 2022)?
   Give the actual address and contact and where applications are filed.
6. Processing times for the relevant visa. Fees.
7. Is a signed Chilean employment contract a prerequisite for the work visa? If so, the ordering
   problem matters: she cannot get hired without status, cannot get status without a job. Say exactly
   how that loop is broken in practice.
8. Age: is there any Chilean rule limiting a work visa or public employment by age? Verify; do not assume.
9. Health cover and pension consequences for an older new resident (FONASA, AFP).
"""),

"L10": ("Every Chilean university with a Medicina programme", """
Build the complete, verified list of institutions offering the Medicina (Medico Cirujano) degree in Chile.

For EACH institution report: official full name; type (estatal / privada CRUCH / privada no-CRUCH);
city and region of each sede offering Medicina; year the Medicina programme started if available;
programme accreditation status and years and expiry (Medicina accreditation is mandatory in Chile —
flag any programme not accredited or barred from admitting); total matricula in Medicina; matricula de
primer ano for the most recent year available; vacantes ofrecidas; the year each number refers to and
which dataset it came from; arancel anual; whether the faculty has a rheumatology unit or a
rheumatology postgraduate programme; the URL of the faculty's academic-vacancies page; and the
decanato contact.

CRITICAL ON NUMBERS: matricula total, matricula de primer ano and vacantes ofrecidas are three
different metrics and are routinely confused. Always name which metric a number is and which year.
Use CNED (cned.cl bases de datos, INDICES) and SIES / mifuturo.cl as the authoritative sources.
Where CNED and SIES disagree, report both. Note that ASOFAMECH membership is NOT the same as the full
list of medical schools — do not equate them.

Put ONE claim per institution carrying its numbers, and put the institutions in entities[] too.
If you cannot verify a number, write it as unknown rather than estimating.
"""),

"L11": ("Vacancies: is anyone actually hiring", """
Establish whether Chilean medical faculties and health providers are currently hiring, with real
live postings.

Answer precisely:
1. Find as many CURRENTLY OPEN academic vacancies (concursos academicos) at Chilean medical faculties
   as you can. For each: university, faculty, post title, jornada, the verbatim requisitos, the
   application deadline, the URL, and whether foreigners/non-residents appear eligible. A posting whose
   deadline has passed is noise — record the deadline so it can be filtered.
2. Find currently open CLINICAL vacancies for rheumatologists or internal medicine physicians:
   Servicios de Salud, public hospitals, private clinicas. Same fields.
3. Name the standing channels she should watch, with URLs: each university's concursos page,
   empleospublicos.cl, the Servicio Civil, trabajando.com, laborum.cl, SOCHIRE's bolsa de trabajo,
   Colegio Medico.
4. The structural picture: published data on the shortage of medical specialists in Chile
   (MINSAL brechas de especialistas reports), rheumatology specifically, waiting lists for
   rheumatological conditions, and regional maldistribution. Numbers with sources.
5. An honest verdict: what is realistic demand for a senior foreign academic rheumatologist who does
   not yet speak Spanish? Do not flatter. State the obstacles plainly.
Record every vacancy in entities[] with its URL, and put the deadline in the entity role field.
"""),

"L12": ("What the open web wrongly says", """
This lane exists to protect the reader from stale advice, and it is deliberately different from the others.

Search the way SHE will search, in three languages:
- Ukrainian: "підтвердження диплома лікаря в Чилі", "нострифікація диплома Чилі", "робота лікарем у Чилі"
- Russian: "подтверждение диплома врача в Чили", "нострификация диплома Чили"
- Spanish: "revalidar titulo medico extranjero Chile", "convalidar titulo medico Chile",
  "homologar titulo medico Chile 2026"

For the top results of each: classify whether the page describes the PRE-17-August-2026 regime
(e.g. says only Universidad de Chile can revalidate, or never mentions Ley 21.325 / Decreto 174),
or the current one. For every stale page that still ranks well, record: the URL, the publisher, the
date if any, and EXACTLY what it gets wrong now. Also record any page that is still correct, so the
reader has somewhere safe to go.

Put each stale page in claims[] as a claim of the form "Page X still states Y, which is no longer
correct because Z", with the page as the source and a verbatim quote of the wrong statement.
Also flag any page that is outright predatory (agencies charging for "nostrification" services).
"""),

"L13": ("Costs and timelines, assembled", """
Produce the money-and-time picture for THREE scenarios. Search for any figure you do not already know.

Scenario A: academic post only, no patient contact.
Scenario B: academic post including clinical teaching with patients.
Scenario C: full clinical practice as a rheumatologist.

For each scenario give, as process_steps: every required step in order, who does it, where, whether
presence in Chile is required, the cost with its unit, and realistic min/max duration in days.
Then in claims[] state, per scenario: the total realistic cost, the total realistic elapsed time,
what is strictly REQUIRED versus merely useful, and the single biggest risk of the scenario failing.

Cover every cost: Ukrainian apostilles and translations, courier of originals, Chilean aranceles for
revalidacion and/or reconocimiento, EUNACOM fee, CONACEM fee, Superintendencia registry, visa fees,
travel and accommodation for any in-person step, and the cost of Spanish tuition to a working level.
Give the current UTM value in CLP and the month it applies to, and a current CLP/USD and CLP/UAH rate
with its date, so every figure can be converted.
""")
}
