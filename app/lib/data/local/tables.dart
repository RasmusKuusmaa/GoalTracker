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
