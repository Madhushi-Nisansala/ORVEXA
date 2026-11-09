import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/tasks_provider.dart';
import '../data/task.dart';

class TasksScreen extends ConsumerStatefulWidget {
  const TasksScreen({super.key});
  @override
  ConsumerState<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends ConsumerState<TasksScreen> {
  final _search = TextEditingController();
  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
	final tasks = ref.watch(tasksProvider);
	final query = ref.watch(taskQueryProvider);
	return Scaffold(
	  appBar: AppBar(title: const Text('Tasks'), actions: [IconButton(onPressed: () => context.push('/tasks/new'), icon: const Icon(Icons.add))]),
	  body: RefreshIndicator(
		onRefresh: () async => ref.refresh(tasksProvider.future),
		child: tasks.when(
		  loading: () => const Center(child: CircularProgressIndicator()),
		  error: (error, _) => ListView(children: [const SizedBox(height: 180), Center(child: Text('Unable to load tasks')), Center(child: TextButton(onPressed: () => ref.invalidate(tasksProvider), child: const Text('Retry')))]),
		  data: (page) => Column(children: [
			Padding(padding: const EdgeInsets.all(12), child: TextField(controller: _search, decoration: InputDecoration(labelText: 'Search tasks', prefixIcon: const Icon(Icons.search), suffixIcon: IconButton(icon: const Icon(Icons.clear), onPressed: () { _search.clear(); _setQuery(query.copyWith(search: '')); })), onSubmitted: (value) => _setQuery(query.copyWith(search: value)))),
			_Filters(query: query, onChanged: _setQuery),
			Expanded(child: page.items.isEmpty ? const _EmptyTasks() : ListView.builder(itemCount: page.items.length, itemBuilder: (_, index) => _TaskTile(task: page.items[index]))),
		  ]),
		),
	  ),
	  floatingActionButton: FloatingActionButton(onPressed: () => context.push('/tasks/new'), child: const Icon(Icons.add)),
	);
  }

  void _setQuery(TaskQuery query) => ref.read(taskQueryProvider.notifier).state = query;
}

class _Filters extends StatelessWidget {
  const _Filters({required this.query, required this.onChanged});
  final TaskQuery query;
  final ValueChanged<TaskQuery> onChanged;
  @override
  Widget build(BuildContext context) => SingleChildScrollView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12), child: Row(children: [
	DropdownButton<String?>(value: query.status, hint: const Text('Status'), items: const [DropdownMenuItem(value: null, child: Text('All status')), DropdownMenuItem(value: 'pending', child: Text('Pending')), DropdownMenuItem(value: 'in_progress', child: Text('In progress')), DropdownMenuItem(value: 'completed', child: Text('Completed')), DropdownMenuItem(value: 'cancelled', child: Text('Cancelled'))], onChanged: (value) => onChanged(value == null ? query.copyWith(clearStatus: true) : query.copyWith(status: value))),
	const SizedBox(width: 16),
	DropdownButton<String?>(value: query.priority, hint: const Text('Priority'), items: const [DropdownMenuItem(value: null, child: Text('All priority')), DropdownMenuItem(value: 'urgent', child: Text('Urgent')), DropdownMenuItem(value: 'high', child: Text('High')), DropdownMenuItem(value: 'medium', child: Text('Medium')), DropdownMenuItem(value: 'low', child: Text('Low'))], onChanged: (value) => onChanged(value == null ? query.copyWith(clearPriority: true) : query.copyWith(priority: value))),
	IconButton(tooltip: 'Sort by due date', onPressed: () => onChanged(query.copyWith(sortBy: 'due_at', descending: !query.descending)), icon: const Icon(Icons.sort)),
  ]));
}

class _TaskTile extends ConsumerWidget {
  const _TaskTile({required this.task});
  final Task task;
  @override
  Widget build(BuildContext context, WidgetRef ref) => ListTile(
	leading: Icon(task.status == 'completed' ? Icons.check_circle : Icons.radio_button_unchecked, color: _priorityColor(task.priority)),
	title: Text(task.title),
	subtitle: Text('${task.status.replaceAll('_', ' ')} • ${task.priority}${task.dueAt == null ? '' : ' • Due ${_date(task.dueAt!)}'}'),
	onTap: () => context.push('/tasks/${task.id}'),
	trailing: PopupMenuButton<String>(onSelected: (status) async { await ref.read(taskActionsProvider).updateStatus(task.id, status); }, itemBuilder: (_) => const [PopupMenuItem(value: 'pending', child: Text('Pending')), PopupMenuItem(value: 'in_progress', child: Text('In progress')), PopupMenuItem(value: 'completed', child: Text('Completed')), PopupMenuItem(value: 'cancelled', child: Text('Cancelled'))]),
  );
}

class _EmptyTasks extends StatelessWidget { const _EmptyTasks(); @override Widget build(BuildContext context) => const Center(child: Text('No tasks match your filters. Create your first task.')); }
Color _priorityColor(String priority) => switch (priority) { 'urgent' => Colors.red, 'high' => Colors.orange, 'low' => Colors.blue, _ => Colors.grey };
String _date(DateTime value) => '${value.month}/${value.day}/${value.year}';
