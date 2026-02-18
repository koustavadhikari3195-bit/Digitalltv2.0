import os
import sys
import traceback

try:
    from config.wsgi import application
    app = application
except Exception:
    # Diagnostic hook: If Django fails to load, create a fake WSGI app that prints the error
    error_trace = traceback.format_exc()
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [f"Django Startup Failed:\n\n{error_trace}".encode('utf-8')]
