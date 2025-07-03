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

  static void showErrorSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'Tamam',
          textColor: Colors.white,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }

  static Future<void> showErrorDialog(BuildContext context, String message) {
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hata'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  static Widget errorWidget(String message, VoidCallback onRetry) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              color: Colors.red,
              size: 48,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.red,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Tekrar Dene'),
            ),
          ],
        ),
      ),
    );
  }
} 