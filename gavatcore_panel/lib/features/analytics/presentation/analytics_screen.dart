// Core Modules bölümünü tamamen yeniden tasarla
Widget _buildCoreModulesSection() {
  return Consumer(
    builder: (context, ref, child) {
      final coreModulesData = ref.watch(coreModulesProvider);
      
      return coreModulesData.when(
        data: (data) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Core Modules - Sistem Çekirdeği',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () => _showSystemDiagnostics(context, ref),
                      icon: Icon(Icons.health_and_safety),
                      label: Text('Sistem Tanılama'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green[700],
                      ),
                    ),
                    SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () => _showPerformanceMetrics(context, ref),
                      icon: Icon(Icons.analytics),
                      label: Text('Performans Metrikleri'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[700],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            SizedBox(height: 16),
            
            // Sistem Durumu Özeti
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.green[700]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green, size: 32),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Sistem Durumu: Mükemmel',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                        Text(
                          '${data['total_modules']} modül aktif • Sistem sağlığı: ${data['system_health']}% • Uptime: 7d 14h 23m',
                          style: TextStyle(color: Colors.grey[300]),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.green[700],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Tümü Aktif',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 20),
            
            // Modül Kartları Grid
            GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: 8, // 8 ana modül
              itemBuilder: (context, index) {
                final modules = [
                  {
                    'id': 'advanced_ai_manager',
                    'name': 'Advanced AI Manager',
                    'description': 'GPT-4 destekli AI görev yönetimi',
                    'icon': Icons.psychology,
                    'color': Colors.purple,
                    'status': 'active',
                    'performance': '98.5%',
                    'tasks': '1,247',
                    'version': '2.1.0'
                  },
                  {
                    'id': 'erko_analyzer',
                    'name': 'Erko Analyzer',
                    'description': 'Erkek kullanıcı davranış analizi',
                    'icon': Icons.person_search,
                    'color': Colors.orange,
                    'status': 'active',
                    'performance': '96.8%',
                    'tasks': '2,156',
                    'version': '3.2.1'
                  },
                  {
                    'id': 'ai_crm_analyzer',
                    'name': 'AI CRM Analyzer',
                    'description': 'GPT-4 Turbo CRM analiz sistemi',
                    'icon': Icons.analytics,
                    'color': Colors.blue,
                    'status': 'active',
                    'performance': '97.3%',
                    'tasks': '456',
                    'version': '4.1.2'
                  },
                  {
                    'id': 'social_gaming_engine',
                    'name': 'Social Gaming Engine',
                    'description': 'Sosyal oyunlaştırma sistemi',
                    'icon': Icons.games,
                    'color': Colors.green,
                    'status': 'active',
                    'performance': '94.2%',
                    'tasks': '67',
                    'version': '2.8.0'
                  },
                  {
                    'id': 'ai_voice_engine',
                    'name': 'AI Voice Engine',
                    'description': 'Sesli etkileşim sistemi',
                    'icon': Icons.record_voice_over,
                    'color': Colors.teal,
                    'status': 'active',
                    'performance': '96.8%',
                    'tasks': '456',
                    'version': '1.9.3'
                  },
                  {
                    'id': 'behavioral_psychological_engine',
                    'name': 'Behavioral Psychology',
                    'description': 'Psikolojik davranış analizi',
                    'icon': Icons.psychology_alt,
                    'color': Colors.indigo,
                    'status': 'active',
                    'performance': '92.7%',
                    'tasks': '234',
                    'version': '3.5.1'
                  },
                  {
                    'id': 'smart_campaign_manager',
                    'name': 'Smart Campaign Manager',
                    'description': 'AI destekli kampanya yönetimi',
                    'icon': Icons.campaign,
                    'color': Colors.red,
                    'status': 'active',
                    'performance': '91.2%',
                    'tasks': '12',
                    'version': '2.3.4'
                  },
                  {
                    'id': 'user_analyzer',
                    'name': 'User Analyzer',
                    'description': 'Kapsamlı kullanıcı analizi',
                    'icon': Icons.person_pin_circle,
                    'color': Colors.cyan,
                    'status': 'active',
                    'performance': '95.1%',
                    'tasks': '3,456',
                    'version': '4.2.1'
                  },
                ];
                
                final module = modules[index];
                
                return Container(
                  decoration: BoxDecoration(
                    color: Colors.grey[900],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey[700]!),
                  ),
                  child: InkWell(
                    onTap: () => _showModuleDetails(context, ref, module['id'] as String),
                    borderRadius: BorderRadius.circular(12),
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: (module['color'] as Color).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  module['icon'] as IconData,
                                  color: module['color'] as Color,
                                  size: 24,
                                ),
                              ),
                              Spacer(),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.green[700],
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  'Aktif',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 12),
                          Text(
                            module['name'] as String,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          SizedBox(height: 4),
                          Text(
                            module['description'] as String,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[400],
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Spacer(),
                          Row(
                            children: [
                              Icon(Icons.speed, color: Colors.green, size: 16),
                              SizedBox(width: 4),
                              Text(
                                module['performance'] as String,
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                              Spacer(),
                              Text(
                                'v${module['version']}',
                                style: TextStyle(
                                  color: Colors.grey[500],
                                  fontSize: 10,
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(Icons.task, color: Colors.blue, size: 16),
                              SizedBox(width: 4),
                              Text(
                                '${module['tasks']} görev',
                                style: TextStyle(
                                  color: Colors.blue,
                                  fontSize: 12,
                                ),
                              ),
                              Spacer(),
                              PopupMenuButton<String>(
                                icon: Icon(Icons.more_vert, color: Colors.grey[400], size: 16),
                                onSelected: (value) => _handleModuleAction(context, ref, module['id'] as String, value),
                                itemBuilder: (context) => [
                                  PopupMenuItem(value: 'details', child: Text('Detaylar')),
                                  PopupMenuItem(value: 'restart', child: Text('Yeniden Başlat')),
                                  PopupMenuItem(value: 'optimize', child: Text('Optimize Et')),
                                  PopupMenuItem(value: 'logs', child: Text('Loglar')),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
        loading: () => Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stack) => Center(
          child: Text(
            'Core Modules yüklenirken hata: $error',
            style: TextStyle(color: Colors.red),
          ),
        ),
      );
    },
  );
}

// Modül detaylarını göster
void _showModuleDetails(BuildContext context, WidgetRef ref, String moduleId) {
  showDialog(
    context: context,
    builder: (context) => Dialog(
      backgroundColor: Colors.grey[900],
      child: Container(
        width: 800,
        height: 600,
        padding: EdgeInsets.all(24),
        child: FutureBuilder(
          future: _fetchModuleDetails(moduleId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator());
            }
            
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Modül detayları yüklenirken hata: ${snapshot.error}',
                  style: TextStyle(color: Colors.red),
                ),
              );
            }
            
            final moduleData = snapshot.data as Map<String, dynamic>;
            
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.settings, color: Colors.blue, size: 32),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            moduleData['name'],
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            moduleData['description'],
                            style: TextStyle(color: Colors.grey[400]),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.green[700],
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        moduleData['status'].toUpperCase(),
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    SizedBox(width: 8),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.close, color: Colors.grey[400]),
                    ),
                  ],
                ),
                SizedBox(height: 24),
                
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Performans Metrikleri
                        _buildDetailSection(
                          'Performans Metrikleri',
                          Icons.speed,
                          Colors.green,
                          moduleData['performance'],
                        ),
                        SizedBox(height: 20),
                        
                        // Özellikler
                        _buildDetailSection(
                          'Özellikler',
                          Icons.star,
                          Colors.blue,
                          {'features': moduleData['features']},
                        ),
                        SizedBox(height: 20),
                        
                        // AI Modelleri (eğer varsa)
                        if (moduleData.containsKey('ai_models'))
                          _buildDetailSection(
                            'AI Modelleri',
                            Icons.psychology,
                            Colors.purple,
                            moduleData['ai_models'],
                          ),
                        
                        // Görev Dağılımı (eğer varsa)
                        if (moduleData.containsKey('task_breakdown'))
                          _buildDetailSection(
                            'Görev Dağılımı',
                            Icons.task,
                            Colors.orange,
                            moduleData['task_breakdown'],
                          ),
                      ],
                    ),
                  ),
                ),
                
                // Aksiyon Butonları
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () => _handleModuleAction(context, ref, moduleId, 'restart'),
                      icon: Icon(Icons.refresh),
                      label: Text('Yeniden Başlat'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.orange[700]),
                    ),
                    SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () => _handleModuleAction(context, ref, moduleId, 'optimize'),
                      icon: Icon(Icons.tune),
                      label: Text('Optimize Et'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.blue[700]),
                    ),
                    SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () => _showModuleLogs(context, moduleId),
                      icon: Icon(Icons.description),
                      label: Text('Logları Görüntüle'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.grey[700]),
                    ),
                  ],
                ),
              ],
            );
          },
        ),
      ),
    ),
  );
}

