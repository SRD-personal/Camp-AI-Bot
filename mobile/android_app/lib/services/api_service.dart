import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/message_model.dart';

class ApiService {
  final Dio _dio = Dio();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  static const String _baseUrl = 'http://localhost:8000/api/v1';
  // For Android emulator use: 'http://10.0.2.2:8000/api/v1'
  
  ApiService() {
    _dio.options.baseUrl = _baseUrl;
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: 'access_token');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
      ),
    );
  }
  
  Future<Map<String, dynamic>> sendQuery(String query, {String? conversationId}) async {
    try {
      final response = await _dio.post(
        '/chat/query',
        data: {
          'query': query,
          'conversation_id': conversationId,
        },
      );
      
      return response.data;
    } catch (e) {
      print('Query error: $e');
      rethrow;
    }
  }
  
  Future<List<MessageModel>> getChatHistory(String conversationId) async {
    try {
      final response = await _dio.get('/chat/history/$conversationId');
      final messages = (response.data['messages'] as List)
          .map((m) => MessageModel.fromJson(m))
          .toList();
      
      return messages;
    } catch (e) {
      print('Get history error: $e');
      rethrow;
    }
  }
  
  Future<List<Map<String, dynamic>>> getChatSessions() async {
    try {
      final response = await _dio.get('/chat/sessions');
      return List<Map<String, dynamic>>.from(response.data['sessions']);
    } catch (e) {
      print('Get sessions error: $e');
      rethrow;
    }
  }
}
