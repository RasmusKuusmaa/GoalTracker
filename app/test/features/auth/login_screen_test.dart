import 'package:app/data/remote/auth_api.dart';
import 'package:app/data/remote/token_store.dart';
import 'package:app/features/auth/auth_providers.dart';
import 'package:app/features/auth/login_screen.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthApi implements AuthApi {
  int loginCalls = 0;
  bool failLogin = false;

  @override
  Future<TokenPair> login({required String email, required String password}) async {
    loginCalls++;
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

  setUp(() {
    fakeAuthApi = _FakeAuthApi();
    fakeTokenStore = _FakeTokenStore();
  });

  Widget buildApp() {
    return ProviderScope(
      overrides: [
        authApiProvider.overrideWithValue(fakeAuthApi),
        tokenStoreProvider.overrideWithValue(fakeTokenStore),
      ],
      child: const MaterialApp(home: LoginScreen()),
    );
  }

  testWidgets('shows validation errors and does not submit when fields are empty', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.tap(find.widgetWithText(FilledButton, 'Sign in'));
    await tester.pump();

    expect(find.text('Email is required'), findsOneWidget);
    expect(find.text('Password is required'), findsOneWidget);
    expect(fakeAuthApi.loginCalls, 0);
  });

  testWidgets('submits valid credentials and signs the user in', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextFormField).first, 'a@example.com');
    await tester.enterText(find.byType(TextFormField).last, 'hunter2hunter2');
    await tester.tap(find.widgetWithText(FilledButton, 'Sign in'));
    await tester.pumpAndSettle();

    expect(fakeAuthApi.loginCalls, 1);
    expect(fakeTokenStore.accessToken, 'access');
  });

  testWidgets('shows an error message when login fails', (tester) async {
    fakeAuthApi.failLogin = true;
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextFormField).first, 'a@example.com');
    await tester.enterText(find.byType(TextFormField).last, 'wrongpassword');
    await tester.tap(find.widgetWithText(FilledButton, 'Sign in'));
    await tester.pumpAndSettle();

    expect(find.text('Could not sign in. Check your email and password.'), findsOneWidget);
  });
}
