# Apply Workflow

Full step-by-step instructions for generating a tailored job application.

---

## Step 0 — Load Context

Read these files before doing anything else:
- `/Users/dh/.claude/skills/apply-for-position/Context.md` — paths and naming rules
- `/Users/dh/Documents/DanielsVault/private/me/profile.md` — contact info, rates, availability
- `/Users/dh/Documents/DanielsVault/private/me/cv.md` — full project history and skills
- `/Users/dh/Documents/DanielsVault/private/me/anschreiben-template.md` — cover letter structure reference

---

## Step 1 — Tooling Check

Run:
```bash
typst --version
```
If this command fails, **stop immediately** and tell the user:
> "typst is not installed. Run `brew install typst` and retry."

Then run the optional PDF review tooling probe:
```bash
command -v pdftotext >/dev/null && pdftotext -v 2>&1 | head -1 || true
command -v pdfinfo >/dev/null && pdfinfo -v 2>&1 | head -1 || true
```

`pdftotext` and `pdfinfo` are strongly preferred for the post-PDF review. If
they are missing, continue only if you can still inspect the generated PDFs with
an equivalent local tool; otherwise stop and tell the user that PDF review cannot
be performed reliably.

---

## Step 2 — Parse Job Description

From the job description provided by the user, extract:

| Field | Notes |
|---|---|
| `job_title` | Full title as written (e.g. "Senior C# Entwickler (m/w/d)") |
| `company` | Hiring company or recruitment agency name |
| `contact_person` | Name if given, else empty |
| `address_salutation` | Address block form: "Frau X" / "Herr X" / "Damen und Herren" / "Hiring Team" |
| `letter_dear` | Typst `dear:` parameter: "Sehr geehrter" for male, "Sehr geehrte" for female/unknown, "Dear" for EN |
| `start_date` | e.g. "ab sofort" / "immediately" |
| `project_id` | Reference number or project ID if present |
| `required_skills` | List of technologies, frameworks, methods mentioned |
| `nice_to_have` | Skills marked as optional/wünschenswert |
| `explicit_utilization` | Percentage or workload explicitly required by the posting, if present |
| `language` | `DE` if description is in German, `EN` if in English |

**Language ambiguity:** If unclear, ask the user before proceeding.

**German salutation rule (hard gate):**
- Address block: `Herr Nachname` / `Frau Nachname`
- For `#letter-heading`, set `addressee: "Herr Nachname"` and `dear: "Sehr geehrter"` for male contacts.
- For `#letter-heading`, set `addressee: "Frau Nachname"` and `dear: "Sehr geehrte"` for female contacts.
- Unknown contact: `addressee: "Damen und Herren"` and `dear: "Sehr geehrte"`.
- Never write `Sehr geehrte Herr ...`.
- If the gendered salutation is uncertain, use `Sehr geehrte Damen und Herren,`.

---

## Step 2b — Choose Offer Variant and Constraints

Read `profile.md` and choose exactly one offer variant:

| Variant | Use when | Availability wording |
|---|---|---|
| A — Standard | Posting does not explicitly require full-time / 100% | `80 % Auslastung` |
| B — Full-time option | Posting explicitly requires 100%, Vollzeit, full-time, or 5 Tage/Woche | `100 % Auslastung` |

Hard rules:
- Default to Variant A.
- Use Variant B only when the posting clearly requires it.
- Keep availability wording identical in CV, cover letter, project profile, and platform text.
- Do not mention that Daniel currently works at SEW in the availability sentence.
- Do not write `neues Vollzeitmandat` unless Variant B was selected.
- If the posting asks for a workload below 80% or conflicts with the profile constraints, ask the user before generating documents.

---

## Step 3 — Compute Naming

