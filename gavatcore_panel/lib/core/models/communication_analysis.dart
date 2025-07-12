/// Model for communication analysis result from API
class CommunicationAnalysisResult {
  final String timestamp;
  final String interactionType;
  final double authenticityScore;
  final String authenticityLevel;
  final double confidenceScore;
  final List<String> evidence;
  final List<String> recommendations;

  CommunicationAnalysisResult({
    required this.timestamp,
    required this.interactionType,
    required this.authenticityScore,
    required this.authenticityLevel,
    required this.confidenceScore,
    required this.evidence,
    required this.recommendations,
  });

  factory CommunicationAnalysisResult.fromJson(Map<String, dynamic> json) {
    return CommunicationAnalysisResult(
      timestamp: json['timestamp'] ?? '',
      interactionType: json['interaction_type'] ?? '',
      authenticityScore: (json['authenticity_score'] ?? 0).toDouble(),
      authenticityLevel: json['authenticity_level'] ?? '',
      confidenceScore: (json['confidence_score'] ?? 0).toDouble(),
      evidence: List<String>.from(json['evidence'] ?? []),
      recommendations: List<String>.from(json['recommendations'] ?? []),
    );
  }
}
