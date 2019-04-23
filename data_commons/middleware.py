from django.conf import settings
from django.utils.cache import patch_vary_headers, add_never_cache_headers


def CacheVaryByProtocol(get_response):
    def middleware(request):
        response = get_response(request)

        #header = settings.SECURE_PROXY_SSL_HEADER[0]
        #patch_vary_headers(response, ['X-Forwarded-Proto'])
        if response.status_code == 301:
            add_never_cache_headers(response)
        return response

    return middleware
