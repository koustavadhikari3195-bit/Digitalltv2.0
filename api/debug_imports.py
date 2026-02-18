from http.server import BaseHTTPRequestHandler
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        out = []
        out.append(f"Python: {sys.version}")
        
        try:
            import sqlite3
            out.append(f"SQLite: OK {sqlite3.sqlite_version}")
        except Exception as e:
            out.append(f"SQLite: FAIL {e}")
            
        try:
            import psycopg2
            out.append(f"psycopg2: OK {psycopg2.__version__}")
        except Exception as e:
            out.append(f"psycopg2: FAIL {e}")

        try:
            import django
            out.append(f"Django: OK {django.get_version()}")
        except Exception as e:
            out.append(f"Django: FAIL {e}")
            
        self.wfile.write("\n".join(out).encode('utf-8'))
