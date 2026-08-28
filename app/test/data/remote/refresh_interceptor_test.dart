import 'package:app/data/remote/auth_interceptors.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

/// Returns 401 on the first call and 200 on every call after, so tests can
/// assert the interceptor retried exactly once with the refreshed token.
class _ScriptedAdapter implements HttpClientAdapter {
  int callCount = 0;
  String? lastAuthHeader;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    callCount++;
    lastAuthHeader = options.headers['Authorization'] as String?;
    final statusCode = callCount == 1 ? 401 : 200;
    return ResponseBody.fromString('{}', statusCode, headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    });
  }
}

void main() {
  late _ScriptedAdapter adapter;
  late Dio dio;

  setUp(() {
    adapter = _ScriptedAdapter();
    dio = Dio(BaseOptions(baseUrl: 'https://example.test'))..httpClientAdapter = adapter;
  });

  test('refreshes the token and retries once on 401', () async {
    var currentToken = 'old-token';
    dio.interceptors.add(AuthHeaderInterceptor(() async => currentToken));
    dio.interceptors.add(
      RefreshOnUnauthorizedInterceptor(
        dio: dio,
        refreshAccessToken: () async {
          currentToken = 'new-token';
          return currentToken;
        },
      ),
    );

    final response = await dio.get<Map<String, dynamic>>('/goals');

    expect(response.statusCode, 200);
    expect(adapter.callCount, 2);
    expect(adapter.lastAuthHeader, 'Bearer new-token');
  });

  test('propagates the 401 without retrying when refresh fails', () async {
    dio.interceptors.add(AuthHeaderInterceptor(() async => 'old-token'));
    dio.interceptors.add(
      RefreshOnUnauthorizedInterceptor(dio: dio, refreshAccessToken: () async => null),
    );

    await expectLater(
      dio.get<Map<String, dynamic>>('/goals'),
      throwsA(isA<DioException>().having((e) => e.response?.statusCode, 'statusCode', 401)),
    );
    expect(adapter.callCount, 1);
  });
}