Widget _buildDetailSection(String title, IconData icon, Color color, dynamic data) {
  return Container(
    padding: EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.grey[850],
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: Colors.grey[700]!),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: color, size: 20),
            SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        SizedBox(height: 12),
        _buildDataContent(data),
      ],
    ),
  );
}

Widget _buildDataContent(dynamic data) {
  if (data is Map<String, dynamic>) {
    return Column(
      children: data.entries.map((entry) {
        if (entry.value is List) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                entry.key,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[300],
                ),
              ),
              SizedBox(height: 4),
              ...((entry.value as List).map((item) => Padding(
                padding: EdgeInsets.only(left: 16, bottom: 2),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green, size: 16),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        item.toString(),
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                    ),
                  ],
                ),
              ))),
              SizedBox(height: 8),
            ],
          );
        } else {
          return Padding(
            padding: EdgeInsets.only(bottom: 4),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    entry.key,
                    style: TextStyle(color: Colors.grey[300]),
                  ),
                ),
                Text(
                  entry.value.toString(),
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          );
        }
      }).toList(),
    );
  }
  
  return Text(
    data.toString(),
    style: TextStyle(color: Colors.grey[400]),
  );
}

// Modül detaylarını API'den çek
Future<Map<String, dynamic>> _fetchModuleDetails(String moduleId) async {
  final response = await http.get(
    Uri.parse('http://127.0.0.1:5050/api/core-modules/detailed/$moduleId'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Modül detayları yüklenemedi');
  }
}

// Modül aksiyonlarını handle et
void _handleModuleAction(BuildContext context, WidgetRef ref, String moduleId, String action) async {
  try {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:5050/api/core-modules/control/$moduleId/$action'),
    );
    
    if (response.statusCode == 200) {
      final result = json.decode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message']),
          backgroundColor: Colors.green,
        ),
      );
      
      // Core modules verilerini yenile
      ref.refresh(coreModulesProvider);
    } else {
      throw Exception('İşlem başarısız');
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Hata: $e'),
        backgroundColor: Colors.red,
      ),
    );
  }
}

