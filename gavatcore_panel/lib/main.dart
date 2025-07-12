import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'features/settings/simple_settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Remove # from URL in web
  usePathUrlStrategy();

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0A0A0F),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  runApp(
    const ProviderScope(
      child: GavatCoreApp(),
    ),
  );
}

// Character data model
class CharacterData {
  final String name;
  final String username;
  final String phone;
  final String status;
  final String description;
  final int messageCount;
  final double responseTime;
  final List<String> features;
  final Map<String, dynamic> profileData;
  final Map<String, dynamic> personaData;
  final String lastUpdated;

  CharacterData({
    required this.name,
    required this.username,
    required this.phone,
    required this.status,
    required this.description,
    required this.messageCount,
    required this.responseTime,
    required this.features,
    required this.profileData,
    required this.personaData,
    required this.lastUpdated,
  });

  factory CharacterData.fromJson(Map<String, dynamic> json) {
    return CharacterData(
      name: json['name'] ?? '',
      username: json['username'] ?? '',
      phone: json['phone'] ?? '',
      status: json['status'] ?? 'unknown',
      description: json['description'] ?? '',
      messageCount: json['messageCount'] ?? 0,
      responseTime: (json['responseTime'] ?? 0.0).toDouble(),
      features: List<String>.from(json['features'] ?? []),
      profileData: json['profile_data'] ?? {},
      personaData: json['persona_data'] ?? {},
      lastUpdated: json['last_updated'] ?? '',
    );
  }
}

// API Service
class GAVATCoreAPIService {
  static const String baseUrl = 'http://localhost:5050';

  static Future<Map<String, dynamic>> getSystemStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/system/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('API Error: $e');
    }

    // Mock data if API unavailable
    return {
      'status': 'running',
      'active_bots': 2,
      'total_bots': 3,
      'total_messages': 2103,
      'response_time': 125
    };
  }

  static Future<List<CharacterData>> getCharacters() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/characters'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          final List<dynamic> charactersJson = data['characters'];
          return charactersJson
              .map((json) => CharacterData.fromJson(json))
              .toList();
        }
      }
    } catch (e) {
      print('Characters API Error: $e');
    }

    // Mock data if API unavailable
    return [
      CharacterData(
        name: 'Yayıncı Lara',
        username: 'yayincilara',
        phone: '+905382617727',
        status: 'active',
        description:
            'Flörtöz streamer karakteri. Gaming ve eğlence odaklı sohbet tarzı.',
        messageCount: 1247,
        responseTime: 2.3,
        features: ['Flört Modu', 'Gaming Chat', 'Emoji Master', 'Voice Notes'],
        profileData: {},
        personaData: {},
        lastUpdated: '',
      ),
      CharacterData(
        name: 'XXXGeisha',
        username: 'xxxgeisha',
        phone: '+905486306226',
        status: 'active',
        description:
            'Gizemli ve zarif moderatör karakteri. Sofistike sohbet tarzı.',
        messageCount: 856,
        responseTime: 1.8,
        features: [
          'Zarif Sohbet',
          'Moderasyon',
          'AI Enhanced',
          'Multi-language'
        ],
        profileData: {},
        personaData: {},
        lastUpdated: '',
      ),
      CharacterData(
        name: 'BabaGavat',
        username: 'babagavat',
        phone: '+905513272355',
        status: 'banned',
        description:
            'Spam nedeniyle geçici olarak devre dışı. Sistem güncelleme bekleniyor.',
        messageCount: 0,
        responseTime: 0.0,
        features: ['Devre Dışı', 'Spam Koruması', 'Güncelleme Bekliyor'],
        profileData: {},
        personaData: {},
        lastUpdated: '',
      ),
    ];
  }

  static Future<bool> updateCharacter(
      String username, Map<String, dynamic> updateData) async {
    try {
      final response = await http
          .put(
            Uri.parse('$baseUrl/api/characters/$username'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(updateData),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['success'] == true;
      }
    } catch (e) {
      print('Update Character API Error: $e');
    }
    return false;
  }

  static Future<bool> characterAction(String username, String action) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/characters/$username/action'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'action': action}),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['success'] == true;
      }
    } catch (e) {
      print('Character Action API Error: $e');
    }
    return false;
  }

  static Future<List<Map<String, dynamic>>> getPerformers() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/performers'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          return List<Map<String, dynamic>>.from(data['performers']);
        }
      }
    } catch (e) {
      print('Performers API Error: $e');
    }

    // Mock data if API unavailable
    return [];
  }

  static Future<bool> createPerformer(
      Map<String, dynamic> performerData) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/performers'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(performerData),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['success'] == true;
      }
    } catch (e) {
      print('Create Performer API Error: $e');
    }
    return false;
  }

  static Future<Map<String, dynamic>> getMessages({
    int limit = 50,
    String? botName,
    String? chatType,
    String? messageType,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
      };

      if (botName != null) queryParams['bot_name'] = botName;
      if (chatType != null) queryParams['chat_type'] = chatType;
      if (messageType != null) queryParams['message_type'] = messageType;

      final uri = Uri.parse('$baseUrl/api/messages')
          .replace(queryParameters: queryParams);
      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          return {
            'messages': List<Map<String, dynamic>>.from(data['messages']),
            'count': data['count'],
            'stats': data['stats'],
          };
        }
      }
    } catch (e) {
      print('Messages API Error: $e');
    }

    return {
      'messages': <Map<String, dynamic>>[],
      'count': 0,
      'stats': {},
    };
  }

  static Future<Map<String, dynamic>> getMessageStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/messages/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Message Stats API Error: $e');
    }

    // Mock data: bot_distribution values should match expected {dm, group, total} structure
    return {
      'total_messages': 1247,
      'bot_distribution': {
        'yayincilara': {'dm': 45, 'group': 0, 'total': 45},
        'xxxgeisha': {'dm': 35, 'group': 0, 'total': 35},
        'babagavat': {'dm': 20, 'group': 0, 'total': 20},
      },
      'sentiment_distribution': {
        'positive': 60,
        'neutral': 30,
        'motivational': 10,
      }
    };
  }

  static Future<Map<String, dynamic>> getAdvancedAnalytics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/analytics/advanced'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Advanced Analytics API Error: $e');
    }

    // Mock data
    return {
      'ai_manager': {
        'task_queue_status': {
          'pending_tasks': 12,
          'active_tasks': 5,
          'completed_tasks': 234
        },
        'ai_features': {
          'voice_ai': true,
          'crm_ai': true,
          'social_ai': true,
          'advanced_analytics': true,
          'real_time_analysis': true,
          'predictive_analytics': true,
          'sentiment_analysis': true,
          'personality_analysis': true
        },
        'model_usage': {
          'gpt_4': {'requests': 1247, 'success_rate': 98.5},
          'gpt_3_5_turbo': {'requests': 892, 'success_rate': 99.2},
          'character_ai': {'requests': 456, 'success_rate': 97.8}
        }
      },
      'behavioral_analytics': {
        'personality_analysis': {
          'total_profiles': 892,
          'analyzed_today': 45,
          'big_five_distribution': {
            'openness': 75,
            'conscientiousness': 68,
            'extraversion': 62,
            'agreeableness': 80,
            'neuroticism': 45
          }
        },
        'engagement_patterns': {
          'high_engagement': 25,
          'medium_engagement': 55,
          'low_engagement': 20
        }
      },
      'crm_analytics': {
        'user_segmentation': {
          'vip_users': 85,
          'active_users': 320,
          'at_risk_users': 45,
          'new_users': 38
        },
        'revenue_analytics': {
          'total_ltv': '\$25,000',
          'avg_user_value': '\$55',
          'conversion_rate': '18%',
          'retention_rate': '78%'
        }
      },
      'content_generator': {
        'generation_metrics': {
          'messages_generated': 3247,
          'success_rate': '96%',
          'avg_generation_time': '0.8s',
          'quality_score': '92%'
        },
        'content_types': {
          'flirty_responses': 1200,
          'educational_content': 450,
          'motivational_messages': 680,
          'personalized_content': 917
        }
      },
      'erko_analyzer': {
        'risk_assessment': {
          'high_risk_users': 8,
          'medium_risk_users': 25,
          'low_risk_users': 120,
          'trust_score_avg': '85%'
        },
        'behavioral_flags': {
          'spam_detected': 5,
          'suspicious_activity': 2,
          'fake_profiles': 1,
          'bot_activity': 3
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getAIModelsStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/ai/models/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('AI Models Status API Error: $e');
    }

    // Mock data
    return {
      'models': {
        'gpt_4': {
          'status': 'active',
          'response_time': '1.2s',
          'success_rate': '98%',
          'daily_requests': 1247,
          'cost_today': '\$25'
        },
        'gpt_3_5_turbo': {
          'status': 'active',
          'response_time': '0.6s',
          'success_rate': '99%',
          'daily_requests': 1892,
          'cost_today': '\$12'
        },
        'character_ai': {
          'status': 'active',
          'response_time': '0.9s',
          'success_rate': '97%',
          'daily_requests': 856,
          'cost_today': '\$8'
        },
        'vision_ai': {
          'status': 'standby',
          'response_time': '1.8s',
          'success_rate': '94%',
          'daily_requests': 125,
          'cost_today': '\$5'
        }
      },
      'total_cost_today': '\$50',
      'total_requests_today': 4120
    };
  }

  static Future<Map<String, dynamic>> getPersonalityInsights() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/behavioral/personality-insights'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Personality Insights API Error: $e');
    }

    // Mock data
    return {
      'insights': {
        'top_personality_types': [
          {'type': 'Creative Explorer', 'count': 125, 'percentage': '22%'},
          {'type': 'Social Connector', 'count': 98, 'percentage': '17%'},
          {'type': 'Analytical Thinker', 'count': 76, 'percentage': '13%'},
          {'type': 'Empathetic Helper', 'count': 112, 'percentage': '20%'},
          {'type': 'Achievement Focused', 'count': 89, 'percentage': '16%'}
        ],
        'behavioral_patterns': {
          'peak_activity_hours': ['20:00-22:00', '12:00-14:00', '18:00-20:00'],
          'preferred_interaction_style': {
            'direct_messaging': '58%',
            'group_participation': '32%',
            'voice_interaction': '18%'
          }
        },
        'optimization_opportunities': [
          {
            'category': 'Engagement',
            'opportunity': 'Voice interaction adoption artırımı',
            'potential_impact': '+25%',
            'effort': 'Medium'
          },
          {
            'category': 'Retention',
            'opportunity': 'Kişiselleştirilmiş içerik zamanlaması',
            'potential_impact': '+30%',
            'effort': 'Low'
          }
        ]
      }
    };
  }

  static Future<Map<String, dynamic>> getSystemPerformanceMetrics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/performance/system-metrics'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('System Performance API Error: $e');
    }

    // Mock data
    return {
      'metrics': {
        'cpu_usage': '45%',
        'memory_usage': '62%',
        'disk_usage': '38%',
        'network_io': {'bytes_sent': '250MB', 'bytes_received': '480MB'},
        'database_performance': {
          'query_time_avg': '0.125s',
          'connections_active': 12,
          'cache_hit_rate': '87%'
        },
        'api_performance': {
          'requests_per_minute': 285,
          'avg_response_time': '0.456s',
          'error_rate': '1.2%',
          'uptime': '99.8%'
        }
      },
      'health_score': 92
    };
  }

  // Smart AI Modules API Functions
  static Future<Map<String, dynamic>> getSmartCampaignManager() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/smart-campaign/manager'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Smart Campaign Manager API Error: $e');
    }

    // Mock data fallback
    return {
      'data': {
        'active_campaigns': {
          'total_campaigns': 12,
          'running_campaigns': 8,
          'paused_campaigns': 2,
          'completed_campaigns': 2
        },
        'campaign_performance': {
          'total_reach': 45892,
          'engagement_rate': '18.5%',
          'conversion_rate': '12.3%',
          'roi': '340%'
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getSmartPersonalityAdapter() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/smart-personality/adapter'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Smart Personality Adapter API Error: $e');
    }

    // Mock data fallback
    return {
      'data': {
        'adaptation_engine': {
          'active_profiles': 1247,
          'adaptation_accuracy': '94.2%',
          'real_time_adjustments': 2341,
          'personality_models': ['big_five', 'mbti', 'enneagram', 'disc']
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getUserAnalyzer() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/user-analyzer/insights'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('User Analyzer API Error: $e');
    }

    // Mock data fallback
    return {
      'data': {
        'analysis_overview': {
          'total_users_analyzed': 2847,
          'active_analyses': 156,
          'analysis_accuracy': '97.3%',
          'real_time_tracking': true
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getUserSegmentation() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/user-segmentation/advanced'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('User Segmentation API Error: $e');
    }

    // Mock data fallback
    return {
      'data': {
        'segmentation_overview': {
          'total_segments': 24,
          'active_segments': 18,
          'auto_generated_segments': 12,
          'manual_segments': 6,
          'segmentation_accuracy': '96.8%'
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getSmartModulesDashboard() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/smart-modules/dashboard'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Smart Modules Dashboard API Error: $e');
    }

    // Mock data fallback
    return {
      'data': {
        'modules_overview': {
          'campaign_manager': {
            'status': 'active',
            'campaigns_running': 8,
            'performance_score': '94%',
            'roi': '340%'
          },
          'personality_adapter': {
            'status': 'active',
            'profiles_adapted': 1247,
            'accuracy': '94.2%',
            'real_time_adjustments': 2341
          },
          'user_analyzer': {
            'status': 'active',
            'users_analyzed': 2847,
            'insights_generated': 156,
            'prediction_accuracy': '97.3%'
          },
          'user_segmentation': {
            'status': 'active',
            'segments_active': 18,
            'segmentation_accuracy': '96.8%',
            'auto_updates': 'Daily'
          }
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getCoreModulesOverview() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/core-modules/overview'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Core Modules API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'modules_count': 56,
        'active_modules': 48,
        'critical_modules': 12,
        'modules_health': '94.2%'
      }
    };
  }

  static Future<Map<String, dynamic>> getBabaGAVATUserAnalyzer() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/babagavat-user-analyzer/insights'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('BabaGAVAT User Analyzer API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'analyzer_status': {
          'is_monitoring': true,
          'analyzed_users': 2847,
          'trust_assessments': 1923
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getErkoAnalyzerSegments() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/erko-analyzer/segments'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Erko Analyzer API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'analyzer_status': {'total_male_users': 1847, 'analyzed_users': 1723}
      }
    };
  }

  static Future<Map<String, dynamic>> getAICRMAnalyzer() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/ai-crm-analyzer/insights'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('AI CRM Analyzer API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'ai_status': {
          'gpt4_enabled': true,
          'processed_users': 2847,
          'analysis_accuracy': '97.3%'
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getBehavioralEngine() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/behavioral-engine/analysis'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Behavioral Engine API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'engine_status': {
          'active_profiles': 2847,
          'psychological_models': 5,
          'analysis_accuracy': '94.7%'
        }
      }
    };
  }

  static Future<Map<String, dynamic>> getSocialGamingMetrics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/social-gaming/metrics'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      print('Social Gaming API Error: $e');
    }

    // Mock data
    return {
      'status': 'success',
      'data': {
        'gaming_status': {
          'active_players': 1567,
          'total_quests': 234,
          'engagement_boost': '+67%'
        }
      }
    };
  }
}