```
ts          = current datetime as yyyyMMddHHmm
ShortTitle  = job_title stripped to key words, CamelCase, no spaces, max 30 chars
              Examples: SeniorCSharpEntwickler, CloudArchitect, BackendDeveloperNet

folder_name = {ts}_{ShortTitle}
output_dir  = /Users/dh/Documents/DanielsVault/private/me/applications/{yyyy-MM}/{folder_name}/

DE filenames:
  cv_typ    = {ts}_Daniel_Hecht_Lebenslauf_{ShortTitle}.typ
  cv_pdf    = {ts}_Daniel_Hecht_Lebenslauf_{ShortTitle}.pdf
  cl_typ    = {ts}_Daniel_Hecht_Anschreiben_{ShortTitle}.typ
  cl_pdf    = {ts}_Daniel_Hecht_Anschreiben_{ShortTitle}.pdf
  pp_md     = {ts}_Daniel_Hecht_Projektprofil_{ShortTitle}.md
  txt_file  = {ts}_Daniel_Hecht_Plattformtext_{ShortTitle}.txt
  review_md = {ts}_Daniel_Hecht_Review_{ShortTitle}.md

EN filenames:
  cv_typ    = {ts}_Daniel_Hecht_CV_{ShortTitle}.typ
  cv_pdf    = {ts}_Daniel_Hecht_CV_{ShortTitle}.pdf
  cl_typ    = {ts}_Daniel_Hecht_CoverLetter_{ShortTitle}.typ
  cl_pdf    = {ts}_Daniel_Hecht_CoverLetter_{ShortTitle}.pdf
  pp_md     = {ts}_Daniel_Hecht_ProjectProfile_{ShortTitle}.md
  txt_file  = {ts}_Daniel_Hecht_PlatformText_{ShortTitle}.txt
  review_md = {ts}_Daniel_Hecht_Review_{ShortTitle}.md
```

Create the output folder:
```bash
mkdir -p "{output_dir}"
```

---

## Step 4 — Generate CV (.typ file)

### 4a — Select and rank projects

From `cv.md`, score each project entry against `required_skills`:
- **High relevance**: project uses 3+ required skills → include, place near top
- **Medium relevance**: 1–2 required skills → include
- **Low relevance**: 0 required skills and old/unrelated → omit or move to bottom
- Keep at most 6–7 project entries for readability
- Put the 2–3 strongest proof projects on page 1 whenever possible.
- Do not include both very old and weakly relevant projects just to show breadth.

### 4b — Tailor technology keywords (strict rule)

For each selected project entry:
- If a required skill from the job description was **genuinely used** in that project (even if not explicitly listed in `cv.md`), **add it** to the technology line
- **Never invent** technologies that were not actually used
- Example: if job requires "Azure DevOps" and a project used CI/CD pipelines on Azure, adding "Azure DevOps" is fine

### 4c — Adapt Management Summary

Write a 3–4 sentence profile summary that:
- Opens with years of experience and primary strength matching the job
- Mentions the 3 most relevant technologies or methods from the job description
- States the target role and business value without sounding generic
- Does not close with availability and does not mention a parallel SEW engagement
- Never uses wording that creates a contradiction with the selected offer variant

After `= Profil`, add a short `= Kernmatch` section before `= Erfahrung`:
- 3–4 bullets only
- Each bullet maps a job must-have to one concrete proof point
- At least one bullet must mention a named reference project
- Keep the whole CV to 2 pages unless the user explicitly asks for a longer profile

### 4d — Write the .typ file

Start with the full content of the matching language template:
- DE: `/Users/dh/.claude/skills/apply-for-position/Tools/Templates/CV_DE.typ`
- EN: `/Users/dh/.claude/skills/apply-for-position/Tools/Templates/CV_EN.typ`

Copy the entire template header (the `#import` and `#show: resume.with(...)` block)
then append the content sections — **remove all comment lines** (lines starting with `//`).

