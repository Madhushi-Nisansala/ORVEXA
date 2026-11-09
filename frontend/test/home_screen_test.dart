import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';

import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/core/network/health_service.dart';
import 'package:orvexa/features/home/application/health_provider.dart';
import 'package:orvexa/features/home.dart';

class FakeHealthService extends HealthService {
  FakeHealthService(this.result) : super(ApiClient(dio: Dio()));

  final BackendHealth result;

  @override
  Future<BackendHealth> check() async => result;
}

void main() {
  testWidgets('shows connected status and database from the health response', (
	tester,
  ) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [
		  healthServiceProvider.overrideWithValue(
			FakeHealthService(
			  const BackendHealth(
				status: 'healthy',
				database: 'connected',
			  ),
			),
		  ),
		],
		child: const MaterialApp(home: HomeScreen()),
	  ),
	);
	await tester.pump();

	expect(find.text('Connected'), findsOneWidget);
	expect(find.text('Database: connected'), findsOneWidget);
	expect(find.text('Retry'), findsOneWidget);
  });

  testWidgets('shows disconnected status after a failed health response', (
	tester,
  ) async {
	await tester.pumpWidget(
	  ProviderScope(
		overrides: [
		  healthServiceProvider.overrideWithValue(
			FakeHealthService(
			  const BackendHealth(status: 'unhealthy'),
			),
		  ),
		],
		child: const MaterialApp(home: HomeScreen()),
	  ),
	);
	await tester.pump();

	expect(find.text('Disconnected'), findsOneWidget);
	expect(find.text('Database: connected'), findsNothing);
  });
}