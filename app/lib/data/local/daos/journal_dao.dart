import 'package:drift/drift.dart';

import '../database.dart';
import '../tables.dart';

part 'journal_dao.g.dart';

@DriftAccessor(tables: [Journals])
class JournalDao extends DatabaseAccessor<AppDatabase> with _$JournalDaoMixin {
  JournalDao(super.db);

  Future<void> insert(JournalsCompanion entry) => into(journals).insert(entry);

  Future<void> updateJournal(String id, JournalsCompanion entry) =>
      (update(journals)..where((t) => t.id.equals(id))).write(entry);

  Stream<List<Journal>> watchAll(String userId) {
    return (select(
      journals,
    )..where((t) => t.userId.equals(userId) & t.deletedAt.isNull())).watch();
  }

  Future<void> softDelete(String id) {
    return (update(journals)..where((t) => t.id.equals(id))).write(
      JournalsCompanion(deletedAt: Value(DateTime.now())),
    );
  }
}
