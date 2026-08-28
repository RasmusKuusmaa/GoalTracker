import 'package:drift/drift.dart';

// Local mirrors of the backend's synced tables (see GT-backend/app/models), plus a
// local-only `dirty` flag marking rows with unpushed changes. Enum-like fields are
// stored as plain text; conversion to the app's enum types happens at the DAO boundary.

class Goals extends Table {
  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get parentId => text().nullable()();
  TextColumn get title => text()();
  TextColumn get description => text().nullable()();
  DateTimeColumn get targetDate => dateTime().nullable()();
  TextColumn get status => text().withDefault(const Constant('active'))();
  DateTimeColumn get completedAt => dateTime().nullable()();
  IntColumn get sortOrder => integer().withDefault(const Constant(0))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();
  BoolColumn get dirty => boolean().withDefault(const Constant(true))();

  @override
  Set<Column> get primaryKey => {id};
}

class Completions extends Table {
  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get commitmentId => text()();
  DateTimeColumn get localDate => dateTime()();
  TextColumn get status => text()();
  RealColumn get value => real().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();
  BoolColumn get dirty => boolean().withDefault(const Constant(true))();

  @override
  Set<Column> get primaryKey => {id};

  @override
  List<Set<Column>> get uniqueKeys => [
    {commitmentId, localDate},
  ];
}

class Commitments extends Table {
  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get goalId => text().nullable()();
  TextColumn get journalId => text().nullable()();
  TextColumn get title => text()();
  TextColumn get type => text()();
  TextColumn get cadence => text()();
  IntColumn get targetCount => integer().nullable()();
  RealColumn get targetValue => real().nullable()();
  TextColumn get comparator => text().nullable()();
  TextColumn get unit => text().nullable()();
  DateTimeColumn get activeFrom => dateTime()();
  DateTimeColumn get activeUntil => dateTime().nullable()();
  DateTimeColumn get archivedAt => dateTime().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();
  BoolColumn get dirty => boolean().withDefault(const Constant(true))();

  @override
  Set<Column> get primaryKey => {id};
}

class Journals extends Table {
  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get name => text()();
  TextColumn get kind => text()();
  TextColumn get unit => text().nullable()();
  IntColumn get sortOrder => integer().withDefault(const Constant(0))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();
  BoolColumn get dirty => boolean().withDefault(const Constant(true))();

  @override
  Set<Column> get primaryKey => {id};
}
