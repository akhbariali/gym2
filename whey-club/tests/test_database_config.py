import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
SETTINGS=Path(__file__).resolve().parents[1]/'backend/config/settings.py'
class DatabaseConfigurationTests(unittest.TestCase):
    def test_postgres_is_default_and_reads_connection_environment(self):
        with patch.dict(os.environ,{'DJANGO_DEBUG':'1','PGDATABASE':'example','PGUSER':'shop','PGPASSWORD':'test-only','PGHOST':'db.internal','PGPORT':'5433','PGSSLMODE':'require'},clear=True):
            db=runpy.run_path(str(SETTINGS))['DATABASES']['default']
        self.assertEqual(db['ENGINE'],'django.db.backends.postgresql')
        self.assertEqual((db['NAME'],db['USER'],db['PASSWORD'],db['HOST'],db['PORT']),('example','shop','test-only','db.internal','5433'))
        self.assertEqual(db['OPTIONS']['sslmode'],'require')
        self.assertTrue(db['CONN_HEALTH_CHECKS'])
    def test_sqlite_requires_explicit_opt_in_and_preserves_rollback_path(self):
        with patch.dict(os.environ,{'DJANGO_DEBUG':'1','WHEY_DB_ENGINE':'sqlite','WHEY_DATABASE':'/tmp/test.sqlite3'},clear=True):
            db=runpy.run_path(str(SETTINGS))['DATABASES']['default']
        self.assertEqual(db['ENGINE'],'django.db.backends.sqlite3')
        self.assertEqual(db['NAME'],'/tmp/test.sqlite3')
