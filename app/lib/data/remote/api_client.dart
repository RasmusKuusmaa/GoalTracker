import 'package:dio/dio.dart';

import '../../core/config.dart';

/// Thin wrapper around the shared [Dio] instance used for every backend call.
/// Auth interceptors are attached separately (see `auth_interceptors.dart`).
class ApiClient {
  ApiClient() : dio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl));

  final Dio dio;
}
