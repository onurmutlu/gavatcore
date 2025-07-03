import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:dio/dio.dart';
import 'package:gavatcore_mobile/core/services/api_service.dart';

@GenerateMocks([Dio])
import 'api_service_test.mocks.dart';

class TestApiService extends ApiService {
  @override
  Dio get dio => _dio;

  final Dio _dio;

  TestApiService(this._dio);
}

void main() {
  late TestApiService apiService;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    apiService = TestApiService(mockDio);
  });

  group('ApiService', () {
    test('login should return user data on success', () async {
      final mockResponse = {
        'token': 'test_token',
        'user': {'id': 1, 'username': 'test_user'}
      };

      when(mockDio.post('/auth/login', data: {
        'username': 'test_user',
        'password': 'test_pass'
      })).thenAnswer((_) async => Response(
            data: mockResponse,
            statusCode: 200,
            requestOptions: RequestOptions(),
          ));

      final result = await apiService.login('test_user', 'test_pass');

      expect(result, equals(mockResponse));
    });

    test('login should throw ApiException on error', () async {
      when(mockDio.post('/auth/login', data: {
        'username': 'test_user',
        'password': 'test_pass'
      })).thenThrow(DioException(
        type: DioExceptionType.badResponse,
        response: Response(
          data: {'message': 'Invalid credentials'},
          statusCode: 401,
          requestOptions: RequestOptions(),
        ),
        requestOptions: RequestOptions(),
      ));

      expect(
        () => apiService.login('test_user', 'test_pass'),
        throwsA(isA<ApiException>()),
      );
    });

    // Add more tests for other endpoints...
  });
} 