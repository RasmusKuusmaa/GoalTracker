import 'package:app/data/remote/auth_api.dart';
import 'package:app/data/remote/token_store.dart';
import 'package:app/features/auth/auth_controller.dart';
import 'package:app/features/auth/auth_providers.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthApi implements AuthApi {
  bool failLogin = false;

  @override
  Future<TokenPair> login({required String email, required String password}) async {
    if (failLogin) throw DioException(requestOptions: RequestOptions());
    return TokenPair(accessToken: 'access', refreshToken: 'refresh');
  }

  @override
  Future<TokenPair> register({
    required String email,
    required String password,
    required String displayName,
    required String timezone,
    int weekStart = 1,
  }) async => TokenPair(accessToken: 'access', refreshToken: 'refresh');

  @override
  Future<TokenPair> refresh(String refreshToken) async =>
      TokenPair(accessToken: 'access', refreshToken: 'refresh');

  @override
  Future<UserProfile> me() async => UserProfile(
    id: 'user-1',
    email: 'a@example.com',
    displayName: 'Ada',
    timezone: 'Europe/Tallinn',
    weekStart: 1,
    createdAt: DateTime(2026),
    updatedAt: DateTime(2026),
  );
}

class _FakeTokenStore implements TokenStore {
  String? accessToken;
  String? refreshToken;

  @override
  Future<String?> readAccessToken() async => accessToken;

  @override
  Future<String?> readRefreshToken() async => refreshToken;

  @override
  Future<void> saveTokens(TokenPair tokens) async {
    accessToken = tokens.accessToken;
    refreshToken = tokens.refreshToken;
  }

  @override
  Future<void> clear() async {
    accessToken = null;
    refreshToken = null;
  }
}

void main() {
  late _FakeAuthApi fakeAuthApi;
  late _FakeTokenStore fakeTokenStore;
  late ProviderContainer container;

  setUp(() {
    fakeAuthApi = _FakeAuthApi();
    fakeTokenStore = _FakeTokenStore();
    container = ProviderContainer(
      overrides: [
        authApiProvider.overrideWithValue(fakeAuthApi),
        tokenStoreProvider.overrideWithValue(fakeTokenStore),
      ],
    );
    addTearDown(container.dispose);
  });

  test('starts signed out', () async {
    final state = await container.read(authControllerProvider.future);
    expect(state, isNull);
  });

  test('login succeeds and stores tokens, exposing the signed-in user', () async {
    await container.read(authControllerProvider.notifier).login(
      email: 'a@example.com',
      password: 'hunter2hunter2',
    );

    final state = container.read(authControllerProvider);
    expect(state.value?.email, 'a@example.com');
    expect(fakeTokenStore.accessToken, 'access');
  });

  test('login failure surfaces as an error state', () async {
    fakeAuthApi.failLogin = true;

    await container.read(authControllerProvider.notifier).login(
      email: 'a@example.com',
      password: 'wrong',
    );

    expect(container.read(authControllerProvider).hasError, isTrue);
  });

  test('logout clears tokens and returns to signed out', () async {
    await container.read(authControllerProvider.notifier).login(
      email: 'a@example.com',
      password: 'hunter2hunter2',
    );

    await container.read(authControllerProvider.notifier).logout();

    expect(container.read(authControllerProvider).value, isNull);
    expect(fakeTokenStore.accessToken, isNull);
  });
}
