import io
import json
import os
import unittest
from unittest.mock import patch

from dmqc_lab.render_app import application


class RenderAppTests(unittest.TestCase):
    def request(self, path='/v1/bounds', method='POST', body=None,
                authorization=True, configured=True, length=None):
        payload = json.dumps(body if body is not None else {'successes': 149, 'total': 149}).encode()
        status = []
        environ = {'PATH_INFO': path, 'REQUEST_METHOD': method,
                   'CONTENT_TYPE': 'application/json',
                   'CONTENT_LENGTH': str(len(payload) if length is None else length),
                   'wsgi.input': io.BytesIO(payload)}
        if authorization:
            environ['HTTP_AUTHORIZATION'] = 'Bearer ' + 'test-only-' * 4
        with patch.dict(os.environ, {'DMQC_API_TOKEN': 'test-only-' * 4 if configured else ''}):
            result = b''.join(application(environ, lambda s, h: status.append(s)))
        return int(status[0].split()[0]), json.loads(result)

    def test_health_does_not_require_credentials(self):
        self.assertEqual(self.request('/healthz', 'GET', authorization=False, configured=False)[0], 200)

    def test_protected_endpoint_fails_closed(self):
        self.assertEqual(self.request(configured=False)[0], 503)
        self.assertEqual(self.request(authorization=False)[0], 401)

    def test_exact_reference_and_no_qualification_claim(self):
        status, result = self.request()
        self.assertEqual(status, 200)
        self.assertAlmostEqual(result['lower_bound'], .05 ** (1 / 149), places=12)
        self.assertEqual(result['qualification'], 'not_assessed')
        _, corrected = self.request(body={'successes': 149, 'total': 149, 'comparisons': 5})
        self.assertLess(corrected['lower_bound'], result['lower_bound'])

    def test_invalid_and_unbounded_inputs_are_rejected(self):
        for body in ({'successes': True, 'total': 1}, {'successes': 2, 'total': 1},
                     {'successes': 0, 'total': 0}, {'successes': 1, 'total': 10_000_001},
                     {'successes': 1, 'total': 1, 'comparisons': 1001},
                     {'successes': 1, 'total': 1, 'shell': 'anything'}, []):
            with self.subTest(body=body):
                self.assertEqual(self.request(body=body)[0], 400)
        self.assertEqual(self.request(length=8193)[0], 413)
        self.assertEqual(self.request(method='GET')[0], 405)
        self.assertEqual(self.request(path='/v1/jobs')[0], 404)


if __name__ == '__main__':
    unittest.main()
