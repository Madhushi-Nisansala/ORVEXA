class DocumentAnalysis {
  const DocumentAnalysis({
    required this.id,
    required this.status,
    required this.version,
    this.errorSummary,
    this.result,
  });

  final String id;
  final String status;
  final int version;
  final String? errorSummary;
  final Map<String, dynamic>? result;

  factory DocumentAnalysis.fromJson(Map<String, dynamic> json) =>
      DocumentAnalysis(
        id: json['id'] as String,
        status: json['status'] as String,
        version: json['version'] as int,
        errorSummary: json['error_summary'] as String?,
        result: json['result'] as Map<String, dynamic>?,
      );

  String? get classification =>
      result?['classification'] is Map<String, dynamic>
      ? (result!['classification'] as Map<String, dynamic>)['primary_type']
            as String?
      : null;

  List<Map<String, dynamic>> get facts => _items('facts');
  List<Map<String, dynamic>> get dates => _items('dates');
  List<Map<String, dynamic>> get obligations => _items('obligations');
  List<Map<String, dynamic>> get risks => _items('risks');
  List<Map<String, dynamic>> get entities => _items('entities');
  List<Map<String, dynamic>> get recommendations => _items('requirements') + _items('obligations');

  String? get summary => result?['executive_summary'] as String? ??
      (result?['classification'] is Map<String, dynamic>
          ? (result!['classification'] as Map<String, dynamic>)['explanation'] as String?
          : null);

  List<Map<String, dynamic>> _items(String key) {
    final values = result?[key];
    if (values is! List) return const [];
    return values.whereType<Map<String, dynamic>>().toList();
  }
}

class DocumentInsight {
  const DocumentInsight({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    this.confidence,
  });

  final String id;
  final String title;
  final String description;
  final String category;
  final double? confidence;

  factory DocumentInsight.fromJson(Map<String, dynamic> json) => DocumentInsight(
        id: json['id'] as String,
        title: json['title'] as String,
        description: json['description'] as String,
        category: json['category'] as String,
        confidence: (json['confidence'] as num?)?.toDouble(),
      );
}
