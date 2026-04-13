# Apply Workflow

Full step-by-step instructions for generating a tailored job application.

---

## Step 0 — Load Context

Read both files before doing anything else:
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
If the command fails, **stop immediately** and tell the user:
> "typst is not installed. Run `brew install typst` and retry."

---

## Step 2 — Parse Job Description

From the job description provided by the user, extract:

| Field | Notes |
|---|---|
| `job_title` | Full title as written (e.g. "Senior C# Entwickler (m/w/d)") |
| `company` | Hiring company or recruitment agency name |
| `contact_person` | Name if given, else empty |
| `salutation` | "Frau X" / "Herr X" / "Damen und Herren" / "Hiring Team" |
| `start_date` | e.g. "ab sofort" / "immediately" |
| `project_id` | Reference number or project ID if present |
| `required_skills` | List of technologies, frameworks, methods mentioned |
| `nice_to_have` | Skills marked as optional/wünschenswert |
| `language` | `DE` if description is in German, `EN` if in English |

**Language ambiguity:** If unclear, ask the user before proceeding.

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

EN filenames:
  cv_typ    = {ts}_Daniel_Hecht_CV_{ShortTitle}.typ
  cv_pdf    = {ts}_Daniel_Hecht_CV_{ShortTitle}.pdf
  cl_typ    = {ts}_Daniel_Hecht_CoverLetter_{ShortTitle}.typ
  cl_pdf    = {ts}_Daniel_Hecht_CoverLetter_{ShortTitle}.pdf
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

### 4b — Tailor technology keywords (strict rule)

For each selected project entry:
- If a required skill from the job description was **genuinely used** in that project (even if not explicitly listed in `cv.md`), **add it** to the technology line
- **Never invent** technologies that were not actually used
- Example: if job requires "Azure DevOps" and a project used CI/CD pipelines on Azure, adding "Azure DevOps" is fine

### 4c — Adapt Management Summary

Write a 3–4 sentence profile summary that:
- Opens with years of experience and primary strength matching the job
- Mentions the 3 most relevant technologies from the job description
- Closes with current engagement at SEW and parallel availability

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

= Erfahrung
#resume-entry(
  title: "Solution-Architekt, Backend Developer",
  location: "Bruchsal",
  date: "04/2024 – heute",
  description: "SEW-EURODRIVE GmbH & Co KG",
)
#resume-item[
  - Architektur und Backend-Entwicklung für Engineering Platform / Solution Finder
  - Microservices mit CQRS, REST- und GraphQL-APIs (Swagger-dokumentiert)
  - CI/CD-Pipeline mit Azure DevOps, Docker, Kubernetes
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
    target: "{salutation}",
    name: "{company}",
    street-address: "",
    city: "",
  ),
)

#letter-heading(
  job-position: "{job_title}",
  addressee: "{salutation}",
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
  - Verfügbarkeit: {start_date}, 100 %
  - Remote: 100 % bevorzugt, professionelle Home-Office-Infrastruktur vorhanden
  - Stundensatz: 90 € (Verhandlungsbasis)
  - Standort: Schlüchtern, Hessen
  - Projekt-ID: {project_id}  ← only if project_id was found
]
```

**Cover letter quality rules:**
- Aim for ~1 page (Typst will wrap naturally)
- Each "Anforderungen" paragraph: 3–5 sentences, concrete, no generic filler
- Use `profile.md` for rates and availability (always current)
- If contact person is unknown, use "Damen und Herren" / "Hiring Team"

Write the complete file to `{output_dir}/{cl_typ}`.

---

## Step 6 — Compile PDFs

Use `Tools/compile.sh` (preferred) or direct `typst compile`. Chain both in a single Bash call:
```bash
COMPILE="/Users/dh/.claude/skills/apply-for-position/Tools/compile.sh" && "$COMPILE" "{output_dir}/{cv_typ}" "{output_dir}/{cv_pdf}" && "$COMPILE" "{output_dir}/{cl_typ}" "{output_dir}/{cl_pdf}"
```

`compile.sh` tries `ConvertToPdf.cs` via `dotnet run` first, then falls back to direct `typst compile`.

**Important:** Always set shell variables and run commands in a single Bash tool call — variables do not persist between calls. Use heredoc (`cat > /tmp/file.txt << 'EOF'`) for multiline text to clipboard.

If either command fails, show the typst error and stop. Do not proceed to Step 7.

---

## Step 7 — Short Platform Text

Generate a plain-text blurb (150–300 words, line breaks allowed, **no markdown**):

Structure:
1. One-line greeting referencing the position
2. 3–5 short paragraphs covering: years of experience + core stack, most relevant project for this role, CI/CD and DevOps experience, availability and rate
3. Sign-off with email

Then run:
```bash
echo "{short_text}" | pbcopy
```
And print the text to the terminal enclosed in a clear separator so the user can see it.

---

## Step 8 — Log Entry

Append to `/Users/dh/Documents/DanielsVault/private/me/bewerbungen.log`:
```
{ts} | {job_title} | {company} | {output_dir}
```

---

## Step 9 — Summary

Print a completion summary:
```
✅ Application created for: {job_title} @ {company}
📁 Folder: {output_dir}

Files:
  {cv_typ}
  {cv_pdf}
  {cl_typ}
  {cl_pdf}

📋 Short platform text copied to clipboard.
```
