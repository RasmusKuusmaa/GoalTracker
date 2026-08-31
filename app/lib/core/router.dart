import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_controller.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';

const loginPath = '/login';
const registerPath = '/register';
const homePath = '/';

/// Notifies [GoRouter] to re-run `redirect` on every auth state change,
/// without rebuilding the router itself — recreating a [GoRouter] on each
/// state change (e.g. by `ref.watch`-ing inside the provider) would drop its
/// internal navigation state.
class _AuthRefreshNotifier extends ChangeNotifier {
  _AuthRefreshNotifier(Ref ref) {
    ref.listen(authControllerProvider, (_, _) => notifyListeners());
  }
}

final routerProvider = Provider<GoRouter>((ref) {
  final refreshNotifier = _AuthRefreshNotifier(ref);
  ref.onDispose(refreshNotifier.dispose);

  return GoRouter(
    initialLocation: homePath,
    refreshListenable: refreshNotifier,
    redirect: (context, state) {
      final isSignedIn = ref.read(authControllerProvider).value != null;
      final isAuthRoute = state.matchedLocation == loginPath || state.matchedLocation == registerPath;

      if (!isSignedIn && !isAuthRoute) return loginPath;
      if (isSignedIn && isAuthRoute) return homePath;
      return null;
    },
    routes: [
      GoRoute(path: loginPath, builder: (context, state) => const LoginScreen()),
      GoRoute(path: registerPath, builder: (context, state) => const RegisterScreen()),
      // Replaced by the real Today screen once it exists (Phase 10).
      GoRoute(path: homePath, builder: (context, state) => const _HomePlaceholder()),
    ],
  );
});

class _HomePlaceholder extends StatelessWidget {
  const _HomePlaceholder();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: Text('Signed in')));
  }
}
