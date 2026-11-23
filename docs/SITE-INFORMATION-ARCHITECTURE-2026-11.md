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


## 11. Product ambition: make learning captivating and worth returning to

The target is not merely a clean course catalogue. The site should create a durable desire to return through curiosity, meaningful progress, intellectual challenge, visual clarity and the satisfaction of understanding something difficult.

**Design principle:** delight must come from the mathematics becoming visible and usable, not from decorative effects or reward mechanics detached from learning.

### 11.1 The emotional learning loop

Each visit should make it easy to enter a purposeful loop:

1. **Intrigue** — a surprising question, real actuarial situation, visual puzzle or short prediction.
2. **Explore** — a simulation, diagram, animation, data view or worked example.
3. **Understand** — a concise explanation that connects the visual experience to the mathematical model.
4. **Apply** — a small decision, calculation, coding task or case.
5. **Reflect** — explain why the result makes sense and what assumptions matter.
6. **Progress** — see the capability gained and the next meaningful question.
7. **Return** — a saved investigation, an open challenge or a connected next concept gives a natural reason to continue.

Avoid forced daily streaks, arbitrary points, leaderboards and notifications designed only to increase time on site. They may create short-term activity without durable understanding. Returning should feel rewarding, never obligatory.

### 11.2 A distinctive visual and editorial identity

The visual language should feel like a premium scientific learning studio: precise, modern, editorial, confident and alive.

- Strong typographic hierarchy and generous breathing room.
- A restrained dark/light palette with a recognizable accent system for concepts, examples, warnings and results.
- High-quality mathematical typesetting and carefully art-directed diagrams.
- Motion only when it explains change, causality, sequence or comparison.
- Consistent visual grammar across the home page, curriculum, modules, lessons and labs.
- Responsive layouts designed intentionally for mobile, tablet and desktop.
- No generic dashboard template, cluttered cards, decorative gradients everywhere or animation for its own sake.

The site should be visually memorable without sacrificing legibility, accessibility, performance or academic seriousness.

### 11.3 Every abstract concept should have a visual or experimental counterpart

Examples of experiences that could make actuarial mathematics tangible:

- **Financial mathematics:** change the rate, frequency or payment timing and watch the present value and cash-flow timeline respond.
- **Life contingencies:** explore a survival curve, mortality table and annuity value; compare assumptions and see how the reserve changes.
- **Probability:** run repeated experiments, compare empirical frequencies with theoretical probabilities and inspect convergence.
- **Statistics:** alter a sample, fit a model, inspect residuals and understand how data quality affects conclusions.
- **Non-life insurance:** vary frequency and severity separately, then observe their effect on pure premium and portfolio loss.
- **Pricing:** change rating variables and compare predicted risk, segmentation and the consequences of a tariff adjustment.
- **Reserving:** develop a claims triangle step by step and see how assumptions affect ultimate losses and uncertainty.
- **ALM:** move yield curves and liability cash flows to observe duration gaps, convexity and immunisation.
- **Risk and solvency:** explore a loss distribution, VaR/TVaR and the impact of stress scenarios.

These are illustrative product ideas, not claims that the relevant modules are already authored or validated. Each experience must be tied to a specific learning objective and include assumptions, units, interpretation and limitations.

### 11.4 A consistent lesson rhythm, with varied teaching forms

A lesson should not be a long sequence of text blocks. Choose the format that best serves the concept, while retaining a recognizable rhythm:

- **Question / hook:** start with a real problem or prediction.
- **Intuition:** a visual, example, analogy or short video.
- **Formalisation:** definitions, assumptions, notation and derivation.
- **Experiment:** learner changes a parameter or makes a prediction.
- **Practice:** a worked example followed by a new problem.
- **Transfer:** a small actuarial case, code lab or decision.
- **Recall:** one or two questions that require retrieval or explanation.
- **Takeaway:** a concise synthesis and a meaningful next step.

Not every lesson needs all eight parts. Do not force a video, quiz or animation into every topic. Vary the rhythm deliberately to prevent monotony while keeping the cognitive load under control.

