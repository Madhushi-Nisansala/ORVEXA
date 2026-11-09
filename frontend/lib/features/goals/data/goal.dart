enum GoalStatus {
  notStarted('not_started', 'Not started'),
  inProgress('in_progress', 'In progress'),
  completed('completed', 'Completed'),
  paused('paused', 'Paused');

  const GoalStatus(this.value, this.label);
  final String value;
  final String label;

  static GoalStatus fromValue(Object? value) => values.firstWhere(
		(status) => status.value == value?.toString(),
		orElse: () => GoalStatus.notStarted,
	  );
}

class Goal {
  const Goal({
	required this.id,
	required this.title,
	required this.status,
	required this.progress,
	this.description,
	this.category,
	this.targetDate,
	this.createdAt,
	this.updatedAt,
  });

  final String id;
  final String title;
  final String? description;
  final String? category;
  final DateTime? targetDate;
  final GoalStatus status;
  final int progress;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  factory Goal.fromJson(Map<String, dynamic> json) => Goal(
		id: json['id'].toString(),
		title: json['title']?.toString() ?? '',
		description: json['description']?.toString(),
		category: json['category']?.toString(),
		targetDate: _date(json['target_date']),
		status: GoalStatus.fromValue(json['status']),
		progress: _progress(json['progress']),
		createdAt: _date(json['created_at']),
		updatedAt: _date(json['updated_at']),
	  );

  static int _progress(Object? value) {
	final progress = value is num ? value.toInt() : int.tryParse('$value') ?? 0;
	return progress.clamp(0, 100);
  }

  static DateTime? _date(Object? value) =>
	  value == null ? null : DateTime.tryParse(value.toString());
}

class GoalPage {
  const GoalPage({required this.items, required this.total, required this.offset, required this.limit});
  final List<Goal> items;
  final int total;
  final int offset;
  final int limit;

  bool get hasPrevious => offset > 0;
  bool get hasNext => offset + items.length < total;
}
