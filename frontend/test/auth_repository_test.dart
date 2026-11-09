import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/features/auth/data/auth_repository.dart';
import 'package:orvexa/features/auth/data/auth_token_store.dart';

class FakeTokenStore implements AuthTokenStore {
  final values = <String, String>{};

  @override
  Future<String?> read({required String key}) async => values[key];

  @override
  Future<void> write({required String key, required String value}) async {
	values[key] = value;
  }

  @override
  Future<void> delete({required String key}) async {
	values.remove(key);
  }
}

void main() {
  test('registers with the backend payload and parses the user', () async {
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) {
			expect(options.path, '/api/v1/auth/register');
			expect(options.data['preferred_language'], 'en');
			handler.resolve(Response<Object?>(
			  requestOptions: options,
			  statusCode: 201,
			  data: _userJson(),
			));
		  },
		),
	  );
	final repository = AuthRepository(
	  ApiClient(dio: dio),
	  storage: FakeTokenStore(),
	);

	final user = await repository.register(
	  email: 'user@example.com',
	  password: 'password123',
	);

	expect(user.email, 'user@example.com');
	expect(user.roles, ['user']);
  });

  test('logs in, stores tokens, and retrieves /auth/me', () async {
	final store = FakeTokenStore();
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) {
			if (options.path == '/api/v1/auth/login') {
			  expect(options.data['email'], 'user@example.com');
			  expect(options.data['password'], 'password123');
			  handler.resolve(Response<Object?>(
				requestOptions: options,
				statusCode: 200,
				data: _tokenJson(),
			  ));
			} else {
			  expect(options.path, '/api/v1/auth/me');
			  expect(options.headers['Authorization'], startsWith('Bearer '));
			  handler.resolve(Response<Object?>(
				requestOptions: options,
				statusCode: 200,
				data: _userJson(),
			  ));
			}
		  },
		),
	  );
	final repository = AuthRepository(ApiClient(dio: dio), storage: store);

	final user = await repository.login(
	  email: 'user@example.com',
	  password: 'password123',
	);

	expect(user.email, 'user@example.com');
	expect(store.values[AuthRepository.accessTokenKey], 'access-token');
	expect(store.values[AuthRepository.refreshTokenKey], 'refresh-token');
  });

  test('maps invalid credentials without exposing secrets', () async {
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) => handler.reject(
			DioException(
			  requestOptions: options,
			  response: Response<Object?>(
				requestOptions: options,
				statusCode: 401,
				data: {'detail': 'Invalid email or password'},
			  ),
			),
		  ),
		),
	  );
	final repository = AuthRepository(
	  ApiClient(dio: dio),
	  storage: FakeTokenStore(),
	);

	expect(
	  () => repository.login(email: 'user@example.com', password: 'secret'),
	  throwsA(
		isA<AuthException>().having(
		  (error) => error.message,
		  'message',
		  'Invalid email or password.',
		),
	  ),
	);
  });

  test('refreshes rotated tokens and logs out by clearing storage', () async {
	final store = FakeTokenStore()
	  ..values[AuthRepository.refreshTokenKey] = 'old-refresh-token';
	final dio = Dio()
	  ..interceptors.add(
		InterceptorsWrapper(
		  onRequest: (options, handler) {
			if (options.path == '/api/v1/auth/refresh') {
			  expect(options.data['refresh_token'], 'old-refresh-token');
			  handler.resolve(Response<Object?>(
				requestOptions: options,
				statusCode: 200,
				data: _tokenJson(
				  accessToken: 'new-access-token',
				  refreshToken: 'new-refresh-token',
				),
			  ));
			} else if (options.path == '/api/v1/auth/me') {
			  handler.resolve(Response<Object?>(
				requestOptions: options,
				statusCode: 200,
				data: _userJson(),
			  ));
			} else {
			  expect(options.path, '/api/v1/auth/logout');
			  expect(options.data['refresh_token'], 'new-refresh-token');
			  handler.resolve(Response<Object?>(
				requestOptions: options,
				statusCode: 200,
				data: {'message': 'Logged out'},
			  ));
			}
		  },
		),
	  );
	final repository = AuthRepository(ApiClient(dio: dio), storage: store);

	final user = await repository.refresh('old-refresh-token');
	expect(user.email, 'user@example.com');
	expect(store.values[AuthRepository.accessTokenKey], 'new-access-token');
	await repository.logout();
	expect(store.values, isEmpty);
  });

  test('clears incomplete persisted sessions during startup', () async {
	final store = FakeTokenStore()
	  ..values[AuthRepository.accessTokenKey] = 'stale-access-token';
	final repository = AuthRepository(ApiClient(dio: Dio()), storage: store);

	expect(await repository.restoreSession(), isNull);
	expect(store.values, isEmpty);
  });
}

Map<String, Object?> _userJson() => {
	  'id': '00000000-0000-0000-0000-000000000001',
	  'email': 'user@example.com',
	  'full_name': 'Test User',
	  'preferred_language': 'en',
	  'is_active': true,
	  'is_verified': false,
	  'created_at': '2025-01-01T00:00:00Z',
	  'updated_at': '2025-01-01T00:00:00Z',
	  'last_login_at': null,
	  'roles': ['user'],
	};

Map<String, Object?> _tokenJson({
  String accessToken = 'access-token',
  String refreshToken = 'refresh-token',
}) => {
	  'access_token': accessToken,
	  'refresh_token': refreshToken,
	  'token_type': 'bearer',
	  'expires_in': 900,
	  'user': _userJson(),
	};
