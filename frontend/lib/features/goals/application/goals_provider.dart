import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/application/auth_provider.dart';
import '../../dashboard/application/dashboard_provider.dart';
import '../data/goal.dart';
import '../data/goals_repository.dart';

final goalsRepositoryProvider = Provider<GoalsRepository>(
  (ref) => GoalsRepository(ref.watch(protectedApiClientProvider)),
);

final goalQueryProvider = NotifierProvider<GoalQueryNotifier, GoalQuery>(GoalQueryNotifier.new);

final goalsProvider = FutureProvider.autoDispose<GoalPage>((ref) {
  final query = ref.watch(goalQueryProvider);
  return ref.watch(goalsRepositoryProvider).list(
		search: query.search,
		status: query.status,
		category: query.category,
		limit: query.limit,
		offset: query.offset,
		sortBy: query.sortBy,
		descending: query.descending,
	  );
});

final goalProvider = FutureProvider.autoDispose.family<Goal, String>(
  (ref, id) => ref.watch(goalsRepositoryProvider).get(id),
);

final goalActionsProvider = Provider<GoalActions>((ref) => GoalActions(ref));

class GoalQuery {
  const GoalQuery({
	this.search,
	this.status,
	this.category,
	this.sortBy = 'created_at',
	this.descending = true,
	this.limit = 10,
	this.offset = 0,
  });

  final String? search;
  final String? status;
  final String? category;
  final String sortBy;
  final bool descending;
  final int limit;
  final int offset;

  GoalQuery copyWith({
	String? search,
	String? status,
	String? category,
	String? sortBy,
	bool? descending,
	int? limit,
	int? offset,
	bool clearStatus = false,
	bool clearCategory = false,
  }) => GoalQuery(
		search: search ?? this.search,
		status: clearStatus ? null : status ?? this.status,
		category: clearCategory ? null : category ?? this.category,
		sortBy: sortBy ?? this.sortBy,
		descending: descending ?? this.descending,
		limit: limit ?? this.limit,
		offset: offset ?? this.offset,
	  );
}

class GoalQueryNotifier extends Notifier<GoalQuery> {
  @override
  GoalQuery build() => const GoalQuery();
}

class GoalActions {
  GoalActions(this._ref);
  final Ref _ref;
  GoalsRepository get _repository => _ref.read(goalsRepositoryProvider);

  void _refresh(String? id) {
	_ref.invalidate(goalsProvider);
	if (id != null) _ref.invalidate(goalProvider(id));
	_ref.invalidate(dashboardProvider);
  }

  Future<Goal> create({required String title, String? description, String? category, DateTime? targetDate, GoalStatus status = GoalStatus.notStarted, int progress = 0}) async {
	final goal = await _repository.create(title: title, description: description, category: category, targetDate: targetDate, status: status, progress: progress);
	_refresh(null);
	return goal;
  }

  Future<Goal> update(String id, {String? title, String? description, String? category, DateTime? targetDate, GoalStatus? status, int? progress}) async {
	final goal = await _repository.update(id, title: title, description: description, category: category, targetDate: targetDate, status: status, progress: progress);
	_refresh(id);
	return goal;
  }

  Future<void> delete(String id) async {
	await _repository.delete(id);
	_refresh(id);
  }

  Future<Goal> updateProgress(String id, int progress) async {
	final goal = await _repository.updateProgress(id, progress);
	_refresh(id);
	return goal;
  }

  Future<Goal> complete(String id) async {
	final goal = await _repository.complete(id);
	_refresh(id);
	return goal;
  }
}
