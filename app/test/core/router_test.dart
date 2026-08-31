import 'package:app/core/router.dart';
import 'package:app/data/remote/auth_api.dart';
import 'package:app/data/remote/token_store.dart';
import 'package:app/features/auth/auth_controller.dart';
import 'package:app/features/auth/auth_providers.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
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

  Widget buildApp() {
    return UncontrolledProviderScope(
      container: container,
      child: MaterialApp.router(routerConfig: container.read(routerProvider)),
    );
  }

  testWidgets('redirects a signed-out user to the login screen', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Sign in'), findsWidgets);
    expect(find.text('Signed in'), findsNothing);
  });

  testWidgets('redirects to home once the signed-out user signs in', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await container.read(authControllerProvider.notifier).login(
      email: 'a@example.com',
      password: 'hunter2hunter2',
    );
    await tester.pumpAndSettle();

    expect(find.text('Signed in'), findsOneWidget);
  });

  testWidgets('lands a user with a stored session directly on home', (tester) async {
    fakeTokenStore.accessToken = 'existing-access';

    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Signed in'), findsOneWidget);
  });
}
