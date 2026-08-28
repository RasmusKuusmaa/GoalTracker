/// App-wide configuration. `apiBaseUrl` is a compile-time value so it can be
/// overridden per build without checking secrets into source, e.g.:
/// `flutter run --dart-define=API_BASE_URL=https://api.example.com`.
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
}
