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
