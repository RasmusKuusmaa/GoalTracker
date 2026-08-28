import 'package:dio/dio.dart';

/// Reads the current access token, or `null` when signed out. Backed by
/// `TokenStore` once it exists (see `feat: add secure token store`).
typedef TokenReader = Future<String?> Function();

/// Attaches `Authorization: Bearer <token>` to every outgoing request that has
/// one available.
class AuthHeaderInterceptor extends Interceptor {
  AuthHeaderInterceptor(this._readAccessToken);

  final TokenReader _readAccessToken;

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _readAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}

/// Refreshes the access token once and retries the request when it fails
/// with 401. Backed by `TokenStore` once it exists (see
/// `feat: add secure token store`). Must persist the new token wherever the
/// paired [TokenReader] reads from *before* returning, so the retried
/// request's [AuthHeaderInterceptor] pass picks it up automatically. Returns
/// the new access token (unused by the retry itself, only as a success
/// signal), or `null` when the refresh failed (e.g. the refresh token also
/// expired).
typedef TokenRefresher = Future<String?> Function();

/// A [QueuedInterceptor] so concurrent requests that all fail with 401 share
/// a single refresh attempt instead of each racing to refresh separately.
class RefreshOnUnauthorizedInterceptor extends QueuedInterceptor {
  RefreshOnUnauthorizedInterceptor({required this.dio, required this.refreshAccessToken});

  final Dio dio;
  final TokenRefresher refreshAccessToken;

  static const _retriedKey = 'goal_tracker.retried_after_refresh';

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final isUnauthorized = err.response?.statusCode == 401;
    final alreadyRetried = err.requestOptions.extra[_retriedKey] == true;
    if (!isUnauthorized || alreadyRetried) {
      handler.next(err);
      return;
    }

    final newToken = await refreshAccessToken();
    if (newToken == null) {
      handler.next(err);
      return;
    }

    // AuthHeaderInterceptor re-runs on this refetch and reattaches the
    // header from the now-refreshed token store — no need to set it here.
    final options = err.requestOptions..extra[_retriedKey] = true;
    try {
      handler.resolve(await dio.fetch(options));
    } on DioException catch (retryError) {
      handler.next(retryError);
    }
  }
}
