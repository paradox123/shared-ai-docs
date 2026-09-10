import json

print(
    json.dumps(
        {
            "orchestrationId": "fixture-run-1",
            "workers": ["fixture-worker-1", "fixture-worker-2"],
            "checkpoints": ["worker-1-checkpoint", "worker-2-complete"],
            "effects": {"before-worker-stop": 1, "after-worker-stop": 1},
            "continued": True,
        }
    )
)
