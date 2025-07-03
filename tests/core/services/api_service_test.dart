import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';
import 'package:gavatcore_mobile/core/services/api_service.dart';
import 'package:gavatcore_mobile/core/storage/storage_service.dart';

class MockDio extends Mock implements Dio {}
class MockStorageService extends Mock implements StorageService {}
class MockResponse extends Mock implements Response {}

void main() {
  late ApiService apiService;
  late MockDio mockDio;
  late MockStorageService mockStorage;

  setUp(() {
    mockDio = MockDio();
    mockStorage = MockStorageService();
    apiService = ApiService(mockStorage);
  });

  group('ApiService Tests', () {
    test('GET request success', () async {
      final mockResponse = MockResponse();
      when(mockResponse.data).thenReturn({'success': true});
      when(mockDio.get(any)).thenAnswer((_) async => mockResponse);

      final result = await apiService.get('/test');
      expect(result['success'], true);
    });

    test('GET request with retry on network error', () async {
      final mockResponse = MockResponse();
      when(mockResponse.data).thenReturn({'success': true});
      
      var attempts = 0;
      when(mockDio.get(any)).thenAnswer((_) async {
        attempts++;
        if (attempts < 2) {
          throw DioException(
            requestOptions: RequestOptions(path: ''),
            type: DioExceptionType.connectionTimeout,
          );
        }
        return mockResponse;
      });

      final result = await apiService.get('/test');
      expect(result['success'], true);
      expect(attempts, 2);
    });

    test('POST request with auth token', () async {
      when(mockStorage.getAuthToken())
          .thenAnswer((_) async => 'test_token');

      final mockResponse = MockResponse();
      when(mockResponse.data).thenReturn({'success': true});
      when(mockDio.post(
        any,
        data: anyNamed('data'),
        options: anyNamed('options'),
      )).thenAnswer((_) async => mockResponse);

      final result = await apiService.post(
        '/test',
        data: {'test': true},
      );
      
      expect(result['success'], true);
      verify(mockStorage.getAuthToken()).called(1);
    });

    test('handles API error correctly', () async {
      when(mockDio.get(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            statusCode: 404,
            data: {'message': 'Not found'},
            requestOptions: RequestOptions(path: ''),
          ),
          type: DioExceptionType.badResponse,
        ),
      );

      expect(
        () => apiService.get('/test'),
        throwsA(isA<ApiException>()),
      );
    });

    test('handles network error correctly', () async {
      when(mockDio.get(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionError,
          message: 'No internet',
        ),
      );

      expect(
        () => apiService.get('/test'),
        throwsA(isA<NetworkException>()),
      );
    });

    test('handles timeout correctly', () async {
      when(mockDio.get(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionTimeout,
        ),
      );

      expect(
        () => apiService.get('/test'),
        throwsA(isA<TimeoutException>()),
      );
    });

    test('handles request cancellation', () async {
      when(mockDio.get(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.cancel,
        ),
      );

      expect(
        () => apiService.get('/test'),
        throwsA(isA<RequestCancelledException>()),
      );
    });
  });
} 