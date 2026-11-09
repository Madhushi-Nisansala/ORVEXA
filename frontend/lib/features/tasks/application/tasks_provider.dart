import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/application/auth_provider.dart';
import '../../dashboard/application/dashboard_provider.dart';
import '../data/task.dart';
import '../data/tasks_repository.dart';

final tasksRepositoryProvider = Provider<TasksRepository>((ref) => TasksRepository(ref.watch(protectedApiClientProvider)));

final tasksProvider = FutureProvider.autoDispose<TaskPage>((ref) {
  final query = ref.watch(taskQueryProvider);
  return ref.watch(tasksRepositoryProvider).list(
		search: query.search,
		status: query.status,
		priority: query.priority,
		sortBy: query.sortBy,
		descending: query.descending,
	  );
});

final taskProvider = FutureProvider.autoDispose.family<Task, String>((ref, id) => ref.watch(tasksRepositoryProvider).get(id));

final taskActionsProvider = Provider<TaskActions>((ref) => TaskActions(ref));

class TaskQuery {
  const TaskQuery({this.search, this.status, this.priority, this.sortBy = 'created_at', this.descending = true});
  final String? search;
  final String? status;
  final String? priority;
  final String sortBy;
  final bool descending;

  TaskQuery copyWith({String? search, String? status, String? priority, String? sortBy, bool? descending, bool clearStatus = false, bool clearPriority = false}) => TaskQuery(
		search: search ?? this.search,
		status: clearStatus ? null : status ?? this.status,
		priority: clearPriority ? null : priority ?? this.priority,
		sortBy: sortBy ?? this.sortBy,
		descending: descending ?? this.descending,
	  );
}

class TaskActions {
  TaskActions(this._ref);
  final Ref _ref;

  TasksRepository get _repository => _ref.read(tasksRepositoryProvider);
  void _refresh() {
	_ref.invalidate(tasksProvider);
	_ref.invalidate(dashboardProvider);
  }

  Future<Task> create({required String title, String? description, required String priority, DateTime? dueAt}) async {
	final task = await _repository.create(title: title, description: description, priority: priority, dueAt: dueAt);
	_refresh();
	return task;
  }

  Future<Task> update(String id, {String? title, String? description, String? priority, DateTime? dueAt}) async {
	final task = await _repository.update(id, title: title, description: description, priority: priority, dueAt: dueAt);
	_ref.invalidate(taskProvider(id));
	_refresh();
	return task;
  }

  Future<void> delete(String id) async {
	await _repository.delete(id);
	_ref.invalidate(taskProvider(id));
	_refresh();
  }

  Future<Task> updateStatus(String id, String status) async {
	final task = await _repository.updateStatus(id, status);
	_ref.invalidate(taskProvider(id));
	_refresh();
	return task;
  }
}
class TaskQueryNotifier extends Notifier<TaskQuery> {
  @override
  TaskQuery build() => const TaskQuery();
}
final taskQueryProvider = NotifierProvider<TaskQueryNotifier, TaskQuery>(TaskQueryNotifier.new);
