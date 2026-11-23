# Site information architecture review — November 2026

**Status: proposal for discussion.** This document records a structural review of the current site and proposes an incremental target architecture. It does not authorize a redesign, a change to the curriculum, a merge, or a production deployment.

## 1. Executive assessment

The repository already has a useful technical foundation: YAML-based course data, a Python static-site generator, French and English editions, domain and module pages, session-level progress, optional accounts, and a focused one-step-at-a-time lesson interface.

The main weakness is no longer the absence of pages. It is the gap between the intended learning experience and the information architecture currently exposed to a learner.

The current hierarchy is:

1. Home
2. Seven domains
3. Modules inside each domain
4. Sessions inside each module
5. One learning step per screen

This is understandable as a content tree, but it does not yet communicate a complete learning journey. A learner can see subject areas, but cannot reliably answer:

- What should I learn first, and why?
- What will I be able to do after this module?
- Which prerequisites am I expected to know?
- How does this subject connect to another actuarial discipline?
- What is available now, what is being prepared, and what has actually been reviewed?
- How do I move from theory to a practical actuarial task?

**Recommendation:** keep the current static architecture and content format for now, but evolve the learner-facing model from a list of domains into a guided competency-based learning path.

## 2. What exists today

Observed in `contenus/parcours.yaml`, `tools/construire.py`, `site/gabarits/page.html` and `site/assets/navigation.js`:

- Seven top-level domains: Foundations, Life, Pensions, P&C, ALM, Risk and Solvency, Tools.
- Domain pages list modules; module pages list sessions.
- The home page offers a generic start/resume action and domain cards.
- The global header exposes all seven domains as primary navigation links on wide screens, plus a compact menu on smaller screens.
- Progress is calculated from completed session steps and aggregated to module/domain cards.
- A module with no referenced sessions is shown as coming soon.
- Session screens deliberately focus on one step at a time.

This is a sound first iteration. It should be improved rather than discarded.

## 3. Structural issues to solve

### 3.1 The home page is a catalogue, not yet a learning dashboard

The hero and domain cards introduce the project, but the learner's next best action is not sufficiently explicit. A first-time visitor, a returning learner, and a learner exploring a new specialty need different entry points.

The current generic start action points to the first session in the plan when no progress exists. That is a reasonable fallback, but it is not a substitute for an onboarding route or a visible explanation of the recommended sequence.

### 3.2 Domains mix different kinds of classification

The seven domains are useful as subject areas, but they are not all the same kind of thing:

- Foundations is a prerequisite layer.
- Life, Pensions, P&C, ALM and Risk are actuarial practice areas.
- Tools is a transversal capability set, not necessarily a discipline to complete after the others.

Keeping these as seven peer navigation items can make the curriculum look flatter than it is. In particular, programming, data analysis and modelling should appear inside the actuarial learning journey as well as in a tools reference area.

### 3.3 The curriculum does not yet expose competencies and prerequisites

The plan contains titles and session references, but no explicit machine-readable metadata for:

- learning outcomes;
- prerequisite modules or concepts;
- target level;
- expected workload;
- competencies demonstrated;
- assessment or module completion criteria;
- jurisdiction or professional framework where relevant.

Without these, the interface can display content but cannot explain the educational logic behind it.

### 3.4 Planned content and validated content are too easy to conflate

A domain or module can be visible while containing no sessions. A session can be authored and technically valid without having received an independent scientific or pedagogical review.

The interface and internal content model should distinguish at least:
- planned;
- in preparation;
- available;
- technically checked;
- scientifically/actuarially reviewed;
- independently reviewed;
- learner-tested;
- published.

These are separate facts, not one generic progress percentage. Learner progress must not be confused with content quality assurance.

### 3.5 Module pages need to explain the destination

A list of session titles, durations and progress bars is not enough for an advanced actuarial module. The module page should state the practical capability being built, the knowledge assumed, the expected outputs and the connection to the next module.

### 3.6 The global navigation is too domain-heavy

Seven domains in the main header give every subject the same prominence. A simpler primary navigation would make room for the learner's actual tasks and reduce the feeling of browsing a static catalogue.

## 4. Proposed learner-facing architecture

This is a proposal, not an adopted design.

### Primary navigation

Use a small number of stable destinations:

1. **My learning path** — dashboard, resume action, current milestones and recommended next step.
2. **Curriculum** — guided sequence, prerequisites and competency map.
3. **Domains** — browse actuarial disciplines and their modules.
4. **Labs and tools** — reusable Python, SQL, Excel and modelling practice, connected back to relevant modules.
5. **Resources** — glossary, references, formula sheets and methodological notes.
6. **Account / language** — existing optional account and FR/EN controls.

On narrow screens, place the same destinations in one accessible menu. Keep the language switch and account access visible without crowding the header.

### Home page: a learner dashboard

Recommended order:

1. **Resume learning** — one clear action, with the exact session and step where the learner left off.
2. **Your route** — a short visual overview of the recommended stages.
3. **Continue with the foundations** — the next available module, not a generic catalogue link.
4. **Explore a domain** — cards for Life, Pensions, P&C, ALM and Risk.
5. **Practice with tools** — transversal labs linked to the relevant lessons.
6. **How the programme works** — prerequisites, expected effort, review standards and the difference between progress and mastery.

For a first-time visitor, offer a short orientation/diagnostic route before recommending the first module. Do not force registration.

### Curriculum page: a guided route

Present the programme as a sequence of stages rather than seven equal cards:

- **Stage 0 — Mathematical and statistical foundations**
- **Stage 1 — Core actuarial techniques**
- **Stage 2 — Actuarial practice areas** (Life, Pensions, P&C)
- **Stage 3 — Enterprise applications** (ALM, Risk and Solvency)
- **Transversal capabilities** (Python, SQL, Excel, data, communication)

