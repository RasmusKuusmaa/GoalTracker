import 'package:drift/drift.dart';

import '../../../core/ids.dart';
import '../database.dart';
import '../tables.dart';

part 'completion_dao.g.dart';

@DriftAccessor(tables: [Completions])
class CompletionDao extends DatabaseAccessor<AppDatabase> with _$CompletionDaoMixin {
  CompletionDao(super.db);

  Future<void> upsert({
    required String userId,
    required String commitmentId,
    required DateTime localDate,
    required String status,
    double? value,
  }) async {
    final existing = await (select(completions)..where(
          (t) => t.commitmentId.equals(commitmentId) & t.localDate.equals(localDate),
        ))
        .getSingleOrNull();

    final now = DateTime.now();
    if (existing == null) {
      await into(completions).insert(
        CompletionsCompanion.insert(
          id: newId(),
          userId: userId,
          commitmentId: commitmentId,
          localDate: localDate,
          status: status,
          value: Value(value),
          createdAt: now,
          updatedAt: now,
        ),
      );
      return;
    }

    await (update(completions)..where((t) => t.id.equals(existing.id))).write(
      CompletionsCompanion(
        status: Value(status),
        value: Value(value),
        updatedAt: Value(now),
        deletedAt: const Value(null),
        dirty: const Value(true),
      ),
    );
  }

  Stream<List<Completion>> watchForDate(String userId, DateTime localDate) {
    return (select(completions)..where(
          (t) =>
              t.userId.equals(userId) &
              t.localDate.equals(localDate) &
              t.deletedAt.isNull(),
        ))
        .watch();
  }

  Stream<List<Completion>> watchForRange(String userId, DateTime from, DateTime to) {
    return (select(completions)..where(
          (t) =>
              t.userId.equals(userId) &
              t.localDate.isBiggerOrEqualValue(from) &
              t.localDate.isSmallerOrEqualValue(to) &
              t.deletedAt.isNull(),
        ))
        .watch();
  }

  Future<void> softDelete(String id) {
    return (update(completions)..where((t) => t.id.equals(id))).write(
      CompletionsCompanion(deletedAt: Value(DateTime.now()), dirty: const Value(true)),
    );
  }
}
