import 'package:app/core/ids.dart';
import 'package:app/data/local/database.dart';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late AppDatabase db;
  const userId = 'user-1';

  setUp(() {
    db = AppDatabase.forTesting(NativeDatabase.memory());
  });

  tearDown(() => db.close());

  group('GoalDao', () {
    test('insert then watchAll returns the goal, marked dirty', () async {
      final id = newId();
      await db.goalDao.insert(
        GoalsCompanion.insert(
          id: id,
          userId: userId,
          title: 'Learn Rust',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ),
      );

      final goals = await db.goalDao.watchAll(userId).first;

      expect(goals, hasLength(1));
      expect(goals.single.title, 'Learn Rust');
      expect(goals.single.dirty, isTrue);
    });

    test('watchChildren filters by parentId', () async {
      final parentId = newId();
      final childId = newId();
      final now = DateTime.now();
      await db.goalDao.insert(
        GoalsCompanion.insert(
          id: parentId,
          userId: userId,
          title: 'Parent',
          createdAt: now,
          updatedAt: now,
        ),
      );
      await db.goalDao.insert(
        GoalsCompanion.insert(
          id: childId,
          userId: userId,
          title: 'Child',
          parentId: Value(parentId),
          createdAt: now,
          updatedAt: now,
        ),
      );

      final roots = await db.goalDao.watchChildren(userId, null).first;
      final children = await db.goalDao.watchChildren(userId, parentId).first;

      expect(roots.map((g) => g.id), [parentId]);
      expect(children.map((g) => g.id), [childId]);
    });

    test('updateGoal bumps updatedAt and sets dirty', () async {
      final id = newId();
      final createdAt = DateTime.now().subtract(const Duration(days: 1));
      await db.goalDao.insert(
        GoalsCompanion.insert(
          id: id,
          userId: userId,
          title: 'Original',
          createdAt: createdAt,
          updatedAt: createdAt,
        ),
      );

      await db.goalDao.updateGoal(id, const GoalsCompanion(title: Value('Renamed')));

      final goal = (await db.goalDao.watchAll(userId).first).single;
      expect(goal.title, 'Renamed');
      expect(goal.dirty, isTrue);
      expect(goal.updatedAt.isAfter(createdAt), isTrue);
    });

    test('softDelete excludes the goal from watchAll', () async {
      final id = newId();
      final now = DateTime.now();
      await db.goalDao.insert(
        GoalsCompanion.insert(id: id, userId: userId, title: 'Gone', createdAt: now, updatedAt: now),
      );

      await db.goalDao.softDelete(id);

      final goals = await db.goalDao.watchAll(userId).first;
      expect(goals, isEmpty);
    });
  });

  group('CommitmentDao', () {
    test('watchActive excludes archived and deleted commitments', () async {
      final activeId = newId();
      final archivedId = newId();
      final now = DateTime.now();
      for (final id in [activeId, archivedId]) {
        await db.commitmentDao.insert(
          CommitmentsCompanion.insert(
            id: id,
            userId: userId,
            title: 'Gym',
            type: 'binary',
            cadence: 'daily',
            activeFrom: now,
            createdAt: now,
            updatedAt: now,
          ),
        );
      }
      await db.commitmentDao.archive(archivedId);

      final active = await db.commitmentDao.watchActive(userId).first;

      expect(active.map((c) => c.id), [activeId]);
    });

    test('softDelete excludes the commitment from watchActive', () async {
      final id = newId();
      final now = DateTime.now();
      await db.commitmentDao.insert(
        CommitmentsCompanion.insert(
          id: id,
          userId: userId,
          title: 'Gym',
          type: 'binary',
          cadence: 'daily',
          activeFrom: now,
          createdAt: now,
          updatedAt: now,
        ),
      );

      await db.commitmentDao.softDelete(id);

      final active = await db.commitmentDao.watchActive(userId).first;
      expect(active, isEmpty);
    });
  });

  group('CompletionDao', () {
    late String commitmentId;

    setUp(() async {
      commitmentId = newId();
      final now = DateTime.now();
      await db.commitmentDao.insert(
        CommitmentsCompanion.insert(
          id: commitmentId,
          userId: userId,
          title: 'Gym',
          type: 'binary',
          cadence: 'daily',
          activeFrom: now,
          createdAt: now,
          updatedAt: now,
        ),
      );
    });

    test('upsert twice for the same day updates the same row', () async {
      final day = DateTime(2026, 1, 2);

      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: day,
        status: 'done',
      );
      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: day,
        status: 'done',
      );

      final rows = await db.completionDao.watchForDate(userId, day).first;
      expect(rows, hasLength(1));
    });

    test('softDelete then upsert again reuses the same row id', () async {
      final day = DateTime(2026, 1, 2);
      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: day,
        status: 'done',
      );
      final firstId = (await db.completionDao.watchForDate(userId, day).first).single.id;

      await db.completionDao.softDelete(firstId);
      expect(await db.completionDao.watchForDate(userId, day).first, isEmpty);

      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: day,
        status: 'done',
      );
      final secondId = (await db.completionDao.watchForDate(userId, day).first).single.id;

      expect(secondId, firstId);
    });

    test('watchForRange returns completions within the date range', () async {
      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: DateTime(2026, 1, 2),
        status: 'done',
      );
      await db.completionDao.upsert(
        userId: userId,
        commitmentId: commitmentId,
        localDate: DateTime(2026, 2, 1),
        status: 'done',
      );

      final inRange = await db.completionDao
          .watchForRange(userId, DateTime(2026, 1, 1), DateTime(2026, 1, 31))
          .first;

      expect(inRange, hasLength(1));
      expect(inRange.single.localDate, DateTime(2026, 1, 2));
    });
  });

  group('JournalDao', () {
    test('insert then watchAll returns the journal', () async {
      final id = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: id,
          userId: userId,
          name: 'General',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );

      final journals = await db.journalDao.watchAll(userId).first;

      expect(journals.map((j) => j.id), [id]);
    });

    test('softDelete excludes the journal from watchAll', () async {
      final id = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: id,
          userId: userId,
          name: 'General',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );

      await db.journalDao.softDelete(id);

      expect(await db.journalDao.watchAll(userId).first, isEmpty);
    });
  });

  group('JournalEntryDao', () {
    test('upsert twice for the same day updates the same row', () async {
      final journalId = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: journalId,
          userId: userId,
          name: 'General',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );
      final day = DateTime(2026, 1, 2);

      await db.journalEntryDao.upsert(
        userId: userId,
        journalId: journalId,
        localDate: day,
        body: 'first',
      );
      await db.journalEntryDao.upsert(
        userId: userId,
        journalId: journalId,
        localDate: day,
        body: 'second',
      );

      final rows = await db.journalEntryDao.watchForDate(userId, day).first;
      expect(rows, hasLength(1));
      expect(rows.single.body, 'second');
    });

    test('a present entry upserts a done completion on the linked commitment', () async {
      final journalId = newId();
      final commitmentId = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: journalId,
          userId: userId,
          name: 'School',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );
      await db.commitmentDao.insert(
        CommitmentsCompanion.insert(
          id: commitmentId,
          userId: userId,
          title: 'Write in school journal',
          type: 'journal',
          cadence: 'daily',
          journalId: Value(journalId),
          activeFrom: now,
          createdAt: now,
          updatedAt: now,
        ),
      );
      final day = DateTime(2026, 1, 2);

      await db.journalEntryDao.upsert(
        userId: userId,
        journalId: journalId,
        localDate: day,
        body: 'Today I learned Dart.',
      );

      final completions = await db.completionDao.watchForDate(userId, day).first;
      expect(completions, hasLength(1));
      expect(completions.single.commitmentId, commitmentId);
      expect(completions.single.status, 'done');
    });

    test('clearing an entry back to empty soft-deletes the linked completion', () async {
      final journalId = newId();
      final commitmentId = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: journalId,
          userId: userId,
          name: 'School',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );
      await db.commitmentDao.insert(
        CommitmentsCompanion.insert(
          id: commitmentId,
          userId: userId,
          title: 'Write in school journal',
          type: 'journal',
          cadence: 'daily',
          journalId: Value(journalId),
          activeFrom: now,
          createdAt: now,
          updatedAt: now,
        ),
      );
      final day = DateTime(2026, 1, 2);
      await db.journalEntryDao.upsert(
        userId: userId,
        journalId: journalId,
        localDate: day,
        body: 'Present',
      );
      expect(await db.completionDao.watchForDate(userId, day).first, hasLength(1));

      await db.journalEntryDao.upsert(userId: userId, journalId: journalId, localDate: day);

      expect(await db.completionDao.watchForDate(userId, day).first, isEmpty);
    });

    test('deleting the entry soft-deletes the linked completion', () async {
      final journalId = newId();
      final commitmentId = newId();
      final now = DateTime.now();
      await db.journalDao.insert(
        JournalsCompanion.insert(
          id: journalId,
          userId: userId,
          name: 'School',
          kind: 'text',
          createdAt: now,
          updatedAt: now,
        ),
      );
      await db.commitmentDao.insert(
        CommitmentsCompanion.insert(
          id: commitmentId,
          userId: userId,
          title: 'Write in school journal',
          type: 'journal',
          cadence: 'daily',
          journalId: Value(journalId),
          activeFrom: now,
          createdAt: now,
          updatedAt: now,
        ),
      );
      final day = DateTime(2026, 1, 2);
      await db.journalEntryDao.upsert(
        userId: userId,
        journalId: journalId,
        localDate: day,
        body: 'Present',
      );
      final entryId = (await db.journalEntryDao.watchForDate(userId, day).first).single.id;

      await db.journalEntryDao.softDelete(entryId);

      expect(await db.completionDao.watchForDate(userId, day).first, isEmpty);
    });
  });
}
