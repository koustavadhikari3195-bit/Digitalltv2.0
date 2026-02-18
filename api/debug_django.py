from http.server import BaseHTTPRequestHandler
import os
import sys
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        output = []
        output.append("--- DIAGNOSTIC RESULT ---")
        
        # 1. Test Environment
        try:
            output.append("1. Environment: OK")
            output.append(f"   Python: {sys.version}")
        except Exception:
            output.append("1. Environment: FAIL")
            
        # 2. Test Django Import
        try:
            # Force production settings for this test
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
            import django
            output.append(f"2. Django Import: OK (Version {django.get_version()})")
        except Exception:
            output.append(f"2. Django Import: FAIL\n{traceback.format_exc()}")
            self.wfile.write("\n".join(output).encode('utf-8'))
            return

        # 3. Test Django Setup (Loading Settings)
        try:
            django.setup()
            output.append("3. Django Setup: OK")
            from django.conf import settings
            output.append(f"   DATABASES Configured: {list(settings.DATABASES.keys())}")
            output.append(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
            output.append(f"   DEBUG: {settings.DEBUG}")
        except Exception:
            output.append(f"3. Django Setup: FAIL\n{traceback.format_exc()}")
            self.wfile.write("\n".join(output).encode('utf-8'))
            return

        # 4. Test Database Connection
        try:
            from django.db import connections
            conn = connections['default']
            conn.ensure_connection()
            output.append("4. Database Connection: OK")
        except Exception:
            output.append(f"4. Database Connection: FAIL\n{traceback.format_exc()}")
            
        self.wfile.write("\n".join(output).encode('utf-8'))
        return
