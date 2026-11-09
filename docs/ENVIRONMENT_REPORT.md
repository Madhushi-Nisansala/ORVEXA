# ORVEXA Environment Report

Inspection date: 2026-09-10

## Detected tools

| Tool | Result |
|---|---|
| OS | Windows 11 or higher, build 26200.9711 (25H2, 2009), x64 |
| CPU architecture | x64 |
| Disk | C: approximately 248.44 GB free, 226.71 GB used at inspection time |
| Git | 2.55.0.windows.2 |
| .NET SDK | 10.0.302 |
| Flutter | 3.47.1 stable |
| Dart | 3.13.1 |
| Flutter doctor | One issue: Android licenses are not accepted/unknown; web and Windows tooling are available |
| Python | 3.13.14 |
| pip | 26.1.2 |
| PostgreSQL service | PostgreSQL 17 Windows service is running |
| `psql` CLI | Not available on PATH |
| Docker | Not available on PATH |
| Docker Compose | Not available on PATH |
| Java on PATH | OpenJDK/Java 24.0.1 |
| Flutter Android JDK | Android Studio bundled OpenJDK 25.0.2 |
| Android SDK | SDK 36.0.0 at the detected Android Studio SDK location; `ANDROID_HOME` and `ANDROID_SDK_ROOT` are unset |
| Android emulator | Pixel 7 - API 36.0 is configured |
| ADB | Not available on PATH |
| Chrome | Available; Google Chrome 156.0.8078.80 |
| Visual Studio | Community 2026 18.8.12009.203; Windows 10 SDK 10.0.26100.0 detected by Flutter |
| Node.js | 24.18.0 |
| npm | Not available on PATH |

## Repository baseline

- The repository is a new Git repository with no commits.
- An existing .NET 10 console project is present at `ORVEXA/` and was inspected but not modified.
- Partial Phase 1 files already existed under `frontend/`, `backend/`, `docs/`, and root configuration files. They are being completed in place rather than blindly overwritten.

## Missing dependencies and configuration issues

- Docker and Docker Compose are unavailable, so Compose validation and container execution are blocked until Docker Desktop is installed/running.
- PostgreSQL is running as a Windows service, but the `psql` client is unavailable on PATH; database credentials/database existence cannot be verified from the CLI in this environment.
- Flutter doctor reports Android license status as unknown. Android builds may require running `flutter doctor --android-licenses` manually.
- `adb`, `ANDROID_HOME`, and `ANDROID_SDK_ROOT` are not available/configured in the current shell.
- iOS builds are not supported on Windows; Flutter iOS project scaffolding can be present but cannot be built here.
- Visual Studio workload details were not available because `vswhere.exe` was not found at the expected path. Flutter confirms Windows desktop tooling and the Windows SDK.

## Recommended actions

1. Install/start Docker Desktop and rerun `docker compose config` and the Compose smoke test.
2. Add PostgreSQL client tools to PATH, or use the installed PostgreSQL service's tools, and verify a local development database with developer-provided credentials.
3. Accept Android SDK licenses with `flutter doctor --android-licenses`.
4. Configure `ANDROID_HOME`/`ANDROID_SDK_ROOT` and add `platform-tools` to PATH if Android CLI work is required.
5. Use macOS/Xcode or CI for iOS builds.

No software was installed and no system-level configuration was changed by this implementation.

## Compatibility assessment

- Flutter 3.47.1/Dart 3.13.1 is suitable for the Phase 1 Material 3 client and current package constraints.
- Python 3.13.14 is suitable for the selected FastAPI, Pydantic Settings, SQLAlchemy 2, asyncpg, Alembic, HTTPX, and pytest versions.
- PostgreSQL 17 is supported by the development configuration and SQLAlchemy/asyncpg foundation.
- Docker configuration is prepared but not runtime-verified because Docker is unavailable.
- The existing .NET 10 project remains compatible and unchanged.
