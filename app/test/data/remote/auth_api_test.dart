import 'dart:convert';

import 'package:app/data/remote/auth_api.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

class _RecordingAdapter implements HttpClientAdapter {
  String? lastPath;
  Map<String, dynamic>? lastBody;
  late Map<String, dynamic> nextResponse;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    lastPath = options.path;
    lastBody = options.data as Map<String, dynamic>?;
    return ResponseBody.fromString(jsonEncode(nextResponse), 200, headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    });
  }
}

void main() {
  late _RecordingAdapter adapter;
  late AuthApi authApi;

  setUp(() {
    adapter = _RecordingAdapter();
    final dio = Dio(BaseOptions(baseUrl: 'https://example.test'))..httpClientAdapter = adapter;
    authApi = AuthApi(dio);
  });

  test('register posts the expected body and parses the token pair', () async {
    adapter.nextResponse = {'access_token': 'access-1', 'refresh_token': 'refresh-1'};

    final tokens = await authApi.register(
      email: 'a@example.com',
      password: 'hunter2hunter2',
      displayName: 'Ada',
      timezone: 'Europe/Tallinn',
    );

    expect(adapter.lastPath, '/auth/register');
    expect(adapter.lastBody, {
      'email': 'a@example.com',
      'password': 'hunter2hunter2',
      'display_name': 'Ada',
      'timezone': 'Europe/Tallinn',
      'week_start': 1,
    });
    expect(tokens.accessToken, 'access-1');
    expect(tokens.refreshToken, 'refresh-1');
  });

  test('login posts credentials and parses the token pair', () async {
    adapter.nextResponse = {'access_token': 'access-2', 'refresh_token': 'refresh-2'};

    final tokens = await authApi.login(email: 'a@example.com', password: 'hunter2hunter2');

    expect(adapter.lastPath, '/auth/login');
    expect(adapter.lastBody, {'email': 'a@example.com', 'password': 'hunter2hunter2'});
    expect(tokens.accessToken, 'access-2');
  });

  test('refresh posts the refresh token and parses the new pair', () async {
    adapter.nextResponse = {'access_token': 'access-3', 'refresh_token': 'refresh-3'};

    final tokens = await authApi.refresh('refresh-2');

    expect(adapter.lastPath, '/auth/refresh');
    expect(adapter.lastBody, {'refresh_token': 'refresh-2'});
    expect(tokens.accessToken, 'access-3');
  });

  test('me parses the user profile', () async {
    adapter.nextResponse = {
      'id': 'user-1',
      'email': 'a@example.com',
      'display_name': 'Ada',
      'timezone': 'Europe/Tallinn',
      'week_start': 1,
      'created_at': '2026-01-01T00:00:00Z',
      'updated_at': '2026-01-02T00:00:00Z',
    };

    final profile = await authApi.me();

    expect(adapter.lastPath, '/auth/me');
    expect(profile.email, 'a@example.com');
    expect(profile.displayName, 'Ada');
    expect(profile.weekStart, 1);
  });
}