// Sistem tanılama göster
void _showSystemDiagnostics(BuildContext context, WidgetRef ref) {
  showDialog(
    context: context,
    builder: (context) => Dialog(
      backgroundColor: Colors.grey[900],
      child: Container(
        width: 900,
        height: 700,
        padding: EdgeInsets.all(24),
        child: FutureBuilder(
          future: _fetchSystemDiagnostics(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator());
            }
            
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Sistem tanılama yüklenirken hata: ${snapshot.error}',
                  style: TextStyle(color: Colors.red),
                ),
              );
            }
            
            final diagnostics = snapshot.data as Map<String, dynamic>;
            
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.health_and_safety, color: Colors.green, size: 32),
                    SizedBox(width: 12),
                    Text(
                      'Sistem Tanılama ve Sağlık Kontrolü',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.close, color: Colors.grey[400]),
                    ),
                  ],
                ),
                SizedBox(height: 24),
                
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // Sistem Durumu
                        _buildDiagnosticCard(
                          'Sistem Durumu',
                          Icons.computer,
                          Colors.blue,
                          diagnostics['system_status'],
                        ),
                        SizedBox(height: 16),
                        
                        // Modül Tanılamaları
                        _buildDiagnosticCard(
                          'Modül Tanılamaları',
                          Icons.extension,
                          Colors.purple,
                          diagnostics['module_diagnostics'],
                        ),
                        SizedBox(height: 16),
                        
                        // Performans Uyarıları
                        _buildDiagnosticCard(
                          'Performans Uyarıları',
                          Icons.warning,
                          Colors.orange,
                          {'alerts': diagnostics['performance_alerts']},
                        ),
                        SizedBox(height: 16),
                        
                        // Optimizasyon Önerileri
                        _buildDiagnosticCard(
                          'Optimizasyon Önerileri',
                          Icons.lightbulb,
                          Colors.yellow[700]!,
                          {'suggestions': diagnostics['optimization_suggestions']},
                        ),
                        SizedBox(height: 16),
                        
                        // Güvenlik Durumu
                        _buildDiagnosticCard(
                          'Güvenlik Durumu',
                          Icons.security,
                          Colors.green,
                          diagnostics['security_status'],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    ),
  );
}

