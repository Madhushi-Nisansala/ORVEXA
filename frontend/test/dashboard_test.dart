import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:orvexa/app/app.dart';
import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/core/network/health_service.dart';
import 'package:orvexa/features/auth/application/auth_provider.dart';
import 'package:orvexa/features/auth/data/auth_models.dart';
import 'package:orvexa/features/home/application/health_provider.dart';

class _AuthenticatedNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => _user;
}

class _UnauthenticatedNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => null;
}

class _FakeHealthService extends HealthService {
  _FakeHealthService() : super(ApiClient(dio: Dio()));

  @override
  Future<BackendHealth> check() async =>
	  const BackendHealth(status: 'healthy', database: 'connected');
}

final _user = AuthUser(
  id: '00000000-0000-0000-0000-000000000001',
  email: 'user@example.com',
  fullName: 'Test User',
  preferredLanguage: 'en',
  isActive: true,
  isVerified: true,
  createdAt: DateTime(2025),
  updatedAt: DateTime(2025),
  lastLoginAt: null,
  roles: ['user'],
);

void main() {
  testWidgets('dashboard displays its implemented and coming-soon sections',
	  (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [authProvider.overrideWith(_AuthenticatedNotifier.new)],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pumpAndSettle();

	expect(find.text('Welcome, Test User'), findsOneWidget);
	expect(find.text('Understand More. Act Smarter.'), findsOneWidget);
	expect(find.text('Documents'), findsOneWidget);
	expect(find.text('Intelligence & Insights'), findsOneWidget);
	expect(find.text('Tasks & Goals'), findsOneWidget);
	expect(find.text('Backend Status'), findsOneWidget);
	expect(find.text('Settings'), findsWidgets);
	expect(find.text('Coming soon'), findsNWidgets(2));
  });

  testWidgets('backend status card opens the existing status screen',
	  (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [
		  authProvider.overrideWith(_AuthenticatedNotifier.new),
		  healthServiceProvider.overrideWithValue(_FakeHealthService()),
		],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pumpAndSettle();
	await tester.tap(find.text('Backend Status'));
	await tester.pumpAndSettle();

	expect(find.text('Backend status'), findsOneWidget);
	expect(find.text('Connected'), findsOneWidget);
	expect(find.text('Database: connected'), findsOneWidget);
  });

  testWidgets('unauthenticated users are redirected to login', (tester) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [authProvider.overrideWith(_UnauthenticatedNotifier.new)],
		child: const OrvexaApp(),
	  ),
	);
	await tester.pumpAndSettle();

	expect(find.text('Welcome to ORVEXA'), findsOneWidget);
	expect(find.text('Welcome, Test User'), findsNothing);
  });
}
