import 'package:flutter/material.dart';

/// ⚡ Power Mode Selector Widget
/// 
/// Allows changing system performance modes with beautiful UI
class PowerModeSelector extends StatelessWidget {
  final String currentMode;
  final Map<String, dynamic> availableModes;
  final Function(String) onModeChanged;

  const PowerModeSelector({
    Key? key,
    required this.currentMode,
    required this.availableModes,
    required this.onModeChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F3A),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _getModeColor(currentMode).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.bolt,
                  color: _getModeColor(currentMode),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Power Mode',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Current: ${_formatModeName(currentMode)}',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildModeGrid(),
        ],
      ),
    );
  }

  Widget _buildModeGrid() {
    final modes = ['normal', 'performance', 'turbo', 'extreme'];
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 2.5,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemCount: modes.length,
      itemBuilder: (context, index) {
        final mode = modes[index];
        final isSelected = mode == currentMode;
        final modeColor = _getModeColor(mode);
        
        return GestureDetector(
          onTap: () => onModeChanged(mode),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected ? modeColor.withOpacity(0.2) : Colors.grey[800],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected ? modeColor : Colors.transparent,
                width: 2,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  _getModeIcon(mode),
                  color: isSelected ? modeColor : Colors.grey[400],
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _formatModeName(mode),
                        style: TextStyle(
                          color: isSelected ? Colors.white : Colors.grey[400],
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                      Text(
                        _getModeDescription(mode),
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 8,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                if (isSelected)
                  Icon(
                    Icons.check_circle,
                    color: modeColor,
                    size: 16,
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _getModeColor(String mode) {
    switch (mode.toLowerCase()) {
      case 'normal':
        return Colors.green;
      case 'performance':
        return Colors.blue;
      case 'turbo':
        return Colors.orange;
      case 'extreme':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getModeIcon(String mode) {
    switch (mode.toLowerCase()) {
      case 'normal':
        return Icons.eco;
      case 'performance':
        return Icons.speed;
      case 'turbo':
        return Icons.flash_on;
      case 'extreme':
        return Icons.rocket_launch;
      default:
        return Icons.settings;
    }
  }

  String _formatModeName(String mode) {
    return mode[0].toUpperCase() + mode.substring(1);
  }

  String _getModeDescription(String mode) {
    switch (mode.toLowerCase()) {
      case 'normal':
        return 'Balanced power';
      case 'performance':
        return 'Enhanced speed';
      case 'turbo':
        return 'High performance';
      case 'extreme':
        return 'Maximum power';
      default:
        return 'Unknown mode';
    }
  }
}

/// ⚡ Power Mode Status Indicator
class PowerModeIndicator extends StatelessWidget {
  final String currentMode;
  final bool isOnline;

  const PowerModeIndicator({
    Key? key,
    required this.currentMode,
    this.isOnline = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final modeColor = _getModeColor(currentMode);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isOnline ? modeColor.withOpacity(0.2) : Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isOnline ? modeColor : Colors.grey[600]!,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isOnline ? Icons.bolt : Icons.bolt_outlined,
            color: isOnline ? modeColor : Colors.grey[400],
            size: 14,
          ),
          const SizedBox(width: 4),
          Text(
            currentMode.toUpperCase(),
            style: TextStyle(
              color: isOnline ? Colors.white : Colors.grey[400],
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (isOnline) ...[
            const SizedBox(width: 4),
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: modeColor,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getModeColor(String mode) {
    switch (mode.toLowerCase()) {
      case 'normal':
        return Colors.green;
      case 'performance':
        return Colors.blue;
      case 'turbo':
        return Colors.orange;
      case 'extreme':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
} 