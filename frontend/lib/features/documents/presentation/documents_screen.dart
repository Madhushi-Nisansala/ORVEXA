import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/application/auth_provider.dart';
import '../data/document.dart';
import '../data/documents_api.dart';
import '../../dashboard/application/dashboard_provider.dart';

const _maximumDocumentSizeBytes = DocumentsApi.maximumFileSizeBytes;
const _supportedDocumentExtensions = DocumentsApi.supportedExtensions;

final documentsApiProvider = Provider<DocumentsApi>((ref) {
  return DocumentsApi(ref.watch(protectedApiClientProvider));
});

final documentsProvider = FutureProvider.autoDispose<List<Document>>((ref) {
  return ref.watch(documentsApiProvider).list();
}, retry: (_, error) => null);

class DocumentsScreen extends ConsumerWidget {
  const DocumentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final documents = ref.watch(documentsProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        leading: BackButton(
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/dashboard');
            }
          },
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _pickAndUpload(context, ref),
        icon: const Icon(Icons.upload_file),
        label: const Text('Upload'),
      ),
      body: documents.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorState(
          message: _documentErrorMessage(error),
          onRetry: () => ref.invalidate(documentsProvider),
        ),
        data: (items) => items.isEmpty
            ? const Center(child: Text('No documents uploaded yet.'))
            : RefreshIndicator(
                onRefresh: () async => ref.invalidate(documentsProvider),
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  itemBuilder: (context, index) => _DocumentTile(
                    document: items[index],
                    onArchive: () => _archive(context, ref, items[index]),
                    onDelete: () => _delete(context, ref, items[index]),
                  ),
                ),
              ),
      ),
    );
  }

  Future<void> _pickAndUpload(BuildContext context, WidgetRef ref) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: _supportedDocumentExtensions.toList(),
      allowMultiple: true,
      withData: true,
    );
    if (result == null || !context.mounted) return;
    final messenger = ScaffoldMessenger.of(context);
    final api = ref.read(documentsApiProvider);
    var uploaded = 0;
    final failures = <String>[];
    final failedFiles = <PlatformFile>[];
    for (final file in result.files) {
      final extension = file.extension?.toLowerCase();
      final validationError = _validateSelectedFile(file, extension);
      if (validationError != null) {
        failures.add('${file.name}: $validationError');
        continue;
      }
      try {
        final cancelToken = CancelToken();
        await api.upload(file, (sent, total) {
          if (context.mounted && total > 0) {
            messenger.hideCurrentSnackBar();
            messenger.showSnackBar(
              SnackBar(
                content: Text(
                  'Uploading ${file.name} (${sent * 100 ~/ total}%)',
                ),
                action: SnackBarAction(
                  label: 'Cancel',
                  onPressed: cancelToken.cancel,
                ),
              ),
            );
          }
        }, cancelToken: cancelToken);
        uploaded++;
      } catch (error) {
        failures.add('${file.name}: ${_uploadErrorMessage(error)}');
        if (error is! DioException || !CancelToken.isCancel(error)) {
          failedFiles.add(file);
        }
      }
    }
    if (context.mounted) {
      ref.invalidate(documentsProvider);
      ref.invalidate(dashboardProvider);
      final message = failures.isEmpty
          ? '$uploaded document${uploaded == 1 ? '' : 's'} uploaded and queued.'
          : '${failures.length} upload${failures.length == 1 ? '' : 's'} failed. ${failures.join('; ')}';
       messenger.showSnackBar(
         SnackBar(
           content: Text(message),
           action: failedFiles.isEmpty
               ? null
               : SnackBarAction(
                   label: 'Retry',
                   onPressed: () => _retryUploads(context, ref, failedFiles),
                 ),
         ),
       );
    }
  }

  Future<void> _retryUploads(
    BuildContext context,
    WidgetRef ref,
    List<PlatformFile> files,
  ) async {
    final api = ref.read(documentsApiProvider);
    var succeeded = 0;
    for (final file in files) {
      try {
        await api.upload(file, null);
        succeeded++;
      } catch (_) {
        // The original failure is already visible; the list refresh exposes the
        // server state after any successful retry.
      }
    }
    if (context.mounted) {
      ref.invalidate(documentsProvider);
      ref.invalidate(dashboardProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$succeeded document${succeeded == 1 ? '' : 's'} retried successfully.')),
      );
    }
  }

  String? _validateSelectedFile(PlatformFile file, String? extension) {
    if (file.size <= 0) return 'The file is empty.';
    if (file.size > _maximumDocumentSizeBytes) return 'Maximum size is 25 MB.';
    if (extension == null ||
        !_supportedDocumentExtensions.contains(extension)) {
      return 'Supported formats: PDF, DOCX, TXT, CSV, PNG, JPG, and JPEG.';
    }
    return null;
  }

  String _uploadErrorMessage(Object error) {
    if (error is DioException) {
      switch (error.response?.statusCode) {
        case 400:
          return 'The upload request is invalid.';
        case 401:
          return 'Your session has expired. Please sign in again.';
        case 403:
          return 'You do not have permission to upload documents.';
        case 409:
          return 'A document with the same content already exists.';
        case 413:
          return 'The file is larger than the server limit of 25 MB.';
        case 415:
          return 'This file type is not supported.';
        case 422:
          return 'The file content or metadata is invalid.';
        case 500:
          return 'The server could not process the upload.';
      }
    }
    if (error is DioException &&
        (error.type == DioExceptionType.connectionError ||
            error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.receiveTimeout)) {
      return 'Unable to reach the ORVEXA server.';
    }
    return 'The server rejected the upload.';
  }

  Future<void> _archive(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    try {
      await ref.read(documentsApiProvider).archive(document.id);
      ref.invalidate(documentsProvider);
      ref.invalidate(dashboardProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Document archived.')),
        );
      }
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Unable to archive document: ${_documentErrorMessage(error)}')),
        );
      }
    }
  }

  Future<void> _delete(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete document?'),
        content: Text('Delete ${document.originalFilename}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      try {
        await ref.read(documentsApiProvider).delete(document.id);
        ref.invalidate(documentsProvider);
        ref.invalidate(dashboardProvider);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Document deleted.')),
          );
        }
      } catch (error) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Unable to delete document: ${_documentErrorMessage(error)}')),
          );
        }
      }
    }
  }
}

