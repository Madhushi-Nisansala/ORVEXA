class Memory {
  const Memory({
	required this.id,
	required this.title,
	required this.category,
	required this.content,
	required this.isActive,
	required this.createdAt,
	required this.updatedAt,
	this.sourceReference,
  });

  factory Memory.fromJson(Map<String, dynamic> json) => Memory(
		id: json['id'] as String,
		title: json['title'] as String? ?? 'Untitled memory',
		category: json['category'] as String,
		content: Map<String, dynamic>.from(json['content'] as Map? ?? const {}),
		isActive: json['is_active'] as bool? ?? true,
		createdAt: DateTime.parse(json['created_at'] as String),
		updatedAt: DateTime.parse(json['updated_at'] as String),
		sourceReference: json['source_reference'] as String?,
	  );

  final String id;
  final String title;
  final String category;
  final Map<String, dynamic> content;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? sourceReference;

  String get text => content['text']?.toString() ?? content.entries.map((e) => '${e.key}: ${e.value}').join('\n');
}
