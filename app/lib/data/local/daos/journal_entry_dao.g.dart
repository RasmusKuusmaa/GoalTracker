// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'journal_entry_dao.dart';

// ignore_for_file: type=lint
mixin _$JournalEntryDaoMixin on DatabaseAccessor<AppDatabase> {
  $JournalEntriesTable get journalEntries => attachedDatabase.journalEntries;
  $JournalsTable get journals => attachedDatabase.journals;
  $CommitmentsTable get commitments => attachedDatabase.commitments;
  $CompletionsTable get completions => attachedDatabase.completions;
  JournalEntryDaoManager get managers => JournalEntryDaoManager(this);
}

class JournalEntryDaoManager {
  final _$JournalEntryDaoMixin _db;
  JournalEntryDaoManager(this._db);
  $$JournalEntriesTableTableManager get journalEntries =>
      $$JournalEntriesTableTableManager(
        _db.attachedDatabase,
        _db.journalEntries,
      );
  $$JournalsTableTableManager get journals =>
      $$JournalsTableTableManager(_db.attachedDatabase, _db.journals);
  $$CommitmentsTableTableManager get commitments =>
      $$CommitmentsTableTableManager(_db.attachedDatabase, _db.commitments);
  $$CompletionsTableTableManager get completions =>
      $$CompletionsTableTableManager(_db.attachedDatabase, _db.completions);
}
