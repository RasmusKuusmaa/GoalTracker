import 'package:uuid/uuid.dart';

const _uuid = Uuid();

/// A client-generated UUIDv4, used as the primary key for every synced entity.
String newId() => _uuid.v4();
