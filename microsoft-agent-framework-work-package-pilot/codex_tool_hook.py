"""PreToolUse authorization. Errors produce an explicit denial."""
import json
from pathlib import Path
import sys
import urllib.request


def main():
    allowed = False
    try:
        configuration = json.loads(Path(sys.argv[1]).read_text())
        tool = json.load(sys.stdin)
        request = urllib.request.Request(configuration['url'], json.dumps(tool).encode(),
            {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + configuration['token']})
        with urllib.request.urlopen(request, timeout=10) as response:
            allowed = json.load(response).get('allowed') is True
    except Exception:
        pass
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
        'permissionDecision': 'allow' if allowed else 'deny',
        'permissionDecisionReason': 'Run authorization checked' if allowed else 'Run control denied or unavailable'}}))


if __name__ == '__main__':
    main()
