import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/communication_analysis.dart';
import '../services/api_service.dart';
import '../models/app_state.dart';
import 'app_providers.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// FutureProvider for fetching communication analysis results
final communicationAnalysisProvider = FutureProvider.autoDispose<
    List<CommunicationAnalysisResult>>((ref) async {
  final resp = await http.post(
    Uri.parse(ApiConfig.communicationAnalysisUrl),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'user_id': ref.read(currentUserIdProvider),
      'character_id': ref.read(currentCharacterIdProvider),
      'transcript': ref.read(currentTranscriptProvider),
    }),
  );
  if (resp.statusCode == 200) {
    final data = json.decode(resp.body) as Map<String, dynamic>;
    final List<dynamic> list = data['analysis'] ?? [];
    return list
        .map((e) => CommunicationAnalysisResult.fromJson(e))
        .toList();
  }
  throw Exception('Failed to load communication analysis');
});

/// Providers that read actual app state for analysis context
/// Use current user ID from app state as user_id
final currentUserIdProvider = Provider<String>((ref) {
  final user = ref.watch(appStateProvider).currentUser;
  return user?.id ?? '';
});

/// Use current user ID also as character_id for now (or map to selected bot/session)
final currentCharacterIdProvider = Provider<String>((ref) {
  final user = ref.watch(appStateProvider).currentUser;
  return user?.id ?? '';
});

/// Use the latest messages as the transcript for analysis
/// Build transcript from recent messages loaded in app
final currentTranscriptProvider = Provider<List<String>>((ref) {
  final messages = ref.watch(messagesProvider).valueOrNull;
  if (messages == null) return [];
  return messages.map((m) => m.content).toList();
});
