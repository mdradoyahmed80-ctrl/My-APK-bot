import hmac
from urllib.parse import urlparse
import ipaddress, socket
from backend.config import settings

def owner_allowed(owner_id: str) -> bool:
    return bool(settings.owner_telegram_id) and hmac.compare_digest(str(owner_id), str(settings.owner_telegram_id))

def is_public_url(url: str) -> bool:
    """Conservative URL gate: only public http(s) hosts; DNS checks reduce SSRF risk.
    For production, also enforce egress firewall and re-check every redirect/IP at fetch time.
    """
    try:
        p=urlparse(url)
        if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password: return False
        host=p.hostname.lower()
        if host in ("localhost", "localhost.localdomain") or host.endswith(".local"): return False
        try: ips=[ipaddress.ip_address(host)]
        except ValueError: ips=[ipaddress.ip_address(x[4][0]) for x in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)]
        return bool(ips) and all(ip.is_global for ip in ips)
    except Exception: return False
