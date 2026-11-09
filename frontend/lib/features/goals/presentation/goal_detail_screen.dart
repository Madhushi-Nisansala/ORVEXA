import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/goals_provider.dart';
import '../data/goal.dart';

class GoalDetailScreen extends ConsumerWidget {
  const GoalDetailScreen({required this.goalId, super.key});
  final String goalId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
	final goal = ref.watch(goalProvider(goalId));
	return Scaffold(
      appBar: AppBar(
        title: const Text('Goal details'),
        actions: [
          IconButton(onPressed: () => goal.whenData((value) => context.push('/goals/${value.id}/edit', extra: value)), icon: const Icon(Icons.edit)),
          IconButton(onPressed: () => _delete(context, ref), icon: const Icon(Icons.delete_outline)),
        ],
      ),
      body: goal.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Unable to load goal: $error')),
        data: (value) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(value.title, style: Theme.of(context).textTheme.headlineSmall),
            if (value.category?.isNotEmpty == true) Text(value.category!, style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 12),
            Text(value.description?.isNotEmpty == true ? value.description! : 'No description'),
            const SizedBox(height: 24),
            LinearProgressIndicator(value: value.progress / 100, minHeight: 10),
            const SizedBox(height: 8),
            Text('${value.progress}% complete'),
            Text('Status: ${value.status.label}'),
            if (value.targetDate != null) Text('Target: ${_date(value.targetDate!)}'),
            const SizedBox(height: 24),
            FilledButton.icon(onPressed: value.status == GoalStatus.completed ? null : () => _setProgress(context, ref, value.progress), icon: const Icon(Icons.trending_up), label: const Text('Update progress')),
            if (value.status != GoalStatus.completed) OutlinedButton.icon(onPressed: () async { await ref.read(goalActionsProvider).complete(value.id); }, icon: const Icon(Icons.check), label: const Text('Mark completed')),
          ],
        ),
      ),
    );
  }

  Future<void> _setProgress(BuildContext context, WidgetRef ref, int current) async { final controller = TextEditingController(text: '$current'); final value = await showDialog<int>(context: context, builder: (context) => AlertDialog(title: const Text('Update progress'), content: TextField(controller: controller, autofocus: true, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Progress (0-100)')), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { final progress = int.tryParse(controller.text); if (progress != null && progress >= 0 && progress <= 100) Navigator.pop(context, progress); }, child: const Text('Update'))])); controller.dispose(); if (value != null) await ref.read(goalActionsProvider).updateProgress(goalId, value); }

  Future<void> _delete(BuildContext context, WidgetRef ref) async { final confirmed = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Delete goal?'), content: const Text('This action cannot be undone.'), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete'))])); if (confirmed == true) { await ref.read(goalActionsProvider).delete(goalId); if (context.mounted) context.go('/goals'); } }
}

String _date(DateTime value) => '${value.month}/${value.day}/${value.year}';
