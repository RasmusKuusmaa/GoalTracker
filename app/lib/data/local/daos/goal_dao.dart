import 'package:drift/drift.dart';

import '../database.dart';
import '../tables.dart';

part 'goal_dao.g.dart';

@DriftAccessor(tables: [Goals])
class GoalDao extends DatabaseAccessor<AppDatabase> with _$GoalDaoMixin {
  GoalDao(super.db);

  Future<void> insert(GoalsCompanion entry) => into(goals).insert(_stamped(entry));

  Future<void> updateGoal(String id, GoalsCompanion entry) =>
      (update(goals)..where((t) => t.id.equals(id))).write(_stamped(entry));

  Stream<List<Goal>> watchAll(String userId) {
    return (select(
      goals,
    )..where((t) => t.userId.equals(userId) & t.deletedAt.isNull())).watch();
  }

  Stream<List<Goal>> watchChildren(String userId, String? parentId) {
    final query = select(goals)
      ..where((t) => t.userId.equals(userId) & t.deletedAt.isNull());
    if (parentId == null) {
      query.where((t) => t.parentId.isNull());
    } else {
      query.where((t) => t.parentId.equals(parentId));
    }
    return query.watch();
  }

  Future<void> softDelete(String id) {
    return (update(goals)..where((t) => t.id.equals(id))).write(
      _stamped(GoalsCompanion(deletedAt: Value(DateTime.now()))),
    );
  }

  /// Every local write marks the row dirty and bumps `updatedAt`, so the sync
  /// service can find rows that still need to be pushed.
  GoalsCompanion _stamped(GoalsCompanion entry) {
    return entry.copyWith(dirty: const Value(true), updatedAt: Value(DateTime.now()));
  }
}
