import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/tasks_provider.dart';
import '../data/task.dart';

class TaskFormScreen extends ConsumerStatefulWidget {
  const TaskFormScreen({super.key, this.task});
  final Task? task;
  @override
  ConsumerState<TaskFormScreen> createState() => _TaskFormScreenState();
}

class _TaskFormScreenState extends ConsumerState<TaskFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _title;
  late final TextEditingController _description;
  late String _priority;
  DateTime? _dueAt;
  bool _saving = false;

  @override
  void initState() { super.initState(); final task = widget.task; _title = TextEditingController(text: task?.title); _description = TextEditingController(text: task?.description); _priority = task?.priority ?? 'medium'; _dueAt = task?.dueAt; }
  @override
  void dispose() { _title.dispose(); _description.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: Text(widget.task == null ? 'Create task' : 'Edit task')), body: Form(key: _formKey, child: ListView(padding: const EdgeInsets.all(20), children: [
	TextFormField(controller: _title, decoration: const InputDecoration(labelText: 'Title'), validator: (value) => value == null || value.trim().isEmpty ? 'Title is required' : null),
	TextFormField(controller: _description, decoration: const InputDecoration(labelText: 'Description'), maxLines: 4),
	DropdownButtonFormField<String>(value: _priority, decoration: const InputDecoration(labelText: 'Priority'), items: const [DropdownMenuItem(value: 'urgent', child: Text('Urgent')), DropdownMenuItem(value: 'high', child: Text('High')), DropdownMenuItem(value: 'medium', child: Text('Medium')), DropdownMenuItem(value: 'low', child: Text('Low'))], onChanged: (value) => setState(() => _priority = value ?? 'medium')),
	ListTile(contentPadding: EdgeInsets.zero, title: Text(_dueAt == null ? 'No due date' : 'Due ${_date(_dueAt!)}'), trailing: IconButton(icon: const Icon(Icons.event), onPressed: () async { final selected = await showDatePicker(context: context, firstDate: DateTime.now(), lastDate: DateTime(2100), initialDate: _dueAt ?? DateTime.now()); if (selected != null) setState(() => _dueAt = selected); })),
	const SizedBox(height: 20), FilledButton(onPressed: _saving ? null : _save, child: _saving ? const CircularProgressIndicator() : const Text('Save task')),
  ])));

  Future<void> _save() async { if (!_formKey.currentState!.validate()) return; setState(() => _saving = true); try { final actions = ref.read(taskActionsProvider); if (widget.task == null) { await actions.create(title: _title.text.trim(), description: _description.text.trim(), priority: _priority, dueAt: _dueAt); } else { await actions.update(widget.task!.id, title: _title.text.trim(), description: _description.text.trim(), priority: _priority, dueAt: _dueAt); } if (mounted) context.pop(); } finally { if (mounted) setState(() => _saving = false); } }
}
String _date(DateTime value) => '${value.month}/${value.day}/${value.year}';
