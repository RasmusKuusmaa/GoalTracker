import 'package:dio/dio.dart';

import '../../core/config.dart';
import 'auth_interceptors.dart';

/// Thin wrapper around the shared [Dio] instance used for every backend call.
class ApiClient {
  ApiClient({required TokenReader getAccessToken, required TokenRefresher refreshAccessToken})
    : dio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl)) {
    dio.interceptors.add(AuthHeaderInterceptor(getAccessToken));
    dio.interceptors.add(
      RefreshOnUnauthorizedInterceptor(dio: dio, refreshAccessToken: refreshAccessToken),
    );
  }

  final Dio dio;
}
