import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/application/auth_provider.dart';
import '../data/memory.dart';
import '../data/memory_repository.dart';

final memoryRepositoryProvider = Provider<MemoryRepository>((ref) => MemoryRepository(ref.watch(protectedApiClientProvider)));
final memorySearchProvider = NotifierProvider<MemorySearchNotifier, String>(MemorySearchNotifier.new);
final memoryCategoryProvider = NotifierProvider<MemoryCategoryNotifier, String?>(MemoryCategoryNotifier.new);

class MemorySearchNotifier extends Notifier<String> {
  @override
  String build() => '';

  void setQuery(String value) => state = value;
}

class MemoryCategoryNotifier extends Notifier<String?> {
  @override
  String? build() => null;

  void setCategory(String? value) => state = value;
}

final memoriesProvider = FutureProvider.autoDispose<List<Memory>>((ref) {
  return ref.watch(memoryRepositoryProvider).list(
		search: ref.watch(memorySearchProvider),
		category: ref.watch(memoryCategoryProvider),
	  );
});

final memoryActionsProvider = Provider<MemoryActions>((ref) => MemoryActions(ref));

class MemoryActions {
  MemoryActions(this._ref);
  final Ref _ref;
  MemoryRepository get _repository => _ref.read(memoryRepositoryProvider);

  void _refresh() => _ref.invalidate(memoriesProvider);

  Future<Memory> create({required String title, required String category, required String text}) async {
	final memory = await _repository.create(title: title, category: category, text: text);
	_refresh();
	return memory;
  }

  Future<Memory> update(String id, {required String title, required String category, required String text}) async {
	final memory = await _repository.update(id, title: title, category: category, text: text);
	_refresh();
	return memory;
  }

  Future<void> archive(String id) async {
	await _repository.archive(id);
	_refresh();
  }

  Future<void> delete(String id) async {
	await _repository.delete(id);
	_refresh();
  }
}