Widget _buildDiagnosticCard(String title, IconData icon, Color color, dynamic data) {
  return Container(
    width: double.infinity,
    padding: EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.grey[850],
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: color.withOpacity(0.3)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            SizedBox(width: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        SizedBox(height: 16),
        _buildDataContent(data),
      ],
    ),
  );
}

// Sistem tanılama verilerini API'den çek
Future<Map<String, dynamic>> _fetchSystemDiagnostics() async {
  final response = await http.get(
    Uri.parse('http://127.0.0.1:5050/api/core-modules/diagnostics'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Sistem tanılama verileri yüklenemedi');
  }
}

// Performans metrikleri göster
void _showPerformanceMetrics(BuildContext context, WidgetRef ref) {
  showDialog(
    context: context,
    builder: (context) => Dialog(
      backgroundColor: Colors.grey[900],
      child: Container(
        width: 1000,
        height: 700,
        padding: EdgeInsets.all(24),
        child: FutureBuilder(
          future: _fetchPerformanceMetrics(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator());
            }
            
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Performans metrikleri yüklenirken hata: ${snapshot.error}',
                  style: TextStyle(color: Colors.red),
                ),
              );
            }
            
            final metrics = snapshot.data as Map<String, dynamic>;
            
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.analytics, color: Colors.blue, size: 32),
                    SizedBox(width: 12),
                    Text(
                      'Performans Metrikleri ve Sistem Analizi',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.close, color: Colors.grey[400]),
                    ),
                  ],
                ),
                SizedBox(height: 24),
                
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // Sistem Sağlığı
                        Row(
                          children: [
                            Expanded(
                              child: _buildMetricCard(
                                'Sistem Sağlığı',
                                '${metrics['system_health']['overall_score']}%',
                                Icons.favorite,
                                Colors.red,
                                'Mükemmel',
                              ),
                            ),
                            SizedBox(width: 16),
                            Expanded(
                              child: _buildMetricCard(
                                'CPU Kullanımı',
                                '${metrics['system_health']['cpu_usage']}%',
                                Icons.memory,
                                Colors.blue,
                                'Normal',
                              ),
                            ),
                            SizedBox(width: 16),
                            Expanded(
                              child: _buildMetricCard(
                                'Bellek Kullanımı',
                                '${metrics['system_health']['memory_usage']}%',
                                Icons.storage,
                                Colors.green,
                                'İyi',
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: 16),
                        
                        // Modül Performansları
                        _buildDiagnosticCard(
                          'Modül Performansları',
                          Icons.extension,
                          Colors.purple,
                          metrics['module_performance'],
                        ),
                        SizedBox(height: 16),
                        
                        // Gerçek Zamanlı Metrikler
                        _buildDiagnosticCard(
                          'Gerçek Zamanlı Metrikler',
                          Icons.speed,
                          Colors.cyan,
                          metrics['real_time_metrics'],
                        ),
                        SizedBox(height: 16),
                        
                        // Trendler
                        _buildDiagnosticCard(
                          'Performans Trendleri',
                          Icons.trending_up,
                          Colors.green,
                          metrics['trends'],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    ),
  );
}

Widget _buildMetricCard(String title, String value, IconData icon, Color color, String status) {
  return Container(
    padding: EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.grey[850],
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: color.withOpacity(0.3)),
    ),
    child: Column(
      children: [
        Icon(icon, color: color, size: 32),
        SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          title,
          style: TextStyle(
            color: Colors.grey[400],
            fontSize: 12,
          ),
        ),
        SizedBox(height: 4),
        Container(
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            status,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    ),
  );
}

