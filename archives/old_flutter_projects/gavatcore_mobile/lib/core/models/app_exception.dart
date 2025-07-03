class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic details;
  
  AppException(this.message, {this.code, this.details});
  
  @override
  String toString() => 'AppException: $message${code != null ? ' (Code: $code)' : ''}';
} 