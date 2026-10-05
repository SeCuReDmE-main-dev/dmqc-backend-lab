"""Bounded WSGI API preparation. No provider calls, jobs, or database access."""
import hmac
import json
import os
from http import HTTPStatus

from .reference import exact_lower_bound

MAX_BODY_BYTES = 8192


def application(environ, start_response):
    def respond(status, payload):
        body = json.dumps(payload, allow_nan=False).encode('utf-8')
        start_response(f'{status} {HTTPStatus(status).phrase}', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body))),
            ('Cache-Control', 'no-store'),
            ('X-Content-Type-Options', 'nosniff'),
        ])
        return [body]

    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', '')
    if path == '/healthz' and method == 'GET':
        return respond(200, {'status': 'ok', 'service': 'dmqc-api',
                             'stage': 'deployment_preparation'})
    if path not in ('/readyz', '/v1/bounds'):
        return respond(404, {'error': 'not_found'})

    token = os.environ.get('DMQC_API_TOKEN', '')
    if len(token) < 32:
        return respond(503, {'error': 'authentication_not_configured'})
    supplied = environ.get('HTTP_AUTHORIZATION', '').encode('utf-8')
    if not hmac.compare_digest(supplied, ('Bearer ' + token).encode('utf-8')):
        return respond(401, {'error': 'unauthorized'})
    if path == '/readyz':
        if method != 'GET':
            return respond(405, {'error': 'method_not_allowed'})
        return respond(200, {'status': 'ready', 'jobs_enabled': False,
                             'database_connected': False})
    if method != 'POST':
        return respond(405, {'error': 'method_not_allowed'})
    if environ.get('CONTENT_TYPE', '').split(';')[0].strip() != 'application/json':
        return respond(415, {'error': 'json_required'})
    try:
        size = int(environ.get('CONTENT_LENGTH', '0'))
    except (ValueError, TypeError):
        return respond(400, {'error': 'invalid_content_length'})
    if size > MAX_BODY_BYTES:
        return respond(413, {'error': 'body_too_large'})
    if size <= 0:
        return respond(400, {'error': 'empty_body'})
    try:
        data = json.loads(environ['wsgi.input'].read(size))
        if not isinstance(data, dict) or not {'successes', 'total'} <= data.keys():
            raise ValueError('Missing fields')
        if data.keys() - {'successes', 'total', 'comparisons'}:
            raise ValueError('Unexpected fields')
        counts = (data['successes'], data['total'], data.get('comparisons', 1))
        if any(type(value) is not int for value in counts):
            raise ValueError('Integer counts required')
        successes, total, comparisons = counts
        if not 0 <= successes <= total <= 10_000_000 or total < 1 or not 1 <= comparisons <= 1000:
            raise ValueError('Counts outside limits')
        lower = exact_lower_bound(successes, total, comparisons)
    except (ValueError, TypeError, UnicodeDecodeError):
        return respond(400, {'error': 'invalid_bound_inputs'})
    return respond(200, {'lower_bound': lower, 'successes': successes,
                         'total': total, 'comparisons': comparisons,
                         'confidence_level': 0.95, 'correction': 'bonferroni',
                         'qualification': 'not_assessed'})
