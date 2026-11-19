import json
from io import StringIO
from pathlib import Path
import tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command,CommandError
from django.test import TestCase

class SnapshotTests(TestCase):
    def test_snapshot_is_private_stable_and_detects_changed_records(self):
        user=get_user_model().objects.create(username='private-test-customer',email='private@example.test',password='!')
        stream=StringIO();call_command('database_snapshot',stdout=stream)
        result=json.loads(stream.getvalue())
        self.assertEqual(result['counts']['auth.user'],1)
        self.assertNotIn('private@example.test',stream.getvalue())
        self.assertNotIn('private-test-customer',stream.getvalue())
        self.assertEqual(len(result['sha256']),64)
        with tempfile.TemporaryDirectory() as folder:
            snapshot=Path(folder)/'snapshot.json';snapshot.write_text(stream.getvalue())
            call_command('database_snapshot',compare=snapshot,stdout=StringIO())
            user.first_name='changed';user.save()
            with self.assertRaises(CommandError):call_command('database_snapshot',compare=snapshot,stdout=StringIO())
