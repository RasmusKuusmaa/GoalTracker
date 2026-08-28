// Local-date helpers mirroring `app/core/dates.py` on the backend. No date math
// belongs anywhere else in this app.

/// Today's date in the device's local timezone, truncated to midnight.
DateTime todayLocal() {
  final now = DateTime.now();
  return DateTime(now.year, now.month, now.day);
}

/// The ISO 8601 (year, week) for [date], per ISO 8601: the week containing a
/// year's first Thursday is week 1, so late-December/early-January dates can
/// belong to a week numbered under the adjacent year.
({int isoYear, int isoWeek}) isoWeekKey(DateTime date) {
  final day = DateTime(date.year, date.month, date.day);
  final thursday = day.add(Duration(days: 4 - day.weekday));
  final firstDayOfYear = DateTime(thursday.year, 1, 1);
  final dayOfYear = thursday.difference(firstDayOfYear).inDays + 1;
  final isoWeek = ((dayOfYear - 1) ~/ 7) + 1;
  return (isoYear: thursday.year, isoWeek: isoWeek);
}

/// The Monday-through-Sunday-ordered week containing [date], starting on
/// [weekStart] (ISO weekday: 1 = Monday .. 7 = Sunday).
({DateTime start, DateTime end}) weekBounds(DateTime date, int weekStart) {
  if (weekStart < 1 || weekStart > 7) {
    throw ArgumentError('weekStart must be between 1 (Monday) and 7 (Sunday)');
  }

  final day = DateTime(date.year, date.month, date.day);
  final offset = (day.weekday - weekStart) % 7;
  final start = day.subtract(Duration(days: offset));
  final end = start.add(const Duration(days: 6));
  return (start: start, end: end);
}
