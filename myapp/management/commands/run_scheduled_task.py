# myapp/management/commands/run_scheduled_task.py

from django.core.management.base import BaseCommand
import schedule
import time

def my_scheduled_task():
    # Define your scheduled task logic here
    print("My scheduled task is running...")

class Command(BaseCommand):
    help = 'Runs a scheduled task'

    def handle(self, *args, **options):
        # Schedule the task to run every day at 8:00 AM
        schedule.every().day.at("08:00").do(my_scheduled_task)

        # Run the scheduler continuously
        while True:
            schedule.run_pending()
            time.sleep(1)
