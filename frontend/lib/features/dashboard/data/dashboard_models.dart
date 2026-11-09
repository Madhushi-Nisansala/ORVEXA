import '../../documents/data/document.dart';

class DashboardData {
  const DashboardData({
    required this.totalDocuments,
    required this.totalTasks,
    required this.totalGoals,
    required this.totalInsights,
    required this.recentDocuments,
    required this.recentTasks,
    required this.recentGoals,
    required this.insights,
    required this.activeContextCount,
    this.errors = const {},
  });

  final int totalDocuments;
  final int totalTasks;
  final int totalGoals;
  final int totalInsights;
  final List<Document> recentDocuments;
  final List<TaskSummary> recentTasks;
  final List<GoalSummary> recentGoals;
  final List<InsightSummary> insights;
  final int activeContextCount;
  final Map<String, Object> errors;

  bool get hasPartialFailures => errors.isNotEmpty;
}

class TaskSummary {
  const TaskSummary({
    required this.id,
    required this.title,
    required this.status,
    this.progress = 0,
    this.dueAt,
    this.createdAt,
  });

  final String id;
  final String title;
  final String status;
  final int progress;
  final DateTime? dueAt;
  final DateTime? createdAt;

  factory TaskSummary.fromJson(Map<String, dynamic> json) => TaskSummary(
    id: json['id']?.toString() ?? '',
    title: json['title']?.toString() ?? 'Untitled task',
    status: json['status']?.toString() ?? 'unknown',
    progress: (json['progress'] as num?)?.toInt() ?? 0,
    dueAt: _parseDate(json['due_at']),
    createdAt: _parseDate(json['created_at']),
  );
}

class GoalSummary {
  const GoalSummary({
    required this.id,
    required this.title,
    required this.status,
    this.progress = 0,
    this.targetDate,
    this.createdAt,
  });

  final String id;
  final String title;
  final String status;
  final int progress;
  final DateTime? targetDate;
  final DateTime? createdAt;

  factory GoalSummary.fromJson(Map<String, dynamic> json) => GoalSummary(
    id: json['id']?.toString() ?? '',
    title: json['title']?.toString() ?? 'Untitled goal',
    status: json['status']?.toString() ?? 'unknown',
    progress: (json['progress'] as num?)?.toInt() ?? 0,
    targetDate: _parseDate(json['target_date']),
    createdAt: _parseDate(json['created_at']),
  );
}

class InsightSummary {
  const InsightSummary({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.status,
    this.createdAt,
  });

  final String id;
  final String title;
  final String description;
  final String category;
  final String status;
  final DateTime? createdAt;

  factory InsightSummary.fromJson(Map<String, dynamic> json) => InsightSummary(
    id: json['id']?.toString() ?? '',
    title: json['title']?.toString() ?? 'Untitled insight',
    description: json['description']?.toString() ?? '',
    category: json['category']?.toString() ?? 'general',
    status: json['status']?.toString() ?? 'unknown',
    createdAt: _parseDate(json['created_at']),
  );
}

DateTime? _parseDate(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}
