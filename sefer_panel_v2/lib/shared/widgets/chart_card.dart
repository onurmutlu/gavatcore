import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class ChartCard extends StatelessWidget {
  final String title;
  final List<dynamic> data;
  final String dataKey;
  final Color color;
  final bool isDonut;

  const ChartCard({
    super.key,
    required this.title,
    required this.data,
    required this.dataKey,
    required this.color,
    this.isDonut = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: isDonut ? _buildPieChart() : _buildLineChart(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLineChart() {
    if (data.isEmpty) {
      return const Center(child: Text('Veri yok'));
    }

    final spots = List<FlSpot>.generate(
      data.length,
      (i) => FlSpot(i.toDouble(), (data[i][dataKey] as num).toDouble()),
    );

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: false),
        titlesData: FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: color,
            barWidth: 3,
            dotData: FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: color.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPieChart() {
    if (data.isEmpty) {
      return const Center(child: Text('Veri yok'));
    }

    final total = data.fold<double>(
      0,
      (sum, item) => sum + (item.value as num).toDouble(),
    );

    final sections = data.map((item) {
      final value = (item.value as num).toDouble();
      final percent = (value / total * 100).toStringAsFixed(1);
      
      return PieChartSectionData(
        color: color.withOpacity(0.5 + data.indexOf(item) * 0.1),
        value: value,
        title: '$percent%',
        radius: 100,
        titleStyle: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    }).toList();

    return PieChart(
      PieChartData(
        sections: sections,
        centerSpaceRadius: isDonut ? 40 : 0,
        sectionsSpace: 2,
      ),
    );
  }
} 