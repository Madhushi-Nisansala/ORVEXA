import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'home/application/health_provider.dart';
import 'auth/application/auth_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;
    final health = ref.watch(healthProvider);
    final isChecking = health.isLoading;
    final result = health.value;
    final statusText = isChecking
        ? 'Checking...'
        : result?.connected == true
        ? 'Connected'
        : 'Disconnected';
    final statusColor = result?.connected == true ? Colors.green : scheme.error;
    final checkedAt = result == null ? null : _formatTime(result.checkedAt);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ORVEXA'),
        actions: [
          IconButton(
            tooltip: 'Settings',
            onPressed: () => context.go('/settings'),
            icon: const Icon(Icons.settings_outlined),
          ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
            icon: const Icon(Icons.logout),
          ),
          IconButton(
            tooltip: 'Documents',
            onPressed: () => context.go('/documents'),
            icon: const Icon(Icons.folder_outlined),
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.auto_awesome, size: 64, color: scheme.primary),
                const SizedBox(height: 24),
                Text(
                  'ORVEXA',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Understand More. Act Smarter.',
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                Card(
                  child: ListTile(
                    leading: Icon(Icons.cloud_outlined, color: scheme.primary),
                    title: const Text('Backend status'),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          checkedAt == null
                              ? 'Last checked: Not available'
                              : 'Last checked: $checkedAt',
                        ),
                        if (result?.databaseStatus != null)
                          Text('Database: ${result!.databaseStatus}'),
                      ],
                    ),
                    trailing: Chip(
                      label: Text(statusText),
                      labelStyle: TextStyle(color: statusColor),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: isChecking
                      ? null
                      : () => ref.read(healthProvider.notifier).checkAgain(),
                  icon: const Icon(Icons.refresh),
                  label: Text(result == null ? 'Check Again' : 'Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    final local = time.toLocal();
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    final second = local.second.toString().padLeft(2, '0');
    return '$hour:$minute:$second';
  }
}
