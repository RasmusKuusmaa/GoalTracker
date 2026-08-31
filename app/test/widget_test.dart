import 'package:app/data/remote/auth_api.dart';
import 'package:app/data/remote/token_store.dart';
import 'package:app/features/auth/auth_providers.dart';
import 'package:app/main.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _NoSessionTokenStore implements TokenStore {
  @override
  Future<String?> readAccessToken() async => null;

  @override
  Future<String?> readRefreshToken() async => null;

  @override
  Future<void> saveTokens(TokenPair tokens) async {}

  @override
  Future<void> clear() async {}
}

void main() {
  testWidgets('shows the sign-in screen on a fresh, signed-out launch', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [tokenStoreProvider.overrideWithValue(_NoSessionTokenStore())],
        child: const GoalTrackerApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Sign in'), findsWidgets);
  });
}
