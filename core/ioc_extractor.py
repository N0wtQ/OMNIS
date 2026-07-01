import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class IOCBundle:
    ips: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    hashes_md5: List[str] = field(default_factory=list)
    hashes_sha256: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    wallets_btc: List[str] = field(default_factory=list)
    wallets_eth: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    other: List[str] = field(default_factory=list)

    def merge(self, other_bundle: "IOCBundle") -> None:
        for attr in vars(self):
            current = getattr(self, attr)
            incoming = getattr(other_bundle, attr)
            merged = list(dict.fromkeys(current + incoming))
            setattr(self, attr, merged)

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v}


_PATTERNS = {
    "ips": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ),
    "domains": re.compile(
        r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"
    ),
    "emails": re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "hashes_md5": re.compile(r"\b[0-9a-fA-F]{32}\b"),
    "hashes_sha256": re.compile(r"\b[0-9a-fA-F]{64}\b"),
    "urls": re.compile(r"https?://[^\s\"'>]+"),
    "wallets_btc": re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"),
    "wallets_eth": re.compile(r"\b0x[0-9a-fA-F]{40}\b"),
}


def extract_iocs(text: str) -> IOCBundle:
    bundle = IOCBundle()
    for field_name, pattern in _PATTERNS.items():
        matches = list(dict.fromkeys(pattern.findall(text)))
        setattr(bundle, field_name, matches)
    # remove emails from domains list
    bundle.domains = [
        d for d in bundle.domains if d not in bundle.emails and "@" not in d
    ]
    return bundle
