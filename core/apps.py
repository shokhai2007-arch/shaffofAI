import threading
import os
from django.apps import AppConfig
from django.core.management import call_command


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Only run if not in the reloader main process to avoid double execution in development
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE'):
            return

        def run_fetch():
            try:
                # We add a small delay to ensure the database and other apps are fully ready
                import time
                time.sleep(2)
                print("Starting background UZEX data fetch...")
                call_command('fetch_uzex', limit=80)
                print("Background UZEX data fetch completed.")
            except Exception as e:
                print(f"Error in background fetch: {e}")

        # In production (Gunicorn/Railway), it's best to run this in a background thread
        thread = threading.Thread(target=run_fetch, daemon=True)
        thread.start()
