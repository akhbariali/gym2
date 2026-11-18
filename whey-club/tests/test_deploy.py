import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DeployTests(unittest.TestCase):
    def run_deploy(self, fail='', **overrides):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            (root / 'frontend').mkdir()
            (root / 'bin').mkdir()
            shutil.copy(ROOT / 'scripts/deploy.sh', root / 'scripts/deploy.sh')
            stub = '''#!/bin/bash
set -eu
tool=${0##*/}
echo "$tool $*" >> "$DEPLOY_TEST_LOG"
if [[ $tool == ssh ]]; then cat >> "$DEPLOY_TEST_LOG"; fi
if [[ ${DEPLOY_TEST_FAIL:-} == "$tool $*" || ${DEPLOY_TEST_FAIL:-} == "$tool" ]]; then exit 9; fi
if [[ "$tool $*" == 'npm run build' ]]; then
    mkdir -p build
    echo html > build/index.html
    echo '{}' > build/react-entry.json
fi
'''
            for name in ('python3', 'node', 'npm', 'ssh', 'rsync'):
                command = root / 'bin' / name
                command.write_text(stub)
                command.chmod(0o755)
            log = root / 'commands.log'
            env = dict(os.environ, PATH=f'{root}/bin:/usr/bin:/bin',
                       DEPLOY_TEST_LOG=str(log), DEPLOY_TEST_FAIL=fail,
                       DEPLOY_HOST='root@example.test', DEPLOY_PORT='2222')
            env.update(overrides)
            result = subprocess.run(['bash', str(root / 'scripts/deploy.sh')],
                                    env=env, capture_output=True, text=True)
            return result, log.read_text() if log.exists() else ''

    def test_build_backup_and_non_destructive_upload(self):
        result, log = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(log.index('npm run build'), log.index('ssh '))
        self.assertLess(log.index('tar -czf'), log.index('rsync -'))
        self.assertIn('--delay-updates', log)
        for path in ('/blog/', '/sitemap.xml', '/robots.txt'):
            self.assertIn('--exclude=' + path, log)
        self.assertIn('root@example.test:/opt/whey-club/site/', log)
        self.assertIn('-p 2222', log)
        self.assertNotIn('--delete', log)
        self.assertLess(log.index('rsync -'), log.index('nginx -t'))
        self.assertLess(log.index('nginx -t'), log.index('systemctl restart whey-club.service'))
        self.assertLess(log.index('systemctl restart whey-club.service'), log.index('systemctl is-active --quiet whey-club.service'))
        self.assertIn('-p /opt/whey-club/ -c /opt/whey-club/nginx.conf', log)

    def test_build_failure_prevents_remote_changes(self):
        result, log = self.run_deploy(fail='npm run build')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('ssh ', log)
        self.assertNotIn('rsync -', log)

    def test_failed_backup_prevents_upload(self):
        result, log = self.run_deploy(fail='ssh')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('rsync -', log)

    def test_failed_upload_prevents_restart(self):
        result, log = self.run_deploy(fail='rsync')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('systemctl restart', log)

    def test_invalid_connection_settings_stop_before_commands(self):
        for settings in ({'DEPLOY_PORT': '0'}, {'DEPLOY_PORT': '65536'},
                         {'DEPLOY_PORT': '22;bad'}, {'DEPLOY_HOST': '-bad'}):
            with self.subTest(settings=settings):
                result, log = self.run_deploy(**settings)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(log, '')
