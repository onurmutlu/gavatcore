import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/widgets/glass_container.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        title: const Text(
          'GavatCore Dashboard',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: const Color(0xFF1A1A2E),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.purple),
            onPressed: () {
              // Refresh dashboard data
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'System Overview',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),
            _buildStatsGrid(),
            const SizedBox(height: 32),
            const Text(
              'Bot Status',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            _buildBotStatusSection(),
            const SizedBox(height: 32),
            const Text(
              'Recent Activity',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            _buildActivitySection(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: MediaQuery.of(context).size.width > 800 ? 4 : 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      children: [
        _buildStatCard('Active Bots', '3', Icons.smart_toy, Colors.green),
        _buildStatCard('Messages Today', '1,247', Icons.message, Colors.blue),
        _buildStatCard('Total Users', '8,392', Icons.people, Colors.purple),
        _buildStatCard('Uptime', '99.8%', Icons.timer, Colors.orange),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return GlassContainer(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 12),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[400],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBotStatusSection() {
    final bots = [
      {'name': 'Lara', 'status': 'online', 'messages': 456},
      {'name': 'BabaGavat', 'status': 'online', 'messages': 321},
      {'name': 'Geisha', 'status': 'offline', 'messages': 189},
    ];

    return Column(
      children: bots.map((bot) => _buildBotStatusCard(bot)).toList(),
    );
  }

  Widget _buildBotStatusCard(Map<String, dynamic> bot) {
    final isOnline = bot['status'] == 'online';
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: GlassContainer(
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: isOnline ? Colors.green : Colors.grey,
            child: Text(
              bot['name'][0],
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          title: Text(
            bot['name'],
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          subtitle: Text(
            isOnline ? 'Online' : 'Offline',
            style: TextStyle(
              color: isOnline ? Colors.green : Colors.grey,
            ),
          ),
          trailing: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '${bot['messages']}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const Text(
                'messages',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActivitySection() {
    final activities = [
      {'time': '10:30 AM', 'message': 'Lara sent message to user #12345'},
      {'time': '10:28 AM', 'message': 'BabaGavat received new message'},
      {'time': '10:25 AM', 'message': 'System health check completed'},
      {'time': '10:20 AM', 'message': 'Geisha went offline'},
      {'time': '10:15 AM', 'message': 'New user registered: @newuser'},
    ];

    return GlassContainer(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: activities.map((activity) {
            return Container(
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.grey, width: 0.2),
                ),
              ),
              child: Row(
                children: [
                  Text(
                    activity['time']!,
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      activity['message']!,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}