"""Compare logical data before/after switching database engines without exposing PII."""
import hashlib
import json
from io import StringIO
from pathlib import Path
from django.apps import apps
from django.core.management import BaseCommand, call_command, CommandError

class Command(BaseCommand):
    help = 'Print model counts and a canonical data digest; optionally compare to a previous snapshot.'
    def add_arguments(self, parser):
        parser.add_argument('--database', default='default')
        parser.add_argument('--compare', type=Path)
    def handle(self, *args, **options):
        stream=StringIO()
        call_command('dumpdata', database=options['database'], natural_foreign=True,
                     exclude=['contenttypes','auth.permission'], stdout=stream)
        objects=json.loads(stream.getvalue())
        for obj in objects:
            model=apps.get_model(obj['model'])
            for field in model._meta.many_to_many:
                if field.name in obj['fields']:
                    obj['fields'][field.name]=sorted(obj['fields'][field.name],key=lambda x:json.dumps(x,sort_keys=True))
        objects.sort(key=lambda o:(o['model'],str(o['pk'])))
        counts={}
        for obj in objects:counts[obj['model']]=counts.get(obj['model'],0)+1
        payload=json.dumps(objects,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        result={'counts':counts,'sha256':hashlib.sha256(payload).hexdigest()}
        if options['compare']:
            try:expected=json.loads(options['compare'].read_text())
            except (OSError,ValueError) as exc:raise CommandError('Cannot read the reference database snapshot.') from exc
            if result!=expected:raise CommandError('Database snapshot mismatch: counts or canonical data differ. Do not cut over.')
        self.stdout.write(json.dumps(result,sort_keys=True))
