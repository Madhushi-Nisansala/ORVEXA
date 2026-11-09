import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import 'memory.dart';

class MemoryRepository {
  MemoryRepository(this._client);
  final ApiClient _client;
  Dio get _dio => _client.dio;

  Future<List<Memory>> list({String? search, String? category, bool activeOnly = true}) async {
	final response = await _dio.get<List<dynamic>>('/api/v1/memory', queryParameters: {
	  'active_only': activeOnly,
	  if (search != null && search.trim().isNotEmpty) 'search': search.trim(),
	  if (category != null && category.isNotEmpty) 'category': category,
	});
	return (response.data ?? const []).map((item) => Memory.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<Memory> create({required String title, required String category, required String text}) async {
	final response = await _dio.post<Map<String, dynamic>>('/api/v1/memory', data: {
	  'title': title,
	  'category': category,
	  'content': {'text': text},
	});
	return Memory.fromJson(response.data!);
  }

  Future<Memory> update(String id, {String? title, String? category, String? text}) async {
	final data = <String, dynamic>{};
	if (title != null) data['title'] = title;
	if (category != null) data['category'] = category;
	if (text != null) data['content'] = {'text': text};
	final response = await _dio.patch<Map<String, dynamic>>('/api/v1/memory/$id', data: {
	  ...data,
	});
	return Memory.fromJson(response.data!);
  }

  Future<void> archive(String id) => _dio.post<void>('/api/v1/memory/$id/archive');
  Future<void> delete(String id) => _dio.delete<void>('/api/v1/memory/$id/permanent');
}
