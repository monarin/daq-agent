"""Offline portability and provenance checks for independent report consumers."""

from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from chat_fixtures import write_report
from daq_agent.cli import main
from daq_agent.report_resource import export_report_resource


class ReportResourceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_export_is_portable_and_excludes_runtime_and_provider_files(self):
        report = write_report(self.root, upstream=True)
        (report / 'events.jsonl').write_text('PRIVATE TRANSCRIPT')
        (report / 'provider.json').write_text('PRIVATE CONFIG')
        manifest_path = report / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['settings']['provider_config'] = '/private/provider.json'
        manifest_path.write_text(json.dumps(manifest))
        before = {str(p.relative_to(report)): p.read_bytes() for p in report.rglob('*') if p.is_file()}
        export = self.root / 'export'
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['export-resource', str(report), '--output', str(export)]), 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'exported')
        self.assertEqual(before, {str(p.relative_to(report)): p.read_bytes()
                                  for p in report.rglob('*') if p.is_file()})
        relocated = self.root / 'relocated'
        shutil.copytree(export, relocated)
        shutil.rmtree(report)
        resource = json.loads((relocated / 'report.json').read_text())
        self.assertEqual(resource['schema_version'], 1)
        self.assertEqual(resource['hutch'], 'tmo')
        self.assertEqual(resource['findings'][0]['id'], 'F001')
        sources = {s['id']: s for s in resource['sources']}
        for finding in resource['findings']:
            for citation in finding['evidence']:
                text = (relocated / sources[citation['source']]['path']).read_text().splitlines()
                self.assertIn('ERROR', text[citation['line_start'] - 1])
        for record in resource['artifacts']:
            path = relocated / record['path']
            self.assertTrue(path.resolve().is_relative_to(relocated))
            self.assertEqual(len(path.read_bytes()), record['bytes'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(resource['diagnostic_skills']['provenance']['source']['revision'], 'a' * 40)
        serialized = (relocated / 'report.json').read_text()
        self.assertNotIn('/private/provider.json', serialized)
        self.assertFalse((relocated / 'events.jsonl').exists())
        self.assertFalse((relocated / 'provider.json').exists())

    def test_combined_report_has_global_citations_and_one_skill_inventory(self):
        report = write_report(self.root, count=9, upstream=True)
        resource = json.loads(export_report_resource(report, self.root / 'export').read_text())
        self.assertEqual(len(resource['sources']), 9)
        self.assertEqual(resource['findings'][-1]['evidence'][0]['source'], 'log-9')
        self.assertEqual(len(resource['diagnostic_skills']['files']), 2)
        self.assertEqual(len(resource['model_sessions']), 2)

    def test_tampered_evidence_or_skills_fail_without_publishing(self):
        for name in ('evidence/log-1.txt', 'upstream-skills/psana-daq/SKILL.md'):
            with self.subTest(name=name):
                report = write_report(self.root, name=name.replace('/', '-'), upstream=True)
                (report / name).write_text('tampered')
                with self.assertRaisesRegex(ValueError, 'integrity'):
                    export_report_resource(report, self.root / 'export')
                self.assertFalse((self.root / 'export').exists())

    def test_skill_inventory_is_not_limited_by_retired_chat_budget(self):
        report = write_report(self.root, upstream=True)
        relative = 'psana-daq/reference.md'
        raw = ('Synthetic reference.\n' * 11000).encode()
        self.assertGreater(len(raw), 192 * 1024)
        (report / 'upstream-skills' / relative).write_bytes(raw)
        path = report / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['upstream_skills']['files'][relative] = {
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        path.write_text(json.dumps(manifest))
        resource = json.loads(export_report_resource(report, self.root / 'export').read_text())
        self.assertEqual((self.root / 'export/skills' / relative).read_bytes(), raw)
        self.assertEqual(len(resource['diagnostic_skills']['files']), 3)

    def test_incomplete_reports_and_existing_destinations_are_rejected(self):
        report = write_report(self.root)
        target = self.root / 'export'
        export_report_resource(report, target)
        before = (target / 'report.json').read_bytes()
        with self.assertRaises(FileExistsError):
            export_report_resource(report, target)
        self.assertEqual((target / 'report.json').read_bytes(), before)
        path = report / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['status'] = 'prepared_only'
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'not a completed report'):
            export_report_resource(report, self.root / 'another-export')


if __name__ == '__main__':
    unittest.main()
