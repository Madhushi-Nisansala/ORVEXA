class AuthUser {
  const AuthUser({
    required this.id,
    required this.email,
    required this.fullName,
    required this.preferredLanguage,
    required this.isActive,
    required this.isVerified,
    required this.createdAt,
    required this.updatedAt,
    required this.lastLoginAt,
    required this.roles,
  });

  factory AuthUser.fromJson(Object? json) {
    final map = _object(json, 'user');
    return AuthUser(
      id: _string(map, 'id'),
      email: _string(map, 'email'),
      fullName: _nullableString(map, 'full_name'),
      preferredLanguage: _string(map, 'preferred_language'),
      isActive: _bool(map, 'is_active'),
      isVerified: _bool(map, 'is_verified'),
      createdAt: DateTime.parse(_string(map, 'created_at')),
      updatedAt: DateTime.parse(_string(map, 'updated_at')),
      lastLoginAt: _nullableDateTime(map, 'last_login_at'),
      roles: _stringList(map, 'roles'),
    );
  }

  final String id;
  final String email;
  final String? fullName;
  final String preferredLanguage;
  final bool isActive;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastLoginAt;
  final List<String> roles;
}

class TokenResponse {
  const TokenResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory TokenResponse.fromJson(Object? json) {
    final map = _object(json, 'token response');
    return TokenResponse(
      accessToken: _string(map, 'access_token'),
      refreshToken: _string(map, 'refresh_token'),
      tokenType: _string(map, 'token_type'),
      expiresIn: _int(map, 'expires_in'),
      user: AuthUser.fromJson(map['user']),
    );
  }

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final AuthUser user;
}

Map<String, Object?> _object(Object? value, String name) {
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return Map<String, Object?>.from(value);
  }
  throw const FormatException('Invalid authentication response.');
}

String _string(Map<String, Object?> map, String key) {
  final value = map[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw const FormatException('Invalid authentication response.');
}

String? _nullableString(Map<String, Object?> map, String key) {
  final value = map[key];
  return value is String ? value : null;
}

bool _bool(Map<String, Object?> map, String key) {
  final value = map[key];
  if (value is bool) {
    return value;
  }
  throw const FormatException('Invalid authentication response.');
}

int _int(Map<String, Object?> map, String key) {
  final value = map[key];
  if (value is int) {
    return value;
  }
  throw const FormatException('Invalid authentication response.');
}

DateTime? _nullableDateTime(Map<String, Object?> map, String key) {
  final value = map[key];
  return value is String ? DateTime.parse(value) : null;
}

List<String> _stringList(Map<String, Object?> map, String key) {
  final value = map[key];
  if (value is List && value.every((item) => item is String)) {
    return List<String>.from(value);
  }
  throw const FormatException('Invalid authentication response.');
}
