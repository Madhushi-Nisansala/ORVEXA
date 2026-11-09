import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/application/auth_provider.dart';
import '../../documents/data/document.dart';
import '../../documents/data/documents_api.dart';
import '../../goals/data/goal.dart';
import '../../goals/data/goals_repository.dart';
import '../../insights/data/insights_repository.dart';
import '../../tasks/data/task.dart';
import '../../tasks/data/tasks_repository.dart';
import '../data/dashboard_models.dart';

const _pageSize = 100;

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  final client = ref.watch(protectedApiClientProvider);
  return DashboardRepository(documents: DocumentsApi(client), tasks: TasksRepository(client), goals: GoalsRepository(client), insights: InsightsRepository(client));
});

final dashboardProvider = FutureProvider.autoDispose<DashboardData>((ref) => ref.watch(dashboardRepositoryProvider).load(), retry: (_, error) => null);

class DashboardRepository {
  DashboardRepository({required this.documents, required this.tasks, required this.goals, required this.insights});
  final DocumentsApi documents;
  final TasksRepository tasks;
  final GoalsRepository goals;
  final InsightsRepository insights;

  Future<DashboardData> load() async {
    final results = await Future.wait<_SectionResult>([
      _section('documents', () => documents.listPage(limit: _pageSize)),
      _section('tasks', () => tasks.list(limit: _pageSize)),
      _section('goals', _loadAllGoals),
      _section('insights', _loadAllInsights),
    ]);
    if (results.every((result) => result.error != null)) throw DashboardLoadException(results.map((result) => result.error!).toList());
    final errors = <String, Object>{for (final result in results) if (result.error != null) result.key: result.error!};
    final documentPage = _value<DocumentList>(results[0]);
    final taskPage = _value<TaskPage>(results[1]);
    final goalItems = _value<List<Goal>>(results[2]);
    final insightItems = _value<List<InsightSummary>>(results[3]);
    return DashboardData(totalDocuments: documentPage?.total ?? 0, totalTasks: taskPage?.total ?? taskPage?.items.length ?? 0, totalGoals: goalItems?.length ?? 0, totalInsights: insightItems?.length ?? 0, recentDocuments: _recentDocuments(documentPage?.items ?? const []), recentTasks: (taskPage?.items ?? const []).take(5).map(_taskSummary).toList(), recentGoals: (goalItems ?? const []).take(5).map(_goalSummary).toList(), insights: (insightItems ?? const []).take(5).toList(), activeContextCount: 0, errors: errors);
  }

  Future<_SectionResult> _section(String key, Future<Object> Function() load) async {
    try { return _SectionResult(key, await load()); } catch (error) { return _SectionResult(key, null, error); }
  }

  Future<List<Goal>> _loadAllGoals() async {
    final records = <Goal>[];
    var offset = 0;
    while (true) {
      final page = await goals.list(limit: _pageSize, offset: offset);
      if (page.items.isEmpty) return records;
      records.addAll(page.items);
      if (page.items.length < _pageSize || page.items.length < page.total - offset) return records;
      offset += page.items.length;
    }
  }

  Future<List<InsightSummary>> _loadAllInsights() async {
    final records = <InsightSummary>[];
    final seen = <String>{};
    var offset = 0;
    while (true) {
      final page = await insights.listPage(limit: _pageSize, offset: offset);
      final newItems = page.where((item) => seen.add(item.id)).toList();
      records.addAll(newItems);
      if (page.length < _pageSize || newItems.isEmpty) return records;
      offset += page.length;
    }
  }

  TaskSummary _taskSummary(Task task) => TaskSummary(id: task.id, title: task.title, status: task.status, dueAt: task.dueAt, createdAt: task.createdAt);
  GoalSummary _goalSummary(Goal goal) => GoalSummary(id: goal.id, title: goal.title, status: goal.status.label, progress: goal.progress, targetDate: goal.targetDate, createdAt: goal.createdAt);
  List<Document> _recentDocuments(List<Document> items) { final sorted = [...items]..sort((a, b) => (b.createdAt ?? DateTime(0)).compareTo(a.createdAt ?? DateTime(0))); return sorted.take(5).toList(); }
  T? _value<T>(_SectionResult result) => result.value is T ? result.value as T : null;
}

class _SectionResult {
  _SectionResult(this.key, this.value, [this.error]);
  final String key;
  final Object? value;
  final Object? error;
}

class DashboardLoadException implements Exception {
  DashboardLoadException(this.errors);
  final List<Object> errors;
  @override
  String toString() => 'DashboardLoadException(${errors.length} failures)';
}
