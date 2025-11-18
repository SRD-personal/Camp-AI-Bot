class MessageModel {
  final String id;
  final String role;
  final String content;
  final DateTime timestamp;
  final List<SourceDocument>? sources;

  MessageModel({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.sources,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'],
      role: json['role'],
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
      sources: json['sources'] != null
          ? (json['sources'] as List)
              .map((s) => SourceDocument.fromJson(s))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'sources': sources?.map((s) => s.toJson()).toList(),
    };
  }
}

class SourceDocument {
  final String? documentTitle;
  final String content;
  final double similarityScore;

  SourceDocument({
    this.documentTitle,
    required this.content,
    required this.similarityScore,
  });

  factory SourceDocument.fromJson(Map<String, dynamic> json) {
    return SourceDocument(
      documentTitle: json['document_title'] ?? json['tool_name'],
      content: json['content'],
      similarityScore: (json['similarity_score'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'document_title': documentTitle,
      'content': content,
      'similarity_score': similarityScore,
    };
  }
}
