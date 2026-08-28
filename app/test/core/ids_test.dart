import 'package:app/core/ids.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('newId returns distinct v4 uuids', () {
    final a = newId();
    final b = newId();

    final uuidV4Pattern = RegExp(
      r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    );
    expect(a, matches(uuidV4Pattern));
    expect(b, matches(uuidV4Pattern));
    expect(a, isNot(equals(b)));
  });
}
