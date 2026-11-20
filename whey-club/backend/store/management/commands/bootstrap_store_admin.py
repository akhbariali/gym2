"""Create a separate store owner; deliver credentials only through a private file."""
import os,secrets
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand,CommandError
from django.db import transaction

class Command(BaseCommand):
    help='Create a new owner account and write one-time credentials into a private file.'
    def add_arguments(self,parser):parser.add_argument('--output',type=Path,required=True)
    def handle(self,*args,**options):
        path=options['output']
        if path.exists():raise CommandError('Credential file already exists. No account or password was changed.')
        username='wc-owner-'+secrets.token_hex(5);password=secrets.token_urlsafe(32)
        try:
            with transaction.atomic():
                get_user_model().objects.create_superuser(username=username,email='',password=password)
                fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                with os.fdopen(fd,'w') as out:
                    out.write('WHEY CLUB ADMIN\nURL: https://wheyclub.ir/admin/\nUsername: '+username+'\nPassword: '+password+'\n\nKeep this file private. You can change the password using the admin password-change page.\n')
        except OSError as exc:raise CommandError('Cannot write the private credential file; account creation rolled back.') from exc
        self.stdout.write('Created separate owner account: '+username)
        self.stdout.write('Credentials written privately to '+str(path))
