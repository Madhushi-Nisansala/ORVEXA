class Document {
  const Document({
    required this.id,
    required this.originalFilename,
    required this.mimeType,
    required this.fileSize,
    required this.processingStatus,
    required this.extractionStatus,
    this.storageKey,
    this.sha256Hash,
    this.documentType,
    this.detectedLanguage,
    this.createdAt,
    this.archivedAt,
  });

  final String id;
  final String originalFilename;
  final String mimeType;
  final int fileSize;
  final String processingStatus;
  final String extractionStatus;
  final String? storageKey;
  final String? sha256Hash;
  final String? documentType;
  final String? detectedLanguage;
  final DateTime? createdAt;
  final DateTime? archivedAt;

  factory Document.fromJson(Map<String, dynamic> json) {
    final id = json['id']?.toString();
    final filename = json['original_filename']?.toString();
    final mimeType = json['mime_type']?.toString();
    final processingStatus = json['processing_status']?.toString();
    final extractionStatus = json['extraction_status']?.toString();
    final fileSize = json['file_size'];
    if (id == null ||
        filename == null ||
        mimeType == null ||
        processingStatus == null ||
        extractionStatus == null ||
        fileSize is! num) {
      throw const FormatException('Invalid document response');
    }
    return Document(
      id: id,
      originalFilename: filename,
      mimeType: mimeType,
      fileSize: fileSize.toInt(),
      processingStatus: processingStatus,
      extractionStatus: extractionStatus,
      storageKey: json['storage_key']?.toString(),
      sha256Hash: json['sha256_hash']?.toString(),
      documentType: json['document_type']?.toString(),
      detectedLanguage: json['detected_language']?.toString(),
      createdAt: _parseDate(json['created_at']),
      archivedAt: _parseDate(json['archived_at']),
    );
  }
}

DateTime? _parseDate(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}