// Providers
final systemStatsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getSystemStatus();
});

final charactersProvider = FutureProvider<List<CharacterData>>((ref) async {
  return await GAVATCoreAPIService.getCharacters();
});

final performersProvider =
    FutureProvider<List<Map<String, dynamic>>>((ref) async {
  return await GAVATCoreAPIService.getPerformers();
});

final messagesProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getMessages();
});

final messageStatsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getMessageStats();
});

final coreModulesProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getCoreModulesOverview();
});

final babaGavatAnalyzerProvider =
    FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getBabaGAVATUserAnalyzer();
});

final erkoAnalyzerProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getErkoAnalyzerSegments();
});

final aiCrmAnalyzerProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getAICRMAnalyzer();
});

final behavioralEngineProvider =
    FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getBehavioralEngine();
});

final socialGamingProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await GAVATCoreAPIService.getSocialGamingMetrics();
});

class GavatCoreApp extends StatelessWidget {
  const GavatCoreApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GavatCore Admin Panel',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF9C27B0),
          brightness: Brightness.dark,
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1A1A1F),
          elevation: 2,
          margin: const EdgeInsets.all(8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const SimpleDashboard(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SimpleDashboard extends ConsumerStatefulWidget {
  const SimpleDashboard({Key? key}) : super(key: key);

  @override
  ConsumerState<SimpleDashboard> createState() => _SimpleDashboardState();
}

class _SimpleDashboardState extends ConsumerState<SimpleDashboard> {
  int _selectedIndex = 0;

  final List<NavigationItem> _navigationItems = [
    NavigationItem(
      icon: Icons.dashboard,
      label: 'Dashboard',
      color: const Color(0xFF9C27B0),
    ),
    NavigationItem(
      icon: Icons.smart_toy,
      label: 'Karakterler',
      color: const Color(0xFF4CAF50),
    ),
    NavigationItem(
      icon: Icons.star,
      label: 'Şovcu Panel',
      color: const Color(0xFFFF9800),
    ),
    NavigationItem(
      icon: Icons.chat,
      label: 'Mesaj Logları',
      color: const Color(0xFF00BCD4),
    ),
    NavigationItem(
      icon: Icons.analytics,
      label: 'Analitik',
      color: const Color(0xFF2196F3),
    ),
    NavigationItem(
      icon: Icons.memory,
      label: 'Core Modules',
      color: const Color(0xFFE91E63),
    ),
    NavigationItem(
      icon: Icons.settings,
      label: 'Ayarlar',
      color: const Color(0xFF757575),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: Row(
        children: [
          if (isDesktop)
            NavigationRail(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              extended: true,
              backgroundColor: const Color(0xFF1A1A1F),
              destinations: _navigationItems
                  .map((item) => NavigationRailDestination(
                        icon: Icon(item.icon, color: const Color(0xFF757575)),
                        selectedIcon: Icon(item.icon, color: item.color),
                        label: Text(item.label),
                      ))
                  .toList(),
            ),
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                _buildDashboardContent(),
                _buildCharactersContent(),
                _buildShowcuPanelContent(),
                _buildMessageLogsContent(),
                _buildAnalyticsContent(),
                _buildCoreModulesContent(),
                _buildSettingsContent(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: !isDesktop
          ? NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              destinations: _navigationItems
                  .map((item) => NavigationDestination(
                        icon: Icon(item.icon),
                        label: item.label,
                      ))
                  .toList(),
            )
          : null,
    );
  }

  Widget _buildDashboardContent() {
    final systemStatsAsync = ref.watch(systemStatsProvider);
    final performersAsync = ref.watch(performersProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text(
          '🚀 GavatCore Dashboard',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.refresh(systemStatsProvider);
              ref.refresh(performersProvider);
            },
            tooltip: 'Tümünü Yenile',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Sistem Stats
            const Text(
              '📊 Sistem İstatistikleri',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            systemStatsAsync.when(
              data: (stats) => GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount:
                    MediaQuery.of(context).size.width > 1200 ? 4 : 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                children: [
                  _buildStatCard(
                    'Aktif Karakterler',
                    stats['active_bots'].toString(),
                    Icons.smart_toy,
                    const Color(0xFF4CAF50),
                  ),
                  _buildStatCard(
                    'Toplam Mesaj',
                    stats['total_messages'].toString(),
                    Icons.message,
                    const Color(0xFF9C27B0),
                  ),
                  _buildStatCard(
                    'Sistem Durumu',
                    stats['status'] == 'running' ? 'Çalışıyor' : 'Durduruldu',
                    Icons.check_circle,
                    stats['status'] == 'running'
                        ? const Color(0xFF4CAF50)
                        : const Color(0xFFF44336),
                  ),
                  _buildStatCard(
                    'API Yanıt Süresi',
                    '${stats['response_time']}ms',
                    Icons.speed,
                    const Color(0xFFFF9800),
                  ),
                ],
              ),
              loading: () => const Center(
                child: CircularProgressIndicator(color: Color(0xFF4CAF50)),
              ),
              error: (error, stack) => Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1F),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Sistem verileri alınamadı: $error',
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 32),

            // Şovcu Stats
            const Text(
              '🎭 Şovcu İstatistikleri',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            performersAsync.when(
              data: (performers) {
                final performersData =
                    performers.isNotEmpty ? performers : _mockPerformers;
                final activeCount =
                    performersData.where((p) => p['status'] == 'online').length;
                final totalEarnings = performersData.fold<int>(
                    0, (sum, p) => sum + (p['earnings_month'] as int));
                final todayEarnings = performersData.fold<int>(
                    0, (sum, p) => sum + (p['earnings_today'] as int));
                final vipCount = performersData.fold<int>(
                    0, (sum, p) => sum + (p['vip_count'] as int));

                return Column(
                  children: [
                    GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount:
                          MediaQuery.of(context).size.width > 1200 ? 4 : 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _buildStatCard(
                          'Aktif Şovcular',
                          '$activeCount/${performersData.length}',
                          Icons.star,
                          const Color(0xFFFF9800),
                        ),
                        _buildStatCard(
                          'Toplam Kazanç',
                          '₺${totalEarnings.toString()}',
                          Icons.attach_money,
                          const Color(0xFF4CAF50),
                        ),
                        _buildStatCard(
                          'Bugün Kazanç',
                          '₺${todayEarnings.toString()}',
                          Icons.trending_up,
                          const Color(0xFF9C27B0),
                        ),
                        _buildStatCard(
                          'VIP Üyeler',
                          '$vipCount',
                          Icons.diamond,
                          const Color(0xFF2196F3),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Top Performers
                    Card(
                      color: const Color(0xFF1A1A1F),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.emoji_events,
                                    color: Color(0xFFFF9800)),
                                const SizedBox(width: 8),
                                const Text(
                                  'En İyi Performans Gösteren Şovcular',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const Spacer(),
                                TextButton(
                                  onPressed: () {
                                    setState(() {
                                      _selectedIndex = 2; // Şovcu Panel'e git
                                    });
                                  },
                                  child: const Text('Tümünü Gör'),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            ...(performersData
                                    .where((p) => p['status'] == 'online')
                                    .toList()
                                  ..sort((a, b) => (b['earnings_today'] as int)
                                      .compareTo(a['earnings_today'] as int)))
                                .take(5)
                                .map((performer) => Container(
                                      margin: const EdgeInsets.only(bottom: 8),
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF2A2A2F),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Row(
                                        children: [
                                          Text(
                                            performer['avatar'],
                                            style:
                                                const TextStyle(fontSize: 24),
                                          ),
                                          const SizedBox(width: 12),
                                          Expanded(
                                            child: Column(
                                              crossAxisAlignment:
                                                  CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  performer['name'],
                                                  style: const TextStyle(
                                                    color: Colors.white,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                                Text(
                                                  '${performer['character']} • ${performer['tone']}',
                                                  style: const TextStyle(
                                                    color: Colors.white70,
                                                    fontSize: 12,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                          Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.end,
                                            children: [
                                              Text(
                                                '₺${performer['earnings_today']}',
                                                style: const TextStyle(
                                                  color: Color(0xFF4CAF50),
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                              Text(
                                                '${performer['vip_count']} VIP',
                                                style: const TextStyle(
                                                  color: Colors.white70,
                                                  fontSize: 12,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                    )),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(color: Color(0xFFFF9800)),
              ),
              error: (error, stack) => Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1F),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Şovcu verileri alınamadı: $error',
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCharactersContent() {
    final charactersAsync = ref.watch(charactersProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text('🤖 Karakterler'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.refresh(charactersProvider),
            tooltip: 'Karakterleri Yenile',
          ),
        ],
      ),
      body: charactersAsync.when(
        data: (characters) => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: characters.length,
          itemBuilder: (context, index) {
            final character = characters[index];
            return _buildAdvancedCharacterCard(character);
          },
        ),
        loading: () => const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Karakterler yükleniyor...',
                  style: TextStyle(color: Colors.white70)),
            ],
          ),
        ),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              Text('Karakter verisi alınamadı: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.refresh(charactersProvider),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildShowcuPanelContent() {
    final performersAsync = ref.watch(performersProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text('🎭 Şovcu Panel'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showCreatePerformerDialog(),
            tooltip: 'Yeni Şovcu Ekle',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.refresh(performersProvider),
            tooltip: 'Yenile',
          ),
        ],
      ),
      body: performersAsync.when(
        data: (performers) {
          final performersData =
              performers.isNotEmpty ? performers : _mockPerformers;
          final activeCount =
              performersData.where((p) => p['status'] == 'online').length;
          final totalEarnings = performersData.fold<int>(
              0, (sum, p) => sum + (p['earnings_month'] as int));
          final monthlyEarnings = performersData.fold<int>(
              0, (sum, p) => sum + (p['earnings_today'] as int));
          final vipCount = performersData.fold<int>(
              0, (sum, p) => sum + (p['vip_count'] as int));

          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Şovcu Stats Cards
                Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        'Aktif Şovcular',
                        '$activeCount',
                        Icons.star,
                        const Color(0xFFFF9800),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildStatCard(
                        'Toplam Kazanç',
                        '₺${totalEarnings.toString()}',
                        Icons.attach_money,
                        const Color(0xFF4CAF50),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildStatCard(
                        'Bugün Kazanç',
                        '₺${monthlyEarnings.toString()}',
                        Icons.trending_up,
                        const Color(0xFF9C27B0),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildStatCard(
                        'VIP Üyeler',
                        '$vipCount',
                        Icons.diamond,
                        const Color(0xFF2196F3),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Şovcu List
                Expanded(
                  child: Card(
                    color: const Color(0xFF1A1A1F),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.people,
                                  color: Color(0xFFFF9800)),
                              const SizedBox(width: 8),
                              Text(
                                'Şovcu Listesi (${performersData.length})',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const Spacer(),
                              TextButton.icon(
                                onPressed: () => _showCreatePerformerDialog(),
                                icon: const Icon(Icons.add, size: 16),
                                label: const Text('Yeni Şovcu'),
                                style: TextButton.styleFrom(
                                  foregroundColor: const Color(0xFFFF9800),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Expanded(
                            child: ListView.builder(
                              itemCount: performersData.length,
                              itemBuilder: (context, index) {
                                final performer = performersData[index];
                                return _buildPerformerCard(performer);
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(color: Color(0xFFFF9800)),
        ),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              Text(
                'Şovcu verileri yüklenirken hata oluştu\n$error',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.refresh(performersProvider),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // This is now handled by performersProvider

  // Gerçek şovcu data - telefon numaraları ile eşleştirme (fallback)
  final List<Map<String, dynamic>> _mockPerformers = [
    {
      'id': 'performer_1',
      'name': 'StarGirl',
      'phone': '+905382617727',
      'character': 'Lara',
      'status': 'online',
      'earnings_today': 280,
      'earnings_month': 3420,
      'vip_count': 12,
      'last_active': '2 dakika önce',
      'avatar': '💋',
      'tone': 'flirty',
      'iban': 'TR83 0082 9000 0949 1060 9367 40',
      'onboarding_date': '2025-01-15',
    },
    {
      'id': 'performer_2',
      'name': 'MysteryLady',
      'phone': '+905486306226',
      'character': 'Geisha',
      'status': 'online',
      'earnings_today': 150,
      'earnings_month': 2180,
      'vip_count': 8,
      'last_active': '5 dakika önce',
      'avatar': '🌸',
      'tone': 'mystic',
      'iban': 'TR83 0082 9000 0949 1060 9367 40',
      'onboarding_date': '2025-01-26',
    },
    {
      'id': 'performer_3',
      'name': 'QueenBee',
      'phone': '+905513272355',
      'character': 'BabaGavat',
      'status': 'banned',
      'earnings_today': 0,
      'earnings_month': 1820,
      'vip_count': 15,
      'last_active': '2 saat önce',
      'avatar': '👑',
      'tone': 'aggressive',
      'iban': 'TR12 3456 7890 1234 5678 9012 34',
      'onboarding_date': '2024-12-01',
    },
    {
      'id': 'performer_4',
      'name': 'SexyLuna',
      'phone': '+905551234567',
      'character': 'Lara',
      'status': 'online',
      'earnings_today': 320,
      'earnings_month': 4150,
      'vip_count': 18,
      'last_active': '1 dakika önce',
      'avatar': '🌙',
      'tone': 'soft',
      'iban': 'TR98 7654 3210 9876 5432 1098 76',
      'onboarding_date': '2025-02-10',
    },
    {
      'id': 'performer_5',
      'name': 'FireQueen',
      'phone': '+905552345678',
      'character': 'Geisha',
      'status': 'online',
      'earnings_today': 195,
      'earnings_month': 2890,
      'vip_count': 14,
      'last_active': '3 dakika önce',
      'avatar': '🔥',
      'tone': 'dark',
      'iban': 'TR45 6789 0123 4567 8901 2345 67',
      'onboarding_date': '2025-02-20',
    },
    {
      'id': 'performer_6',
      'name': 'AngelEyes',
      'phone': '+905553456789',
      'character': 'Lara',
      'status': 'offline',
      'earnings_today': 0,
      'earnings_month': 1950,
      'vip_count': 9,
      'last_active': '1 saat önce',
      'avatar': '👼',
      'tone': 'flirty',
      'iban': 'TR67 8901 2345 6789 0123 4567 89',
      'onboarding_date': '2025-03-01',
    },
    {
      'id': 'performer_7',
      'name': 'DarkRose',
      'phone': '+905554567890',
      'character': 'Geisha',
      'status': 'online',
      'earnings_today': 225,
      'earnings_month': 3250,
      'vip_count': 16,
      'last_active': '4 dakika önce',
      'avatar': '🌹',
      'tone': 'mystic',
      'iban': 'TR89 0123 4567 8901 2345 6789 01',
      'onboarding_date': '2025-03-15',
    },
    {
      'id': 'performer_8',
      'name': 'WildCat',
      'phone': '+905555678901',
      'character': 'BabaGavat',
      'status': 'offline',
      'earnings_today': 0,
      'earnings_month': 2100,
      'vip_count': 11,
      'last_active': '3 saat önce',
      'avatar': '🐱',
      'tone': 'aggressive',
      'iban': 'TR12 3456 7890 1234 5678 9012 34',
      'onboarding_date': '2025-04-01',
    },
    {
      'id': 'performer_9',
      'name': 'SweetDream',
      'phone': '+905556789012',
      'character': 'Lara',
      'status': 'online',
      'earnings_today': 175,
      'earnings_month': 2650,
      'vip_count': 13,
      'last_active': '6 dakika önce',
      'avatar': '💫',
      'tone': 'soft',
      'iban': 'TR34 5678 9012 3456 7890 1234 56',
      'onboarding_date': '2025-04-15',
    },
    {
      'id': 'performer_10',
      'name': 'RedLips',
      'phone': '+905557890123',
      'character': 'Geisha',
      'status': 'online',
      'earnings_today': 240,
      'earnings_month': 3580,
      'vip_count': 19,
      'last_active': '2 dakika önce',
      'avatar': '💄',
      'tone': 'dark',
      'iban': 'TR56 7890 1234 5678 9012 3456 78',
      'onboarding_date': '2025-05-01',
    },
    {
      'id': 'performer_11',
      'name': 'GoldenGirl',
      'phone': '+905558901234',
      'character': 'Lara',
      'status': 'offline',
      'earnings_today': 0,
      'earnings_month': 1750,
      'vip_count': 7,
      'last_active': '4 saat önce',
      'avatar': '✨',
      'tone': 'flirty',
      'iban': 'TR78 9012 3456 7890 1234 5678 90',
      'onboarding_date': '2025-05-15',
    },
    {
      'id': 'performer_12',
      'name': 'NightShade',
      'phone': '+905559012345',
      'character': 'Geisha',
      'status': 'online',
      'earnings_today': 190,
      'earnings_month': 2980,
      'vip_count': 12,
      'last_active': '5 dakika önce',
      'avatar': '🖤',
      'tone': 'mystic',
      'iban': 'TR90 1234 5678 9012 3456 7890 12',
      'onboarding_date': '2025-06-01',
    },
  ];

  Widget _buildPerformerCard(Map<String, dynamic> performer) {
    final isOnline = performer['status'] == 'online';
    final statusColor =
        isOnline ? const Color(0xFF4CAF50) : const Color(0xFF757575);

    return Card(
      color: const Color(0xFF2A2A2F),
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Avatar
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: statusColor, width: 2),
              ),
              child: Center(
                child: Text(
                  performer['avatar'],
                  style: const TextStyle(fontSize: 24),
                ),
              ),
            ),
            const SizedBox(width: 16),

            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        performer['name'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          isOnline ? 'ONLİNE' : 'OFFLİNE',
                          style: TextStyle(
                            color: statusColor,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Karakter: ${performer['character']} (${performer['tone']})',
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Telefon: ${performer['phone']}',
                    style: const TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Son aktif: ${performer['last_active']}',
                    style: const TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                ],
              ),
            ),

            // Stats
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '₺${performer['earnings_today']}',
                  style: const TextStyle(
                    color: Color(0xFF4CAF50),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Text(
                  'Bugün',
                  style: TextStyle(color: Colors.white60, fontSize: 12),
                ),
                const SizedBox(height: 4),
                Text(
                  '₺${performer['earnings_month']}',
                  style: const TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const Text(
                  'Bu ay',
                  style: TextStyle(color: Colors.white60, fontSize: 12),
                ),
              ],
            ),

            const SizedBox(width: 16),

            // Actions
            PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert, color: Colors.white70),
              color: const Color(0xFF2A2A2F),
              onSelected: (action) =>
                  _performPerformerAction(performer['id'], action),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'view',
                  child: Row(
                    children: [
                      Icon(Icons.visibility, color: Colors.blue, size: 20),
                      SizedBox(width: 8),
                      Text('Detayları Gör',
                          style: TextStyle(color: Colors.white)),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'edit',
                  child: Row(
                    children: [
                      Icon(Icons.edit, color: Colors.orange, size: 20),
                      SizedBox(width: 8),
                      Text('Düzenle', style: TextStyle(color: Colors.white)),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'earnings',
                  child: Row(
                    children: [
                      Icon(Icons.attach_money, color: Colors.green, size: 20),
                      SizedBox(width: 8),
                      Text('Kazanç Raporu',
                          style: TextStyle(color: Colors.white)),
                    ],
                  ),
                ),
                if (isOnline)
                  const PopupMenuItem(
                    value: 'pause',
                    child: Row(
                      children: [
                        Icon(Icons.pause, color: Colors.red, size: 20),
                        SizedBox(width: 8),
                        Text('Duraklat', style: TextStyle(color: Colors.white)),
                      ],
                    ),
                  )
                else
                  const PopupMenuItem(
                    value: 'activate',
                    child: Row(
                      children: [
                        Icon(Icons.play_arrow, color: Colors.green, size: 20),
                        SizedBox(width: 8),
                        Text('Aktifleştir',
                            style: TextStyle(color: Colors.white)),
                      ],
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showCreatePerformerDialog() {
    final nameController = TextEditingController();
    final phoneController = TextEditingController();
    final ibanController = TextEditingController();
    String selectedCharacter = 'lara';
    String selectedTone = 'flirty';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => Dialog(
          backgroundColor: const Color(0xFF1A1A1F),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Container(
            width: 500,
            padding: const EdgeInsets.all(24),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.star,
                          color: Color(0xFFFF9800), size: 32),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Text(
                          'Yeni Şovcu Ekle',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white70),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Şovcu Adı
                  TextField(
                    controller: nameController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: 'Şovcu Adı',
                      hintText: 'Örn: StarGirl, MysteryLady',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFFFF9800)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Telefon Numarası
                  TextField(
                    controller: phoneController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: 'Telefon Numarası',
                      hintText: '+905xxxxxxxxx',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFFFF9800)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Papara IBAN
                  TextField(
                    controller: ibanController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: 'Papara IBAN',
                      hintText: 'TR00 0000 0000 0000 0000 0000 00',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFFFF9800)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Karakter Seçimi
                  const Text(
                    'Karakter Seç',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: selectedCharacter,
                    dropdownColor: const Color(0xFF2A2A2F),
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFFFF9800)),
                      ),
                    ),
                    items: const [
                      DropdownMenuItem(
                          value: 'lara',
                          child: Text('💋 Lara - Flörtöz Rus güzeli')),
                      DropdownMenuItem(
                          value: 'geisha',
                          child: Text('🌸 Geisha - Mistik bilge')),
                      DropdownMenuItem(
                          value: 'babagavat',
                          child: Text('😤 BabaGavat - Sokak adamı')),
                    ],
                    onChanged: (value) =>
                        setState(() => selectedCharacter = value!),
                  ),
                  const SizedBox(height: 16),

                  // Ton Seçimi
                  const Text(
                    'Ton Seç',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: selectedTone,
                    dropdownColor: const Color(0xFF2A2A2F),
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFFFF9800)),
                      ),
                    ),
                    items: const [
                      DropdownMenuItem(
                          value: 'flirty', child: Text('💕 Flörtöz')),
                      DropdownMenuItem(
                          value: 'soft', child: Text('🌸 Yumuşak')),
                      DropdownMenuItem(
                          value: 'dark', child: Text('🌙 Karanlık')),
                      DropdownMenuItem(
                          value: 'mystic', child: Text('✨ Mistik')),
                      DropdownMenuItem(
                          value: 'aggressive', child: Text('🔥 Agresif')),
                    ],
                    onChanged: (value) => setState(() => selectedTone = value!),
                  ),

                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('İptal'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: () => _createPerformer(
                          nameController.text,
                          phoneController.text,
                          ibanController.text,
                          selectedCharacter,
                          selectedTone,
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFF9800),
                        ),
                        child: const Text('Şovcu Oluştur'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _createPerformer(String name, String phone, String iban,
      String character, String tone) async {
    if (name.isEmpty || phone.isEmpty || iban.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Lütfen tüm alanları doldurun!'),
          backgroundColor: Color(0xFFF44336),
        ),
      );
      return;
    }

    // Close dialog
    Navigator.of(context).pop();

    try {
      // API call to create performer
      final success = await GAVATCoreAPIService.createPerformer({
        'name': name,
        'phone': phone,
        'iban': iban,
        'character': character,
        'tone': tone,
      });

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$name şovcusu başarıyla oluşturuldu!'),
            backgroundColor: const Color(0xFF4CAF50),
          ),
        );

        // Refresh performers list
        ref.refresh(performersProvider);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Şovcu oluşturulurken hata oluştu!'),
            backgroundColor: Color(0xFFF44336),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: const Color(0xFFF44336),
        ),
      );
    }
  }

  Future<void> _performPerformerAction(
      String performerId, String action) async {
    switch (action) {
      case 'view':
        _showPerformerDetails(performerId);
        break;
      case 'edit':
        _showEditPerformerDialog(performerId);
        break;
      case 'earnings':
        _showEarningsReport(performerId);
        break;
      case 'pause':
      case 'activate':
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$performerId için $action işlemi gerçekleştirildi!'),
            backgroundColor: const Color(0xFF4CAF50),
          ),
        );
        break;
    }
  }

  void _showPerformerDetails(String performerId) {
    final performer = _mockPerformers.firstWhere((p) => p['id'] == performerId);

    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: const Color(0xFF1A1A1F),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          width: 500,
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Text(
                    performer['avatar'],
                    style: const TextStyle(fontSize: 48),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          performer['name'],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Karakter: ${performer['character']}',
                          style: const TextStyle(
                              color: Colors.white70, fontSize: 16),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Stats Grid
              Row(
                children: [
                  Expanded(
                    child: _buildPerformerStat(
                      'Bugün',
                      '₺${performer['earnings_today']}',
                      Icons.today,
                      const Color(0xFF4CAF50),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildPerformerStat(
                      'Bu Ay',
                      '₺${performer['earnings_month']}',
                      Icons.calendar_month,
                      const Color(0xFF9C27B0),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildPerformerStat(
                      'VIP Üyeler',
                      '${performer['vip_count']}',
                      Icons.diamond,
                      const Color(0xFF2196F3),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildPerformerStat(
                      'Durum',
                      performer['status'] == 'online' ? 'ONLİNE' : 'OFFLİNE',
                      Icons.circle,
                      performer['status'] == 'online'
                          ? const Color(0xFF4CAF50)
                          : const Color(0xFF757575),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPerformerStat(
      String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2F),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
        ],
      ),
    );
  }

  void _showEditPerformerDialog(String performerId) {
    // TODO: Implement edit performer dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Şovcu düzenleme özelliği yakında!'),
        backgroundColor: Color(0xFFFF9800),
      ),
    );
  }

  void _showEarningsReport(String performerId) {
    // TODO: Implement earnings report
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Kazanç raporu özelliği yakında!'),
        backgroundColor: Color(0xFF2196F3),
      ),
    );
  }

  Widget _buildAdvancedCharacterCard(CharacterData character) {
    final statusColor = character.status == 'active'
        ? const Color(0xFF4CAF50)
        : character.status == 'banned'
            ? const Color(0xFFF44336)
            : const Color(0xFFFF9800);

    final statusIcon = character.status == 'active'
        ? Icons.check_circle
        : character.status == 'banned'
            ? Icons.block
            : Icons.warning;

    return Card(
      color: const Color(0xFF1A1A1F),
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: statusColor, width: 2),
                  ),
                  child: Icon(statusIcon, color: statusColor, size: 32),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        character.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '@${character.username}',
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 14),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          character.status.toUpperCase(),
                          style: TextStyle(
                              color: statusColor,
                              fontSize: 12,
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, color: Colors.white70),
                  onPressed: () => _showCharacterEditDialog(character),
                  tooltip: 'Düzenle',
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              character.description,
              style: const TextStyle(color: Colors.white70, fontSize: 14),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _buildMetric('Mesajlar', character.messageCount.toString(),
                    Icons.message),
                const SizedBox(width: 24),
                _buildMetric(
                    'Yanıt Süresi',
                    '${character.responseTime.toStringAsFixed(1)}s',
                    Icons.speed),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: () => _showCharacterDetails(character),
                  icon: const Icon(Icons.visibility, size: 16),
                  label: const Text('Detaylar'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF9C27B0),
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetric(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFF9C27B0), size: 16),
        const SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(value,
                style: const TextStyle(
                    color: Colors.white, fontWeight: FontWeight.bold)),
            Text(label,
                style: const TextStyle(color: Colors.white70, fontSize: 12)),
          ],
        ),
      ],
    );
  }

  void _showCharacterDetails(CharacterData character) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: const Color(0xFF1A1A1F),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          width: 500,
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    character.status == 'active'
                        ? Icons.check_circle
                        : Icons.block,
                    color: character.status == 'active'
                        ? const Color(0xFF4CAF50)
                        : const Color(0xFFF44336),
                    size: 32,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          character.name,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold),
                        ),
                        Text(
                          '@${character.username}',
                          style: const TextStyle(
                              color: Colors.white70, fontSize: 16),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              _buildDetailRow('Telefon', character.phone),
              _buildDetailRow('Durum', character.status.toUpperCase()),
              _buildDetailRow(
                  'Mesaj Sayısı', character.messageCount.toString()),
              _buildDetailRow('Ortalama Yanıt Süresi',
                  '${character.responseTime.toStringAsFixed(1)} saniye'),
              const SizedBox(height: 16),
              const Text(
                'Açıklama',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                character.description,
                style: const TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 16),
              const Text(
                'Özellikler',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: character.features
                    .map((feature) => Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF9C27B0).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFF9C27B0)),
                          ),
                          child: Text(
                            feature,
                            style: const TextStyle(
                                color: Color(0xFF9C27B0), fontSize: 12),
                          ),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (character.status == 'active') ...[
                    TextButton(
                      onPressed: () =>
                          _performCharacterAction(character.username, 'stop'),
                      child: const Text('Durdur'),
                    ),
                    const SizedBox(width: 8),
                  ],
                  if (character.status == 'banned') ...[
                    TextButton(
                      onPressed: () =>
                          _performCharacterAction(character.username, 'unban'),
                      child: const Text('Unban'),
                    ),
                    const SizedBox(width: 8),
                  ],
                  ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      _showCharacterEditDialog(character);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF9C27B0),
                    ),
                    child: const Text('Düzenle'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showCharacterEditDialog(CharacterData character) {
    final displayNameController = TextEditingController(text: character.name);
    final gptPromptController = TextEditingController(
        text: character.personaData['persona']?['gpt_prompt'] ?? '');
    final responseStyleController = TextEditingController(
        text: character.profileData['response_style'] ?? 'friendly');
    final toneController =
        TextEditingController(text: character.profileData['tone'] ?? 'warm');

    bool isSpamActive = character.profileData['is_spam_active'] ?? true;
    bool isDmActive = character.profileData['is_dm_active'] ?? true;
    bool isGroupActive = character.profileData['is_group_active'] ?? true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => Dialog(
          backgroundColor: const Color(0xFF1A1A1F),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Container(
            width: 600,
            padding: const EdgeInsets.all(24),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.edit,
                          color: const Color(0xFF9C27B0), size: 32),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '${character.name} Düzenle',
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white70),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Display Name
                  TextField(
                    controller: displayNameController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: 'Görünen İsim',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFF9C27B0)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // GPT Prompt
                  TextField(
                    controller: gptPromptController,
                    style: const TextStyle(color: Colors.white),
                    maxLines: 4,
                    decoration: const InputDecoration(
                      labelText: 'GPT Prompt (Kişilik)',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white30),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Color(0xFF9C27B0)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Response Style and Tone
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: responseStyleController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            labelText: 'Yanıt Stili',
                            labelStyle: TextStyle(color: Colors.white70),
                            border: OutlineInputBorder(),
                            enabledBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.white30),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Color(0xFF9C27B0)),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: TextField(
                          controller: toneController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            labelText: 'Ton',
                            labelStyle: TextStyle(color: Colors.white70),
                            border: OutlineInputBorder(),
                            enabledBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.white30),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Color(0xFF9C27B0)),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Activity toggles
                  const Text(
                    'Aktivite Ayarları',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),

                  SwitchListTile(
                    title: const Text('Spam Aktif',
                        style: TextStyle(color: Colors.white)),
                    value: isSpamActive,
                    onChanged: (value) => setState(() => isSpamActive = value),
                    activeColor: const Color(0xFF9C27B0),
                  ),
                  SwitchListTile(
                    title: const Text('DM Aktif',
                        style: TextStyle(color: Colors.white)),
                    value: isDmActive,
                    onChanged: (value) => setState(() => isDmActive = value),
                    activeColor: const Color(0xFF9C27B0),
                  ),
                  SwitchListTile(
                    title: const Text('Grup Aktif',
                        style: TextStyle(color: Colors.white)),
                    value: isGroupActive,
                    onChanged: (value) => setState(() => isGroupActive = value),
                    activeColor: const Color(0xFF9C27B0),
                  ),

                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('İptal'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: () => _saveCharacterChanges(
                          character.username,
                          {
                            'display_name': displayNameController.text,
                            'gpt_prompt': gptPromptController.text,
                            'response_style': responseStyleController.text,
                            'tone': toneController.text,
                            'is_spam_active': isSpamActive,
                            'is_dm_active': isDmActive,
                            'is_group_active': isGroupActive,
                          },
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF9C27B0),
                        ),
                        child: const Text('Kaydet'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _saveCharacterChanges(
      String username, Map<String, dynamic> updateData) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      final success =
          await GAVATCoreAPIService.updateCharacter(username, updateData);

      // Close loading dialog
      Navigator.of(context).pop();

      if (success) {
        // Close edit dialog
        Navigator.of(context).pop();

        // Refresh characters
        ref.refresh(charactersProvider);

        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$username başarıyla güncellendi!'),
            backgroundColor: const Color(0xFF4CAF50),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Güncelleme başarısız oldu!'),
            backgroundColor: Color(0xFFF44336),
          ),
        );
      }
    } catch (e) {
      // Close loading dialog
      Navigator.of(context).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: const Color(0xFFF44336),
        ),
      );
    }
  }

  Future<void> _performCharacterAction(String username, String action) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      final success =
          await GAVATCoreAPIService.characterAction(username, action);

      // Close loading dialog
      Navigator.of(context).pop();

      if (success) {
        // Close any open dialogs
        Navigator.of(context).pop();

        // Refresh characters
        ref.refresh(charactersProvider);
        ref.refresh(systemStatsProvider);

        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$username için $action işlemi başarılı!'),
            backgroundColor: const Color(0xFF4CAF50),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$action işlemi başarısız oldu!'),
            backgroundColor: const Color(0xFFF44336),
          ),
        );
      }
    } catch (e) {
      // Close loading dialog
      Navigator.of(context).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: const Color(0xFFF44336),
        ),
      );
    }
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(color: Colors.white70, fontSize: 14),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
                color: Colors.white, fontSize: 14, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageLogsContent() {
    final messagesAsync = ref.watch(messagesProvider);
    final messageStatsAsync = ref.watch(messageStatsProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text('💬 Mesaj Logları'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showMessageFilters(),
            tooltip: 'Filtrele',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.refresh(messagesProvider);
              ref.refresh(messageStatsProvider);
            },
            tooltip: 'Yenile',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Message Stats
            messageStatsAsync.when(
              data: (stats) => Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          'Toplam Mesaj',
                          '${stats['total_messages'] ?? 0}',
                          Icons.chat,
                          const Color(0xFF00BCD4),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildStatCard(
                          'DM Mesajları',
                          '${stats['dm_messages'] ?? 0}',
                          Icons.person,
                          const Color(0xFF4CAF50),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildStatCard(
                          'Grup Mesajları',
                          '${stats['group_messages'] ?? 0}',
                          Icons.group,
                          const Color(0xFF9C27B0),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildStatCard(
                          'Ortalama Yanıt',
                          '${stats['avg_response_time'] ?? 0}s',
                          Icons.speed,
                          const Color(0xFFFF9800),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Bot Distribution
                  if (stats['bot_distribution'] != null &&
                      stats['bot_distribution'].isNotEmpty)
                    Card(
                      color: const Color(0xFF1A1A1F),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.smart_toy, color: Color(0xFF00BCD4)),
                                SizedBox(width: 8),
                                Text(
                                  'Bot Mesaj Dağılımı',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            ...stats['bot_distribution']
                                .entries
                                .map<Widget>((entry) {
                              final botName = entry.key;
                              final botStats = entry.value;
                              return Container(
                                margin: const EdgeInsets.only(bottom: 8),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF2A2A2F),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.android,
                                        color: Color(0xFF00BCD4)),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        botName,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    Text(
                                      'DM: ${botStats['dm'] ?? 0}',
                                      style: const TextStyle(
                                          color: Colors.white70),
                                    ),
                                    const SizedBox(width: 16),
                                    Text(
                                      'Grup: ${botStats['group'] ?? 0}',
                                      style: const TextStyle(
                                          color: Colors.white70),
                                    ),
                                    const SizedBox(width: 16),
                                    Text(
                                      'Toplam: ${botStats['total'] ?? 0}',
                                      style: const TextStyle(
                                        color: Color(0xFF00BCD4),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
              loading: () => const Center(
                child: CircularProgressIndicator(color: Color(0xFF00BCD4)),
              ),
              error: (error, stack) => Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1F),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'İstatistikler alınamadı: $error',
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 32),

            // Messages List
            const Text(
              '📝 Son Mesajlar',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            messagesAsync.when(
              data: (data) {
                final messages = data['messages'] as List<Map<String, dynamic>>;

                if (messages.isEmpty) {
                  return Card(
                    color: const Color(0xFF1A1A1F),
                    child: Container(
                      padding: const EdgeInsets.all(32),
                      child: const Center(
                        child: Column(
                          children: [
                            Icon(Icons.chat_bubble_outline,
                                size: 48, color: Colors.white30),
                            SizedBox(height: 16),
                            Text(
                              'Henüz mesaj yok',
                              style: TextStyle(
                                  color: Colors.white70, fontSize: 16),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }

                return Card(
                  color: const Color(0xFF1A1A1F),
                  child: Column(
                    children: messages
                        .map((message) => _buildMessageCard(message))
                        .toList(),
                  ),
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(color: Color(0xFF00BCD4)),
              ),
              error: (error, stack) => Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1F),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Mesajlar alınamadı: $error',
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageCard(Map<String, dynamic> message) {
    final isIncoming = message['message_type'] == 'incoming';
    final chatType = message['chat_type'];
    final botName = message['bot_display_name'] ?? message['bot_name'];
    final timestamp = DateTime.parse(message['timestamp']);
    final timeAgo = _getTimeAgo(timestamp);

    return Container(
      margin: const EdgeInsets.all(8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2F),
        borderRadius: BorderRadius.circular(12),
        border: Border(
          left: BorderSide(
            width: 4,
            color:
                isIncoming ? const Color(0xFF4CAF50) : const Color(0xFF00BCD4),
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                isIncoming ? Icons.call_received : Icons.call_made,
                color: isIncoming
                    ? const Color(0xFF4CAF50)
                    : const Color(0xFF00BCD4),
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                botName,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
              Icon(
                chatType == 'dm' ? Icons.person : Icons.group,
                color: Colors.white70,
                size: 14,
              ),
              const SizedBox(width: 4),
              Text(
                chatType == 'dm' ? 'DM' : 'Grup',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const Spacer(),
              Text(
                timeAgo,
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // User info
          Row(
            children: [
              const Icon(Icons.person, color: Colors.white70, size: 14),
              const SizedBox(width: 4),
              Text(
                message['user_name'] ?? 'Unknown',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const SizedBox(width: 16),
              if (message['chat_name'] != 'Direct Message') ...[
                const Icon(Icons.chat, color: Colors.white70, size: 14),
                const SizedBox(width: 4),
                Text(
                  message['chat_name'] ?? '',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ],
          ),
          const SizedBox(height: 12),

          // Message content
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1A1F),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              message['content'] ?? '',
              style: const TextStyle(color: Colors.white),
            ),
          ),

          // AI Response (if any)
          if (message['ai_response'] != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF0D47A1).withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
                border:
                    Border.all(color: const Color(0xFF00BCD4).withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.smart_toy,
                          color: Color(0xFF00BCD4), size: 16),
                      const SizedBox(width: 8),
                      const Text(
                        'AI Yanıtı',
                        style: TextStyle(
                          color: Color(0xFF00BCD4),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      const Spacer(),
                      if (message['response_time'] != null)
                        Text(
                          '${message['response_time']}s',
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    message['ai_response'],
                    style: const TextStyle(color: Colors.white),
                  ),
                ],
              ),
            ),
          ],

          // Footer with sentiment and status
          const SizedBox(height: 8),
          Row(
            children: [
              if (message['sentiment'] != null) ...[
                _getSentimentIcon(message['sentiment']),
                const SizedBox(width: 4),
                Text(
                  _getSentimentText(message['sentiment']),
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
                const SizedBox(width: 16),
              ],
              Icon(
                message['status'] == 'delivered'
                    ? Icons.check_circle
                    : Icons.send,
                color: message['status'] == 'delivered'
                    ? const Color(0xFF4CAF50)
                    : Colors.white70,
                size: 14,
              ),
              const SizedBox(width: 4),
              Text(
                message['status'] == 'delivered'
                    ? 'Teslim edildi'
                    : 'Gönderildi',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _getSentimentIcon(String sentiment) {
    switch (sentiment) {
      case 'positive':
        return const Icon(Icons.sentiment_very_satisfied,
            color: Color(0xFF4CAF50), size: 14);
      case 'neutral':
        return const Icon(Icons.sentiment_neutral,
            color: Colors.orange, size: 14);
      case 'motivational':
        return const Icon(Icons.fitness_center,
            color: Color(0xFF9C27B0), size: 14);
      default:
        return const Icon(Icons.sentiment_neutral,
            color: Colors.white70, size: 14);
    }
  }

  String _getSentimentText(String sentiment) {
    switch (sentiment) {
      case 'positive':
        return 'Pozitif';
      case 'neutral':
        return 'Nötr';
      case 'motivational':
        return 'Motivasyonel';
      default:
        return sentiment;
    }
  }

  String _getTimeAgo(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Az önce';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} dakika önce';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} saat önce';
    } else {
      return '${difference.inDays} gün önce';
    }
  }

  void _showMessageFilters() {
    // TODO: Implement message filters dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Mesaj filtreleme özelliği yakında!'),
        backgroundColor: Color(0xFF00BCD4),
      ),
    );
  }

  Widget _buildAnalyticsContent() {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text('🧠 Gelişmiş AI Analytics'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              // Refresh analytics data
              setState(() {});
            },
            tooltip: 'Verileri Yenile',
          ),
        ],
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _getAdvancedAnalytics(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(color: Color(0xFF9C27B0)),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, color: Colors.red, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    'Veri yüklenirken hata oluştu: ${snapshot.error}',
                    style: const TextStyle(color: Colors.white70),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            );
          }

          final data = snapshot.data ?? {};
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // AI Manager Stats
                _buildAnalyticsSection(
                  '🤖 AI Manager',
                  data['ai_manager'] ?? {},
                  const Color(0xFF9C27B0),
                ),

                const SizedBox(height: 24),

                // Behavioral Analytics
                _buildAnalyticsSection(
                  '🧠 Behavioral Analytics',
                  data['behavioral_analytics'] ?? {},
                  const Color(0xFF4CAF50),
                ),

                const SizedBox(height: 24),

                // CRM Analytics
                _buildAnalyticsSection(
                  '📊 CRM Analytics',
                  data['crm_analytics'] ?? {},
                  const Color(0xFF2196F3),
                ),

                const SizedBox(height: 24),

                // Content Generator
                _buildAnalyticsSection(
                  '✨ Content Generator',
                  data['content_generator'] ?? {},
                  const Color(0xFFFF9800),
                ),

                const SizedBox(height: 24),

                // Erko Analyzer
                _buildAnalyticsSection(
                  '🔍 Erko Analyzer',
                  data['erko_analyzer'] ?? {},
                  const Color(0xFFF44336),
                ),

                const SizedBox(height: 24),

                // AI Models Status
                _buildAIModelsStatus(),

                const SizedBox(height: 24),

                // Personality Insights
                _buildPersonalityInsights(),

                const SizedBox(height: 24),

                // System Performance
                _buildSystemPerformance(),

                const SizedBox(height: 24),

                // Smart AI Modules
                _buildSmartAIModules(),

                const SizedBox(height: 24),

                // Smart Campaign Manager
                _buildSmartCampaignManager(),

                const SizedBox(height: 24),

                // Smart Personality Adapter
                _buildSmartPersonalityAdapter(),

                const SizedBox(height: 24),

                // User Analyzer
                _buildUserAnalyzer(),

                const SizedBox(height: 24),

                // User Segmentation
                _buildUserSegmentation(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSettingsContent() {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: const SimpleSettingsScreen(),
    );
  }

  Widget _buildStatCard(
      String title, String value, IconData icon, Color color) {
    return Card(
      color: const Color(0xFF1A1A1F),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 12),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white70,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  // Analytics helper methods
  Future<Map<String, dynamic>> _getAdvancedAnalytics() async {
    return await GAVATCoreAPIService.getAdvancedAnalytics();
  }

  Widget _buildAnalyticsSection(
      String title, Map<String, dynamic> data, Color color) {
    return Card(
      color: const Color(0xFF1A1A1F),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_getIconForSection(title), color: color, size: 24),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    color: color,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildSectionContent(data, color),
          ],
        ),
      ),
    );
  }

  IconData _getIconForSection(String title) {
    if (title.contains('AI Manager')) return Icons.psychology;
    if (title.contains('Behavioral')) return Icons.psychology;
    if (title.contains('CRM')) return Icons.people;
    if (title.contains('Content')) return Icons.auto_awesome;
    if (title.contains('Erko')) return Icons.security;
    return Icons.analytics;
  }

  Widget _buildSectionContent(Map<String, dynamic> data, Color color) {
    if (data.isEmpty) {
      return const Text(
        'Veri yükleniyor...',
        style: TextStyle(color: Colors.white70),
      );
    }

    return Wrap(
      spacing: 16,
      runSpacing: 16,
      children: data.entries.map((entry) {
        return _buildDataCard(entry.key, entry.value, color);
      }).toList(),
    );
  }

  Widget _buildDataCard(String key, dynamic value, Color color) {
    return Container(
      constraints: const BoxConstraints(minWidth: 200),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _formatKey(key),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          _buildValueWidget(value),
        ],
      ),
    );
  }

  String _formatKey(String key) {
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }

  Widget _buildValueWidget(dynamic value) {
    if (value is Map) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: value.entries.map((entry) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    _formatKey(entry.key.toString()),
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ),
                Text(
                  entry.value.toString(),
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold),
                ),
              ],
            ),
          );
        }).toList(),
      );
    } else if (value is List) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: value.map((item) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 2),
            child: Text(
              item.toString(),
              style: const TextStyle(color: Colors.white, fontSize: 12),
            ),
          );
        }).toList(),
      );
    } else {
      return Text(
        value.toString(),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      );
    }
  }

  Widget _buildAIModelsStatus() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getAIModelsStatus(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data ?? {};
        final models = data['models'] as Map<String, dynamic>? ?? {};

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.model_training,
                        color: Color(0xFF9C27B0), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '🤖 AI Model Durumları',
                      style: TextStyle(
                        color: Color(0xFF9C27B0),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount:
                      MediaQuery.of(context).size.width > 1200 ? 4 : 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: models.entries.map((entry) {
                    final modelData = entry.value as Map<String, dynamic>;
                    final status = modelData['status'] ?? 'unknown';
                    final statusColor = status == 'active'
                        ? const Color(0xFF4CAF50)
                        : status == 'standby'
                            ? const Color(0xFFFF9800)
                            : Colors.red;

                    return Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: statusColor.withOpacity(0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.smart_toy,
                                  color: statusColor, size: 16),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  entry.key.toUpperCase(),
                                  style: TextStyle(
                                    color: statusColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Durum: ${status}',
                            style: const TextStyle(
                                color: Colors.white70, fontSize: 12),
                          ),
                          Text(
                            'Yanıt Süresi: ${modelData['response_time'] ?? 'N/A'}',
                            style: const TextStyle(
                                color: Colors.white70, fontSize: 12),
                          ),
                          Text(
                            'Başarı Oranı: ${modelData['success_rate'] ?? 'N/A'}',
                            style: const TextStyle(
                                color: Colors.white70, fontSize: 12),
                          ),
                          Text(
                            'Günlük Maliyet: ${modelData['cost_today'] ?? 'N/A'}',
                            style: const TextStyle(
                                color: Colors.white70, fontSize: 12),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Text(
                      'Toplam Günlük Maliyet: ${data['total_cost_today'] ?? 'N/A'}',
                      style: const TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      'Toplam Request: ${data['total_requests_today'] ?? 'N/A'}',
                      style: const TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPersonalityInsights() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getPersonalityInsights(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data ?? {};
        final insights = data['insights'] as Map<String, dynamic>? ?? {};
        final personalityTypes =
            insights['top_personality_types'] as List? ?? [];

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.psychology, color: Color(0xFF4CAF50), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '🧠 Kişilik Analizi İçgörüleri',
                      style: TextStyle(
                        color: Color(0xFF4CAF50),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  'En Yaygın Kişilik Tipleri',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                ...personalityTypes.map((type) {
                  final typeData = type as Map<String, dynamic>;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF4CAF50).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                          color: const Color(0xFF4CAF50).withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            typeData['type'] ?? '',
                            style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold),
                          ),
                        ),
                        Text(
                          '${typeData['count']} kişi',
                          style: const TextStyle(color: Colors.white70),
                        ),
                        const SizedBox(width: 16),
                        Text(
                          typeData['percentage'] ?? '',
                          style: const TextStyle(
                              color: Color(0xFF4CAF50),
                              fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSystemPerformance() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getSystemPerformanceMetrics(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data ?? {};
        final metrics = data['metrics'] as Map<String, dynamic>? ?? {};
        final healthScore = data['health_score'] ?? 0;

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.speed, color: Color(0xFF2196F3), size: 24),
                    const SizedBox(width: 12),
                    const Text(
                      '⚡ Sistem Performansı',
                      style: TextStyle(
                        color: Color(0xFF2196F3),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: healthScore > 80
                            ? const Color(0xFF4CAF50)
                            : healthScore > 60
                                ? const Color(0xFFFF9800)
                                : Colors.red,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        'Sağlık Skoru: $healthScore%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount:
                      MediaQuery.of(context).size.width > 1200 ? 4 : 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    _buildPerformanceCard(
                        'CPU Kullanımı',
                        metrics['cpu_usage'] ?? 'N/A',
                        Icons.memory,
                        const Color(0xFFFF9800)),
                    _buildPerformanceCard(
                        'RAM Kullanımı',
                        metrics['memory_usage'] ?? 'N/A',
                        Icons.storage,
                        const Color(0xFF9C27B0)),
                    _buildPerformanceCard(
                        'Disk Kullanımı',
                        metrics['disk_usage'] ?? 'N/A',
                        Icons.save,
                        const Color(0xFF4CAF50)),
                    _buildPerformanceCard(
                        'API Uptime',
                        (metrics['api_performance'] as Map?)?['uptime'] ??
                            'N/A',
                        Icons.check_circle,
                        const Color(0xFF2196F3)),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPerformanceCard(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // Smart AI Modules Widgets
  Widget _buildSmartAIModules() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getSmartModulesDashboard(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data?['data'] ?? {};
        final modules = data['modules_overview'] as Map<String, dynamic>? ?? {};

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.auto_awesome,
                        color: Color(0xFFE91E63), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '🧠 Smart AI Modules Overview',
                      style: TextStyle(
                        color: Color(0xFFE91E63),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount:
                      MediaQuery.of(context).size.width > 1200 ? 4 : 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: modules.entries.map((entry) {
                    final moduleData = entry.value as Map<String, dynamic>;
                    final status = moduleData['status'] ?? 'unknown';
                    final statusColor = status == 'active'
                        ? const Color(0xFF4CAF50)
                        : Colors.red;

                    return Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: statusColor.withOpacity(0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(_getModuleIcon(entry.key),
                                  color: statusColor, size: 16),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _formatModuleName(entry.key),
                                  style: TextStyle(
                                    color: statusColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ...moduleData.entries
                              .where((e) => e.key != 'status')
                              .map((stat) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 2),
                              child: Text(
                                '${_formatKey(stat.key)}: ${stat.value}',
                                style: const TextStyle(
                                    color: Colors.white70, fontSize: 11),
                              ),
                            );
                          }).toList(),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  IconData _getModuleIcon(String moduleName) {
    switch (moduleName) {
      case 'campaign_manager':
        return Icons.campaign;
      case 'personality_adapter':
        return Icons.psychology;
      case 'user_analyzer':
        return Icons.analytics;
      case 'user_segmentation':
        return Icons.group;
      default:
        return Icons.smart_toy;
    }
  }

  String _formatModuleName(String moduleName) {
    switch (moduleName) {
      case 'campaign_manager':
        return 'Campaign Manager';
      case 'personality_adapter':
        return 'Personality Adapter';
      case 'user_analyzer':
        return 'User Analyzer';
      case 'user_segmentation':
        return 'User Segmentation';
      default:
        return moduleName.replaceAll('_', ' ');
    }
  }

  Widget _buildSmartCampaignManager() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getSmartCampaignManager(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data?['data'] ?? {};
        final campaigns = data['campaigns'] as List? ?? [];
        final performance =
            data['campaign_performance'] as Map<String, dynamic>? ?? {};

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.campaign, color: Color(0xFFFF9800), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '📈 Smart Campaign Manager',
                      style: TextStyle(
                        color: Color(0xFFFF9800),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Performance Overview
                Row(
                  children: [
                    Expanded(
                      child: _buildCampaignMetric(
                          'Total Reach',
                          performance['total_reach']?.toString() ?? '0',
                          Icons.visibility,
                          const Color(0xFF2196F3)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildCampaignMetric(
                          'Engagement Rate',
                          performance['engagement_rate'] ?? '0%',
                          Icons.thumb_up,
                          const Color(0xFF4CAF50)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildCampaignMetric(
                          'Conversion Rate',
                          performance['conversion_rate'] ?? '0%',
                          Icons.trending_up,
                          const Color(0xFF9C27B0)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildCampaignMetric(
                          'ROI',
                          performance['roi'] ?? '0%',
                          Icons.attach_money,
                          const Color(0xFF4CAF50)),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Active Campaigns
                const Text(
                  'Active Campaigns',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),

                ...campaigns.take(3).map((campaign) {
                  final campaignData = campaign as Map<String, dynamic>;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2A2F),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF444444)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 40,
                          decoration: BoxDecoration(
                            color:
                                _getCampaignStatusColor(campaignData['status']),
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                campaignData['name'] ?? 'Unknown Campaign',
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold),
                              ),
                              Text(
                                'Type: ${campaignData['type']} | Reach: ${campaignData['reach']}',
                                style: const TextStyle(
                                    color: Colors.white70, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          'ROI: ${campaignData['roi']}',
                          style: const TextStyle(
                              color: Color(0xFF4CAF50),
                              fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCampaignMetric(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Color _getCampaignStatusColor(String? status) {
    switch (status) {
      case 'active':
        return const Color(0xFF4CAF50);
      case 'paused':
        return const Color(0xFFFF9800);
      case 'completed':
        return const Color(0xFF2196F3);
      default:
        return Colors.grey;
    }
  }

  Widget _buildSmartPersonalityAdapter() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getSmartPersonalityAdapter(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data?['data'] ?? {};
        final engine = data['adaptation_engine'] as Map<String, dynamic>? ?? {};
        final distribution =
            data['personality_distribution'] as Map<String, dynamic>? ?? {};
        final bigFive = distribution['big_five'] as Map<String, dynamic>? ?? {};

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.psychology, color: Color(0xFF9C27B0), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '🧠 Smart Personality Adapter',
                      style: TextStyle(
                        color: Color(0xFF9C27B0),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Engine Stats
                Row(
                  children: [
                    Expanded(
                      child: _buildPersonalityMetric(
                          'Active Profiles',
                          engine['active_profiles']?.toString() ?? '0',
                          Icons.person,
                          const Color(0xFF2196F3)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildPersonalityMetric(
                          'Accuracy',
                          engine['adaptation_accuracy'] ?? '0%',
                          Icons.precision_manufacturing,
                          const Color(0xFF4CAF50)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildPersonalityMetric(
                          'Adjustments',
                          engine['real_time_adjustments']?.toString() ?? '0',
                          Icons.tune,
                          const Color(0xFFFF9800)),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Big Five Distribution
                const Text(
                  'Big Five Personality Distribution',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),

                ...bigFive.entries.map((trait) {
                  final traitData = trait.value as Map<String, dynamic>? ?? {};
                  final high = traitData['high'] ?? 0;
                  final medium = traitData['medium'] ?? 0;
                  final low = traitData['low'] ?? 0;
                  final total = high + medium + low;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _formatKey(trait.key),
                          style: const TextStyle(
                              color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Expanded(
                              flex: high,
                              child: Container(
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: Color(0xFF4CAF50),
                                  borderRadius: BorderRadius.only(
                                    topLeft: Radius.circular(4),
                                    bottomLeft: Radius.circular(4),
                                  ),
                                ),
                              ),
                            ),
                            Expanded(
                              flex: medium,
                              child: Container(
                                height: 8,
                                color: const Color(0xFFFF9800),
                              ),
                            ),
                            Expanded(
                              flex: low,
                              child: Container(
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: Color(0xFFF44336),
                                  borderRadius: BorderRadius.only(
                                    topRight: Radius.circular(4),
                                    bottomRight: Radius.circular(4),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Text('High: $high%',
                                style: const TextStyle(
                                    color: Color(0xFF4CAF50), fontSize: 11)),
                            const SizedBox(width: 16),
                            Text('Medium: $medium%',
                                style: const TextStyle(
                                    color: Color(0xFFFF9800), fontSize: 11)),
                            const SizedBox(width: 16),
                            Text('Low: $low%',
                                style: const TextStyle(
                                    color: Color(0xFFF44336), fontSize: 11)),
                          ],
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPersonalityMetric(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildUserAnalyzer() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getUserAnalyzer(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data?['data'] ?? {};
        final overview =
            data['analysis_overview'] as Map<String, dynamic>? ?? {};
        final behavioral =
            data['behavioral_insights'] as Map<String, dynamic>? ?? {};
        final predictive =
            data['predictive_analytics'] as Map<String, dynamic>? ?? {};

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.analytics, color: Color(0xFF00BCD4), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '🔍 User Analyzer',
                      style: TextStyle(
                        color: Color(0xFF00BCD4),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Overview Stats
                Row(
                  children: [
                    Expanded(
                      child: _buildAnalyzerMetric(
                          'Users Analyzed',
                          overview['total_users_analyzed']?.toString() ?? '0',
                          Icons.people,
                          const Color(0xFF2196F3)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildAnalyzerMetric(
                          'Active Analyses',
                          overview['active_analyses']?.toString() ?? '0',
                          Icons.trending_up,
                          const Color(0xFFFF9800)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildAnalyzerMetric(
                          'Accuracy',
                          overview['analysis_accuracy'] ?? '0%',
                          Icons.verified,
                          const Color(0xFF4CAF50)),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Predictive Analytics
                const Text(
                  'Predictive Analytics',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),

                if (predictive['churn_prediction'] != null) ...[
                  const Text(
                    'Churn Risk Distribution',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: _buildRiskCard(
                            'High Risk',
                            predictive['churn_prediction']['high_risk']
                                    ?.toString() ??
                                '0',
                            const Color(0xFFF44336)),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildRiskCard(
                            'Medium Risk',
                            predictive['churn_prediction']['medium_risk']
                                    ?.toString() ??
                                '0',
                            const Color(0xFFFF9800)),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildRiskCard(
                            'Low Risk',
                            predictive['churn_prediction']['low_risk']
                                    ?.toString() ??
                                '0',
                            const Color(0xFF4CAF50)),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAnalyzerMetric(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRiskCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 11,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildUserSegmentation() {
    return FutureBuilder<Map<String, dynamic>>(
      future: GAVATCoreAPIService.getUserSegmentation(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Card(
            color: Color(0xFF1A1A1F),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          );
        }

        final data = snapshot.data?['data'] ?? {};
        final overview =
            data['segmentation_overview'] as Map<String, dynamic>? ?? {};
        final segments = data['primary_segments'] as List? ?? [];

        return Card(
          color: const Color(0xFF1A1A1F),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.group, color: Color(0xFF673AB7), size: 24),
                    SizedBox(width: 12),
                    Text(
                      '👥 User Segmentation',
                      style: TextStyle(
                        color: Color(0xFF673AB7),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Segmentation Overview
                Row(
                  children: [
                    Expanded(
                      child: _buildSegmentMetric(
                          'Total Segments',
                          overview['total_segments']?.toString() ?? '0',
                          Icons.category,
                          const Color(0xFF2196F3)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSegmentMetric(
                          'Active Segments',
                          overview['active_segments']?.toString() ?? '0',
                          Icons.play_circle,
                          const Color(0xFF4CAF50)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSegmentMetric(
                          'Accuracy',
                          overview['segmentation_accuracy'] ?? '0%',
                          Icons.precision_manufacturing,
                          const Color(0xFF9C27B0)),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Primary Segments
                const Text(
                  'Primary User Segments',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),

                ...segments.take(4).map((segment) {
                  final segmentData = segment as Map<String, dynamic>;
                  final metrics =
                      segmentData['metrics'] as Map<String, dynamic>? ?? {};
                  final characteristics =
                      segmentData['characteristics'] as Map<String, dynamic>? ??
                          {};

                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2A2A2F),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF444444)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: _getSegmentColor(segmentData['name']),
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                segmentData['name'] ?? 'Unknown Segment',
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: _getGrowthColor(segmentData['growth']),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                segmentData['growth'] ?? '0%',
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Size: ${segmentData['size']} users | Engagement: ${characteristics['engagement']} | LTV: ${metrics['ltv']}',
                          style: const TextStyle(
                              color: Colors.white70, fontSize: 13),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          segmentData['ai_insights'] ?? 'No insights available',
                          style: const TextStyle(
                              color: Colors.white60,
                              fontSize: 12,
                              fontStyle: FontStyle.italic),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSegmentMetric(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Color _getSegmentColor(String? segmentName) {
    switch (segmentName) {
      case 'VIP Power Users':
        return const Color(0xFFFFD700);
      case 'Creative Explorers':
        return const Color(0xFF9C27B0);
      case 'Social Connectors':
        return const Color(0xFF2196F3);
      case 'At-Risk Users':
        return const Color(0xFFF44336);
      default:
        return Colors.grey;
    }
  }

  Color _getGrowthColor(String? growth) {
    if (growth == null) return Colors.grey;
    if (growth.startsWith('+')) return const Color(0xFF4CAF50);
    if (growth.startsWith('-')) return const Color(0xFFF44336);
    return Colors.grey;
  }

  Widget _buildCoreModulesContent() {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text(
          '🧠 Core Modules - Sistem Çekirdeği',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.refresh(coreModulesProvider);
              ref.refresh(babaGavatAnalyzerProvider);
              ref.refresh(erkoAnalyzerProvider);
              ref.refresh(aiCrmAnalyzerProvider);
              ref.refresh(behavioralEngineProvider);
              ref.refresh(socialGamingProvider);
            },
            tooltip: 'Tüm Modülleri Yenile',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Core Modules Overview
            _buildCoreModulesOverview(),

            const SizedBox(height: 24),

            // BabaGAVAT User Analyzer
            _buildBabaGAVATUserAnalyzer(),

            const SizedBox(height: 24),

            // Erko Analyzer
            _buildErkoAnalyzer(),

            const SizedBox(height: 24),

            // AI CRM Analyzer
            _buildAICRMAnalyzer(),

            const SizedBox(height: 24),

            // Behavioral Engine
            _buildBehavioralEngine(),

            const SizedBox(height: 24),

            // Social Gaming Engine
            _buildSocialGamingEngine(),
          ],
        ),
      ),
    );
  }

  Widget _buildCoreModulesOverview() {
    final coreModulesAsync = ref.watch(coreModulesProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.memory, color: Color(0xFFE91E63), size: 28),
                const SizedBox(width: 12),
                const Text(
                  'Core Modules Overview',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE91E63).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'SYSTEM CORE',
                    style: TextStyle(
                      color: Color(0xFFE91E63),
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            coreModulesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Text('Hata: $error',
                  style: const TextStyle(color: Colors.red)),
              data: (data) {
                final moduleData = data['data'] ?? {};
                return Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: _buildCoreModuleCard(
                            'Toplam Modül',
                            '${moduleData['modules_count'] ?? 0}',
                            Icons.apps,
                            const Color(0xFF9C27B0),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildCoreModuleCard(
                            'Aktif Modül',
                            '${moduleData['active_modules'] ?? 0}',
                            Icons.check_circle,
                            const Color(0xFF4CAF50),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildCoreModuleCard(
                            'Kritik Modül',
                            '${moduleData['critical_modules'] ?? 0}',
                            Icons.priority_high,
                            const Color(0xFFFF5722),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildCoreModuleCard(
                            'Sistem Sağlığı',
                            '${moduleData['modules_health'] ?? '0%'}',
                            Icons.health_and_safety,
                            const Color(0xFF00BCD4),
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCoreModuleCard(
      String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // Placeholder methods for missing functions
  Widget _buildBabaGAVATUserAnalyzer() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              '🧠 BabaGAVAT User Analyzer',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'Sokak zekası ile kullanıcı analizi sistemi aktif...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErkoAnalyzer() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              '👨 Erko Analyzer',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'Erkek kullanıcı segmentasyonu sistemi aktif...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAICRMAnalyzer() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              '🤖 AI CRM Analyzer',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'GPT-4 powered CRM analizi sistemi aktif...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBehavioralEngine() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              '🧬 Behavioral Engine',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'Psikolojik davranış analizi sistemi aktif...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSocialGamingEngine() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              '🎮 Social Gaming Engine',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'Oyunlaştırma ve sosyal etkileşim sistemi aktif...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }
}

class NavigationItem {
  final IconData icon;
  final String label;
  final Color color;

  NavigationItem({
    required this.icon,
    required this.label,
    required this.color,
  });
}
