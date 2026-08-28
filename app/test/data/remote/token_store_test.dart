import 'package:app/data/remote/auth_api.dart';
import 'package:app/data/remote/token_store.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  test('reads null before anything is saved', () async {
    final store = TokenStore();

    expect(await store.readAccessToken(), isNull);
    expect(await store.readRefreshToken(), isNull);
  });

  test('saveTokens persists both tokens for later reads', () async {
    final store = TokenStore();

    await store.saveTokens(TokenPair(accessToken: 'access-1', refreshToken: 'refresh-1'));

    expect(await store.readAccessToken(), 'access-1');
    expect(await store.readRefreshToken(), 'refresh-1');
  });

  test('clear removes both tokens', () async {
    final store = TokenStore();
    await store.saveTokens(TokenPair(accessToken: 'access-1', refreshToken: 'refresh-1'));

    await store.clear();

    expect(await store.readAccessToken(), isNull);
    expect(await store.readRefreshToken(), isNull);
  });
}
