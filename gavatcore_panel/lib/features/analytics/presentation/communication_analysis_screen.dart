import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/communication_analysis_provider.dart';
import '../../../core/models/communication_analysis.dart';

/// Screen to display real-time communication analysis
class CommunicationAnalysisScreen extends ConsumerWidget {
  const CommunicationAnalysisScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(communicationAnalysisProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Communication Analysis')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.refresh(communicationAnalysisProvider);
          await Future.delayed(const Duration(seconds: 1));
        },
        child: asyncData.when(
          data: (results) {
            if (results.isEmpty) {
              return const ListView(
                physics: AlwaysScrollableScrollPhysics(),
                children: [Center(child: Text('No analysis data available.'))],
              );
            }
            final avg = results
                .map((r) => r.authenticityScore)
                .fold<double>(0, (a, b) => a + b) /
                results.length;
            return ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: results.length + 1,
              separatorBuilder: (_, __) => const Divider(),
              itemBuilder: (context, i) {
                if (i == 0) {
                  return Center(
                    child: Column(
                      children: [
                        Text('Average Score: ${avg.toStringAsFixed(2)}',
                            style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        SizedBox(
                          width: 100,
                          height: 100,
                          child: CircularProgressIndicator(
                            value: avg,
                            strokeWidth: 8,
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                    ),
                  );
                }
                final r = results[i - 1];
                return ListTile(
                  title: Text(r.interactionType,
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Score: ${r.authenticityScore.toStringAsFixed(2)}'),
                      Text('Level: ${r.authenticityLevel}'),
                      Text('Confidence: ${r.confidenceScore.toStringAsFixed(2)}'),
                      if (r.evidence.isNotEmpty)
                        Text('Evidence: ${r.evidence.join(', ')}'),
                      if (r.recommendations.isNotEmpty)
                        Text('Recommendations: ${r.recommendations.join(', ')}'),
                    ],
                  ),
                  isThreeLine: true,
                  trailing: Text(r.timestamp),
                );
              },
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            children: [Center(child: Text('Error: $e'))],
          ),
        ),
      ),
    );
  }
}
