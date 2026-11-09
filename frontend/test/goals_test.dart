import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/features/goals/data/goal.dart';
import 'package:orvexa/features/goals/data/goals_repository.dart';

void main() {
  test('parses goal fields and status', () {
	final goal = Goal.fromJson({
	  'id': 'g-1',
	  'title': 'Ship feature',
	  'description': 'Complete the work',
	  'category': 'Product',
	  'target_date': '2030-01-02T00:00:00Z',
	  'status': 'in_progress',
	  'progress': 42,
	  'created_at': '2029-01-01T00:00:00Z',
	  'updated_at': '2029-01-02T00:00:00Z',
	});
	expect(goal.status, GoalStatus.inProgress);
	expect(goal.progress, 42);
	expect(goal.category, 'Product');
  });

  test('rejects progress outside 0 through 100 before making a request', () async {
	final repository = GoalsRepository(ApiClient(dio: Dio(BaseOptions(baseUrl: 'http://test'))));
	expect(() => repository.updateProgress('g-1', 101), throwsArgumentError);
	expect(() => repository.updateProgress('g-1', -1), throwsArgumentError);
  });

  test('lists goals with pagination and query parameters', () async {
	final dio = Dio(BaseOptions(baseUrl: 'http://test'));
	late RequestOptions request;
	dio.interceptors.add(InterceptorsWrapper(onRequest: (options, handler) {
	  request = options;
	  handler.resolve(Response<Object?>(
		requestOptions: options,
		statusCode: 200,
		headers: Headers.fromMap({'x-total-count': ['12']}),
		data: [
		  {'id': 'g-1', 'title': 'Goal', 'status': 'not_started', 'progress': 0},
		],
	  ));
	}));
	final page = await GoalsRepository(ApiClient(dio: dio)).list(search: 'ship', status: 'not_started', limit: 5, offset: 5, sortBy: 'target_date', descending: false);
	expect(page.total, 12);
	expect(page.offset, 5);
	expect(page.items.single.id, 'g-1');
	expect(request.queryParameters['search'], 'ship');
	expect(request.queryParameters['sort_order'], 'asc');
  });
}
