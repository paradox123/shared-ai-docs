---
name: apply-for-position
description: Creates tailored job application documents (CV and cover letter as Typst/PDF, a one-page project profile, plus a short plain-text platform blurb) from a pasted job description. USE WHEN user pastes a job posting and wants to apply, generate Bewerbungsunterlagen, create application documents, write an Anschreiben and Lebenslauf, or prepare a freelancer/project application package.
---

# ApplyForPosition

Generates a complete, tailored job application from a pasted job description.
Produces a compact application package: CV PDF, cover-letter PDF, one-page
project profile, and a short plain-text blurb for web portals — all in one
workflow. The workflow includes a strict preflight check for salutation,
availability, consistency, and concrete senior-level evidence before anything is
compiled. After PDF generation, it must run a real artifact review over the
compiled PDFs and generated text files, fix blocking findings, and only hand back
documents after the package is explicitly marked approved for sending.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **Apply** | User pastes a job description and wants to apply | `Workflows/Apply.md` |

## Examples

**Example 1: German job posting**
```
User: [pastes German job description for "Senior C# Entwickler"]
→ Invokes Apply workflow
→ Detects DE, extracts job metadata
→ Generates tailored Lebenslauf + Anschreiben as .typ → .pdf, plus Projektprofil
→ Reviews compiled PDFs and generated text artifacts before handoff
→ Prints short platform text to terminal + clipboard only after approval
```

**Example 2: English job posting**
```
User: [pastes English job description for "Cloud Architect"]
→ Invokes Apply workflow
→ Detects EN, generates CV + CoverLetter in English
→ Compiles PDFs, reviews artifacts, outputs platform text after approval
```

**Example 3: Ambiguous / partial input**
```
User: "Apply for this: [short snippet without clear language]"
→ Asks user to confirm language (DE/EN) before proceeding
```
