# ApplyForPosition – Context References

All profile content is maintained in the documentation folder.
This file contains **only paths** — never duplicate content here.

## Profile Data Sources

```
Base dir:  /Users/dh/Documents/DanielsVault/private/me/

cv.md                  Full project history, skills, certifications, education
profile.md             Contact info, rates, availability, keywords
anschreiben-template.md  Cover letter structural reference and placeholder list
bewerbungen.log        Application log — append only
applications/          Output root → {yyyy-MM}/{ts_TitleOfPosition}/
```

## Skill Tools

```
Skill dir:  /Users/dh/.claude/skills/apply-for-position/

Tools/compile.sh                   Preferred: compiles .typ → .pdf (tries dotnet→ConvertToPdf.cs, falls back to typst)
  Invoke: /path/Tools/compile.sh <input.typ> <output.pdf>
  Requires: typst in PATH (brew install typst)

Tools/ConvertToPdf.cs              C# wrapper around typst compile (used by compile.sh)
  Direct invoke: cd /tmp && dotnet run <path>/ConvertToPdf.cs -- <input.typ> <output.pdf>

Tools/Templates/CV_DE.typ          Resume header — German, Daniel's author block
Tools/Templates/CV_EN.typ          Resume header — English, Daniel's author block
Tools/Templates/Anschreiben_DE.typ Cover letter header — German
Tools/Templates/CoverLetter_EN.typ Cover letter header — English
```

## Output Naming Rules

```
Folder:   applications/{yyyy-MM}/{yyyyMMddHHmm}_{TitleCamelCase}/

DE files:
  {ts}_Daniel_Hecht_Lebenslauf_{ShortTitle}.typ   →  .pdf
  {ts}_Daniel_Hecht_Anschreiben_{ShortTitle}.typ  →  .pdf

EN files:
  {ts}_Daniel_Hecht_CV_{ShortTitle}.typ           →  .pdf
  {ts}_Daniel_Hecht_CoverLetter_{ShortTitle}.typ  →  .pdf

ShortTitle: CamelCase, max 30 chars, derived from job title
```

## Log Format

```
bewerbungen.log entry:
{yyyyMMddHHmm} | {position title} | {company} | {output folder path}
```
