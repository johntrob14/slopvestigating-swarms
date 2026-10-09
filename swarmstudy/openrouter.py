"""The sole inference network boundary. Never accepts a tool URL or follows redirects."""
import http.client
import json


class TransportError(RuntimeError):
    pass


def complete(payload, api_key):
    connection = http.client.HTTPSConnection('openrouter.ai', timeout=180)
    try:
        connection.request('POST', '/api/v1/chat/completions',
                           body=json.dumps(payload, ensure_ascii=False).encode(),
                           headers={'Authorization': 'Bearer ' + api_key,
                                    'Content-Type': 'application/json'})
        response = connection.getresponse()
        raw = response.read().decode('utf-8')
        if response.status != 200:
            # No retries: the billing state of a failed request may be unknown.
            raise TransportError(f'OpenRouter HTTP {response.status}: {raw[:2000]}')
        result = json.loads(raw)
        if result.get('error'):
            raise TransportError('OpenRouter error: ' + json.dumps(result['error']))
        return result
    finally:
        connection.close()
