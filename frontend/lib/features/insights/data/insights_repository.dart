import '../../../core/network/api_client.dart';
import '../../dashboard/data/dashboard_models.dart';

class InsightsRepository {
  InsightsRepository(this._client);

  final ApiClient _client;

  Future<List<InsightSummary>> listPage({int limit = 100, int offset = 0}) async {
	final response = await _client.dio.get<List<dynamic>>(
	  '/api/v1/insights',
	  queryParameters: {'limit': limit, 'offset': offset},
	);
	final values = response.data;
	if (values == null) throw const FormatException('Invalid insights response');
	return values.map((item) {
	  if (item is! Map<String, dynamic>) {
		throw const FormatException('Invalid insight item');
	  }
	  return InsightSummary.fromJson(item);
	}).toList();
  }
}
