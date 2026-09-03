from __future__ import annotations
import ipaddress
import socket
from urllib.parse import urlparse
from packages.collectors.base.errors import CollectorPolicyError

ALLOWED_SCHEMES = {"http", "https"}

def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise CollectorPolicyError(f"Unsupported URL scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise CollectorPolicyError("URL must contain a hostname.")
    hostname = parsed.hostname.lower()
    if hostname == "localhost":
        raise CollectorPolicyError("Localhost targets are prohibited.")

async def resolve_and_validate_host(hostname: str) -> list[str]:
    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise CollectorPolicyError(f"Unable to resolve hostname: {hostname}") from exc

    validated: list[str] = []
    for address in addresses:
        ip_text = address[4][0]
        ip = ipaddress.ip_address(ip_text)
        if (ip.is_private or ip.is_loopback or ip.is_link_local or 
            ip.is_multicast or ip.is_reserved or ip.is_unspecified):
            raise CollectorPolicyError(f"Blocked non-public address: {ip}")
        validated.append(str(ip))
    return sorted(set(validated))
