import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../application/memory_provider.dart';
import '../data/memory.dart';

class MemoryScreen extends ConsumerStatefulWidget {
  const MemoryScreen({super.key});
  @override
  ConsumerState<MemoryScreen> createState() => _MemoryScreenState();
}

class _MemoryScreenState extends ConsumerState<MemoryScreen> {
  final _search = TextEditingController();
  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
	final memories = ref.watch(memoriesProvider);
	final category = ref.watch(memoryCategoryProvider);
	return Scaffold(
	  appBar: AppBar(title: const Text('AI Memory'), actions: [IconButton(onPressed: () => _edit(), icon: const Icon(Icons.add))]),
	  body: Column(children: [
		Padding(padding: const EdgeInsets.all(12), child: TextField(controller: _search, onChanged: (value) => ref.read(memorySearchProvider.notifier).setQuery(value), decoration: const InputDecoration(labelText: 'Search memory', prefixIcon: Icon(Icons.search)))),
		Padding(padding: const EdgeInsets.symmetric(horizontal: 12), child: DropdownButton<String?>(isExpanded: true, value: category, hint: const Text('All categories'), items: const [DropdownMenuItem(value: null, child: Text('All categories')), DropdownMenuItem(value: 'preferences', child: Text('Preferences')), DropdownMenuItem(value: 'project', child: Text('Project')), DropdownMenuItem(value: 'decisions', child: Text('Decisions')), DropdownMenuItem(value: 'tasks', child: Text('Tasks')), DropdownMenuItem(value: 'milestones', child: Text('Milestones')), DropdownMenuItem(value: 'notes', child: Text('Notes'))], onChanged: (value) => ref.read(memoryCategoryProvider.notifier).setCategory(value))),
		Expanded(child: memories.when(
		  loading: () => const Center(child: CircularProgressIndicator()),
		  error: (error, _) => Center(child: TextButton(onPressed: () => ref.invalidate(memoriesProvider), child: const Text('Unable to load memory. Retry'))),
		  data: (items) => items.isEmpty ? const Center(child: Text('No saved memories.')) : RefreshIndicator(onRefresh: () async => ref.refresh(memoriesProvider.future), child: ListView.builder(itemCount: items.length, itemBuilder: (_, index) => _MemoryTile(memory: items[index], onEdit: () => _edit(items[index])))),
		)),
	  ]),
	  floatingActionButton: FloatingActionButton(onPressed: () => _edit(), child: const Icon(Icons.add)),
	);
  }

  Future<void> _edit([Memory? memory]) async {
	final result = await showDialog<_MemoryDraft>(context: context, builder: (_) => _MemoryDialog(memory: memory));
	if (result == null || !mounted) return;
	try {
	  if (memory == null) {
		await ref.read(memoryActionsProvider).create(title: result.title, category: result.category, text: result.text);
	  } else {
		await ref.read(memoryActionsProvider).update(memory.id, title: result.title, category: result.category, text: result.text);
	  }
	} catch (_) {
	  if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Memory could not be saved')));
	}
  }
}

class _MemoryTile extends ConsumerWidget {
  const _MemoryTile({required this.memory, required this.onEdit});
  final Memory memory;
  final VoidCallback onEdit;
  @override
  Widget build(BuildContext context, WidgetRef ref) => Card(child: ListTile(
	title: Text(memory.title),
	subtitle: Text('${memory.category} • ${memory.text}', maxLines: 2, overflow: TextOverflow.ellipsis),
	onTap: onEdit,
	trailing: PopupMenuButton<String>(onSelected: (action) async {
	  if (action == 'archive') await ref.read(memoryActionsProvider).archive(memory.id);
	  if (action == 'delete' && context.mounted && await _confirmDelete(context)) await ref.read(memoryActionsProvider).delete(memory.id);
	}, itemBuilder: (_) => const [PopupMenuItem(value: 'archive', child: Text('Archive')), PopupMenuItem(value: 'delete', child: Text('Delete permanently'))]),
  ));
}

Future<bool> _confirmDelete(BuildContext context) async => await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Delete memory?'), content: const Text('This cannot be undone.'), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete'))])) ?? false;

class _MemoryDraft {
  const _MemoryDraft(this.title, this.category, this.text);
  final String title;
  final String category;
  final String text;
}

class _MemoryDialog extends StatefulWidget {
  const _MemoryDialog({this.memory});
  final Memory? memory;
  @override
  State<_MemoryDialog> createState() => _MemoryDialogState();
}

class _MemoryDialogState extends State<_MemoryDialog> {
  late final title = TextEditingController(text: widget.memory?.title);
  late final category = TextEditingController(text: widget.memory?.category ?? 'notes');
  late final text = TextEditingController(text: widget.memory?.text);
  @override
  void dispose() { title.dispose(); category.dispose(); text.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => AlertDialog(title: Text(widget.memory == null ? 'Add memory' : 'Edit memory'), content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: title, decoration: const InputDecoration(labelText: 'Title')), TextField(controller: category, decoration: const InputDecoration(labelText: 'Category')), TextField(controller: text, minLines: 3, maxLines: 8, decoration: const InputDecoration(labelText: 'Content'))])), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { if (title.text.trim().isEmpty || category.text.trim().isEmpty || text.text.trim().isEmpty) return; Navigator.pop(context, _MemoryDraft(title.text.trim(), category.text.trim(), text.text.trim())); }, child: const Text('Save'))]);
}
