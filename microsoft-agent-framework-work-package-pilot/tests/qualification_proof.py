"""Optional redacted acceptance observations from the public qualification seam."""
import json
import os
from pathlib import Path


def record(case, run, fixture, runtime_kind):
    if not (destination := os.environ.get('WPCP_QUALIFICATION_PROOF_DIR')):
        return
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    path = root / (case + '.json')
    values = json.loads(path.read_text()) if path.exists() else []
    values.append({'runId': run['runId'], 'state': run['state'],
        'headQualification': run['publication'].get('headQualification'),
        'publicationBlocker': run['publication'].get('blocker'),
        'providerPullRequests': fixture.pulls, 'providerCreates': fixture.creates,
        'controlledReviewStarts': len(fixture.review_requests),
        'controlledRepairStarts': len(fixture.repair_requests),
        'runtimeKind': runtime_kind, 'providerKind': 'controlled HTTP provider with real local and bare Git'})
    path.write_text(json.dumps(values, indent=2) + '\n')
