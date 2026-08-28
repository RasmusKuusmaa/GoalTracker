import 'package:drift/drift.dart';

import '../database.dart';
import '../tables.dart';

part 'commitment_dao.g.dart';

@DriftAccessor(tables: [Commitments])
class CommitmentDao extends DatabaseAccessor<AppDatabase> with _$CommitmentDaoMixin {
  CommitmentDao(super.db);

  Future<void> insert(CommitmentsCompanion entry) => into(commitments).insert(_stamped(entry));

  Future<void> updateCommitment(String id, CommitmentsCompanion entry) =>
      (update(commitments)..where((t) => t.id.equals(id))).write(_stamped(entry));

  Stream<List<Commitment>> watchActive(String userId) {
    return (select(commitments)..where(
          (t) => t.userId.equals(userId) & t.deletedAt.isNull() & t.archivedAt.isNull(),
        ))
        .watch();
  }

  Future<void> archive(String id) {
    return (update(commitments)..where((t) => t.id.equals(id))).write(
      _stamped(CommitmentsCompanion(archivedAt: Value(DateTime.now()))),
    );
  }

  Future<void> softDelete(String id) {
    return (update(commitments)..where((t) => t.id.equals(id))).write(
      _stamped(CommitmentsCompanion(deletedAt: Value(DateTime.now()))),
    );
  }

  /// Every local write marks the row dirty and bumps `updatedAt`, so the sync
  /// service can find rows that still need to be pushed.
  CommitmentsCompanion _stamped(CommitmentsCompanion entry) {
    return entry.copyWith(dirty: const Value(true), updatedAt: Value(DateTime.now()));
  }
}
