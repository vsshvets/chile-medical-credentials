"""Shared HTTP fetch. This Python has no usable system trust store, so SSL verification fails on
every https URL until certifi is wired in explicitly. Every fetcher in this repo uses this."""
import ssl, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def ctx():
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        pass
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_CTX = ctx()


def opener():
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=_CTX))


def get(url, timeout=45, extra_headers=None):
    """-> (status, bytes, final_url, content_type). Raises only on transport failure."""
    h = {"User-Agent": UA,
         "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
         "Accept-Language": "es-CL,es;q=0.9,en;q=0.8,uk;q=0.7"}
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, headers=h)
    with opener().open(req, timeout=timeout) as r:
        return r.status, r.read(), r.geturl(), (r.headers.get_content_type() or "").lower()
