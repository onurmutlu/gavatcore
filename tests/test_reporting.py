#!/usr/bin/env python3
"""
Comprehensive Behavioral Reporting Test Script
"""

import asyncio
import sys
sys.path.append('.')
from core.behavioral_psychological_engine import AdvancedBehavioralPsychologicalEngine

async def test_reporting():
    engine = AdvancedBehavioralPsychologicalEngine()
    
    # Test kullanıcısı oluştur
    messages = [
        'Başarı için çalışıyorum ve hedeflerime odaklanıyorum',
        'Yaratıcı projeler yapıp yeni şeyler deniyorum',
        'Arkadaşlarımla birlikte sosyal aktivitelerde bulunuyorum',
        'Düzenli ve sistematik çalışmayı seviyorum',
        'Bazen stresli oluyorum ama genelde mutluyum'
    ]
    from datetime import datetime, timedelta
    now = datetime.now()
    timestamps = [now - timedelta(hours=i) for i in range(5)]
    
    # Comprehensive analysis
    profile = await engine.comprehensive_user_analysis(
        user_id=9999, 
        messages=messages, 
        message_timestamps=timestamps
    )
    
    # Comprehensive report oluştur
    report = engine.generate_comprehensive_report(9999)
    
    print('📊 COMPREHENSIVE BEHAVIORAL REPORT')
    print('=' * 50)
    print(f'User ID: {report["user_id"]}')
    print(f'Analysis Version: {report["profile_version"]}')
    print()
    
    # Big Five Personality
    big_five = report['big_five_personality']
    print('🧠 BIG FIVE PERSONALITY TRAITS:')
    for trait, score in big_five['scores'].items():
        print(f'   • {trait.capitalize()}: {score:.2f}')
    print(f'   Dominant Traits: {big_five["dominant_traits"]}')
    print(f'   Summary: {big_five["personality_summary"]}')
    print()
    
    # Behavioral Patterns
    patterns = report['behavioral_patterns']
    print('⏰ TIMING PATTERNS:')
    print(f'   • Peak Hours: {patterns["timing"]["peak_hours"]}')
    print(f'   • Optimal Contact: {patterns["timing"]["optimal_contact_time"]}')
    print()
    
    print('😊 SENTIMENT ANALYSIS:')
    print(f'   • Trend: {patterns["sentiment"]["trend"]}')
    print(f'   • Dominant Emotion: {patterns["sentiment"]["dominant_emotion"]}')
    print(f'   • Emotional Stability: {patterns["sentiment"]["emotional_stability"]:.2f}')
    print()
    
    print('👥 SOCIAL DYNAMICS:')
    print(f'   • Role: {patterns["social"]["role"]}')
    print(f'   • Influence Score: {patterns["social"]["influence_score"]:.2f}')
    print(f'   • Leadership Tendency: {patterns["social"]["leadership_tendency"]:.2f}')
    print()
    
    # Motivation
    motivation = report['motivation_analysis']
    print('🎯 MOTIVATION PROFILE:')
    print(f'   • Primary: {motivation["primary_motivation"]}')
    print(f'   • Drive Level: {motivation["drive_level"]:.2f}')
    print(f'   • Goal Orientation: {motivation["goal_orientation"]}')
    print()
    
    # Predictions
    predictions = report['predictive_insights']
    print('🔮 PREDICTIVE INSIGHTS:')
    print(f'   • Conversion Probability: {predictions["conversion_probability"]:.2f}')
    print(f'   • Churn Risk: {predictions["churn_risk"]:.2f}')
    print(f'   • Engagement Forecast: {predictions["engagement_forecast"]}')
    print(f'   • Next Action: {predictions["next_action_prediction"]}')
    print()
    
    # Recommendations
    print('💡 RECOMMENDATIONS:')
    for i, rec in enumerate(report['recommendations'], 1):
        print(f'   {i}. {rec}')
    print()
    
    print('✅ Comprehensive report generated successfully!')

if __name__ == "__main__":
    asyncio.run(test_reporting()) 