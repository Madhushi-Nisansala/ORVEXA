abstract final class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'ORVEXA_API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const isProduction = bool.fromEnvironment(
    'ORVEXA_PRODUCTION',
    defaultValue: false,
  );

  static const appVersion = String.fromEnvironment(
    'ORVEXA_APP_VERSION',
    defaultValue: '0.1.0',
  );
}
