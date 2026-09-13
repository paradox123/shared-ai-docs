import unittest
from codex_contract import validate_result, canonical_schema, endpoint_schema


class CodexContractTests(unittest.TestCase):
    def test_completed_result_without_evidence_is_rejected(self):
        result = {'schema_version': '3', 'outcome': 'completed', 'summary': 'Done',
                  'red_green_slices': [], 'changed_files': [], 'verification': [],
                  'evidence': [], 'findings': [], 'intervention': None}
        self.assertIn('evidence:minItems', validate_result(result))

    def test_endpoint_projection_preserves_fields_without_canonical_conditionals(self):
        canonical = canonical_schema()
        endpoint = endpoint_schema()
        self.assertNotIn('allOf', endpoint)
        self.assertEqual(canonical['required'], endpoint['required'])
        self.assertIn('allOf', canonical_schema())
        self.assertIn('anyOf', endpoint['properties']['intervention'])
        self.assertEqual({'command', 'observed'}, set(endpoint['$defs']['command_observation']['properties']))
