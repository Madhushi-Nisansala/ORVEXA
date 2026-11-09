import 'package:dio/dio.dart';

import 'api_client.dart';

class BackendHealth {
  const BackendHealth({
    required this.status,
    this.application,
    this.version,
    this.database,
  });

  factory BackendHealth.fromJson(Object? json) {
    if (json is! Map) {
      throw const FormatException('Health response must be an object.');
    }

    final status = json['status'];
    if (status is! String || status.isEmpty) {
      throw const FormatException('Health response has no valid status.');
    }

    String? optionalString(Object? value) => value is String ? value : null;

    return BackendHealth(
      status: status,
      application: optionalString(json['application']),
      version: optionalString(json['version']),
      database: optionalString(json['database']),
    );
  }

  final String status;
  final String? application;
  final String? version;
  final String? database;
}

class HealthService {
  HealthService(this._apiClient);

  final ApiClient _apiClient;

  Future<BackendHealth> check() async {
    final response = await _apiClient.dio.get<Object?>('/health');
    if (response.statusCode != 200) {
      throw DioException.badResponse(
        statusCode: response.statusCode ?? 0,
        requestOptions: response.requestOptions,
        response: response,
      );
    }

    return BackendHealth.fromJson(response.data);
  }
}