**Typst syntax reference (CV):**
```typst
= Profil
#resume-item[
  Management summary paragraph here (no bullet points in this section).
]

= Kernmatch
#resume-item[
  - C\#/.NET: konkrete Senior-Erfahrung aus SEW, BNP, DekaBank oder DZR
  - Delivery/Betrieb: konkrete CI/CD-, Kubernetes- oder Monitoring-Erfahrung
  - Ergebnisbezug: belastbare Wirkung, Umfang oder Verantwortungsniveau nennen
]

= Erfahrung
#resume-entry(
  title: "Solution-Architekt, Backend Developer",
  location: "Bruchsal",
  date: "04/2024 – heute",
  description: "SEW-EURODRIVE GmbH & Co KG",
)
#resume-item[
  - Architektur und Backend-Entwicklung für eine Engineering-Plattform mit Microservices, CQRS sowie REST-/GraphQL-Schnittstellen
  - Stabilisierung von Delivery- und Betriebsprozessen in Kubernetes-Umgebungen mit Monitoring- und CI/CD-Bezug
  - Technische Schnittstellen- und Datenflussarbeit in einem produktionsnahen Enterprise-Kontext
  Technologien: C#, .NET 8, ASP.NET Core, MS SQL Server, Entity Framework, Azure DevOps, Docker, Kubernetes
]

= Kenntnisse
#resume-skill-item("Backend & APIs", (strong("C#"), strong(".NET 8"), strong("ASP.NET Core"), "REST", "GraphQL", "WPF", "Blazor"))
#resume-skill-item("Datenbanken", (strong("MS SQL Server"), "Entity Framework 4–8", "LINQ", "Dapper.NET", "SSIS"))
#resume-skill-item("DevOps", (strong("Azure DevOps"), "Docker", "Kubernetes", "GitHub Actions", "Jenkins"))
#resume-skill-item("Methoden", ("Scrum", "Kanban", "CQRS", "TDD", "TOGAF", "ITIL"))
#block(below: 0.65em)

= Zertifizierungen
#resume-item[
  - iSAQB Certified Professional for Software Architecture
  - TOGAF 9 Certified
  - ITIL 4 Foundation Certificate in IT Service Management
]

= Ausbildung
#resume-entry(
  title: "Fachschule Wiesbaden",
  location: "Wiesbaden",
  date: "2003 – 2007",
  description: "Dipl. Inform. (FH), Allgemeine Informatik",
)
#resume-entry(
  title: "HBFS Informatik Kaiserslautern",
  location: "Kaiserslautern",
  date: "2001 – 2003",
  description: "Staatl. gepr. Informatikassistent, Technische Informatik",
)
```

**Typst escaping rules (IMPORTANT):**
- Inside content blocks `[...]`: escape `#` as `\#` — e.g. `C\#`, `C\#/.NET`
- Inside string arguments `"..."`: do NOT escape — `"C#"` and `"C#/.NET"` are correct as-is
- `.NET`, `ASP.NET`, `/`, `-` need no escaping anywhere

Write the complete file to `{output_dir}/{cv_typ}`.

**CV quality rules (hard gate):**
- Top projects must not be only task lists. Each of the first 3 projects needs at least one bullet that shows outcome, scope, stability, responsibility, or business relevance.
- Avoid weak generic verbs as the main signal: `Mitarbeit`, `Unterstützung`, `Begleitung`, `Konzeption` without concrete result.
- Do not overfit by adding technologies that are not genuinely supported by Daniel's history.
- Do not expose internal availability tension; use only the selected variant.

---

## Step 5 — Generate Cover Letter (.typ file)

Start with the full content of the matching language template:
- DE: `/Users/dh/.claude/skills/apply-for-position/Tools/Templates/Anschreiben_DE.typ`
- EN: `/Users/dh/.claude/skills/apply-for-position/Tools/Templates/CoverLetter_EN.typ`

Copy the template header, remove all comment lines, then append:

**Typst syntax reference (cover letter, DE):**
```typst
#hiring-entity-info(
  entity-info: (
    target: "{address_salutation}",
    name: "{company}",
    street-address: "",
    city: "",
  ),
)

#letter-heading(
  job-position: "{job_title}",
  addressee: "{address_salutation}",
  dear: "{letter_dear}",
)

= Über mich
#coverletter-content[
  Opening: reference the job posting, express specific interest in this role.
  One paragraph, 3–5 sentences.
]

= Ihre Anforderungen – Meine Qualifikationen
#coverletter-content[
  For each major required skill group (2–4 groups):
  Write a short paragraph matching the requirement to a concrete project from Daniel's history.
  Be specific: name the client, the technology, and what was achieved.
  Do NOT use bullet points here — flowing prose only.
]

= Verfügbarkeit und Konditionen
#coverletter-content[
  - Verfügbarkeit: {start_date}, {selected_availability}
  - Remote: 100 % bevorzugt
  - Stundensatz: 90 € (Verhandlungsbasis)
  - Standort: Schlüchtern, Hessen
  - Projekt-ID: {project_id}  ← only if project_id was found
]
```

**Cover letter quality rules:**
- Aim for ~1 page (Typst will wrap naturally)
- Each "Anforderungen" paragraph: 3–5 sentences, concrete, no generic filler
- Use `profile.md` for rates and availability (always current)
- If contact person is unknown or gender is uncertain, use "Damen und Herren" / "Hiring Team"
- Do not repeat the full CV. The cover letter should prove fit, remove risk, and state conditions.
- Put the selected availability variant in conditions only; do not over-explain the parallel-search situation.

