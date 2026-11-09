import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:orvexa/features/home.dart';
import 'package:orvexa/features/dashboard/presentation/dashboard_screen.dart';
import 'package:orvexa/features/auth/application/auth_provider.dart';
import 'package:orvexa/features/auth/presentation/login_screen.dart';
import 'package:orvexa/features/auth/presentation/register_screen.dart';
import '../../features/settings/presentation/settings_screen.dart';
import '../../features/documents/presentation/documents_screen.dart';
import '../../features/documents/presentation/document_detail_screen.dart';
import '../../features/tasks/data/task.dart';
import '../../features/tasks/presentation/task_detail_screen.dart';
import '../../features/tasks/presentation/task_form_screen.dart';
import '../../features/tasks/presentation/task_screen.dart';
import '../../features/goals/data/goal.dart';
import '../../features/goals/presentation/goal_detail_screen.dart';
import '../../features/goals/presentation/goal_form_screen.dart';
import '../../features/goals/presentation/goal_screen.dart';
import '../../features/memory/presentation/memory_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  var authState = ref.read(authProvider);
  late final GoRouter router;
  router = GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isAuthRoute =
          state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';
      if (authState.isLoading) {
        return isAuthRoute ? null : '/login';
      }
      if (authState.value == null && !isAuthRoute) {
        return '/login';
      }
      if (authState.value != null && isAuthRoute) {
        return '/dashboard';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/tasks',
        name: 'tasks',
        builder: (context, state) => const TasksScreen(),
      ),
      GoRoute(
        path: '/tasks/new',
        name: 'task-create',
        builder: (context, state) => const TaskFormScreen(),
      ),
      GoRoute(
        path: '/tasks/:id/edit',
        name: 'task-edit',
        builder: (context, state) => TaskFormScreen(task: state.extra as Task?),
      ),
      GoRoute(
        path: '/tasks/:id',
        name: 'task-detail',
        builder: (context, state) => TaskDetailScreen(taskId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/goals',
        name: 'goals',
        builder: (context, state) => const GoalsScreen(),
      ),
      GoRoute(
        path: '/goals/new',
        name: 'goal-create',
        builder: (context, state) => const GoalFormScreen(),
      ),
      GoRoute(
        path: '/goals/:id/edit',
        name: 'goal-edit',
        builder: (context, state) => GoalFormScreen(goal: state.extra as Goal?),
      ),
      GoRoute(
        path: '/goals/:id',
        name: 'goal-detail',
        builder: (context, state) => GoalDetailScreen(goalId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/',
        name: 'home',
        redirect: (context, state) => '/dashboard',
      ),
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/status',
        name: 'status',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/documents/:id',
        name: 'document-detail',
        builder: (context, state) =>
            DocumentDetailScreen(documentId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/documents',
        name: 'documents',
        builder: (context, state) => const DocumentsScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/memory',
        name: 'memory',
        builder: (context, state) => const MemoryScreen(),
      ),
    ],
  );
  ref.listen(authProvider, (previous, next) {
    authState = next;
    router.refresh();
  });
  ref.onDispose(router.dispose);
  return router;
});
