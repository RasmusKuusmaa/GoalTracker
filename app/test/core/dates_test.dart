import 'package:app/core/dates.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('todayLocal', () {
    test('truncates to midnight', () {
      final today = todayLocal();

      expect(today.hour, 0);
      expect(today.minute, 0);
      expect(today.second, 0);
    });
  });

  group('isoWeekKey', () {
    test('regular date', () {
      final key = isoWeekKey(DateTime(2024, 1, 1));
      expect(key.isoYear, 2024);
      expect(key.isoWeek, 1);
    });

    test('year rolls backward at start of year', () {
      // 2023-01-01 is a Sunday, part of ISO week 52 of the *previous* ISO year.
      final key = isoWeekKey(DateTime(2023, 1, 1));
      expect(key.isoYear, 2022);
      expect(key.isoWeek, 52);
    });

    test('week 53', () {
      final key = isoWeekKey(DateTime(2020, 12, 31));
      expect(key.isoYear, 2020);
      expect(key.isoWeek, 53);
    });

    test('year rolls forward into next year\'s week 53', () {
      // 2021-01-01 is a Friday, still part of ISO week 53 of 2020.
      final key = isoWeekKey(DateTime(2021, 1, 1));
      expect(key.isoYear, 2020);
      expect(key.isoWeek, 53);
    });
  });

  group('weekBounds', () {
    test('monday start', () {
      final bounds = weekBounds(DateTime(2024, 1, 10), 1);
      expect(bounds.start, DateTime(2024, 1, 8));
      expect(bounds.end, DateTime(2024, 1, 14));
    });

    test('sunday start', () {
      final bounds = weekBounds(DateTime(2024, 1, 10), 7);
      expect(bounds.start, DateTime(2024, 1, 7));
      expect(bounds.end, DateTime(2024, 1, 13));
    });

    test('on boundary day', () {
      final bounds = weekBounds(DateTime(2024, 1, 8), 1);
      expect(bounds.start, DateTime(2024, 1, 8));
      expect(bounds.end, DateTime(2024, 1, 14));
    });

    test('rejects invalid week start', () {
      expect(() => weekBounds(DateTime(2024, 1, 10), 0), throwsArgumentError);
    });
  });
}
