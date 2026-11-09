# ORVEXA Stage 9.1 — Post-Login Navigation Diagnostic

## Scope

This diagnostic traces the Flutter authentication and GoRouter flow. No source files were modified, and no PostgreSQL database, migrations, document worker, `.env` files, credentials, tokens, or external providers were accessed.

## Root cause

**Confirmed root cause:** successful Login explicitly navigates to `/`, and the `/` route explicitly renders `HomeScreen`. `HomeScreen` is currently the Backend Status screen.

This is not caused by an authentication-state race, an unexpected redirect, or duplicate route definitions. The current implementation defines the Backend Status screen as the authenticated home screen.

Evidence:

- `frontend/lib/features/auth/presentation/login_screen.dart:32-43` awaits the authentication call, checks for an error, and then calls `context.go('/')`.
- `frontend/lib/app/router/app_router.dart:42-45` defines `/` with the route name `home` and builds `HomeScreen`.
- `frontend/lib/features/home/presentation/home_screen.dart:71-96` renders the backend status card, database status, last-checked time, and retry action.

## Actual route flow

### Before Login

1. `frontend/lib/main.dart:6-8` starts the app inside Riverpod's `ProviderScope`.
2. `frontend/lib/app/app.dart:15-22` creates `MaterialApp.router` using `appRouterProvider`.
3. `frontend/lib/app/router/app_router.dart:12-16` creates the router with `initialLocation: '/login'`.
4. `frontend/lib/app/router/app_router.dart:32-35` maps `/login` to `LoginScreen`.
5. The Login screen is therefore the initial screen unless an existing session causes the redirect logic to select another route.

### During Login

1. `frontend/lib/features/auth/presentation/login_screen.dart:32-35` calls `authProvider.notifier.login(...)` and awaits it.
2. `frontend/lib/features/auth/application/auth_provider.dart:21-33` sets the provider to loading, calls the repository, and assigns the resulting `AsyncValue<AuthUser?>` to the provider state.
3. `frontend/lib/features/auth/data/auth_repository.dart:53-81` posts to `/api/v1/auth/login`, saves the returned access and refresh tokens, and calls `/api/v1/auth/me` to obtain the authenticated user.
4. After the awaited call completes, `login_screen.dart:39-41` reads the provider and stops if it contains an error.

### After successful Login

1. `frontend/lib/features/auth/presentation/login_screen.dart:43` calls `context.go('/')`.
2. GoRouter matches `/` to the route declared in `frontend/lib/app/router/app_router.dart:42-46`.
3. That route builds `HomeScreen`.
4. `frontend/lib/features/home/presentation/home_screen.dart:14-21` watches the health provider and formats the backend status result.
5. `frontend/lib/features/home/presentation/home_screen.dart:71-96` displays the Backend Status card and retry action.

The observed result—Backend Status after Login—is therefore the direct result of the explicit `/` navigation and current `/` route definition.

## Redirect and authentication-state analysis

### Redirect rules

`frontend/lib/app/router/app_router.dart:17-30` contains the only router redirect callback found:

- `/login` and `/register` are treated as authentication routes (`:18-19`).
- While authentication state is loading, non-authentication routes redirect to `/login` (`:20-22`).
- An unauthenticated user on a non-authentication route redirects to `/login` (`:23-25`).
- An authenticated user on `/login` or `/register` redirects to `/` (`:26-28`).

The authenticated-user redirect is also intentionally `/`, not a Dashboard route.

### Does the provider update before GoRouter evaluates redirects?

Yes, based on the inspected code:

- `AuthNotifier.login` awaits the repository operation and assigns the completed result to `state` at `frontend/lib/features/auth/application/auth_provider.dart:27-33`.
- The Login screen awaits that method at `frontend/lib/features/auth/presentation/login_screen.dart:32-35` before reading the provider and navigating at line 43.
- The router captures the current auth state at `frontend/lib/app/router/app_router.dart:13`, listens for later provider changes at `:64-67`, updates its local `authState`, and calls `router.refresh()`.

Thus, authenticated state is established before the explicit post-login navigation. The redirect machinery may also refresh in response to the provider update, but it does not change the destination to a separate Dashboard; its authenticated destination is also `/`.

