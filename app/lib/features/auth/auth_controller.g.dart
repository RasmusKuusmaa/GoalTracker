// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// `state.value == null` means signed out; a non-null [UserProfile] means
/// signed in. Loading/error are the ordinary [AsyncValue] states, covering
/// both the initial session bootstrap and in-flight login/register calls.

@ProviderFor(AuthController)
final authControllerProvider = AuthControllerProvider._();

/// `state.value == null` means signed out; a non-null [UserProfile] means
/// signed in. Loading/error are the ordinary [AsyncValue] states, covering
/// both the initial session bootstrap and in-flight login/register calls.
final class AuthControllerProvider
    extends $AsyncNotifierProvider<AuthController, UserProfile?> {
  /// `state.value == null` means signed out; a non-null [UserProfile] means
  /// signed in. Loading/error are the ordinary [AsyncValue] states, covering
  /// both the initial session bootstrap and in-flight login/register calls.
  AuthControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authControllerHash();

  @$internal
  @override
  AuthController create() => AuthController();
}

String _$authControllerHash() => r'f149ec4e5c8fec5b714cc6c8977952fd5f8369eb';

/// `state.value == null` means signed out; a non-null [UserProfile] means
/// signed in. Loading/error are the ordinary [AsyncValue] states, covering
/// both the initial session bootstrap and in-flight login/register calls.

abstract class _$AuthController extends $AsyncNotifier<UserProfile?> {
  FutureOr<UserProfile?> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<AsyncValue<UserProfile?>, UserProfile?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<UserProfile?>, UserProfile?>,
              AsyncValue<UserProfile?>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}
