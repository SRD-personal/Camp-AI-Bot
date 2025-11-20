import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import '../models/user_model.dart';

class AuthService {
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
    serverClientId:
        '736642447930-4c56ipjloo1tj6tvodrmj5uomlccs4ic.apps.googleusercontent.com',
  );

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final Dio _dio = Dio();

  static const String _baseUrl =
      'https://kit-campusai-backend.onrender.com/api/v1';
  //static const String _baseUrl = 'http://localhost:8000/api/v1';
  // For Android emulator use: 'http://10.0.2.2:8000/api/v1'
  // For production use: 'https://kit-campusai-backend.onrender.com/api/v1'

  Future<UserModel?> signInWithGoogle() async {
    try {
      // Sign in with Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        return null; // User cancelled
      }

      // Get authentication
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;
      final String? idToken = googleAuth.idToken;

      if (idToken == null) {
        throw Exception('Failed to get ID token');
      }

      // Send to backend
      final response = await _dio.post(
        '$_baseUrl/auth/google',
        data: {
          'id_token': idToken,
          'user_data': {
            'email': googleUser.email,
            'name': googleUser.displayName,
            'picture': googleUser.photoUrl,
          },
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;

        // Store tokens
        await _storage.write(key: 'access_token', value: data['access_token']);
        await _storage.write(
          key: 'refresh_token',
          value: data['refresh_token'],
        );

        // Return user
        return UserModel.fromJson(data['user']);
      }

      throw Exception('Authentication failed');
    } catch (e) {
      print('Sign in error: $e');
      rethrow;
    }
  }

  Future<void> signOut() async {
    await _googleSignIn.signOut();
    await _storage.deleteAll();
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<bool> isSignedIn() async {
    final token = await getAccessToken();
    return token != null;
  }
}
