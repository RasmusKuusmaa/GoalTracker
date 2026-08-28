import 'package:dio/dio.dart';

/// Mirrors the backend's `TokenPair` schema (`app/schemas/auth.py`).
class TokenPair {
  TokenPair({required this.accessToken, required this.refreshToken});

  factory TokenPair.fromJson(Map<String, dynamic> json) => TokenPair(
    accessToken: json['access_token'] as String,
    refreshToken: json['refresh_token'] as String,
  );

  final String accessToken;
  final String refreshToken;
}

/// Mirrors the backend's `UserRead` schema (`app/schemas/user.py`).
class UserProfile {
  UserProfile({
    required this.id,
    required this.email,
    required this.displayName,
    required this.timezone,
    required this.weekStart,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
    id: json['id'] as String,
    email: json['email'] as String,
    displayName: json['display_name'] as String,
    timezone: json['timezone'] as String,
    weekStart: json['week_start'] as int,
    createdAt: DateTime.parse(json['created_at'] as String),
    updatedAt: DateTime.parse(json['updated_at'] as String),
  );

  final String id;
  final String email;
  final String displayName;
  final String timezone;
  final int weekStart;
  final DateTime createdAt;
  final DateTime updatedAt;
}

/// Wraps `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` and
/// `GET /auth/me`.
class AuthApi {
  AuthApi(this._dio);

  final Dio _dio;

  Future<TokenPair> register({
    required String email,
    required String password,
    required String displayName,
    required String timezone,
    int weekStart = 1,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/register',
      data: {
        'email': email,
        'password': password,
        'display_name': displayName,
        'timezone': timezone,
        'week_start': weekStart,
      },
    );
    return TokenPair.fromJson(response.data!);
  }

  Future<TokenPair> login({required String email, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    return TokenPair.fromJson(response.data!);
  }

  Future<TokenPair> refresh(String refreshToken) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    return TokenPair.fromJson(response.data!);
  }

  Future<UserProfile> me() async {
    final response = await _dio.get<Map<String, dynamic>>('/auth/me');
    return UserProfile.fromJson(response.data!);
  }
}
