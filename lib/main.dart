import 'package:flutter/material.dart';

void main() {
  runApp(const SeferPanelApp());
}

class SeferPanelApp extends StatelessWidget {
  const SeferPanelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SEFER Panel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.black,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.purpleAccent),
        useMaterial3: true,
      ),
      home: const MockLoginPage(),
    );
  }
}

class MockLoginPage extends StatelessWidget {
  const MockLoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton.icon(
          icon: const Icon(Icons.telegram),
          label: const Text('Demo ile Giriş Yap'),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const DashboardPage()),
            );
          },
        ),
      ),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SEFER Dashboard')),
      body: const Center(
        child: Text('🧠 AI Rating, 💬 Mesaj, 💸 Gelir buraya gelecek!', style: TextStyle(fontSize: 20)),
      ),
    );
  }
} 