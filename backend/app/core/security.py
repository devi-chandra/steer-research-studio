import ipaddress
import re
import socket
from pathlib import Path
from urllib.parse import urlparse
from fastapi import HTTPException
from app.core.config import settings

def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validates a URL against SSRF attacks.
    Ensures scheme is http or https and does not resolve to private/loopback/cloud metadata IP ranges.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, "Only HTTP and HTTPS URLs are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: hostname missing."

        # Block localhost and common local domain names
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"):
            return False, "Access to localhost or private metadata services is blocked."

        # Resolve hostname to IP to protect against DNS rebinding
        try:
            ip_str = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
                return False, f"URL resolves to restricted IP range ({ip_str})."
        except socket.gaierror:
            return False, "Could not resolve hostname."

        return True, ""
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent path traversal and shell injection.
    """
    # Remove directory separators
    clean = Path(filename).name
    # Keep only alphanumeric, hyphens, underscores, and dots
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean)
    # Avoid hidden files or leading dots
    clean = clean.lstrip('.')
    if not clean:
        clean = "document.pdf"
    return clean

def validate_path_containment(file_path: Path, allowed_root: Path = settings.STORAGE_DIR) -> bool:
    """
    Ensures that file_path resides strictly within the allowed_root directory.
    """
    try:
        resolved_file = file_path.resolve()
        resolved_root = allowed_root.resolve()
        return resolved_root in resolved_file.parents or resolved_file == resolved_root
    except Exception:
        return False
