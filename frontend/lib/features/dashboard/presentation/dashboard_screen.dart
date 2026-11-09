import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';

import '../../auth/application/auth_provider.dart';
import '../../documents/data/document.dart';
import '../application/dashboard_provider.dart';
import '../data/dashboard_models.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('ORVEXA'),
        actions: [
          IconButton(
            tooltip: 'Tasks',
            onPressed: () => context.go('/tasks'),
            icon: const Icon(Icons.checklist),
          ),
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
          const SizedBox(width: 8),
        ],
      ),
      body: auth.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => const Center(
          child: Text('Unable to load your profile. Please sign in again.'),
        ),
        data: (user) {
          final name = user?.fullName?.trim().isNotEmpty == true
              ? user!.fullName!.trim()
              : user?.email ?? 'there';
          final dashboard = ref.watch(dashboardProvider);
          return dashboard.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => _DashboardError(
              message: dashboardErrorMessage(error),
              onRetry: () => ref.invalidate(dashboardProvider),
            ),
            data: (data) => RefreshIndicator(
              onRefresh: () async => ref.refresh(dashboardProvider.future),
              child: _DashboardContent(name: name, data: data),
            ),
          );
        },
      ),
    );
  }
}

class _PartialFailureBanner extends StatelessWidget {
  const _PartialFailureBanner({required this.errors});

  final Map<String, Object> errors;

  @override
  Widget build(BuildContext context) => Card(
        color: Theme.of(context).colorScheme.errorContainer,
        child: ListTile(
          leading: const Icon(Icons.warning_amber_outlined),
          title: const Text('Some dashboard data is unavailable'),
          subtitle: Text('Failed sections: ${errors.keys.join(', ')}. Pull to refresh or retry later.'),
        ),
      );
}

class _Statistics extends StatelessWidget {
  const _Statistics({required this.data});

  final DashboardData data;

  @override
  Widget build(BuildContext context) => Wrap(
    spacing: 16,
    runSpacing: 16,
    children: [
      _StatCard(label: 'Total Documents', value: data.totalDocuments),
      _StatCard(label: 'Total Tasks', value: data.totalTasks),
      _StatCard(label: 'Total Goals', value: data.totalGoals),
      _StatCard(label: 'Total Insights', value: data.totalInsights),
    ],
  );
}

class _StatCard extends StatelessWidget {
  const _StatCard({required this.label, required this.value});

  final String label;
  final int value;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 220,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label),
            const SizedBox(height: 8),
            Text('$value', style: Theme.of(context).textTheme.headlineMedium),
          ],
        ),
      ),
    ),
  );
}

class _RecentDocuments extends StatelessWidget {
  const _RecentDocuments(this.documents);

  final List<Document> documents;

  @override
  Widget build(BuildContext context) => _SectionCard(
    title: 'Recent Documents',
    action: TextButton(
      onPressed: () => context.push('/documents'),
      child: const Text('View All Documents'),
    ),
    child: documents.isEmpty
        ? const Text('No documents uploaded yet.')
        : Column(
            children: documents
                .map(
                  (document) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.description_outlined),
                    title: Text(document.originalFilename),
                    subtitle: Text(
                       '${document.mimeType} • ${document.processingStatus} • ${document.extractionStatus}${document.createdAt == null ? '' : ' • ${_formatDate(document.createdAt!)}'}',
                    ),
                    onTap: () => context.push('/documents/${document.id}'),
                  ),
                )
                .toList(),
          ),
  );
}

class _RecentActions extends StatelessWidget {
  const _RecentActions({required this.data});

  final DashboardData data;

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Expanded(
        child: _SummaryList(
          title: 'Recent Tasks',
          items: data.recentTasks
              .map((task) => '${task.title} • ${task.status}${task.dueAt == null ? '' : ' • Due ${_formatDate(task.dueAt!)}'}')
              .toList(),
        ),
      ),
      const SizedBox(width: 16),
      Expanded(
        child: _SummaryList(
          title: 'Recent Goals',
          items: data.recentGoals
              .map((goal) => '${goal.title} • ${goal.status} • ${goal.progress}%${goal.targetDate == null ? '' : ' • Target ${_formatDate(goal.targetDate!)}'}')
              .toList(),
        ),
      ),
    ],
  );
}

class _SummaryList extends StatelessWidget {
  const _SummaryList({required this.title, required this.items});

  final String title;
  final List<String> items;

  @override
  Widget build(BuildContext context) => _SectionCard(
    title: title,
    child: items.isEmpty
        ? Text('No ${title.toLowerCase()} available yet.')
        : Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: items
                .map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(item),
                  ),
                )
                .toList(),
          ),
  );
}

class _Insights extends StatelessWidget {
  const _Insights(this.insights);

  final List<InsightSummary> insights;