The final order and prerequisites must be established by a curriculum review; this grouping is a candidate model only. A learner should be able to see both the recommended path and the option to explore another domain.

### Domain page: orientation before catalogue

Each domain page should answer:

- What problems does this discipline solve?
- What should I know before starting?
- Which modules are included?
- What practical work will I be able to perform?
- How does this domain connect to other domains?
- Which content is currently available and reviewed?

A compact dependency map can show incoming prerequisites and outgoing pathways without requiring a complex interactive graph in the first iteration.

### Module page: a learning contract

Each module should expose:

- purpose and real actuarial use cases;
- learning outcomes written as observable actions;
- prerequisites and recommended refreshers;
- level and expected workload;
- ordered sessions and their status;
- a practical deliverable or applied case;
- completion criteria and the next recommended module;
- sources, jurisdiction and reference date where applicable.

### Session page: keep the one-step focus, improve orientation

Preserve the one-step-per-screen principle. Add a compact session overview with:

- learning objectives;
- estimated time;
- prerequisite reminder;
- step sequence (video, recap, quiz, hand calculation, code, vocabulary as appropriate);
- progress within the session;
- a clear return to module and curriculum;
- next session and further practice.

Do not turn the session into a long, overloaded page.

## 5. Proposed content metadata — incremental extension

Do not replace the existing YAML format. Add optional fields gradually, validate them centrally and preserve backward compatibility during migration.

Candidate module metadata:

```yaml
objectif: "Évaluer la valeur actuelle d'engagements financiers."
niveau: "intermediaire"
charge_heures: 8
prerequis: []
competences:
  - "actualiser des flux"
  - "comparer des taux équivalents"
resultat_attendu: "Construire et expliquer un échéancier actuariel."
statut_contenu: "disponible"
```

Candidate session metadata:

```yaml
objectifs:
  - "Calculer un taux effectif à partir d'un taux nominal."
prerequis:
  - "intérêt composé"
competences:
  - "conversion des taux"
```

These are illustrative fields only. Before implementation, agree a small schema, define allowed values, decide whether metadata belongs in the plan or module files, and add validator tests. Avoid duplicating information already present in the session content.

## 6. Quality model: separate learner progress from content assurance

Use two independent dimensions.

**Learner progress**
- not started;
- in progress;
- completed;
- mastery demonstrated (only where explicit, repeatable criteria exist).

**Content assurance**
- planned;
- drafted;
- structurally validated;
- calculations and code checked;
- scientifically/actuarially reviewed;
- pedagogically reviewed;
- independently reviewed;
- tested with learners;
- published.

A green progress bar must never imply that the content has been independently validated. A completed lesson is not proof of mastery.

## 7. Implementation sequence

Work in small, reversible steps.

### Phase 0 — Curriculum inventory (no UI change)

- Inventory all domains, modules and sessions.
- Record availability, language coverage, estimated effort and review status.
- Identify missing prerequisites and duplicate/overlapping modules.
- Produce a dependency table and a proposed learning sequence.
- Decide which modules are core and which are specialist extensions.

### Phase 1 — Agree the information model

- Agree module/session metadata and status vocabulary.
- Update `docs/SCHEMA-CONTENUS.md` and the canonical validator.
- Add fixtures and negative tests.
- Do not change the visual hierarchy yet.

### Phase 2 — Improve the home and primary navigation

- Add a learner dashboard state for first-time and returning visitors.
- Reduce the number of primary navigation destinations.
- Make the recommended next action explicit.
- Keep the existing routes working and preserve local-first progress.

### Phase 3 — Improve domain and module pages

- Add learning outcomes, prerequisites, workload and applied outcomes.
- Show the sequence and relationships between modules.
- Distinguish planned content from available and reviewed content.

### Phase 4 — Competency map and transversal labs

- Connect competencies to sessions and modules.
- Make labs discoverable from both the tools area and the relevant actuarial modules.
- Add a capstone or applied case only after its prerequisites and evaluation criteria are defined.

## 8. Acceptance criteria for a future UI implementation

A learner unfamiliar with the repository should be able to:

1. Explain the recommended starting point and why it comes first.
2. Identify the prerequisites and outcomes of a module before opening it.
3. Find the next available session in no more than two clear actions.
4. Resume a session without losing the selected language or current step.
5. Distinguish planned, available and reviewed content.
6. Find a Python/SQL/Excel lab from the actuarial concept it supports.
7. Navigate the same structure in French and English.
8. Use the site on mobile without horizontal overflow or a crowded navigation bar.
9. Browse and learn without creating an account.
10. Understand that learner progress is not the same as demonstrated mastery or independent content validation.

## 9. Constraints and non-goals

- Preserve the static Python generator and YAML content architecture unless evidence demonstrates a real limitation.
- No framework migration, database redesign or large rewrite as part of this work.
- Do not move or rewrite actuarial content merely to improve navigation.
- Do not claim a prerequisite sequence or professional accreditation without a documented review.
- Do not expose unfinished modules as if they were complete courses.
- Keep ACTU-BASICS as the accessible popularisation/video project; Parcours Actuariel remains the deeper learning platform.
- Keep Programme B as a separate mathematics/statistics curriculum.
- No merge or production deployment is authorized by this proposal.

## 10. Evidence reviewed

Repository files reviewed on 23 November 2026:

- `contenus/parcours.yaml`
- `tools/construire.py`
- `site/gabarits/page.html`
- `site/assets/navigation.js`
- `site/assets/style.css`
- `CLAUDE.md`

The assessment is based on source inspection, not on a moderated usability study. The proposed architecture must be validated with learners before it is treated as final.
