import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:orvexa/core/network/api_client.dart';

void main() {
  test('API service returns false for an unreachable backend', () async {
	final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:1'));
	final client = ApiClient(dio: dio);

	expect(await client.isBackendReachable(), isFalse);
  });

  test('refreshes once and retries an unauthorized protected request', () async {
	final dio = Dio(BaseOptions(baseUrl: 'http://test'));
	var requests = 0;
	var refreshes = 0;
	final client = ApiClient(
	  dio: dio,
	  accessTokenProvider: () async => refreshes == 0 ? 'old-token' : 'new-token',
	  onUnauthorized: () async {
		refreshes++;
		return true;
	  },
	);
	dio.interceptors.add(
	  InterceptorsWrapper(
		onRequest: (options, handler) {
		  requests++;
		  expect(options.headers['Authorization'],
			  'Bearer ${requests == 1 ? 'old-token' : 'new-token'}');
		  if (requests == 1) {
			handler.reject(
			  DioException(
				requestOptions: options,
				response: Response<Object?>(
				  requestOptions: options,
				  statusCode: 401,
				),
			  ),
			);
		  } else {
			handler.resolve(Response<Object?>(
			  requestOptions: options,
			  statusCode: 200,
			  data: {'items': [], 'total': 0},
			));
		  }
		},
	  ),
	);

	final response = await client.dio.get<Object?>('/api/v1/documents');
	expect(response.statusCode, 200);
	expect(requests, 2);
	expect(refreshes, 1);
  });

  test('does not refresh authentication endpoints after a 401', () async {
	final dio = Dio(BaseOptions(baseUrl: 'http://test'));
	var refreshes = 0;
	final client = ApiClient(
	  dio: dio,
	  accessTokenProvider: () async => 'token',
	  onUnauthorized: () async {
		refreshes++;
		return true;
	  },
	);
	dio.interceptors.add(
	  InterceptorsWrapper(
		onRequest: (options, handler) => handler.reject(
		  DioException(
			requestOptions: options,
			response: Response<Object?>(requestOptions: options, statusCode: 401),
		  ),
		),
	  ),
	);

	await expectLater(
		client.dio.post<Object?>(
		'/api/v1/auth/refresh',
		options: Options(extra: {'_skipAuthRefresh': true}),
	  ),
	  throwsA(isA<DioException>()),
	);
	expect(refreshes, 0);
  });
}
