import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import 'task.dart';

class TasksRepository {
  TasksRepository(this._client);
  final ApiClient _client;
  Dio get _dio => _client.dio;

  Future<TaskPage> list({String? search, String? status, String? priority, int limit = 50, int offset = 0, String sortBy = 'created_at', bool descending = true}) async {
	final response = await _dio.get<List<dynamic>>('/api/v1/tasks', queryParameters: {
	  'limit': limit,
	  'offset': offset,
	  if (search != null && search.trim().isNotEmpty) 'search': search.trim(),
	  if (status != null) 'status': status,
	  if (priority != null) 'priority': priority,
	  'sort_by': sortBy,
	  'sort_order': descending ? 'desc' : 'asc',
	});
	return TaskPage(
	  items: (response.data ?? const []).map((item) => Task.fromJson(item as Map<String, dynamic>)).toList(),
	  total: int.tryParse(response.headers.value('x-total-count') ?? '') ?? (response.data?.length ?? 0),
	);
  }

  Future<Task> get(String id) async {
	final response = await _dio.get<Map<String, dynamic>>('/api/v1/tasks/$id');
	return Task.fromJson(response.data!);
  }

  Future<Task> create({required String title, String? description, String priority = 'medium', DateTime? dueAt}) async {
	final response = await _dio.post<Map<String, dynamic>>('/api/v1/tasks', data: {
	  'title': title,
	  if (description != null && description.isNotEmpty) 'description': description,
	  'priority': priority,
	  if (dueAt != null) 'due_at': dueAt.toUtc().toIso8601String(),
	});
	return Task.fromJson(response.data!);
  }

  Future<Task> update(String id, {String? title, String? description, String? priority, DateTime? dueAt}) async {
	final response = await _dio.patch<Map<String, dynamic>>('/api/v1/tasks/$id', data: {
	  if (title != null) 'title': title,
	  if (description != null) 'description': description,
	  if (priority != null) 'priority': priority,
	  if (dueAt != null) 'due_at': dueAt.toUtc().toIso8601String(),
	});
	return Task.fromJson(response.data!);
  }

  Future<void> delete(String id) => _dio.delete<void>('/api/v1/tasks/$id');

  Future<Task> updateStatus(String id, String status) async {
	final response = await _dio.post<Map<String, dynamic>>('/api/v1/tasks/$id/status', data: {'status': status});
	return Task.fromJson(response.data!);
  }
}
