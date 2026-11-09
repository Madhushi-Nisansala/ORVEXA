import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/health_service.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final healthServiceProvider = Provider<HealthService>(
  (ref) => HealthService(ref.watch(apiClientProvider)),
);

final healthProvider = AsyncNotifierProvider<HealthNotifier, HealthCheckResult>(
  HealthNotifier.new,
);

class HealthCheckResult {
  const HealthCheckResult({
    required this.connected,
    required this.checkedAt,
    this.databaseStatus,
  });

  final bool connected;
  final DateTime checkedAt;
  final String? databaseStatus;
}

class HealthNotifier extends AsyncNotifier<HealthCheckResult> {
  bool _isChecking = false;

  @override
  Future<HealthCheckResult> build() => _request();

  Future<void> checkAgain() async {
    if (_isChecking) {
      return;
    }

    state = const AsyncLoading();
    state = await AsyncValue.guard(_request);
  }

  Future<HealthCheckResult> _request() async {
    if (_isChecking) {
      return state.value ??
          HealthCheckResult(connected: false, checkedAt: DateTime.now());
    }

    _isChecking = true;
    try {
      final health = await ref.read(healthServiceProvider).check();
      return HealthCheckResult(
        connected: health.status.toLowerCase() == 'healthy',
        checkedAt: DateTime.now(),
        databaseStatus: health.database,
      );
    } on DioException {
      return HealthCheckResult(connected: false, checkedAt: DateTime.now());
    } on FormatException {
      return HealthCheckResult(connected: false, checkedAt: DateTime.now());
    } catch (_) {
      return HealthCheckResult(connected: false, checkedAt: DateTime.now());
    } finally {
      _isChecking = false;
    }
  }
}