class _DocumentTile extends StatelessWidget {
  const _DocumentTile({
    required this.document,
    required this.onArchive,
    required this.onDelete,
  });

  final Document document;
  final VoidCallback onArchive;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      leading: Icon(_documentIcon(document.documentType)),
      title: Text(document.originalFilename),
      onTap: () => context.push('/documents/${document.id}'),
       subtitle: Text(
         '${document.documentType?.toUpperCase() ?? 'FILE'} • ${_formatBytes(document.fileSize)} • ${document.processingStatus} • ${document.extractionStatus}${document.createdAt == null ? '' : ' • ${_formatDate(document.createdAt!)}'}',
       ),
      trailing: PopupMenuButton<String>(
        onSelected: (value) => value == 'archive' ? onArchive() : onDelete(),
        itemBuilder: (context) => const [
          PopupMenuItem(value: 'archive', child: Text('Archive')),
          PopupMenuItem(value: 'delete', child: Text('Delete')),
        ],
      ),
    ),
  );
}

IconData _documentIcon(String? type) {
  switch (type?.toLowerCase()) {
    case 'pdf':
      return Icons.picture_as_pdf_outlined;
    case 'png':
    case 'jpg':
    case 'jpeg':
      return Icons.image_outlined;
    case 'csv':
      return Icons.table_chart_outlined;
    case 'docx':
      return Icons.article_outlined;
    default:
      return Icons.description_outlined;
  }
}

String _formatBytes(int bytes) {
  if (bytes < 1024) return '$bytes B';
  if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
  return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
}

String _formatDate(DateTime value) {
  final local = value.toLocal();
  return '${local.year}-${local.month.toString().padLeft(2, '0')}-${local.day.toString().padLeft(2, '0')}';
}

String _documentErrorMessage(Object error) {
  if (error is DioException) {
    final status = error.response?.statusCode;
    if (status == 401) return 'Your session has expired. Please sign in again.';
    if (status != null && status >= 500) {
      return 'The ORVEXA server is unavailable. Please try again.';
    }
    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Unable to reach the ORVEXA server. Check your connection and try again.';
    }
  }
  return 'Unable to load documents. Please try again.';
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) => Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(message, textAlign: TextAlign.center),
        const SizedBox(height: 12),
        OutlinedButton(onPressed: onRetry, child: const Text('Retry')),
      ],
    ),
  );
}
