import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ErrorHandler {
  static String getErrorMessage(dynamic error) {
    if (error is ApiException) {
      switch (error.statusCode) {
        case 400:
          return 'Geçersiz istek: ${error.message}';
        case 401:
          return 'Oturum süresi doldu. Lütfen tekrar giriş yapın.';
        case 403:
          return 'Bu işlem için yetkiniz yok.';
        case 404:
          return 'İstenen kaynak bulunamadı.';
        case 422:
          return 'Geçersiz veri: ${error.message}';
        case 429:
          return 'Çok fazla istek gönderildi. Lütfen biraz bekleyin.';
        case 500:
          return 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.';
        default:
          return 'Bir hata oluştu: ${error.message}';
      }
    } else if (error is NetworkException) {
      return 'Ağ bağlantısı hatası: ${error.message}';
    } else if (error is TimeoutException) {
      return 'İstek zaman aşımına uğradı. Lütfen tekrar deneyin.';
    } else if (error is RequestCancelledException) {
      return 'İstek iptal edildi: ${error.message}';
    }
    return 'Beklenmeyen bir hata oluştu: $error';
  }

  static void showErrorSnackBar(
    BuildContext context,
    String message, {
    Duration duration = const Duration(seconds: 4),
    SnackBarAction? action,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
        behavior: SnackBarBehavior.floating,
        duration: duration,
        action: action ??
            SnackBarAction(
              label: 'Tamam',
              textColor: Colors.white,
              onPressed: () {
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
              },
            ),
      ),
    );
  }

  static Future<void> showErrorDialog(
    BuildContext context,
    String message, {
    String title = 'Hata',
    String buttonText = 'Tamam',
    VoidCallback? onRetry,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          if (onRetry != null)
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                onRetry();
              },
              child: const Text('Tekrar Dene'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(buttonText),
          ),
        ],
      ),
    );
  }

  static Widget errorWidget(
    String message,
    VoidCallback onRetry, {
    IconData icon = Icons.error_outline,
    double iconSize = 48,
    Color? iconColor,
    TextStyle? messageStyle,
    String retryButtonText = 'Tekrar Dene',
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: iconColor ?? Colors.red,
              size: iconSize,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: messageStyle ??
                  const TextStyle(
                    fontSize: 16,
                    color: Colors.red,
                  ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: Text(retryButtonText),
            ),
          ],
        ),
      ),
    );
  }

  static Widget buildErrorPage({
    required String message,
    required VoidCallback onRetry,
    String title = 'Bir Hata Oluştu',
    String description = 'Üzgünüz, bir sorun oluştu.',
    String buttonText = 'Tekrar Dene',
  }) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 24),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                description,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                message,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.red,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(buttonText),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 