Write the complete file to `{output_dir}/{cl_typ}`.

---

## Step 6 — Generate Project Profile (.md file)

Generate a one-page project profile from:
- `/Users/dh/Documents/DanielsVault/private/me/workflows/projektprofil-template.md`
- selected offer variant
- the 2–3 strongest matching projects from the CV

Write `{output_dir}/{pp_md}`.

Quality rules:
- Keep it skimmable: one page when rendered or pasted.
- The first screen must answer: target role, strongest match, availability, rate.
- Use 3–5 direct skill-match bullets: `Requirement -> proof project / concrete experience`.
- Use 2–3 reference projects with role, stack, and result/scope.
- If exact metrics are unknown, use honest scope wording such as `produktionsnah`, `mehrere Teams`, `regulierungsnah`, `plattformkritisch`, or `langlaufendes Mandat`; never invent numbers.

---

## Step 7 — Short Platform Text

Generate a plain-text blurb (150–300 words, line breaks allowed, **no markdown**).

Structure:
1. One-line greeting referencing the position
2. 3–5 short paragraphs covering: years of experience + core stack, most relevant project for this role, CI/CD and DevOps experience, selected availability and rate
3. Sign-off with email

Quality rules:
- Lead with fit and availability in the first 4 lines.
- Mention exactly the same availability variant as the PDFs and project profile.
- Keep it more direct than the cover letter; this is often the first thing a recruiter scans.

Write the text to `{output_dir}/{txt_file}`.

Do **not** copy the platform text to the clipboard yet. Clipboard copy happens
only after the post-PDF artifact review passes.

---

## Step 8 — Preflight Quality Gate

Before compiling or returning files, review all generated text. Stop and fix the files if any gate fails:

1. German greeting compiles grammatically correct via `#letter-heading(..., dear: ...)`: `Sehr geehrter Herr`, `Sehr geehrte Frau`, or `Sehr geehrte Damen und Herren`.
2. Availability is identical in CV, cover letter, project profile, and platform text.
3. Variant B / 100% is used only when the posting explicitly requires it.
4. No sentence says Daniel is available for a new full-time mandate while also implying a current parallel engagement.
5. The first CV page contains `Profil`, `Kernmatch`, and the strongest matching projects.
6. The first 3 CV projects include concrete proof of outcome, scope, responsibility, or system relevance.
7. Cover letter names 2–3 concrete reference projects and does not rely on generic claims.
8. Project ID, contact person, company, rate, and remote preference are consistent across all outputs.
9. No invented technologies, metrics, certifications, public references, or contact channels.
10. Date and language conventions match the application language.

---

## Step 9 — Compile PDFs

Use `Tools/compile.sh` (preferred) or direct `typst compile`. Chain both in a single Bash call:
```bash
COMPILE="/Users/dh/.claude/skills/apply-for-position/Tools/compile.sh" && "$COMPILE" "{output_dir}/{cv_typ}" "{output_dir}/{cv_pdf}" && "$COMPILE" "{output_dir}/{cl_typ}" "{output_dir}/{cl_pdf}"
```

`compile.sh` tries `ConvertToPdf.cs` via `dotnet run` first, then falls back to direct `typst compile`.

**Important:** Always set shell variables and run commands in a single Bash tool call — variables do not persist between calls. Use heredoc (`cat > /tmp/file.txt << 'EOF'`) for multiline text to clipboard.

If either command fails, show the typst error and stop.

---

## Step 10 — Post-PDF Artifact Review and Approval Gate

After both PDFs were generated, perform a real review of the compiled artifacts.
This is mandatory because the user may upload the generated files without
reading them again.

### 10a — Extract review text from PDFs

Create temporary review text files from the generated PDFs:
```bash
pdftotext -layout "{output_dir}/{cv_pdf}" "{output_dir}/.review_cv.txt"
pdftotext -layout "{output_dir}/{cl_pdf}" "{output_dir}/.review_cl.txt"
```

If `pdfinfo` is available, also check page counts:
```bash
pdfinfo "{output_dir}/{cv_pdf}" | rg "^Pages:"
pdfinfo "{output_dir}/{cl_pdf}" | rg "^Pages:"
```

Review the extracted PDF text, not only the `.typ` source. The compiled PDF text
is the artifact the recipient will see.

### 10b — Review all sendable artifacts

