import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../data/analysis.dart';
import '../data/document.dart';
import '../data/documents_api.dart';
import 'documents_screen.dart';

final documentProvider = FutureProvider.autoDispose
    .family<Document, String>((ref, id) => ref.watch(documentsApiProvider).get(id));

final extractedPagesProvider = FutureProvider.autoDispose
    .family<List<ExtractedPage>, String>((ref, id) {
      return ref.watch(documentsApiProvider).pages(id);
    });

final documentInsightsProvider = FutureProvider.autoDispose
    .family<List<DocumentInsight>, String>((ref, id) {
      return ref.watch(documentsApiProvider).insights(id);
    });

final extractionProvider = FutureProvider.autoDispose
    .family<ExtractionDetails?, String>((ref, id) {
      return ref.watch(documentsApiProvider).extraction(id);
    });

final documentAnalysisProvider = FutureProvider.autoDispose
    .family<DocumentAnalysis?, String>((ref, id) async {
      try {
        return await ref.watch(documentsApiProvider).analysis(id);
      } on DioException catch (error) {
        if (error.response?.statusCode == 404) return null;
        rethrow;
      }
    });

class DocumentDetailScreen extends ConsumerWidget {
  const DocumentDetailScreen({required this.documentId, super.key});

  final String documentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final document = ref.watch(documentProvider(documentId));
    final pages = ref.watch(extractedPagesProvider(documentId));
    final extraction = ref.watch(extractionProvider(documentId));
    final analysis = ref.watch(documentAnalysisProvider(documentId));
    final insights = ref.watch(documentInsightsProvider(documentId));
    return Scaffold(
      appBar: AppBar(
        title: const Text('Extracted content'),
        actions: [
          IconButton(
            tooltip: 'Refresh status',
            onPressed: () {
              ref.invalidate(documentProvider(documentId));
              ref.invalidate(extractionProvider(documentId));
              ref.invalidate(extractedPagesProvider(documentId));
            },
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Column(
        children: [
          document.when(
            loading: () => const LinearProgressIndicator(),
            error: (error, _) => Padding(
              padding: const EdgeInsets.all(16),
              child: Text('Unable to load document details: $error'),
            ),
            data: (value) => _DocumentSummary(
              value,
              onRetry: value.processingStatus == 'failed'
                  ? () async {
                      await ref.read(documentsApiProvider).retryExtraction(documentId);
                      ref.invalidate(documentProvider(documentId));
                      ref.invalidate(extractionProvider(documentId));
                      ref.invalidate(extractedPagesProvider(documentId));
                    }
                  : null,
            ),
          ),
          extraction.when(
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
            data: (value) => value?.errorSummary == null
                ? const SizedBox.shrink()
                : Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text('Extraction error: ${value!.errorSummary}'),
                  ),
          ),
           _AnalysisPanel(documentId: documentId, analysis: analysis, insights: insights, ref: ref),
          Expanded(
            child: pages.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) =>
                  Center(child: Text('Unable to load extraction: $error')),
              data: (items) => items.isEmpty
                  ? Center(
                       child: document.asData?.value.processingStatus == 'failed'
                          ? const Text('Extraction failed. Use Retry to try again.')
                           : document.asData?.value.processingStatus == 'completed'
                              ? const Text('No text was extracted.')
                              : const Text('Extraction is queued or processing.'),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: items.length,
                      itemBuilder: (context, index) => Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SelectableText(
                                items[index].text.isEmpty
                                ? '[Empty page]'
                                : items[index].text,
                              ),
                              if (items[index].errorSummary != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 8),
                                  child: Text('Page error: ${items[index].errorSummary}'),
                                ),
                            ],
                          ),
                        ),
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
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

class _DocumentSummary extends StatelessWidget {
  const _DocumentSummary(this.document, {this.onRetry});

  final Document document;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) => Card(
        margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
        child: ListTile(
          leading: Icon(_documentIcon(document.documentType)),
          title: Text(document.originalFilename),
          subtitle: Text(
            '${document.documentType?.toUpperCase() ?? 'FILE'} • ${_formatBytes(document.fileSize)}\n'
            'Processing: ${document.processingStatus} • Extraction: ${document.extractionStatus}',
          ),
          trailing: onRetry == null
              ? null
              : TextButton(onPressed: onRetry, child: const Text('Retry')),
        ),
      );
}

class _AnalysisPanel extends ConsumerWidget {
  const _AnalysisPanel({
    required this.documentId,
    required this.analysis,
    required this.insights,
    required this.ref,
  });

  final String documentId;
  final AsyncValue<DocumentAnalysis?> analysis;
  final AsyncValue<List<DocumentInsight>> insights;
  final WidgetRef ref;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: analysis.when(
          loading: () => const LinearProgressIndicator(),
          error: (error, _) => _AnalysisAction(
            label: 'Analysis unavailable: $error',
            onPressed: () => _analyze(context),
          ),
          data: (value) => value == null
              ? _AnalysisAction(label: 'Analyze document', onPressed: () => _analyze(context))
              : _AnalysisContent(value, insights: insights, onRetry: () => _analyze(context)),
        ),
      ),
    );
  }

  Future<void> _analyze(BuildContext context) async {
    try {
      await ref.read(documentsApiProvider).analyze(documentId);
      ref.invalidate(documentAnalysisProvider(documentId));
      ref.invalidate(documentInsightsProvider(documentId));
    } on DioException catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.response?.data?['detail']?.toString() ?? 'Analysis failed')),
        );
      }
    }
  }
}

class _AnalysisAction extends StatelessWidget {
  const _AnalysisAction({required this.label, required this.onPressed});

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) => Row(
        children: [
          Expanded(child: Text(label)),
          TextButton(onPressed: onPressed, child: const Text('Analyze')),
        ],
      );
}

class _AnalysisContent extends StatelessWidget {
  const _AnalysisContent(this.value, {required this.insights, required this.onRetry});

  final DocumentAnalysis value;
  final AsyncValue<List<DocumentInsight>> insights;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    if (value.status == 'processing') {
      return const Column(children: [LinearProgressIndicator(), SizedBox(height: 8), Text('Analysis in progress…')]);
    }
    if (value.status == 'failed' || value.status == 'provider_unavailable') {
      return _AnalysisAction(label: value.errorSummary ?? 'Analysis failed', onPressed: onRetry);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(value.summary ?? 'Analysis completed', style: Theme.of(context).textTheme.titleMedium),
        if (value.facts.isNotEmpty) ...[
          const SizedBox(height: 12),
          const Text('Key findings', style: TextStyle(fontWeight: FontWeight.bold)),
          ...value.facts.take(5).map((item) => Text('• ${item['value'] ?? item['fact_type']}')),
        ],
        if (value.recommendations.isNotEmpty) ...[
          const SizedBox(height: 12),
          const Text('Recommendations', style: TextStyle(fontWeight: FontWeight.bold)),
          ...value.recommendations.take(5).map((item) => Text('• ${item['description'] ?? ''}')),
        ],
        const SizedBox(height: 12),
        const Text('Insights', style: TextStyle(fontWeight: FontWeight.bold)),
        insights.when(
          loading: () => const LinearProgressIndicator(),
          error: (error, _) => Text('Unable to load insights: $error'),
          data: (items) => items.isEmpty
              ? const Text('No additional insights were generated.')
              : Column(
                  children: items
                      .take(5)
                      .map((item) => ListTile(
                            dense: true,
                            title: Text(item.title),
                            subtitle: Text(item.description),
                          ))
                      .toList(),
                ),
        ),
      ],
    );
  }
}
