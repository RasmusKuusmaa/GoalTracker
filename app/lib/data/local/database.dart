import 'package:drift/drift.dart';
import 'package:drift_flutter/drift_flutter.dart';

import 'daos/goal_dao.dart';
import 'tables.dart';

part 'database.g.dart';

@DriftDatabase(
  tables: [Goals, Commitments, Completions, Journals, JournalEntries, SyncState],
  daos: [GoalDao],
)
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(driftDatabase(name: 'goal_tracker'));

  @override
  int get schemaVersion => 1;
}
