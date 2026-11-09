import 'package:dio/dio.dart';
import 'dart:developer' as developer;

import '../config/app_config.dart';

class ApiClient {
  ApiClient({
    Dio? dio,
    String? accessToken,
    Future<String?> Function()? accessTokenProvider,
    Future<bool> Function()? onUnauthorized,
  }) : _dio = dio ?? Dio() {
    if (dio == null) {
      _dio.options = BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 3),
        receiveTimeout: const Duration(seconds: 3),
        headers: {
          'Accept': 'application/json',
          if (accessToken != null) 'Authorization': 'Bearer $accessToken',
        },
      );
    }
    if (accessTokenProvider != null || onUnauthorized != null) {
      _dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) async {
            if (accessTokenProvider != null) {
              final token = await accessTokenProvider();
              if (token != null && token.isNotEmpty) {
                options.headers['Authorization'] = 'Bearer $token';
              }
            }
            handler.next(options);
          },
          onResponse: (response, handler) {
            _logResponse(response.requestOptions, response.statusCode);
            handler.next(response);
          },
          onError: (error, handler) async {
            _logResponse(error.requestOptions, error.response?.statusCode);
            final options = error.requestOptions;
            if (error.response?.statusCode == 401 &&
                onUnauthorized != null &&
                options.extra['_skipAuthRefresh'] != true &&
                options.extra['_authRetry'] != true) {
              options.extra['_authRetry'] = true;
              final refreshed = await _refreshOnce(onUnauthorized);
              if (refreshed && accessTokenProvider != null) {
                final token = await accessTokenProvider();
                if (token != null && token.isNotEmpty) {
                  options.headers['Authorization'] = 'Bearer $token';
                  try {
                    handler.resolve(await _dio.fetch<Object?>(options));
                    return;
                  } on DioException catch (retryError) {
                    handler.next(retryError);
                    return;
                  }
                }
              }
            }
            handler.next(error);
          },
        ),
      );
    }
  }

  final Dio _dio;
  Future<bool>? _refreshFuture;

  Dio get dio => _dio;

  Future<bool> _refreshOnce(Future<bool> Function() refresh) {
    return _refreshFuture ??= refresh().whenComplete(() => _refreshFuture = null);
  }

  void _logResponse(RequestOptions options, int? statusCode) {
    developer.log(
      '${options.method} ${options.uri.path} -> ${statusCode ?? 'network-error'}',
      name: 'orvexa.http',
    );
  }

  Future<bool> isBackendReachable() async {
    try {
      final response = await _dio.get<Object?>('/health');
      return response.statusCode == 200;
    } on DioException {
      return false;
    }
  }
}
