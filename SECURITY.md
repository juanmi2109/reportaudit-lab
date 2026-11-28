# Security Policy

## Supported versions

| Version | Supported | End of security support |
|---|---|---|
| 1.x | Yes | 2031-11-30 |
| < 1.0 | No | N/A |

## Reporting a vulnerability

Please report security vulnerabilities privately through GitHub:

https://github.com/juanmi2109/reportaudit-lab/security/advisories/new

Do not disclose vulnerabilities in public issues.
Include the affected version, reproduction details, impact
and a proposed fix if available.

## What to expect

- Acknowledgement within 3 business days.
- Initial assessment within 10 business days.
- Target for coordinated disclosure and remediation: 90 days.
- Researchers will receive credit unless they decline it.

## Safe harbour

Good-faith security research is welcome, provided researchers
respect privacy, avoid disruption and allow reasonable time
for remediation.

## Verifying our releases

Starting with version 1.0.0, releases will include a CycloneDX
SBOM, SHA-256 checksums and signed provenance attestations.

    sha256sum -c SHA256SUMS

    gh attestation verify reportaudit-1.0.0.tar.gz --repo juanmi2109/reportaudit-lab
