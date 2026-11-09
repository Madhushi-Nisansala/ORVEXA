import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import 'auth_models.dart';
import 'auth_token_store.dart';

class AuthException implements Exception {
  const AuthException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class AuthRepository {
  AuthRepository(this._apiClient, {AuthTokenStore? storage})
    : _storage = storage ?? SecureAuthTokenStore();

  static const accessTokenKey = 'orvexa.access_token';
  static const refreshTokenKey = 'orvexa.refresh_token';

  final ApiClient _apiClient;
  final AuthTokenStore _storage;

  Future<AuthUser> register({
    required String email,
    required String password,
    String? fullName,
    String preferredLanguage = 'en',
  }) async {
    try {
      final response = await _apiClient.dio.post<Object?>(
        '/api/v1/auth/register',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
          'preferred_language': preferredLanguage,
        },
      );
      return AuthUser.fromJson(response.data);
    } on DioException catch (error) {
      throw _authException(error);
    } on FormatException {
      throw const AuthException('The server returned an invalid response.');
    }
  }

  Future<AuthUser> login({
    required String email,
    required String password,
    String? deviceName,
  }) async {
    try {
      final response = await _apiClient.dio.post<Object?>(
        '/api/v1/auth/login',
        data: {'email': email, 'password': password, 'device_name': deviceName},
      );
      final tokens = TokenResponse.fromJson(response.data);
      await _saveTokens(tokens);
      try {
        return await _currentUser(tokens.accessToken);
      } catch (_) {
        await clearTokens();
        rethrow;
      }
    } on DioException catch (error) {
      throw _authException(error);
    } on FormatException {
      await clearTokens();
      throw const AuthException('The server returned an invalid response.');
    }
  }

  Future<AuthUser?> restoreSession() async {
    final accessToken = await _storage.read(key: accessTokenKey);
    final refreshToken = await _storage.read(key: refreshTokenKey);
    if (accessToken == null || refreshToken == null) {
      await clearTokens();
      return null;
    }

    try {
      return await _currentUser(accessToken);
    } on DioException catch (error) {
      if (error.response?.statusCode != 401) {
        await clearTokens();
        return null;
      }
      try {
        final tokens = await _refresh(refreshToken);
        return await _currentUser(tokens.accessToken);
      } catch (_) {
        await clearTokens();
        return null;
      }
    } catch (_) {
      await clearTokens();
      return null;
    }
  }

  Future<AuthUser> refresh(String refreshToken) async {
    try {
      final tokens = await _refresh(refreshToken);
      return await _currentUser(tokens.accessToken);
    } on DioException catch (error) {
      if (error.response?.statusCode == 401) {
        await clearTokens();
      }
      throw _authException(error);
    } on FormatException {
      throw const AuthException('The server returned an invalid response.');
    }
  }

  Future<void> logout() async {
    final refreshToken = await _storage.read(key: refreshTokenKey);
    try {
      if (refreshToken != null) {
        await _apiClient.dio.post<Object?>(
          '/api/v1/auth/logout',
          data: {'refresh_token': refreshToken},
        );
      }
    } finally {
      await clearTokens();
    }
  }

  Future<void> logoutAll() async {
    final accessToken = await _storage.read(key: accessTokenKey);
    try {
      if (accessToken != null) {
        await _apiClient.dio.post<Object?>(
          '/api/v1/auth/logout-all',
          options: _authorizedOptions(accessToken),
        );
      }
    } finally {
      await clearTokens();
    }
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: accessTokenKey);
    await _storage.delete(key: refreshTokenKey);
  }

  Future<void> _saveTokens(TokenResponse tokens) async {
    await _storage.write(key: accessTokenKey, value: tokens.accessToken);
    await _storage.write(key: refreshTokenKey, value: tokens.refreshToken);
  }

  Future<TokenResponse> _refresh(String refreshToken) async {
    final response = await _apiClient.dio.post<Object?>(
      '/api/v1/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    final tokens = TokenResponse.fromJson(response.data);
    await _saveTokens(tokens);
    return tokens;
  }

  Future<AuthUser> _currentUser(String accessToken) async {
    final response = await _apiClient.dio.get<Object?>(
      '/api/v1/auth/me',
      options: _authorizedOptions(accessToken),
    );
    try {
      return AuthUser.fromJson(response.data);
    } on FormatException {
      throw const AuthException('The server returned an invalid response.');
    }
  }

  Options _authorizedOptions(String accessToken) =>
      Options(headers: {'Authorization': 'Bearer $accessToken'});

  AuthException _authException(DioException error) {
    final statusCode = error.response?.statusCode;
    if (statusCode == 401) {
      return const AuthException('Invalid email or password.', statusCode: 401);
    }
    if (statusCode == 409) {
      return const AuthException('Unable to create account.', statusCode: 409);
    }
    if (statusCode == 422) {
      return const AuthException(
        'Please check the information you entered.',
        statusCode: 422,
      );
    }
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return const AuthException(
        'Unable to reach the ORVEXA server. Please try again.',
      );
    }
    return const AuthException('Authentication failed. Please try again.');
  }
}
