import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/tasks_provider.dart';

class TaskDetailScreen extends ConsumerWidget {
  const TaskDetailScreen({required this.taskId, super.key});
  final String taskId;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
	final task = ref.watch(taskProvider(taskId));
	return Scaffold(
	  appBar: AppBar(
		title: const Text('Task details'),
		actions: [
		  IconButton(
			onPressed: () => task.whenData(
			  (value) => context.push('/tasks/${value.id}/edit', extra: value),
			),
			icon: const Icon(Icons.edit),
		  ),
		  IconButton(
			onPressed: () => _delete(context, ref),
			icon: const Icon(Icons.delete_outline),
		  ),
		],
	  ),
	  body: task.when(
		loading: () => const Center(child: CircularProgressIndicator()),
		error: (error, _) => Center(child: Text('Unable to load task: $error')),
		data: (value) => ListView(
		  padding: const EdgeInsets.all(20),
		  children: [
			Text(value.title, style: Theme.of(context).textTheme.headlineSmall),
			const SizedBox(height: 12),
			Text(value.description?.isNotEmpty == true ? value.description! : 'No description'),
			const SizedBox(height: 20),
			Text('Status: ${value.status.replaceAll('_', ' ')}'),
			Text('Priority: ${value.priority}'),
			if (value.dueAt != null) Text('Due: ${value.dueAt!.toLocal()}'),
			const SizedBox(height: 20),
			DropdownButtonFormField<String>(
			  initialValue: value.status,
			  decoration: const InputDecoration(labelText: 'Update status'),
			  items: const [
				DropdownMenuItem(value: 'pending', child: Text('Pending')),
				DropdownMenuItem(value: 'in_progress', child: Text('In progress')),
				DropdownMenuItem(value: 'completed', child: Text('Completed')),
				DropdownMenuItem(value: 'cancelled', child: Text('Cancelled')),
			  ],
			  onChanged: (status) async {
				if (status != null) {
				  await ref.read(taskActionsProvider).updateStatus(value.id, status);
				}
			  },
			),
		  ],
		),
	  ),
	);
  }

  Future<void> _delete(BuildContext context, WidgetRef ref) async { final confirmed = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Delete task?'), content: const Text('This action cannot be undone.'), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete'))])); if (confirmed == true) { await ref.read(taskActionsProvider).delete(taskId); if (context.mounted) context.go('/tasks'); } }
}
