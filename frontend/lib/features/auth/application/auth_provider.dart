import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../data/auth_models.dart';
import '../data/auth_repository.dart';
import '../data/auth_token_store.dart';

final authApiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final authTokenStoreProvider = Provider<AuthTokenStore>(
  (ref) => SecureAuthTokenStore(),
);

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(
    ref.watch(authApiClientProvider),
    storage: ref.watch(authTokenStoreProvider),
  ),
);

final protectedApiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(authTokenStoreProvider);
  final repository = ref.watch(authRepositoryProvider);
  return ApiClient(
    accessTokenProvider: () => storage.read(key: AuthRepository.accessTokenKey),
    onUnauthorized: () async {
      final refreshToken = await storage.read(
        key: AuthRepository.refreshTokenKey,
      );
      if (refreshToken == null || refreshToken.isEmpty) return false;
      try {
        await repository.refresh(refreshToken);
        return true;
      } catch (_) {
        await repository.clearTokens();
        ref.read(authProvider.notifier).expireSession();
        return false;
      }
    },
  );
});

final authProvider = AsyncNotifierProvider<AuthNotifier, AuthUser?>(
  AuthNotifier.new,
);

class AuthNotifier extends AsyncNotifier<AuthUser?> {
  @override
  Future<AuthUser?> build() =>
      ref.read(authRepositoryProvider).restoreSession();

  Future<void> login({
    required String email,
    required String password,
    String? deviceName,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref
          .read(authRepositoryProvider)
          .login(email: email, password: password, deviceName: deviceName),
    );
  }

  Future<AuthUser> register({
    required String email,
    required String password,
    String? fullName,
    String preferredLanguage = 'en',
  }) {
    return ref
        .read(authRepositoryProvider)
        .register(
          email: email,
          password: password,
          fullName: fullName,
          preferredLanguage: preferredLanguage,
        );
  }

  Future<void> logout() async {
    final repository = ref.read(authRepositoryProvider);
    state = const AsyncLoading();
    try {
      await repository.logout();
    } finally {
      state = const AsyncData(null);
    }
  }

  void expireSession() {
    if (state.value != null) {
      state = const AsyncData(null);
    }
  }
}
