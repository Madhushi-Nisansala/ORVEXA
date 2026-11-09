import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';

import '../../../core/network/api_client.dart';
import 'document.dart';
import 'analysis.dart';

class DocumentsApi {
  DocumentsApi(this._client);

  final ApiClient _client;

  Dio get _dio => _client.dio;

  static const maximumFileSizeBytes = 25 * 1024 * 1024;
  static const supportedExtensions = {
    'pdf',
    'docx',
    'txt',
    'csv',
    'png',
    'jpg',
    'jpeg',
  };

  Future<DocumentList> listPage({int limit = 100, int offset = 0}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/documents',
      queryParameters: {'limit': limit, 'offset': offset},
    );
    final items = response.data?['items'] as List<dynamic>? ?? const [];
    return DocumentList(
      items: items
          .map((item) => Document.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: (response.data?['total'] as num?)?.toInt() ?? 0,
    );
  }

  Future<List<DocumentInsight>> insights(String documentId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/documents/$documentId/insights',
    );
    final values = response.data?['items'] as List<dynamic>? ?? const [];
    return values
        .map((item) => DocumentInsight.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<DocumentInsight> insight(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/insights/$id');
    return DocumentInsight.fromJson(response.data!);
  }

  Future<void> deleteInsight(String id) =>
      _dio.delete<void>('/api/v1/insights/$id');

  Future<List<Document>> list() async {
    return (await listPage()).items;
  }

  Future<Document> get(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/documents/$id');
    return Document.fromJson(response.data!);
  }

  Future<Document> upload(
    PlatformFile file,
    void Function(int sent, int total)? onProgress, {
    CancelToken? cancelToken,
  }) async {
    final extension = file.extension?.toLowerCase();
    if (file.size <= 0) {
      throw StateError('The selected file is empty');
    }
    if (file.size > maximumFileSizeBytes) {
      throw StateError('The selected file exceeds the 25 MB limit');
    }
    if (extension == null || !supportedExtensions.contains(extension)) {
      throw StateError('The selected file type is not supported');
    }
    final MultipartFile multipartFile;
    if (file.path != null) {
      multipartFile = await MultipartFile.fromFile(
        file.path!,
        filename: file.name,
      );
    } else if (file.bytes != null) {
      multipartFile = MultipartFile.fromBytes(file.bytes!, filename: file.name);
    } else {
      throw StateError('The selected file could not be read');
    }

    final form = FormData.fromMap({'file': multipartFile});
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/documents',
      data: form,
      onSendProgress: onProgress,
      cancelToken: cancelToken,
    );
    return Document.fromJson(response.data!);
  }

  Future<void> archive(String id) =>
      _dio.post<void>('/api/v1/documents/$id/archive');

  Future<void> delete(String id) => _dio.delete<void>('/api/v1/documents/$id');

  Future<void> extract(String id) =>
      _dio.post<void>('/api/v1/documents/$id/extract');

  Future<void> retryExtraction(String id) =>
      _dio.post<void>('/api/v1/documents/$id/retry');

  Future<ExtractionDetails?> extraction(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/documents/$id/extraction',
      );
      return ExtractionDetails.fromJson(response.data!);
    } on DioException catch (error) {
      if (error.response?.statusCode == 404) return null;
      rethrow;
    }
  }

  Future<DocumentAnalysis> analyze(String id) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/documents/$id/analyze',
    );
    return DocumentAnalysis.fromJson(response.data!);
  }

  Future<DocumentAnalysis> analysis(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/documents/$id/analysis',
    );
    return DocumentAnalysis.fromJson(response.data!);
  }

  Future<DocumentAnalysis> retryAnalysis(String id) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/analyses/$id/retry',
    );
    return DocumentAnalysis.fromJson(response.data!);
  }

  Future<List<ExtractedPage>> pages(String id) async {
    final response = await _dio.get<List<dynamic>>(
      '/api/v1/documents/$id/pages',
    );
    return (response.data ?? const [])
        .map((item) => ExtractedPage.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}

class ExtractionDetails {
  const ExtractionDetails({
    required this.status,
    this.errorCode,
    this.errorSummary,
    this.completedAt,
  });

  final String status;
  final String? errorCode;
  final String? errorSummary;
  final DateTime? completedAt;

  factory ExtractionDetails.fromJson(Map<String, dynamic> json) {
    return ExtractionDetails(
      status: json['status']?.toString() ?? 'unknown',
      errorCode: json['error_code']?.toString(),
      errorSummary: json['error_summary']?.toString(),
      completedAt: _parseDate(json['completed_at']),
    );
  }
}

DateTime? _parseDate(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}

class ExtractedPage {
  const ExtractedPage({
    required this.pageNumber,
    required this.text,
    required this.status,
    this.method,
    this.errorSummary,
  });

  final int pageNumber;
  final String text;
  final String status;
  final String? method;
  final String? errorSummary;

  factory ExtractedPage.fromJson(Map<String, dynamic> json) {
    return ExtractedPage(
      pageNumber: (json['page_number'] as num?)?.toInt() ?? 0,
      text: json['text']?.toString() ?? '',
      status: json['extraction_status']?.toString() ?? 'unknown',
      method: json['extraction_method']?.toString(),
      errorSummary: json['error_summary']?.toString(),
    );
  }
}

class DocumentList {
  const DocumentList({required this.items, required this.total});

  final List<Document> items;
  final int total;
}
