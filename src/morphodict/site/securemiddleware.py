"""
Use secure.py to set OWASP approved headers.

Test security on by going to this site: https://securityheaders.com/

See: https://owasp.org/www-project-secure-headers/
Based on: https://github.com/TypeError/secure/blob/main/docs/frameworks.md#django
"""

from secure import Secure, ContentSecurityPolicy

# TODO Improve precision of style_src and remove unsafe-inline CSS

csp = (
    ContentSecurityPolicy()
    .default_src("'self'", "speech-db.altlab.app")
    .script_src("'self'")
    .style_src("'self'", "fonts.googleapis.com", "'unsafe-inline'")
    .img_src("'self'")
    .connect_src("'self'", "speech-db.altlab.app")
    .font_src("'self'", "fonts.gstatic.com", "fonts.googleapis.com")
    .media_src("'self'", "http://speech-db.altlab.app", "https://speech-db.altlab.app")
)

secure_headers = Secure(csp=csp)


def set_secure_headers(get_response):
    def middleware(request):
        response = get_response(request)
        secure_headers.set_headers(response)
        return response

    return middleware
