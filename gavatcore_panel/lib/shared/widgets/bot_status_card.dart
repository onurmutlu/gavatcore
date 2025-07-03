import 'package:flutter/material.dart';
import '../../core/models/bot_status.dart';

class BotStatusCard extends StatelessWidget {
  final BotStatus bot;
  final VoidCallback? onStart;
  final VoidCallback? onStop;
  final VoidCallback? onRestart;
  final bool isLoading;

  const BotStatusCard({
    Key? key,
    required this.bot,
    this.onStart,
    this.onStop,
    this.onRestart,
    this.isLoading = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: EdgeInsets.all(8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: _getGradientColors(),
          ),
        ),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              SizedBox(height: 12),
              _buildStats(),
              SizedBox(height: 12),
              _buildControls(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Text(
          bot.statusIcon,
          style: TextStyle(fontSize: 24),
        ),
        SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                bot.name,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Text(
                bot.telegramHandle,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ),
        _buildStatusChip(),
      ],
    );
  }

  Widget _buildStatusChip() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor().withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getStatusColor(),
          width: 1,
        ),
      ),
      child: Text(
        _getStatusText(),
        style: TextStyle(
          color: _getStatusColor(),
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildStats() {
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatItem('Uptime', bot.formattedUptime, Icons.access_time),
              _buildStatItem('Mesaj', '${bot.messagesSent}', Icons.message),
            ],
          ),
          if (bot.isRunning) ...[
            SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildStatItem('RAM', '${bot.memoryUsage.toStringAsFixed(1)}MB', Icons.memory),
                _buildStatItem('CPU', '${bot.cpuUsage.toStringAsFixed(1)}%', Icons.speed),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: Colors.white70,
        ),
        SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: Colors.white70,
              ),
            ),
            Text(
              value,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildControls() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildControlButton(
          'Start',
          Icons.play_arrow,
          Colors.green,
          bot.isStopped ? onStart : null,
        ),
        _buildControlButton(
          'Stop',
          Icons.stop,
          Colors.red,
          bot.isRunning ? onStop : null,
        ),
        _buildControlButton(
          'Restart',
          Icons.refresh,
          Colors.orange,
          bot.isRunning ? onRestart : null,
        ),
      ],
    );
  }

  Widget _buildControlButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback? onPressed,
  ) {
    return Expanded(
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 4),
        child: ElevatedButton.icon(
          onPressed: isLoading ? null : onPressed,
          icon: isLoading && onPressed != null
              ? SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: color,
                  ),
                )
              : Icon(icon, size: 16),
          label: Text(
            label,
            style: TextStyle(fontSize: 10),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: onPressed != null ? color : Colors.grey,
            foregroundColor: Colors.white,
            padding: EdgeInsets.symmetric(vertical: 8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
    );
  }

  List<Color> _getGradientColors() {
    switch (bot.status) {
      case 'running':
        return [Colors.green.shade400, Colors.green.shade600];
      case 'error':
        return [Colors.red.shade400, Colors.red.shade600];
      case 'stopped':
      default:
        return [Colors.grey.shade500, Colors.grey.shade700];
    }
  }

  Color _getStatusColor() {
    switch (bot.status) {
      case 'running':
        return Colors.green;
      case 'error':
        return Colors.red;
      case 'stopped':
      default:
        return Colors.orange;
    }
  }

  String _getStatusText() {
    switch (bot.status) {
      case 'running':
        return 'AKTİF';
      case 'error':
        return 'HATA';
      case 'stopped':
      default:
        return 'PASİF';
    }
  }
} 