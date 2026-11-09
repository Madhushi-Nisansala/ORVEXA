# Security

Security is a design constraint and this document is an operational baseline, not a penetration-test certificate.

## Foundation controls

- Configuration is environment-driven; secrets are excluded from source control.
- CORS origins are configurable and production rejects wildcard origins.
- Production disables public API documentation and adds security headers.
- Argon2 password hashing, short-lived access tokens, rotating refresh tokens, and authentication rate limiting are enabled.
- Uploads have size, extension, MIME, signature, filename, and private-path controls.
- Resource queries enforce user ownership and errors avoid internal details.
- Mobile tokens use `flutter_secure_storage`; provider credentials remain backend-only.

## Required operational controls

Use HTTPS, managed secrets, least-privilege database roles, dependency scanning, malware scanning appropriate to the file types, backup encryption, retention/deletion policy, audit logs, prompt-injection defenses for AI inputs, and independent security testing. Review JWT issuer/audience requirements if tokens are shared across services.
