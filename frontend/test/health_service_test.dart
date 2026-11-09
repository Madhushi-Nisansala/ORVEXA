import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/core/network/health_service.dart';

void main() {
  test('parses a mocked healthy response', () async {
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) => handler.resolve(
			Response<Object?>(
			  requestOptions: options,
			  statusCode: 200,
			  data: {
				'status': 'healthy',
				'application': 'ORVEXA',
				'version': '0.1.0',
				'database': 'connected',
			  },
			),
		  ),
		),
	  );

	final result = await HealthService(ApiClient(dio: dio)).check();

	expect(result.status, 'healthy');
	expect(result.application, 'ORVEXA');
	expect(result.database, 'connected');
  });

  test('rejects an invalid mocked response', () async {
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) => handler.resolve(
			Response<Object?>(
			  requestOptions: options,
			  statusCode: 200,
			  data: {'database': 'connected'},
			),
		  ),
		),
	  );

	expect(
	  HealthService(ApiClient(dio: dio)).check(),
	  throwsA(isA<FormatException>()),
	);
  });
}