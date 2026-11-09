import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import 'goal.dart';

class GoalsRepository {
  GoalsRepository(this._client);
  final ApiClient _client;
  Dio get _dio => _client.dio;

  Future<GoalPage> list({
	String? search,
	String? status,
	String? category,
	int limit = 10,
	int offset = 0,
	String sortBy = 'created_at',
	bool descending = true,
  }) async {
	final response = await _dio.get<Object?>('/api/v1/goals', queryParameters: {
	  'limit': limit,
	  'offset': offset,
	  if (search != null && search.trim().isNotEmpty) 'search': search.trim(),
	  if (status != null) 'status': status,
	  if (category != null && category.trim().isNotEmpty) 'category': category.trim(),
	  'sort_by': sortBy,
	  'sort_order': descending ? 'desc' : 'asc',
	});
	final data = response.data;
	final rawItems = data is Map<String, dynamic> ? data['items'] : data;
	if (rawItems is! List) throw const FormatException('Invalid goals response');
	final items = rawItems.map((item) {
	  if (item is! Map<String, dynamic>) throw const FormatException('Invalid goal item');
	  return Goal.fromJson(item);
	}).toList();
	final envelopeTotal = data is Map<String, dynamic> && data['total'] is num
		? (data['total'] as num).toInt()
		: null;
	final headerTotal = int.tryParse(response.headers.value('x-total-count') ?? '');
	return GoalPage(
	  items: items,
	  total: envelopeTotal ?? headerTotal ?? offset + items.length,
	  offset: offset,
	  limit: limit,
	);
  }

  Future<Goal> get(String id) async {
	final response = await _dio.get<Map<String, dynamic>>('/api/v1/goals/$id');
	return Goal.fromJson(response.data!);
  }

  Future<Goal> create({
	required String title,
	String? description,
	String? category,
	DateTime? targetDate,
	GoalStatus status = GoalStatus.notStarted,
	int progress = 0,
  }) async {
	_validateProgress(progress);
	final response = await _dio.post<Map<String, dynamic>>('/api/v1/goals', data: {
	  'title': title,
	  if (description != null && description.trim().isNotEmpty) 'description': description.trim(),
	  if (category != null && category.trim().isNotEmpty) 'category': category.trim(),
	  if (targetDate != null) 'target_date': targetDate.toUtc().toIso8601String(),
	  'status': status.value,
	  'progress': progress,
	});
	return Goal.fromJson(response.data!);
  }

  Future<Goal> update(
	String id, {
	String? title,
	String? description,
	String? category,
	DateTime? targetDate,
	GoalStatus? status,
	int? progress,
  }) async {
	if (progress != null) _validateProgress(progress);
	final response = await _dio.patch<Map<String, dynamic>>('/api/v1/goals/$id', data: {
	  if (title != null) 'title': title,
	  if (description != null) 'description': description,
	  if (category != null) 'category': category,
	  if (targetDate != null) 'target_date': targetDate.toUtc().toIso8601String(),
	  if (status != null) 'status': status.value,
	  if (progress != null) 'progress': progress,
	});
	return Goal.fromJson(response.data!);
  }

  Future<void> delete(String id) => _dio.delete<void>('/api/v1/goals/$id');

  Future<Goal> updateProgress(String id, int progress) async {
	_validateProgress(progress);
	final response = await _dio.post<Map<String, dynamic>>(
	  '/api/v1/goals/$id/progress',
	  data: {'progress': progress},
	);
	return Goal.fromJson(response.data!);
  }

  Future<Goal> complete(String id) async {
	final response = await _dio.post<Map<String, dynamic>>(
	  '/api/v1/goals/$id/status',
	  data: {'status': GoalStatus.completed.value},
	);
	return Goal.fromJson(response.data!);
  }

  static void _validateProgress(int progress) {
	if (progress < 0 || progress > 100) {
	  throw ArgumentError.value(progress, 'progress', 'Progress must be between 0 and 100');
	}
  }
}
