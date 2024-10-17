"""
Use secure.py to set OWASP approved headers.

Test security on by going to this site: https://securityheaders.com/

See: https://owasp.org/www-project-secure-headers/
Based on: https://github.com/TypeError/secure/blob/main/docs/frameworks.md#django
"""

from secure import Secure

secure_headers = Secure.with_default_headers()


def set_secure_headers(get_response):
    def middleware(request):
        response = get_response(request)
        secure_headers.set_headers(response)
        return response

    return middleware
