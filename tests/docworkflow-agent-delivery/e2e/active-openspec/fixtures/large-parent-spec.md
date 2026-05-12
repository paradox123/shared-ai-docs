# Active OpenSpec E2E Parent Spec Fixture

This fixture simulates a large parent spec that must not be implemented as one
monolithic context. The E2E runner derives five narrow OpenSpec changes from the
work-package markers below.

## Goal

Create one final output file containing the ordered result values from five
independent implementation slices:

```text
1
2
3
4
5
```

## Work Packages

### Work Package 1: Initialize output

Scope: create the first isolated slice result.
Result value: 1
Target part: target/output/parts/part-1.txt

### Work Package 2: Add second output

Scope: create the second isolated slice result.
Result value: 2
Target part: target/output/parts/part-2.txt

### Work Package 3: Add third output

Scope: create the third isolated slice result.
Result value: 3
Target part: target/output/parts/part-3.txt

### Work Package 4: Add fourth output

Scope: create the fourth isolated slice result.
Result value: 4
Target part: target/output/parts/part-4.txt

### Work Package 5: Add fifth output

Scope: create the fifth isolated slice result and allow final aggregation.
Result value: 5
Target part: target/output/parts/part-5.txt

## Parent-Only Constraints

- The parent spec is reference-only context.
- Each work package must become one active OpenSpec change before simulated
  implementation output is written.
- A slice must not write another slice's result file.
- The final aggregate file is valid only when all five slice outputs exist and
  contain the exact ordered values.
