// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'commitment_dao.dart';

// ignore_for_file: type=lint
mixin _$CommitmentDaoMixin on DatabaseAccessor<AppDatabase> {
  $CommitmentsTable get commitments => attachedDatabase.commitments;
  CommitmentDaoManager get managers => CommitmentDaoManager(this);
}

class CommitmentDaoManager {
  final _$CommitmentDaoMixin _db;
  CommitmentDaoManager(this._db);
  $$CommitmentsTableTableManager get commitments =>
      $$CommitmentsTableTableManager(_db.attachedDatabase, _db.commitments);
}