## Is Backend Status currently the home screen?

**Yes.** `/` is named `home` and builds `HomeScreen` (`frontend/lib/app/router/app_router.dart:42-46`). The `HomeScreen` implementation is the Backend Status screen: it displays connection status, last checked time, database status, and a retry button (`frontend/lib/features/home/presentation/home_screen.dart:17-21` and `:71-96`).

The screen also provides navigation to Settings and Documents (`frontend/lib/features/home/presentation/home_screen.dart:28-45`), but those are secondary routes and do not represent a separate authenticated Dashboard.

## Does a separate authenticated Dashboard exist?

**No separate Dashboard was found.** A repository-wide search of `frontend/lib/**/*.dart` found:

- No `DashboardScreen` or equivalent Dashboard widget.
- No `/dashboard` route.
- No `dashboard` route name.
- No post-login navigation target other than `/`.

The existing authenticated feature routes are:

- `/` → `HomeScreen` (`app_router.dart:42-46`)
- `/documents` → `DocumentsScreen` (`app_router.dart:52-55`)
- `/documents/:id` → `DocumentDetailScreen` (`app_router.dart:47-50`)
- `/settings` → `SettingsScreen` (`app_router.dart:57-60`)

## Registration flow

Registration does not authenticate the user in the inspected code:

- `frontend/lib/features/auth/presentation/register_screen.dart:44-50` calls the repository registration operation.
- On success, `:54-57` displays a confirmation and calls `context.go('/login')`.
- `frontend/lib/features/auth/application/auth_provider.dart:36-47` returns the repository registration result but does not assign it to the authentication provider state.

This behavior is consistent with the UI message, `Account created. Please sign in.` It is not the cause of the post-login Backend Status result.

## Duplicate or conflicting routes

No duplicate or conflicting route definitions were found in `frontend/lib/app/router/app_router.dart`. Each declared path is unique:

- `/login`
- `/register`
- `/`
- `/documents/:id`
- `/documents`
- `/settings`

The issue is a destination/ screen-definition mismatch, not a duplicate route conflict.

## Recommended minimal fix

If the intended authenticated landing page is a Dashboard, introduce or designate an actual Dashboard screen and route, then update both authenticated landing targets consistently:

1. Add a Dashboard widget/screen representing the intended authenticated landing experience.
2. Add a uniquely named route such as `/dashboard` in `frontend/lib/app/router/app_router.dart`.
3. Change the successful Login navigation at `frontend/lib/features/auth/presentation/login_screen.dart:43` from `/` to `/dashboard`.
4. Change the authenticated auth-route redirect at `frontend/lib/app/router/app_router.dart:26-28` from `/` to `/dashboard`.
5. Decide whether `/` should remain an alias/redirect to `/dashboard` or continue to be the Backend Status screen.

The smallest behavioral correction, once a Dashboard screen exists, is to use the same Dashboard path in both the Login `context.go(...)` call and the authenticated redirect. No authentication-provider timing change is indicated by this investigation.

## Tests needed to verify the fix

Do not treat these as run during this read-only diagnostic; they are the tests needed after human approval and implementation:

1. **Successful Login navigation test**
   - Stub a successful login and `/api/v1/auth/me` response.
   - Verify the authenticated provider contains a user.
   - Verify the router lands on `/dashboard` (or the approved Dashboard path), not `/`.
   - Verify the Dashboard widget is rendered.

2. **Authenticated redirect test**
   - Start with authenticated provider state.
   - Navigate to `/login` and `/register`.
   - Verify both routes redirect to the Dashboard path.

3. **Unauthenticated guard test**
   - Start with a null authentication state.
   - Navigate to the Dashboard path and other protected routes.
   - Verify unauthenticated users are redirected to `/login`.

4. **Authentication loading test**
   - Hold session restoration in a loading state.
   - Verify protected routes do not render prematurely and the eventual authenticated state reaches the Dashboard.

5. **Registration flow test**
   - Stub successful registration.
   - Verify registration returns to `/login` and does not incorrectly mark the user authenticated unless that behavior is intentionally changed.

6. **Home/Backend Status regression test**
   - Verify the Backend Status screen remains available at its approved path and still displays status, last-checked time, database status, and retry behavior.
