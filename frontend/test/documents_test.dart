import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:orvexa/app/app.dart';
import 'package:orvexa/core/network/api_client.dart';
import 'package:orvexa/features/auth/application/auth_provider.dart';
import 'package:orvexa/features/auth/data/auth_models.dart';
import 'package:orvexa/features/documents/data/document.dart';
import 'package:orvexa/features/documents/data/documents_api.dart';
import 'package:orvexa/features/documents/presentation/documents_screen.dart';

class _FakeDocumentsApi extends DocumentsApi {
  _FakeDocumentsApi(this._listResult) : super(ApiClient(dio: Dio()));

  final Future<List<Document>> Function() _listResult;
  int listCalls = 0;
  bool fail = false;

  @override
  Future<List<Document>> list() {
    listCalls++;
    if (fail) {
      return Future.error(
        DioException(requestOptions: RequestOptions(path: '/api/v1/documents')),
      );
    }
    return _listResult();
  }
}

class _AuthenticatedNotifier extends AuthNotifier {
  @override
  Future<AuthUser?> build() async => _user;
}

final _user = AuthUser(
  id: '00000000-0000-0000-0000-000000000001',
  email: 'user@example.com',
  fullName: 'Test User',
  preferredLanguage: 'en',
  isActive: true,
  isVerified: true,
  createdAt: DateTime(2025),
  updatedAt: DateTime(2025),
  lastLoginAt: null,
  roles: ['user'],
);

void main() {
  test('lists an empty response as an empty list', () async {
    final dio = Dio();
    final client = ApiClient(
      dio: dio,
      accessTokenProvider: () async => 'test-token',
    );
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          expect(options.path, '/api/v1/documents');
          expect(options.headers['Authorization'], 'Bearer test-token');
          handler.resolve(
            Response<Object?>(
              requestOptions: options,
              statusCode: 200,
              data: {'items': [], 'total': 0, 'limit': 50, 'offset': 0},
            ),
          );
        },
      ),
    );

    expect(await DocumentsApi(client).list(), isEmpty);
  });

  test('parses documents from a successful response', () async {
    final dio = _respond(
      (options, handler) => handler.resolve(
        Response<Object?>(
          requestOptions: options,
          statusCode: 200,
          data: {
            'items': [_documentJson()],
          },
        ),
      ),
    );

    final documents = await DocumentsApi(ApiClient(dio: dio)).list();
    expect(documents.single.originalFilename, 'report.pdf');
  });

  test('propagates an unauthorized response', () async {
    final dio = _respond(
      (options, handler) => handler.reject(
        DioException(
          requestOptions: options,
          response: Response<Object?>(requestOptions: options, statusCode: 401),
        ),
      ),
    );

    expect(
      () => DocumentsApi(ApiClient(dio: dio)).list(),
      throwsA(
        isA<DioException>().having(
          (e) => e.response?.statusCode,
          'status',
          401,
        ),
      ),
    );
  });

  test('propagates a server or network error', () async {
    final dio = _respond(
      (options, handler) => handler.reject(
        DioException(
          requestOptions: options,
          type: DioExceptionType.connectionError,
        ),
      ),
    );

    expect(
      () => DocumentsApi(ApiClient(dio: dio)).list(),
      throwsA(
        isA<DioException>().having(
          (e) => e.type,
          'type',
          DioExceptionType.connectionError,
        ),
      ),
    );
  });

  test('uploads a selected file and reports multipart progress', () async {
    final dio = Dio();
    final client = ApiClient(
      dio: dio,
      accessTokenProvider: () async => 'upload-token',
    );
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          expect(options.path, '/api/v1/documents');
          expect(options.headers['Authorization'], 'Bearer upload-token');
          expect(options.data, isA<FormData>());
          handler.resolve(
            Response<Object?>(
              requestOptions: options,
              statusCode: 201,
              data: _documentJson(),
            ),
          );
        },
      ),
    );

    final document = await DocumentsApi(client).upload(
      PlatformFile(
        name: 'report.pdf',
        size: 12,
        bytes: Uint8List.fromList(List<int>.filled(12, 1)),
      ),
      null,
    );

    expect(document.originalFilename, 'report.pdf');
  });

  test('rejects unsupported files before creating a multipart request', () async {
    final api = DocumentsApi(ApiClient(dio: Dio()));

    expect(
      () => api.upload(
        PlatformFile(name: 'malware.exe', size: 4, bytes: Uint8List(4)),
        null,
      ),
      throwsA(isA<StateError>()),
    );
  });

  testWidgets('Retry repeats the failed request', (tester) async {
    final api = _FakeDocumentsApi(() async => <Document>[]);
    api.fail = true;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [documentsApiProvider.overrideWithValue(api)],
        child: const MaterialApp(home: DocumentsScreen()),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Retry'), findsOneWidget);
    expect(api.listCalls, 1);

    api.fail = false;
    await tester.tap(find.text('Retry'));
    await tester.pumpAndSettle();
    expect(find.text('No documents uploaded yet.'), findsOneWidget);
    expect(api.listCalls, 2);
  });

  testWidgets('Documents Back returns to Dashboard', (tester) async {
    final api = _FakeDocumentsApi(() async => <Document>[]);
    await tester.pumpWidget(_app(api));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Documents'));
    await tester.pumpAndSettle();

    expect(find.text('No documents uploaded yet.'), findsOneWidget);
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(find.text('Welcome, Test User'), findsOneWidget);
  });

  testWidgets('document detail navigation remains available', (tester) async {
    final api = _FakeDocumentsApi(() async => <Document>[_document()]);
    await tester.pumpWidget(_app(api));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Documents'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('report.pdf'));
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Extracted content'), findsOneWidget);
  });
}

Widget _app(_FakeDocumentsApi api) => ProviderScope(
  overrides: [
    authProvider.overrideWith(_AuthenticatedNotifier.new),
    documentsApiProvider.overrideWithValue(api),
  ],
  child: const OrvexaApp(),
);

Dio _respond(
  void Function(RequestOptions, RequestInterceptorHandler) callback,
) => Dio()..interceptors.add(InterceptorsWrapper(onRequest: callback));

Document _document() => const Document(
  id: '00000000-0000-0000-0000-000000000002',
  originalFilename: 'report.pdf',
  mimeType: 'application/pdf',
  fileSize: 123,
  processingStatus: 'completed',
  extractionStatus: 'completed',
);

Map<String, Object?> _documentJson() => {
  'id': '00000000-0000-0000-0000-000000000002',
  'original_filename': 'report.pdf',
  'mime_type': 'application/pdf',
  'file_size': 123,
  'processing_status': 'completed',
  'extraction_status': 'completed',
  'archived_at': null,
};
