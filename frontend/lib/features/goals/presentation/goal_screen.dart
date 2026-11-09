import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/goals_provider.dart';
import '../data/goal.dart';

class GoalsScreen extends ConsumerStatefulWidget {
  const GoalsScreen({super.key});
  @override
  ConsumerState<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends ConsumerState<GoalsScreen> {
  final _search = TextEditingController();

  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
	final goals = ref.watch(goalsProvider);
	final query = ref.watch(goalQueryProvider);
	return Scaffold(
	  appBar: AppBar(title: const Text('Goals'), actions: [IconButton(onPressed: () => context.push('/goals/new'), icon: const Icon(Icons.add))]),
	  body: RefreshIndicator(
		onRefresh: () async => ref.refresh(goalsProvider.future),
		child: goals.when(
		  loading: () => const Center(child: CircularProgressIndicator()),
		  error: (error, _) => ListView(children: [const SizedBox(height: 180), const Center(child: Text('Unable to load goals')), Center(child: TextButton(onPressed: () => ref.invalidate(goalsProvider), child: const Text('Retry')))]),
		  data: (page) => Column(children: [
			Padding(padding: const EdgeInsets.all(12), child: TextField(controller: _search, textInputAction: TextInputAction.search, onSubmitted: (value) => _change(query.copyWith(search: value, offset: 0)), decoration: InputDecoration(labelText: 'Search goals', prefixIcon: const Icon(Icons.search), suffixIcon: IconButton(onPressed: () { _search.clear(); _change(query.copyWith(search: '', offset: 0)); }, icon: const Icon(Icons.clear))))),
			_Filters(query: query, onChanged: _change),
			Expanded(child: page.items.isEmpty ? const _EmptyGoals() : ListView.builder(padding: const EdgeInsets.only(bottom: 80), itemCount: page.items.length, itemBuilder: (_, index) => _GoalCard(goal: page.items[index]))),
			if (page.total > query.limit) _Pager(page: page, query: query, onChanged: _change),
		  ]),
		),
	  ),
	  floatingActionButton: FloatingActionButton(onPressed: () => context.push('/goals/new'), child: const Icon(Icons.add)),
	);
  }

  void _change(GoalQuery value) => ref.read(goalQueryProvider.notifier).state = value;
}

class _Filters extends StatelessWidget {
  const _Filters({required this.query, required this.onChanged});
  final GoalQuery query;
  final ValueChanged<GoalQuery> onChanged;
  @override
  Widget build(BuildContext context) => SingleChildScrollView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12), child: Row(children: [
	DropdownButton<String?>(value: query.status, hint: const Text('Status'), items: const [DropdownMenuItem(value: null, child: Text('All status')), DropdownMenuItem(value: 'not_started', child: Text('Not started')), DropdownMenuItem(value: 'in_progress', child: Text('In progress')), DropdownMenuItem(value: 'completed', child: Text('Completed')), DropdownMenuItem(value: 'paused', child: Text('Paused'))], onChanged: (value) => onChanged(value == null ? query.copyWith(clearStatus: true, offset: 0) : query.copyWith(status: value, offset: 0))),
	const SizedBox(width: 12),
	SizedBox(width: 150, child: TextField(decoration: const InputDecoration(labelText: 'Category', isDense: true), onSubmitted: (value) => onChanged(query.copyWith(category: value, offset: 0)))),
	IconButton(tooltip: 'Sort', onPressed: () => onChanged(query.copyWith(sortBy: query.sortBy == 'created_at' ? 'target_date' : 'created_at', descending: !query.descending, offset: 0)), icon: const Icon(Icons.sort)),
  ]));
}

class _GoalCard extends StatelessWidget {
  const _GoalCard({required this.goal});
  final Goal goal;
  @override
  Widget build(BuildContext context) => Card(margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5), child: ListTile(onTap: () => context.push('/goals/${goal.id}'), leading: CircularProgressIndicator(value: goal.progress / 100, backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest), title: Text(goal.title), subtitle: Text('${goal.status.label} • ${goal.progress}%${goal.targetDate == null ? '' : ' • Target ${_date(goal.targetDate!)}'}'), trailing: const Icon(Icons.chevron_right)));
}

class _Pager extends StatelessWidget {
  const _Pager({required this.page, required this.query, required this.onChanged});
  final GoalPage page;
  final GoalQuery query;
  final ValueChanged<GoalQuery> onChanged;
  @override
  Widget build(BuildContext context) => Row(mainAxisAlignment: MainAxisAlignment.center, children: [IconButton(onPressed: page.hasPrevious ? () => onChanged(query.copyWith(offset: query.offset - query.limit)) : null, icon: const Icon(Icons.chevron_left)), Text('${page.total == 0 ? 0 : query.offset + 1}-${query.offset + page.items.length} of ${page.total}'), IconButton(onPressed: page.hasNext ? () => onChanged(query.copyWith(offset: query.offset + query.limit)) : null, icon: const Icon(Icons.chevron_right))]);
}

class _EmptyGoals extends StatelessWidget { const _EmptyGoals(); @override Widget build(BuildContext context) => const Center(child: Text('No goals match your filters. Create your first goal.')); }
String _date(DateTime value) => '${value.month}/${value.day}/${value.year}';
