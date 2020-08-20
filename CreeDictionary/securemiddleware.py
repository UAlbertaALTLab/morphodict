#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Use secure.py to set OWASP approved headers.

Test security on by going to this site: https://securityheaders.com/

See: https://owasp.org/www-project-secure-headers/
Based on: https://secure.readthedocs.io/en/latest/frameworks.html#django
"""

from secure import SecureHeaders

secure_headers = SecureHeaders()


def set_secure_headers(get_response):
    def middleware(request):
        response = get_response(request)
        secure_headers.django(response)
        return response

    return middleware
