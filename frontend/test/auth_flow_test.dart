import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';

import 'package:orvexa/app/app.dart';
import 'package:orvexa/features/auth/application/auth_provider.dart';
import 'package:orvexa/features/auth/data/auth_models.dart';

class _UnauthenticatedNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => null;
}

class _LoginNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => null;

  @override
  Future<void> login({
	required String email,
	required String password,
	String? deviceName,
  }) async {
	state = AsyncData(_user);
  }
}

class _AuthenticatedNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => _user;
}

final _user = AuthUser(
  id: '00000000-0000-0000-0000-000000000001',
  email: 'user@example.com',
  fullName: 'Test User',
  preferredLanguage: 'en',
  isActive: true,
  isVerified: false,
  createdAt: DateTime(2025),
  updatedAt: DateTime(2025),
  lastLoginAt: null,
  roles: ['user'],
);

void main() {
  testWidgets('unauthenticated users start at login and can open registration',
	  (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [
		  authProvider.overrideWith(_UnauthenticatedNotifier.new),
		],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pump();

	expect(find.text('Welcome to ORVEXA'), findsOneWidget);
	await tester.tap(find.text('Create an account'));
	await tester.pumpAndSettle();
	expect(find.text('Create account'), findsWidgets);
  });

  testWidgets('authenticated users are redirected to the dashboard',
	  (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [
		  authProvider.overrideWith(_AuthenticatedNotifier.new),
		],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pumpAndSettle();

	expect(find.text('Welcome, Test User'), findsOneWidget);
	await tester.tap(find.byTooltip('Settings'));
	await tester.pumpAndSettle();
	expect(find.text('Appearance'), findsOneWidget);
  });

  testWidgets('successful login navigates to the dashboard', (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [authProvider.overrideWith(_LoginNotifier.new)],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pumpAndSettle();
	await tester.enterText(find.byType(TextFormField).at(0), 'user@example.com');
	await tester.enterText(find.byType(TextFormField).at(1), 'password');
	await tester.tap(find.text('Sign in'));
	await tester.pumpAndSettle();

	expect(find.text('Welcome, Test User'), findsOneWidget);
  });
}
