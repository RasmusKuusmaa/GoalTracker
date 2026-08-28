import 'package:app/data/remote/auth_interceptors.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AuthHeaderInterceptor', () {
    test('attaches the bearer header when a token is available', () async {
      final interceptor = AuthHeaderInterceptor(() async => 'token-123');
      final options = RequestOptions(path: '/goals');
      final handler = RequestInterceptorHandler();

      await interceptor.onRequest(options, handler);

      expect(options.headers['Authorization'], 'Bearer token-123');
    });

    test('leaves the header unset when signed out', () async {
      final interceptor = AuthHeaderInterceptor(() async => null);
      final options = RequestOptions(path: '/goals');
      final handler = RequestInterceptorHandler();

      await interceptor.onRequest(options, handler);

      expect(options.headers.containsKey('Authorization'), isFalse);
    });
  });
}
