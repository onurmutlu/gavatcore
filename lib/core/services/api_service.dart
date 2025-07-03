import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../storage/storage_service.dart';
import '../utils/connectivity_utils.dart';

class ApiService {
  final Dio _dio;
  
  ApiService() : _dio = Dio() {
    _dio.options.baseUrl = 'https://api.gavatcore.com/v1';
    _dio.options.connectTimeout = const Duration(seconds: 30);
    _dio.options.receiveTimeout = const Duration(seconds: 30);
    _dio.options.sendTimeout = const Duration(seconds: 30);
    _dio.options.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    };
    
    _dio.interceptors.addAll([
      _AuthInterceptor(),
      _ErrorInterceptor(),
      _RetryInterceptor(),
      if (kDebugMode)
        LogInterceptor(
          requestBody: true,
          responseBody: true,
        ),
    ]);
  }

  Future<T> _retryRequest<T>(
    Future<T> Function() request, {
    int maxRetries = 3,
    Duration retryDelay = const Duration(seconds: 2),
  }) async {
    int attempts = 0;
    DioException? lastError;

    while (attempts < maxRetries) {
      try {
        if (attempts > 0) {
          debugPrint('Retrying request attempt ${attempts + 1}/$maxRetries');
          
          // Bağlantı kontrolü
          final status = await ConnectivityUtils.checkConnection();
          if (status != ConnectionStatus.connected) {
            debugPrint('Connection check failed: ${status.message}');
            throw NetworkException(status.message);
          }
        }
        return await request();
      } on DioException catch (e) {
        lastError = e;
        attempts++;

        if (attempts == maxRetries || 
            e.type == DioExceptionType.cancel ||
            e.response?.statusCode == 401 ||
            e.response?.statusCode == 403 ||
            e.response?.statusCode == 404) {
          rethrow;
        }

        if (e.type != DioExceptionType.connectionTimeout &&
            e.type != DioExceptionType.sendTimeout &&
            e.type != DioExceptionType.receiveTimeout &&
            e.type != DioExceptionType.connectionError) {
          rethrow;
        }

        // Bağlantı kontrolü
        final status = await ConnectivityUtils.checkConnection();
        if (status != ConnectionStatus.connected) {
          debugPrint('Connection check failed: ${status.message}');
          throw NetworkException(status.message);
        }

        await Future.delayed(retryDelay * attempts);
      } catch (e) {
        debugPrint('Non-Dio error during retry: $e');
        rethrow;
      }
    }

    throw lastError ?? Exception('Maximum retry attempts reached');
  }

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    bool retry = true,
  }) async {
    try {
      // İlk istek öncesi bağlantı kontrolü
      final status = await ConnectivityUtils.checkConnection();
      if (status != ConnectionStatus.connected) {
        throw NetworkException(status.message);
      }

      final request = () => _dio.get(
            path,
            queryParameters: queryParameters,
          );
      
      final response = retry
          ? await _retryRequest(() => request())
          : await request();
          
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    bool retry = true,
  }) async {
    try {
      // İlk istek öncesi bağlantı kontrolü
      final status = await ConnectivityUtils.checkConnection();
      if (status != ConnectionStatus.connected) {
        throw NetworkException(status.message);
      }

      final request = () => _dio.post(
            path,
            data: data,
            queryParameters: queryParameters,
          );
      
      final response = retry
          ? await _retryRequest(() => request())
          : await request();
          
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    bool retry = true,
  }) async {
    try {
      // İlk istek öncesi bağlantı kontrolü
      final status = await ConnectivityUtils.checkConnection();
      if (status != ConnectionStatus.connected) {
        throw NetworkException(status.message);
      }

      final request = () => _dio.put(
            path,
            data: data,
            queryParameters: queryParameters,
          );
      
      final response = retry
          ? await _retryRequest(() => request())
          : await request();
          
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
    bool retry = true,
  }) async {
    try {
      // İlk istek öncesi bağlantı kontrolü
      final status = await ConnectivityUtils.checkConnection();
      if (status != ConnectionStatus.connected) {
        throw NetworkException(status.message);
      }

      final request = () => _dio.delete(
            path,
            queryParameters: queryParameters,
          );
      
      if (retry) {
        await _retryRequest(() => request());
      } else {
        await request();
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(dynamic error) {
    if (error is NetworkException) {
      return error;
    }

    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return TimeoutException('Bağlantı zaman aşımına uğradı. Lütfen internet bağlantınızı kontrol edin.');
        case DioExceptionType.connectionError:
          return NetworkException('İnternet bağlantısı bulunamadı. Lütfen bağlantınızı kontrol edin.');
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          final message = error.response?.data['message'] ?? 'Bilinmeyen hata';
          return ApiException(statusCode ?? 500, message);
        case DioExceptionType.cancel:
          return RequestCancelledException('İstek iptal edildi');
        default:
          return NetworkException('Ağ hatası: ${error.message}. Lütfen internet bağlantınızı kontrol edin.');
      }
    }
    return Exception('Beklenmeyen hata: $error');
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    try {
      final token = await StorageService.getAuthToken();
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    } catch (e) {
      debugPrint('Auth interceptor error: $e');
      handler.next(options);
    }
  }
}

class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    try {
      if (err.response?.statusCode == 401) {
        await StorageService.clearAll();
        // TODO: Navigate to login page using a global navigator key
      }
      handler.next(err);
    } catch (e) {
      debugPrint('Error interceptor error: $e');
      handler.next(err);
    }
  }
}

class _RetryInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.type == DioExceptionType.connectionError ||
        err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      try {
        debugPrint('Connection error, checking internet connectivity...');
        final status = await ConnectivityUtils.checkConnection();
        if (status != ConnectionStatus.connected) {
          debugPrint('Connection check failed: ${status.message}');
        }
      } catch (e) {
        debugPrint('Retry interceptor error: $e');
      }
    }
    handler.next(err);
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException: [$statusCode] $message';
}

class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}

class TimeoutException implements Exception {
  final String message;

  TimeoutException(this.message);

  @override
  String toString() => 'TimeoutException: $message';
}

class RequestCancelledException implements Exception {
  final String message;

  RequestCancelledException(this.message);

  @override
  String toString() => 'RequestCancelledException: $message';
} 