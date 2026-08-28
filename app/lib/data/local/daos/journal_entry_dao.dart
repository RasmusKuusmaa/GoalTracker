import 'package:drift/drift.dart';

import '../../../core/ids.dart';
import '../database.dart';
import '../tables.dart';

part 'journal_entry_dao.g.dart';

@DriftAccessor(tables: [JournalEntries, Journals, Commitments, Completions])
class JournalEntryDao extends DatabaseAccessor<AppDatabase> with _$JournalEntryDaoMixin {
  JournalEntryDao(super.db);

  Future<void> upsert({
    required String userId,
    required String journalId,
    required DateTime localDate,
    String? body,
    double? value,
  }) async {
    final existing = await (select(journalEntries)..where(
          (t) => t.journalId.equals(journalId) & t.localDate.equals(localDate),
        ))
        .getSingleOrNull();

    final now = DateTime.now();
    if (existing == null) {
      await into(journalEntries).insert(
        JournalEntriesCompanion.insert(
          id: newId(),
          userId: userId,
          journalId: journalId,
          localDate: localDate,
          body: Value(body),
          value: Value(value),
          createdAt: now,
          updatedAt: now,
        ),
      );
    } else {
      await (update(journalEntries)..where((t) => t.id.equals(existing.id))).write(
        JournalEntriesCompanion(
          body: Value(body),
          value: Value(value),
          updatedAt: Value(now),
          deletedAt: const Value(null),
          dirty: const Value(true),
        ),
      );
    }

    await _syncLinkedCompletions(userId: userId, journalId: journalId, localDate: localDate);
  }

  Stream<List<JournalEntry>> watchForDate(String userId, DateTime localDate) {
    return (select(journalEntries)..where(
          (t) =>
              t.userId.equals(userId) &
              t.localDate.equals(localDate) &
              t.deletedAt.isNull(),
        ))
        .watch();
  }

  Stream<List<JournalEntry>> watchForRange(String userId, DateTime from, DateTime to) {
    return (select(journalEntries)..where(
          (t) =>
              t.userId.equals(userId) &
              t.localDate.isBiggerOrEqualValue(from) &
              t.localDate.isSmallerOrEqualValue(to) &
              t.deletedAt.isNull(),
        ))
        .watch();
  }

  Future<void> softDelete(String id) async {
    final entry = await (select(
      journalEntries,
    )..where((t) => t.id.equals(id))).getSingleOrNull();
    if (entry == null) return;

    await (update(journalEntries)..where((t) => t.id.equals(id))).write(
      JournalEntriesCompanion(deletedAt: Value(DateTime.now()), dirty: const Value(true)),
    );

    await _syncLinkedCompletions(
      userId: entry.userId,
      journalId: entry.journalId,
      localDate: entry.localDate,
    );
  }

  /// Keeps every `type = journal` commitment linked to [journalId] in sync with
  /// whether it has a present entry for [localDate] (see domain spec: a completion
  /// upserted from a present journal entry, or soft-deleted when the entry is
  /// cleared or removed).
  Future<void> _syncLinkedCompletions({
    required String userId,
    required String journalId,
    required DateTime localDate,
  }) async {
    final journal = await (select(
      journals,
    )..where((t) => t.id.equals(journalId))).getSingleOrNull();
    if (journal == null) return;

    final entry = await (select(journalEntries)..where(
          (t) => t.journalId.equals(journalId) & t.localDate.equals(localDate),
        ))
        .getSingleOrNull();
    final isPresent = entry != null && entry.deletedAt == null && _isPresent(journal, entry);

    final linkedCommitments = await (select(commitments)..where(
          (t) =>
              t.journalId.equals(journalId) &
              t.type.equals('journal') &
              t.deletedAt.isNull(),
        ))
        .get();

    for (final commitment in linkedCommitments) {
      if (isPresent) {
        await _upsertCompletion(userId: userId, commitmentId: commitment.id, localDate: localDate);
      } else {
        await _softDeleteCompletionFor(commitmentId: commitment.id, localDate: localDate);
      }
    }
  }

  bool _isPresent(Journal journal, JournalEntry entry) {
    return journal.kind == 'numeric' ? entry.value != null : (entry.body?.isNotEmpty ?? false);
  }

  Future<void> _upsertCompletion({
    required String userId,
    required String commitmentId,
    required DateTime localDate,
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
          status: 'done',
          createdAt: now,
          updatedAt: now,
        ),
      );
    } else {
      await (update(completions)..where((t) => t.id.equals(existing.id))).write(
        CompletionsCompanion(
          status: const Value('done'),
          updatedAt: Value(now),
          deletedAt: const Value(null),
          dirty: const Value(true),
        ),
      );
    }
  }

  Future<void> _softDeleteCompletionFor({
    required String commitmentId,
    required DateTime localDate,
  }) async {
    final existing = await (select(completions)..where(
          (t) =>
              t.commitmentId.equals(commitmentId) &
              t.localDate.equals(localDate) &
              t.deletedAt.isNull(),
        ))
        .getSingleOrNull();
    if (existing == null) return;

    await (update(completions)..where((t) => t.id.equals(existing.id))).write(
      CompletionsCompanion(deletedAt: Value(DateTime.now()), dirty: const Value(true)),
    );
  }
}
