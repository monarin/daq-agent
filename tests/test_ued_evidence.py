"""Synthetic detector signatures; no production logs, hardware or model calls."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from fake_runtime import write_fake_runtime
from daq_agent.collectors.session_logs import COMPILED, collect_logs
from daq_agent.reporting import generate_report, report_settings


class UEDEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.logs = self.root / 'logs'
        self.start = datetime(2026, 9, 1, tzinfo=timezone.utc)
        self.end = self.start + timedelta(days=1)

    def log(self, component, body, *, hour=0, platform=0):
        path = self.logs / '2026/09' / f'01_{hour:02}:00:00_node:{component}.log'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'# ID: {component}\n# PLATFORM: {platform}\n# HOST: node\n'
                        f'# TESTRELDIR: /synthetic/release-{hour}\n# GIT_DESCRIBE: synthetic-{hour}\n'
                        '# SLURM_JOB_ID: 12345\n' + body + '\n')
        os.utime(path, (self.start.timestamp(), self.start.timestamp()))
        return path

    def collect(self, hutch='ued'):
        documents = collect_logs(self.logs, self.root / 'collection', hutch,
                                 self.start, self.end, 'UTC')
        metadata = json.loads((self.root / 'collection/collection.json').read_text())
        return [p.read_text() for p in documents], metadata

    def test_bare_signatures_and_healthy_near_matches(self):
        cases = {
            'detector_subframe': [
                'Missing data: subframe count 3 [expected 4]',
                'Missing data: subframe[0] (timing/meta) has zero size',
                'Missing data: subframe[2] size 0',
                'Missing data: subframe[2] size 1600',
            ],
            'adc_calibration': [
                'AxiVersion.GitHash = abc != Calibration Githash = def',
                'Please re-train the ADC lanes',
            ],
        }
        for category, messages in cases.items():
            for message in messages:
                with self.subTest(message=message):
                    self.assertEqual([key for key, regex in COMPILED.items() if regex.search(message)],
                                     [category])
        healthy = '\n'.join([
            'Setting expert.EpixQuad.AsicMask to 0xffff',
            'AxiVersion.GitHash = abc == Calibration Githash = abc',
            'AxiVersion.GitHash = abc', 'Calibration Githash = abc',
            'ADC lanes trained', 'subframe[2] size 270336',
            'subframe count 4 [expected 4]', 'Missing data counter: 0',
        ])
        self.log('epixquad1kfps_0', healthy)
        _, metadata = self.collect()
        self.assertEqual(metadata['files'][0]['matches'], {})
        self.assertEqual(metadata['analysis_matching_lines'], 0)

    def test_launch_identity_time_buckets_and_configuration_context(self):
        traceback = ('Traceback (most recent call last):\n' +
                     '  File "synthetic.py", line 7, in configure\n' * 12 +
                     'RuntimeError: AsicMask verification failed')
        self.log('control', traceback)
        self.log('teb0', '2026-09-01T01:00:00Z MissingData contributor 2')
        detector = self.log('epixquad1kfps_0', '\n'.join([
            'Setting AsicMask to 0xffff', 'start_ns = 123; frame bytes = 1600',
            '2026-09-01T01:00:00Z Missing data: subframe[2] size 1600',
            'Authorization: Bearer synthetic-sensitive-value',
            '2026-08-31T23:59:59Z Missing data: subframe[0] (timing/meta) has zero size',
            '2026-09-01 01:01:00 AxiVersion.GitHash = abc != Calibration Githash = def',
            'Please re-train the ADC lanes',
        ]), platform=6)
        self.log('control', 'Configure completed', hour=2)
        self.log('teb0', 'Contributor connected', hour=2)
        self.log('epixquad1kfps_0', 'Missing data: subframe count 3 [expected 4]', hour=2)
        docs, metadata = self.collect()
        self.assertEqual(len(docs), 3)
        self.assertEqual(len(metadata['files']), 6)
        record = next(r for r in metadata['files'] if r['path'] == str(detector))
        self.assertEqual(record['partition'], 6)
        self.assertEqual(record['headers']['GIT_DESCRIBE'], 'synthetic-0')
        self.assertEqual(record['sha256'], hashlib.sha256(detector.read_bytes()).hexdigest())
        for category, bucket in [('detector_subframe', 'inside'), ('detector_subframe', 'outside'),
                                 ('adc_calibration', 'inside_if_local'), ('adc_calibration', 'untimed_or_unparsed')]:
            self.assertEqual(record['analysis_matches'][f'{category}|{bucket}'], 1)
        for text in ('start_ns = 123', 'frame bytes = 1600', 'Setting AsicMask',
                     'RuntimeError: AsicMask verification failed', '[REDACTED sensitive field]'):
            self.assertIn(text, docs[1])
        line = next(i for i, value in enumerate(detector.read_text().splitlines(), 1)
                    if 'subframe[2]' in value)
        self.assertIn(f'match original-line={line}', docs[1])
        self.assertNotIn('synthetic-sensitive-value', '\n'.join(docs))
        self.assertNotIn('subframe count 3', docs[1])
        self.assertIn('subframe count 3', docs[2])
        self.assertNotIn('AsicMask verification failed', docs[2])
        self.assertEqual(metadata['known_conditions']['enabled_rules'], [])

    def test_subframe_indices_and_large_sizes_remain_distinct_examples(self):
        messages = [f'Missing data: subframe[{index}] size {size}'
                    for index, size in [(0, 0), (2, 0), (2, 16000), (2, 32000)]]
        self.log('epixquad1kfps_0', ('\n' + 'normal context\n' * 6).join(messages))
        docs, _ = self.collect()
        examples = docs[1].split('REPRESENTATIVE CONTEXT WITH ORIGINAL LINE NUMBERS:')[1]
        self.assertEqual(examples.count('EXAMPLE category=detector_subframe'), 4)
        for message in messages:
            self.assertIn(message, examples)

    def test_detector_examples_survive_generic_noise_with_explicit_budget_omissions(self):
        self.log('control', '\n'.join(f'ERROR generic-{i} ' + 'x' * 180 for i in range(100)))
        self.log('epixquad1kfps_0', '\n'.join([
            'normal context', 'Missing data: subframe[2] size 0', 'normal context',
            'AxiVersion.GitHash = abc != Calibration Githash = def', 'Please re-train the ADC lanes',
        ]))
        with patch('daq_agent.collectors.session_logs.MAX_DOCUMENT', 6500):
            docs, metadata = self.collect()
        examples = docs[1].split('REPRESENTATIVE CONTEXT WITH ORIGINAL LINE NUMBERS:')[1]
        self.assertIn('EXAMPLE category=detector_subframe', examples)
        self.assertIn('EXAMPLE category=adc_calibration', examples)
        self.assertIn('Missing data: subframe[2] size 0', examples)
        self.assertIn('Calibration Githash = def', examples)
        self.assertLessEqual(len(docs[1].encode()), 6500)
        omitted = re.search(r'Stored example blocks omitted for input budget: (\d+)', docs[1])
        self.assertGreater(int(omitted[1]), 0)
        control = next(r for r in metadata['files'] if r['headers']['ID'] == 'control')
        self.assertEqual(control['matches']['error|untimed_or_unparsed'], 100)

    def test_varying_pids_and_counters_do_not_consume_subframe_slots(self):
        repeated = [f'process[{10000+i}] counter={123456+i} Missing data: subframe[2] size 16000'
                    for i in range(5)]
        distinct = ['Missing data: subframe[0] size 0', 'Missing data: subframe[2] size 0',
                    'Missing data: subframe[2] size 32000']
        self.log('epixquad1kfps_0', ('\n' + 'normal context\n' * 6).join(repeated + distinct))
        docs, metadata = self.collect()
        examples = docs[1].split('REPRESENTATIVE CONTEXT WITH ORIGINAL LINE NUMBERS:')[1]
        self.assertEqual(examples.count('EXAMPLE category=detector_subframe'), 4)
        for message in distinct:
            self.assertIn(message, examples)
        self.assertIn('5 | untimed_or_unparsed | process[PID] counter=N Missing data: subframe[2] size 16000', docs[1])
        self.assertEqual(metadata['files'][0]['matches']['detector_subframe|untimed_or_unparsed'], 8)

    def test_numeric_and_hex_hash_pairs_remain_distinct_without_pid_noise(self):
        hashes = [('1234567', '7654321'), ('2345678', '8765432'), ('0xabc', '0xdef'), ('0xaaa', '0xbbb')]
        messages = [f'AxiVersion.GitHash = {a} != Calibration Githash = {b}' for a, b in hashes]
        repeated = [f'process[{10000+i}] counter={123456+i} {messages[0]}' for i in range(5)]
        self.log('epixquad1kfps_0', ('\n' + 'normal context\n' * 6).join(repeated + messages[1:]))
        docs, _ = self.collect()
        examples = docs[1].split('REPRESENTATIVE CONTEXT WITH ORIGINAL LINE NUMBERS:')[1]
        self.assertEqual(examples.count('EXAMPLE category=adc_calibration'), 4)
        for message in messages:
            self.assertIn(message, examples)
        self.assertIn(f'5 | untimed_or_unparsed | process[PID] counter=N {messages[0]}', docs[1])

    def test_generic_signatures_also_work_for_tmo(self):
        self.log('epixquad', 'Missing data: subframe[2] size 1600')
        docs, metadata = self.collect('tmo')
        self.assertIn('EXAMPLE category=detector_subframe', docs[1])
        self.assertEqual(metadata['hutch'], 'tmo')

    def test_completed_report_resource_retains_detector_evidence(self):
        self.log('epixquad1kfps_0', 'Missing data: subframe[2] size 0\nPlease re-train the ADC lanes')
        provider = self.root / 'provider.json'
        provider.write_text(json.dumps({'provider': {'example': {'npm': '@ai-sdk/anthropic',
            'models': {'test': {}}, 'options': {'apiKey': '{env:SYNTHETIC_KEY}', 'baseURL': 'https://example.invalid'}}}}))
        runtime = write_fake_runtime(self.root, {'summary': 'Synthetic detector evidence.',
                                                'findings': [], 'limitations': ['No diagnosis evaluated.']})
        settings = replace(report_settings('ued'), timezone='UTC', log_root=str(self.logs),
                           runtime='opencode', model='example/test', opencode=str(runtime),
                           provider_config=str(provider), daq_skills=None)
        output = self.root / 'report'
        generate_report(settings, self.start, self.end, output)
        resource = json.loads((output / 'agent-resource/report.json').read_text())
        self.assertEqual(resource['hutch'], 'ued')
        texts = []
        for source in resource['sources']:
            path = output / 'agent-resource' / source['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['sha256'])
            texts.append(path.read_text())
        for message in ('Missing data: subframe[2] size 0', 'Please re-train the ADC lanes'):
            self.assertIn(message, '\n'.join(texts))
        for name in ('report.md', 'report.html'):
            self.assertIn('Synthetic detector evidence.', (output / name).read_text())
