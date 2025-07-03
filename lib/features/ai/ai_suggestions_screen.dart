import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AISuggestionsScreen extends StatelessWidget {
  const AISuggestionsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                'AI Önerileri',
                style: GoogleFonts.poppins(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Text(
                'GPT destekli mesaj analizi ve öneriler',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 16,
                ),
              ),
              SizedBox(height: 24),
              
              // Message Analysis
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.blue.withOpacity(0.1),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          backgroundColor: Colors.purple.withOpacity(0.2),
                          child: Text('🤖'),
                        ),
                        SizedBox(width: 12),
                        Text(
                          'Son Mesaj Analizi',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16),
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'Merhaba, VIP hizmetleriniz hakkında bilgi alabilir miyim?',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    SizedBox(height: 16),
                    _buildScoreCard(
                      title: 'Empati Skoru',
                      score: 85,
                      color: Colors.green,
                    ),
                    SizedBox(height: 8),
                    _buildScoreCard(
                      title: 'Satış Potansiyeli',
                      score: 92,
                      color: Colors.amber,
                    ),
                    SizedBox(height: 8),
                    _buildScoreCard(
                      title: 'Dil Kalitesi',
                      score: 88,
                      color: Colors.blue,
                    ),
                  ],
                ),
              ),
              SizedBox(height: 24),
              
              // AI Suggestions
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.purple.withOpacity(0.1),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          backgroundColor: Colors.amber.withOpacity(0.2),
                          child: Text('💡'),
                        ),
                        SizedBox(width: 12),
                        Text(
                          'Önerilen Yanıtlar',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16),
                    _buildSuggestionCard(
                      message: 'Tabii ki! Size özel VIP paketlerimiz hakkında detaylı bilgi verebilirim. Hangi konuda daha çok bilgi almak istersiniz? 🌟',
                      score: 95,
                    ),
                    SizedBox(height: 12),
                    _buildSuggestionCard(
                      message: 'Merhaba! VIP üyelerimize sunduğumuz özel avantajları anlatmaktan mutluluk duyarım. Size nasıl yardımcı olabilirim? ✨',
                      score: 92,
                    ),
                    SizedBox(height: 12),
                    _buildSuggestionCard(
                      message: 'Hoş geldiniz! VIP hizmetlerimiz hakkında bilgi almak istemeniz harika. Size özel fırsatlarımızı paylaşabilir miyim? 💎',
                      score: 88,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScoreCard({
    required String title,
    required int score,
    required Color color,
  }) {
    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: TextStyle(
              color: Colors.grey,
              fontSize: 14,
            ),
          ),
        ),
        Container(
          width: 120,
          height: 6,
          decoration: BoxDecoration(
            color: Colors.grey.withOpacity(0.2),
            borderRadius: BorderRadius.circular(3),
          ),
          child: Row(
            children: [
              Container(
                width: 120 * (score / 100),
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
            ],
          ),
        ),
        SizedBox(width: 8),
        Text(
          '$score%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildSuggestionCard({
    required String message,
    required int score,
  }) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.amber.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  'AI Skoru: $score%',
                  style: TextStyle(
                    color: Colors.green,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Spacer(),
              IconButton(
                icon: Icon(
                  Icons.copy,
                  color: Colors.grey,
                  size: 20,
                ),
                onPressed: () {},
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            message,
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
} 