// Performans metrikleri verilerini API'den çek
Future<Map<String, dynamic>> _fetchPerformanceMetrics() async {
  final response = await http.get(
    Uri.parse('http://127.0.0.1:5050/api/core-modules/performance-metrics'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Performans metrikleri yüklenemedi');
  }
}

// Modül loglarını göster
void _showModuleLogs(BuildContext context, String moduleId) {
  showDialog(
    context: context,
    builder: (context) => Dialog(
      backgroundColor: Colors.grey[900],
      child: Container(
        width: 1000,
        height: 700,
        padding: EdgeInsets.all(24),
        child: FutureBuilder(
          future: _fetchModuleLogs(moduleId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator());
            }
            
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'Modül logları yüklenirken hata: ${snapshot.error}',
                  style: TextStyle(color: Colors.red),
                ),
              );
            }
            
            final logsData = snapshot.data as Map<String, dynamic>;
            final logs = logsData['logs'] as List;
            
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.description, color: Colors.blue, size: 32),
                    SizedBox(width: 12),
                    Text(
                      '${logsData['module']} - Modül Logları',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.close, color: Colors.grey[400]),
                    ),
                  ],
                ),
                SizedBox(height: 24),
                
                Expanded(
                  child: ListView.builder(
                    itemCount: logs.length,
                    itemBuilder: (context, index) {
                      final log = logs[index];
                      final level = log['level'];
                      Color levelColor = Colors.grey;
                      IconData levelIcon = Icons.info;
                      
                      switch (level) {
                        case 'error':
                          levelColor = Colors.red;
                          levelIcon = Icons.error;
                          break;
                        case 'warning':
                          levelColor = Colors.orange;
                          levelIcon = Icons.warning;
                          break;
                        case 'info':
                          levelColor = Colors.blue;
                          levelIcon = Icons.info;
                          break;
                      }
                      
                      return Container(
                        margin: EdgeInsets.only(bottom: 8),
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey[850],
                          borderRadius: BorderRadius.circular(8),
                          border: Border.left(color: levelColor, width: 4),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(levelIcon, color: levelColor, size: 20),
                            SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        level.toUpperCase(),
                                        style: TextStyle(
                                          color: levelColor,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                      Spacer(),
                                      Text(
                                        log['timestamp'],
                                        style: TextStyle(
                                          color: Colors.grey[500],
                                          fontSize: 10,
                                        ),
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    log['message'],
                                    style: TextStyle(color: Colors.white),
                                  ),
                                  if (log['details'] != null) ...[
                                    SizedBox(height: 8),
                                    Container(
                                      padding: EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: Colors.grey[800],
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'Detaylar:',
                                            style: TextStyle(
                                              color: Colors.grey[300],
                                              fontWeight: FontWeight.bold,
                                              fontSize: 12,
                                            ),
                                          ),
                                          SizedBox(height: 4),
                                          ...log['details'].entries.map<Widget>((entry) =>
                                            Text(
                                              '${entry.key}: ${entry.value}',
                                              style: TextStyle(
                                                color: Colors.grey[400],
                                                fontSize: 11,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        ),
      ),
    ),
  );
}

// Modül loglarını API'den çek
Future<Map<String, dynamic>> _fetchModuleLogs(String moduleId) async {
  final response = await http.get(
    Uri.parse('http://127.0.0.1:5050/api/core-modules/logs/$moduleId?limit=50'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Modül logları yüklenemedi');
  }
} 