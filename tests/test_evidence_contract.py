import copy
import json
from pathlib import Path
import unittest

from repo_response_judge.judge import judge_comparison

ROOT = Path(__file__).resolve().parents[1]


def payload():
    return {
        'task_id': 'task-001',
        'requirements': [{'id': 'duplicate', 'expected_behavior': 'Same key has one side effect', 'kind': 'correctness'},
                         {'id': 'retry', 'expected_behavior': 'Failure can be retried', 'kind': 'regression'}],
        'allowed_paths': ['src/**', 'tests/**'],
        'response_a': response(), 'response_b': response(),
    }


def response():
    return {
        'files_changed': ['src/service.py'],
        'commands': [{'id': 'unit', 'argv': ['python', '-m', 'unittest'], 'exit_code': 0,
                      'started_at': '2026-09-18T12:00:00+00:00', 'finished_at': '2026-09-18T12:00:01+00:00'}],
        'test_results': [{'command_id': 'unit', 'requirement_ids': ['duplicate', 'retry'], 'passed': 2, 'failed': 0, 'skipped': 0}],
        'explanation': {'text': 'Share work for the key, then clear failures.', 'source_refs': ['duplicate', 'retry', 'src/service.py']},
    }


class EvidenceContractTests(unittest.TestCase):
    def test_missing_evidence_rejected_instead_of_rated(self):
        data = payload()
        data['response_a'] = {'final_status': 'solves_task', 'tests_passed': True, 'files_changed': ['src/service.py'],
                              'commands': ['python -m unittest'], 'rationale_has_evidence': True}
        with self.assertRaises(ValueError):
            judge_comparison(data)

    def test_missing_requirements_rejected(self):
        data = payload(); del data['requirements']
        with self.assertRaises(ValueError):
            judge_comparison(data)

    def test_failed_implementation_loses_despite_convincing_explanation(self):
        data = payload()
        data['response_a']['explanation']['text'] = 'A polished but unsupported assertion that all edge cases are solved.'
        data['response_a']['commands'][0]['exit_code'] = 1
        data['response_a']['test_results'][0].update(passed=1, failed=1)
        result = judge_comparison(data).to_dict()
        self.assertEqual(result['winner'], 'B')
        self.assertEqual(result['response_a']['assessments']['correctness'], 'failed')
        self.assertEqual(result['response_a']['assessments']['explanation_quality'], 'referenced')

    def test_contradictory_exit_and_pass_counts_rejected(self):
        data = payload(); data['response_a']['commands'][0]['exit_code'] = 1
        with self.assertRaises(ValueError):
            judge_comparison(data)

    def test_skipped_only_requirement_is_missing_evidence(self):
        data = payload(); data['response_a']['test_results'][0].update(passed=0, skipped=2)
        with self.assertRaises(ValueError):
            judge_comparison(data)

    def test_missing_regression_evidence_rejected(self):
        data = payload(); data['response_a']['test_results'][0]['requirement_ids'] = ['duplicate']
        with self.assertRaises(ValueError):
            judge_comparison(data)

    def test_scope_violation_rejected(self):
        for path in ['../secret.py', '/tmp/secret.py', 'evaluator/verifier.py']:
            with self.subTest(path=path):
                data = payload(); data['response_a']['files_changed'] = [path]
                with self.assertRaises(ValueError): judge_comparison(data)

    def test_invalid_or_reversed_timestamps_rejected(self):
        for timestamp in ['not-time', '2026-09-18T11:00:00+00:00', '2026-09-18T12:00:02']:
            with self.subTest(timestamp=timestamp):
                data = payload(); data['response_a']['commands'][0]['finished_at'] = timestamp
                with self.assertRaises(ValueError): judge_comparison(data)

    def test_duplicate_ids_and_unknown_evidence_references_rejected(self):
        for change in ['duplicate', 'unknown']:
            data = payload()
            if change == 'duplicate': data['response_a']['commands'] *= 2
            else: data['response_a']['test_results'][0]['command_id'] = 'unrun'
            with self.assertRaises(ValueError): judge_comparison(data)

    def test_boolean_exit_code_rejected(self):
        data = payload(); data['response_a']['commands'][0]['exit_code'] = False
        with self.assertRaises(ValueError): judge_comparison(data)

    def test_well_formed_tie_has_separate_assessments(self):
        result = judge_comparison(payload()).to_dict()
        self.assertEqual(result['winner'], 'tie')
        self.assertEqual(result['response_a']['assessments']['correctness'], 'passed')
        self.assertEqual(result['response_a']['assessments']['regression_risk'], 'tested')


if __name__ == '__main__': unittest.main()
