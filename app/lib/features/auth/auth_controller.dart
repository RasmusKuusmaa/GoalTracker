import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../data/remote/auth_api.dart';
import 'auth_providers.dart';

part 'auth_controller.g.dart';

/// `state.value == null` means signed out; a non-null [UserProfile] means
/// signed in. Loading/error are the ordinary [AsyncValue] states, covering
/// both the initial session bootstrap and in-flight login/register calls.
@Riverpod(keepAlive: true)
class AuthController extends _$AuthController {
  @override
  Future<UserProfile?> build() async {
    final accessToken = await ref.read(tokenStoreProvider).readAccessToken();
    if (accessToken == null) return null;

    try {
      return await ref.read(authApiProvider).me();
    } on DioException catch (error) {
      // A definitively dead session (both tokens rejected, refresh already
      // attempted by the interceptor) starts clean. Any other failure
      // (offline at launch, etc.) leaves the stored tokens alone so restore
      // can succeed once connectivity returns.
      if (error.response?.statusCode == 401) {
        await ref.read(tokenStoreProvider).clear();
      }
      return null;
    }
  }

  Future<void> login({required String email, required String password}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final tokens = await ref.read(authApiProvider).login(email: email, password: password);
      await ref.read(tokenStoreProvider).saveTokens(tokens);
      return ref.read(authApiProvider).me();
    });
  }

  Future<void> register({
    required String email,
    required String password,
    required String displayName,
    required String timezone,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final tokens = await ref
          .read(authApiProvider)
          .register(
            email: email,
            password: password,
            displayName: displayName,
            timezone: timezone,
          );
      await ref.read(tokenStoreProvider).saveTokens(tokens);
      return ref.read(authApiProvider).me();
    });
  }

  Future<void> logout() async {
    await ref.read(tokenStoreProvider).clear();
    state = const AsyncData(null);
  }
}