  @override
  Widget build(BuildContext context) => _SectionCard(
    title: 'Insights',
    child: insights.isEmpty
        ? const Text('No insights available yet.')
        : Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: insights
                .take(5)
                .map(
                  (insight) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(insight.title),
                    subtitle: Text(insight.description),
                  ),
                )
                .toList(),
          ),
  );
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child, this.action});

  final String title;
  final Widget child;
  final Widget? action;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              ?action,
            ],
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    ),
  );
}

class _DashboardError extends StatelessWidget {
  const _DashboardError({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          OutlinedButton(onPressed: onRetry, child: const Text('Retry')),
        ],
      ),
    ),
  );
}

String dashboardErrorMessage(Object error) {
  if (error is DioException) {
    final status = error.response?.statusCode;
    if (status == 401) return 'Your session has expired. Please sign in again.';
    if (status == 403) {
      return 'You do not have permission to load this dashboard.';
    }
    if (status != null && status >= 500) {
      return 'The ORVEXA server is unavailable. Please try again.';
    }
    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Unable to reach the ORVEXA server. Check your connection and try again.';
    }
  }
  return 'Unable to load dashboard data. Please try again.';
}

String _formatDate(DateTime value) =>
    '${value.month}/${value.day}/${value.year}';

class _DashboardContent extends StatelessWidget {
  const _DashboardContent({required this.name, required this.data});

  final String name;
  final DashboardData data;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) => SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1180),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _WelcomeSection(name: name),
              const SizedBox(height: 32),
              _Statistics(data: data),
              if (data.hasPartialFailures) ...[
                const SizedBox(height: 12),
                _PartialFailureBanner(errors: data.errors),
              ],
              const SizedBox(height: 32),
              Text(
                'Workspace',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              GridView.extent(
                maxCrossAxisExtent: 420,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisExtent: 220,
                children: [
                  _NavigationCard(
                    icon: Icons.folder_outlined,
                    title: 'Documents',
                    description: 'Upload, review and manage your documents.',
                    onTap: () => context.push('/documents'),
                  ),
                  const _NavigationCard(
                    icon: Icons.auto_awesome_outlined,
                    title: 'Intelligence & Insights',
                    description: 'Review insights from your documents below.',
                    comingSoon: true,
                  ),
                  const _NavigationCard(
                    icon: Icons.flag_outlined,
                    title: 'Tasks & Goals',
                    description: 'Plan and track your next actions.',
                    comingSoon: true,
                  ),
                  _NavigationCard(
                    icon: Icons.cloud_outlined,
                    title: 'Backend Status',
                    description: 'Check service and database connectivity.',
                    onTap: () => context.go('/status'),
                  ),
                  _NavigationCard(
                    icon: Icons.settings_outlined,
                    title: 'Settings',
                    description: 'Configure appearance and preferences.',
                    onTap: () => context.go('/settings'),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              _RecentDocuments(data.recentDocuments),
              const SizedBox(height: 24),
              _RecentActions(data: data),
              const SizedBox(height: 24),
              _Insights(data.insights),
              const SizedBox(height: 32),
              Card(
                color: Theme.of(context).colorScheme.primaryContainer,
                child: const Padding(
                  padding: EdgeInsets.all(24),
                  child: Row(
                    children: [
                      Icon(Icons.lightbulb_outline),
                      SizedBox(width: 16),
                      Expanded(
                        child: Text(
                          'ORVEXA helps you turn information into clearer next steps.',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class _WelcomeSection extends StatelessWidget {
  const _WelcomeSection({required this.name});
  final String name;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          Icon(
            Icons.auto_awesome,
            size: 40,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(width: 12),
          Text(
            'ORVEXA',
            style: Theme.of(
              context,
            ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
        ],
      ),
      const SizedBox(height: 20),
      Text('Welcome, $name', style: Theme.of(context).textTheme.headlineSmall),
      const SizedBox(height: 8),
      Text(
        'Understand More. Act Smarter.',
        style: Theme.of(context).textTheme.titleLarge,
      ),
    ],
  );
}

class _NavigationCard extends StatelessWidget {
  const _NavigationCard({
    required this.icon,
    required this.title,
    required this.description,
    this.onTap,
    this.comingSoon = false,
  });
  final IconData icon;
  final String title;
  final String description;
  final VoidCallback? onTap;
  final bool comingSoon;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                icon,
                size: 30,
                color: onTap == null ? scheme.outline : scheme.primary,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text(description),
                    if (comingSoon) ...[
                      const SizedBox(height: 8),
                      const Chip(
                        visualDensity: VisualDensity.compact,
                        padding: EdgeInsets.symmetric(horizontal: 8),
                        label: Text('Coming soon'),
                      ),
                    ],
                  ],
                ),
              ),
              if (onTap != null) const Icon(Icons.arrow_forward, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
