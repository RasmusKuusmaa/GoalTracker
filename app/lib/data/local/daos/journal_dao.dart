import 'package:drift/drift.dart';

import '../database.dart';
import '../tables.dart';

part 'journal_dao.g.dart';

@DriftAccessor(tables: [Journals])
class JournalDao extends DatabaseAccessor<AppDatabase> with _$JournalDaoMixin {
  JournalDao(super.db);

  Future<void> insert(JournalsCompanion entry) => into(journals).insert(_stamped(entry));

  Future<void> updateJournal(String id, JournalsCompanion entry) =>
      (update(journals)..where((t) => t.id.equals(id))).write(_stamped(entry));

  Stream<List<Journal>> watchAll(String userId) {
    return (select(
      journals,
    )..where((t) => t.userId.equals(userId) & t.deletedAt.isNull())).watch();
  }

  Future<void> softDelete(String id) {
    return (update(journals)..where((t) => t.id.equals(id))).write(
      _stamped(JournalsCompanion(deletedAt: Value(DateTime.now()))),
    );
  }

  /// Every local write marks the row dirty and bumps `updatedAt`, so the sync
  /// service can find rows that still need to be pushed.
  JournalsCompanion _stamped(JournalsCompanion entry) {
    return entry.copyWith(dirty: const Value(true), updatedAt: Value(DateTime.now()));
  }
}