Review these files together:
- `{output_dir}/{cv_pdf}` via `.review_cv.txt`
- `{output_dir}/{cl_pdf}` via `.review_cl.txt`
- `{output_dir}/{pp_md}`
- `{output_dir}/{txt_file}`

Use a strict reviewer stance. Treat the package as not sendable if any blocking
finding exists.

Blocking findings:
1. Broken or grammatically wrong greeting, address, company, contact person, job title, project ID, date, language, or filename signal.
2. Availability, rate, remote preference, start date, or workload differs across artifacts.
3. The package implies 100% / full-time availability without a posting requirement.
4. The package mentions the SEW parallel engagement in availability or creates credibility risk around current workload.
5. The first CV page does not clearly show `Profil`, `Kernmatch`, and the strongest matching proof projects.
6. CV or project profile rely on generic task lists without outcome, scope, responsibility, seniority, or system relevance.
7. Cover letter reads like generic boilerplate, repeats the CV mechanically, or fails to name concrete reference projects.
8. Technologies, metrics, certifications, public references, contact channels, client names, or role titles are invented, exaggerated, or unsupported by `cv.md` / `profile.md`.
9. The generated PDF text shows Typst artifacts, broken escaping, missing characters, broken line flow, orphan headings, or obviously awkward wrapping.
10. Project profile or platform text contains markdown/table/layout that is unsuitable for direct portal copy.
11. Any artifact contains internal workflow notes, private caveats, prompts, review markers, or `[ZU PRÜFEN]`-style uncertainty markers.
12. The application undersells the strongest match from the job posting or selects weaker projects while stronger proof exists in `cv.md` / `profile.md`.

Non-blocking findings:
- Minor wording polish that does not affect credibility, fit, correctness, or sendability.
- Slight length imperfections when the document remains readable and professional.

### 10c — Fix loop

If a blocking finding is found:
1. Edit the affected source file(s): `.typ`, project profile, or platform text.
2. Re-run Step 8 preflight for all generated text.
3. Re-run Step 9 compilation for affected PDFs.
4. Re-run Step 10 from the beginning.

Do not ask the user to review or approve routine fixes. Only interrupt the user
when a finding depends on factual information that cannot be inferred safely from
`cv.md`, `profile.md`, or the job posting.

### 10d — Write review report

Write `{output_dir}/{review_md}` with:
```markdown
# Bewerbungsartefakt-Review

- Position: {job_title}
- Unternehmen: {company}
- Zeitpunkt: {ts}
- Verdict: freigegeben / nicht freigegeben

## Geprüfte Artefakte
- {cv_pdf}
- {cl_pdf}
- {pp_md}
- {txt_file}

## Prüfergebnis
- PDF-Text extrahiert und geprüft: ja
- Verfügbarkeit/Konditionen konsistent: ja/nein
- Anrede/Adressierung geprüft: ja/nein
- CV-Kernmatch und erste Projekte geprüft: ja/nein
- Anschreiben auf konkrete Referenzprojekte geprüft: ja/nein
- Projektprofil und Plattformtext auf Copy/Paste-Tauglichkeit geprüft: ja/nein
- Keine erfundenen oder privaten internen Angaben: ja/nein

## Findings
- Keine blocking Findings.

## Freigabe
Nur bei `Verdict: freigegeben` dürfen die Unterlagen an den User übergeben werden.
```

If any blocking finding remains, set `Verdict: nicht freigegeben`, summarize the
blocker, and do not proceed to clipboard copy, log entry, or completion summary.

### 10e — Clipboard copy after approval

Only after `{review_md}` contains `Verdict: freigegeben`, copy the platform text:
```bash
pbcopy < "{output_dir}/{txt_file}"
```

Print the platform text to the terminal enclosed in a clear separator so the user
can see what will be pasted.

---

## Step 11 — Log Entry

Append to `/Users/dh/Documents/DanielsVault/private/me/bewerbungen.log`:
```
{ts} | {job_title} | {company} | {output_dir} | reviewed: freigegeben
```

---

## Step 12 — Summary

Print a completion summary:
```
✅ Application created and reviewed for: {job_title} @ {company}
📁 Folder: {output_dir}

Files:
  {cv_typ}
  {cv_pdf}
  {cl_typ}
  {cl_pdf}
  {pp_md}
  {txt_file}
  {review_md}

📋 Short platform text copied to clipboard after artifact review.
🧾 Review verdict: freigegeben
```
