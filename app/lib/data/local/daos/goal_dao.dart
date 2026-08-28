import 'package:drift/drift.dart';

import '../database.dart';
import '../tables.dart';

part 'goal_dao.g.dart';

@DriftAccessor(tables: [Goals])
class GoalDao extends DatabaseAccessor<AppDatabase> with _$GoalDaoMixin {
  GoalDao(super.db);

  Future<void> insert(GoalsCompanion entry) => into(goals).insert(entry);

  Future<void> updateGoal(String id, GoalsCompanion entry) =>
      (update(goals)..where((t) => t.id.equals(id))).write(entry);

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
    return (update(
      goals,
    )..where((t) => t.id.equals(id))).write(GoalsCompanion(deletedAt: Value(DateTime.now())));
  }
}
