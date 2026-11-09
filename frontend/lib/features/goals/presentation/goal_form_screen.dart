import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../application/goals_provider.dart';
import '../data/goal.dart';

class GoalFormScreen extends ConsumerStatefulWidget {
  const GoalFormScreen({super.key, this.goal});
  final Goal? goal;
  @override
  ConsumerState<GoalFormScreen> createState() => _GoalFormScreenState();
}

class _GoalFormScreenState extends ConsumerState<GoalFormScreen> {
  final _key = GlobalKey<FormState>();
  late final TextEditingController _title, _description, _category, _progress;
  late GoalStatus _status;
  DateTime? _targetDate;
  bool _saving = false;

  @override
  void initState() { super.initState(); final goal = widget.goal; _title = TextEditingController(text: goal?.title); _description = TextEditingController(text: goal?.description); _category = TextEditingController(text: goal?.category); _progress = TextEditingController(text: '${goal?.progress ?? 0}'); _status = goal?.status ?? GoalStatus.notStarted; _targetDate = goal?.targetDate; }
  @override
  void dispose() { _title.dispose(); _description.dispose(); _category.dispose(); _progress.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: Text(widget.goal == null ? 'Create goal' : 'Edit goal')), body: Form(key: _key, child: ListView(padding: const EdgeInsets.all(20), children: [
	TextFormField(controller: _title, decoration: const InputDecoration(labelText: 'Title'), validator: (value) => value == null || value.trim().isEmpty ? 'Title is required' : null),
	const SizedBox(height: 12), TextFormField(controller: _description, decoration: const InputDecoration(labelText: 'Description'), maxLines: 4),
	const SizedBox(height: 12), TextFormField(controller: _category, decoration: const InputDecoration(labelText: 'Category')),
	const SizedBox(height: 12), DropdownButtonFormField<GoalStatus>(value: _status, decoration: const InputDecoration(labelText: 'Status'), items: GoalStatus.values.map((status) => DropdownMenuItem(value: status, child: Text(status.label))).toList(), onChanged: (value) => setState(() => _status = value ?? GoalStatus.notStarted)),
	const SizedBox(height: 12), TextFormField(controller: _progress, decoration: const InputDecoration(labelText: 'Progress (%)'), keyboardType: TextInputType.number, validator: (value) { final progress = int.tryParse(value ?? ''); return progress == null || progress < 0 || progress > 100 ? 'Enter a value between 0 and 100' : null; }),
	ListTile(contentPadding: EdgeInsets.zero, title: Text(_targetDate == null ? 'No target date' : 'Target ${_date(_targetDate!)}'), trailing: IconButton(icon: const Icon(Icons.event), onPressed: _pickDate)),
	const SizedBox(height: 20), FilledButton(onPressed: _saving ? null : _save, child: _saving ? const CircularProgressIndicator() : const Text('Save goal')),
  ])));

  Future<void> _pickDate() async { final value = await showDatePicker(context: context, firstDate: DateTime.now(), lastDate: DateTime(2100), initialDate: _targetDate ?? DateTime.now()); if (value != null) setState(() => _targetDate = value); }

  Future<void> _save() async { if (!_key.currentState!.validate()) return; setState(() => _saving = true); try { final actions = ref.read(goalActionsProvider); final progress = int.parse(_progress.text); if (widget.goal == null) { await actions.create(title: _title.text.trim(), description: _description.text, category: _category.text, targetDate: _targetDate, status: _status, progress: progress); } else { await actions.update(widget.goal!.id, title: _title.text.trim(), description: _description.text, category: _category.text, targetDate: _targetDate, status: _status, progress: progress); } if (mounted) context.pop(); } catch (error) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Unable to save goal: $error'))); } finally { if (mounted) setState(() => _saving = false); } }
}

String _date(DateTime value) => '${value.month}/${value.day}/${value.year}';
