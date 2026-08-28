import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../data/remote/api_client.dart';
import '../../data/remote/auth_api.dart';
import '../../data/remote/token_store.dart';

part 'auth_providers.g.dart';

@Riverpod(keepAlive: true)
TokenStore tokenStore(Ref ref) => TokenStore();

@Riverpod(keepAlive: true)
ApiClient apiClient(Ref ref) {
  final store = ref.watch(tokenStoreProvider);

  // `AuthApi` wraps this same client's Dio to call `/auth/refresh`, but the
  // client's refresh callback has to exist before the client itself does.
  // Assigned once, immediately below, before the callback can ever run.
  late final AuthApi refreshAuthApi;

  final client = ApiClient(
    getAccessToken: store.readAccessToken,
    refreshAccessToken: () async {
      final refreshToken = await store.readRefreshToken();
      if (refreshToken == null) return null;
      try {
        final tokens = await refreshAuthApi.refresh(refreshToken);
        await store.saveTokens(tokens);
        return tokens.accessToken;
      } on Exception {
        return null;
      }
    },
  );

  refreshAuthApi = AuthApi(client.dio);
  return client;
}

@Riverpod(keepAlive: true)
AuthApi authApi(Ref ref) => AuthApi(ref.watch(apiClientProvider).dio);
