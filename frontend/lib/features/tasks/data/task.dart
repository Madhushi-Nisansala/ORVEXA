class Task {
  const Task({
	required this.id,
	required this.title,
	required this.status,
	required this.priority,
	required this.createdAt,
	required this.updatedAt,
	this.description,
	this.dueAt,
	this.completedAt,
	this.estimatedDurationMinutes,
  });

  final String id;
  final String title;
  final String? description;
  final String status;
  final String priority;
  final DateTime? dueAt;
  final DateTime? completedAt;
  final int? estimatedDurationMinutes;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  factory Task.fromJson(Map<String, dynamic> json) => Task(
		id: json['id'].toString(),
		title: json['title']?.toString() ?? '',
		description: json['description']?.toString(),
		status: json['status']?.toString() ?? 'pending',
		priority: json['priority']?.toString() ?? 'medium',
		dueAt: _date(json['due_at']),
		completedAt: _date(json['completed_at']),
		estimatedDurationMinutes: (json['estimated_duration_minutes'] as num?)?.toInt(),
		createdAt: _date(json['created_at']),
		updatedAt: _date(json['updated_at']),
	  );

  static DateTime? _date(Object? value) => value == null ? null : DateTime.tryParse(value.toString());
}

class TaskPage {
  const TaskPage({required this.items, required this.total});
  final List<Task> items;
  final int total;
}
