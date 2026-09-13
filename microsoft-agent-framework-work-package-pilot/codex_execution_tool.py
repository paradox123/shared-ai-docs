"""Small MCP stdio surface: execution is authorized and sandboxed by the gateway."""
import json
import os
import sys
import urllib.request


def main():
    for line in sys.stdin:
        message = json.loads(line)
        if 'id' not in message:
            continue
        method, params = message['method'], message.get('params', {})
        if method == 'initialize':
            result = {'protocolVersion': params['protocolVersion'], 'capabilities': {'tools': {}},
                      'serverInfo': {'name': 'wpcp-execution', 'version': '1'}}
        elif method == 'ping':
            result = {}
        elif method == 'tools/list':
            result = {'tools': [{'name': 'execute',
                'description': 'Run a bounded command in the disposable repository. This is the only file-write tool.',
                'inputSchema': {'type': 'object', 'properties': {'command': {'type': 'array',
                    'items': {'type': 'string'}, 'minItems': 1}}, 'required': ['command'],
                    'additionalProperties': False}}]}
        elif method == 'tools/call' and params.get('name') == 'execute':
            try:
                request = urllib.request.Request(os.environ['WPCP_EXECUTION_URL'],
                    json.dumps(params['arguments']).encode(),
                    {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + os.environ['WPCP_EXECUTION_TOKEN']})
                with urllib.request.urlopen(request, timeout=15) as response:
                    output = json.load(response)
                result = {'content': [{'type': 'text', 'text': json.dumps(output)}], 'isError': False}
            except Exception:
                result = {'content': [{'type': 'text', 'text': 'Execution denied or unavailable.'}], 'isError': True}
        else:
            print(json.dumps({'jsonrpc': '2.0', 'id': message['id'],
                'error': {'code': -32601, 'message': 'Method not supported'}}), flush=True)
            continue
        print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}), flush=True)


if __name__ == '__main__':
    main()
