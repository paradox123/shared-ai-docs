| Child | Target Output Action | Predecessor | Readiness State | Handoff Path | Allowed Write-Set | Final State |
|---|---|---|---|---|---|---|
| ML-C1 | append_or_set_line:1 | parent-control | implementation-ready | large/parent-control/handoffs/ML-C1-handoff.md | large/mock-target/output/count.txt; large/sessions/ML-C1-delivery.json | ran-target + closed |
| ML-C2 | append_or_set_line:2 | ML-C1 | implementation-ready | large/parent-control/handoffs/ML-C2-handoff.md | large/mock-target/output/count.txt; large/sessions/ML-C2-delivery.json | ran-target + closed |
| ML-C3 | append_or_set_line:3 | ML-C2 | implementation-ready | large/parent-control/handoffs/ML-C3-handoff.md | large/mock-target/output/count.txt; large/sessions/ML-C3-delivery.json | ran-target + closed |
| ML-C4 | append_or_set_line:4 | ML-C3 | implementation-ready | large/parent-control/handoffs/ML-C4-handoff.md | large/mock-target/output/count.txt; large/sessions/ML-C4-delivery.json | ran-target + closed |
| ML-C5 | append_or_set_line:5 | ML-C4 | implementation-ready | large/parent-control/handoffs/ML-C5-handoff.md | large/mock-target/output/count.txt; large/sessions/ML-C5-delivery.json | ran-target + closed |