### 11.5 Meaningful reasons to return

Build return value around learning, not habit mechanics:

- a personal learning map showing concepts understood, in progress and to revisit;
- a "continue where you left off" action that restores context;
- spaced review of important concepts, with transparent and adjustable reminders inside the learning environment;
- optional weekly or thematic challenges tied to the curriculum;
- a library of interactive experiments that learners can revisit with new assumptions;
- a visible trail of completed case studies and practical outputs;
- "what changed when you changed this assumption?" investigations;
- connections between a current lesson and a previously learned concept;
- a capstone case that gradually becomes solvable as the learner acquires the necessary tools.

Do not imply mastery solely from clicks or completion. Use short explanations, retrieval questions and applied tasks to help learners calibrate what they really understand.

### 11.6 A practical editorial standard for engagement

For each new module, ask:

1. What is the most interesting real question this module can answer?
2. What misconception or surprising result can open the subject?
3. Which representation makes the invisible structure visible?
4. What can the learner manipulate, predict, calculate or decide?
5. What feedback explains the reasoning, not only whether the answer is right?
6. What practical actuarial task makes the knowledge relevant?
7. What question naturally leads to the next module?

If a module is only a collection of definitions and formulas, it is not yet ready to be considered an engaging learning experience.

### 11.7 Experience quality and evaluation

Do not use page views or time-on-site as the primary definition of success. Evaluate whether learners:

- can state what they are trying to learn and why;
- complete meaningful experiments and practice tasks;
- explain concepts in their own words;
- transfer a method to a new problem;
- return voluntarily to continue a project or revisit a concept;
- can navigate without confusion or unnecessary friction;
- report that the experience is clear, stimulating and appropriately challenging.

Test prototypes with learners before a full redesign. Track only proportionate, privacy-conscious measures; no invasive behavioural profiling is required.

## 12. Research basis and design cautions

The engagement direction is informed by, but should not be confused with, proof that any single interface feature will work for this audience:

- The OECD's *Digital Education Outlook 2021* distinguishes shallow engagement from deeper cognitive engagement and discusses the ICAP framework (interactive, constructive, active, passive). It cautions that superficial gamification may not sustain deep engagement and recommends experiences that promote constructive and interactive learning: https://www.oecd.org/en/publications/oecd-digital-education-outlook-2021_589b283f-en/full-report/component-7.html
- OECD's *Unlocking High-Quality Teaching* recommends first-hand experiences tied clearly to learning goals and prior knowledge, with reflection that connects the experience back to the intended learning: https://www.oecd.org/en/publications/2025/04/unlocking-high-quality-teaching_808bd876/full-report/ensuring-cognitive-engagement_998c3147.html
- Asher and Carvalho (2026), *Conditions for Effective Learning Without Upfront Instruction*, report benefits of practice with feedback and emphasize that explanatory feedback and sufficient prior knowledge matter for generalisation: https://doi.org/10.1007/s10648-025-10103-6

The design must balance curiosity with cognitive load. A beautiful interaction that distracts from the mathematical idea is a failed learning feature.

## 13. Additional acceptance criteria: captivating without becoming distracting

A future implementation should also satisfy:

1. The first screen communicates the identity, purpose and immediate next action without requiring the learner to decode a dense menu.
2. Each module has at least one compelling real-world question and one meaningful application, where the subject permits it.
3. Interactive elements let learners make a prediction or change an assumption and receive explanatory feedback.
4. Animations and visualisations have a clear instructional purpose, can be paused or controlled, and respect reduced-motion preferences.
5. The visual system is consistent and polished across FR and EN, and across mobile and desktop.
6. A returning learner can resume immediately and see a meaningful next step.
7. Optional review and challenge features support durable learning without punitive streaks, manipulative notifications or public ranking.
8. Learners can explain more after the experience, not merely report that it looked attractive.
9. Performance, keyboard access, contrast, captions and readable mathematical notation are treated as core requirements.
10. The product is tested with actual learners before claiming that it is engaging or successful.
