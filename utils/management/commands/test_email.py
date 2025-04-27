from django.core.management.base import BaseCommand
from utils.email_utils import test_email_configuration

class Command(BaseCommand):
    help = 'Test the email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send the test email to')

    def handle(self, *args, **options):
        email = options.get('email')
        
        self.stdout.write(self.style.WARNING('Testing email configuration...'))
        
        result = test_email_configuration(email)
        
        if result:
            self.stdout.write(self.style.SUCCESS('Email sent successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Failed to send email. Check the logs for details.'))
