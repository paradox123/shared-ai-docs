---
name: apply-for-position
description: Creates tailored job application documents (CV and cover letter as Typst/PDF, plus a short plain-text platform blurb) from a pasted job description. USE WHEN user pastes a job posting and wants to apply, generate Bewerbungsunterlagen, create application documents, or write an Anschreiben and Lebenslauf.
---

# ApplyForPosition

Generates a complete, tailored job application from a pasted job description.
Produces two PDF documents (CV + cover letter) via Typst and a short plain-text
blurb for web portals — all in one workflow.

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
→ Generates tailored Lebenslauf + Anschreiben as .typ → .pdf
→ Prints short platform text to terminal + clipboard
```

**Example 2: English job posting**
```
User: [pastes English job description for "Cloud Architect"]
→ Invokes Apply workflow
→ Detects EN, generates CV + CoverLetter in English
→ Compiles PDFs, outputs platform text
```

**Example 3: Ambiguous / partial input**
```
User: "Apply for this: [short snippet without clear language]"
→ Asks user to confirm language (DE/EN) before proceeding
```
