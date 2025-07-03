import 'package:flutter/material.dart';
import 'package:glassmorphism/glassmorphism.dart';
import '../theme/app_theme.dart';

class GlassContainer extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final BorderRadius? borderRadius;
  final double blur;
  final double opacity;
  final Color? borderColor;
  final bool isNeonBorder;
  final VoidCallback? onTap;
  final BoxShadow? shadow;

  const GlassContainer({
    super.key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.borderRadius,
    this.blur = 10.0,
    this.opacity = 0.1,
    this.borderColor,
    this.isNeonBorder = false,
    this.onTap,
    this.shadow,
  });

  @override
  Widget build(BuildContext context) {
    final borderRadiusValue = borderRadius ?? BorderRadius.circular(16);
    
    Widget container = GlassmorphicContainer(
      width: width ?? double.infinity,
      height: height,
      borderRadius: borderRadiusValue.topLeft.x,
      blur: blur,
      alignment: Alignment.center,
      border: 1,
      linearGradient: LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Colors.white.withOpacity(opacity),
          Colors.white.withOpacity(opacity * 0.5),
        ],
      ),
      borderGradient: isNeonBorder
          ? LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppTheme.neonColors.purple.withOpacity(0.5),
                AppTheme.neonColors.blue.withOpacity(0.5),
              ],
            )
          : LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                borderColor?.withOpacity(0.3) ?? Colors.white.withOpacity(0.1),
                borderColor?.withOpacity(0.1) ?? Colors.white.withOpacity(0.05),
              ],
            ),
      child: Container(
        padding: padding,
        child: child,
      ),
    );

    if (shadow != null) {
      container = Container(
        decoration: BoxDecoration(
          borderRadius: borderRadiusValue,
          boxShadow: [shadow!],
        ),
        child: container,
      );
    }

    if (margin != null) {
      container = Container(
        margin: margin,
        child: container,
      );
    }

    if (onTap != null) {
      container = InkWell(
        onTap: onTap,
        borderRadius: borderRadiusValue,
        child: container,
      );
    }

    return container;
  }
}

class NeonGlassContainer extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color neonColor;
  final double glowIntensity;
  final VoidCallback? onTap;

  const NeonGlassContainer({
    super.key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.neonColor = const Color(0xFF8B5CF6),
    this.glowIntensity = 0.3,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    const borderRadius = BorderRadius.all(Radius.circular(16));
    
    Widget container = Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        borderRadius: borderRadius,
        border: Border.all(
          color: neonColor.withOpacity(0.5),
          width: 1,
        ),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            neonColor.withOpacity(0.1),
            neonColor.withOpacity(0.05),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: neonColor.withOpacity(glowIntensity),
            blurRadius: 20,
            spreadRadius: 2,
          ),
          BoxShadow(
            color: neonColor.withOpacity(glowIntensity * 0.5),
            blurRadius: 40,
            spreadRadius: 4,
          ),
        ],
      ),
      child: child,
    );

    if (margin != null) {
      container = Container(
        margin: margin,
        child: container,
      );
    }

    if (onTap != null) {
      container = InkWell(
        onTap: onTap,
        borderRadius: borderRadius,
        child: container,
      );
    }

    return container;
  }
}

class AnimatedGlassContainer extends StatefulWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Duration animationDuration;
  final bool isHovered;
  final VoidCallback? onTap;

  const AnimatedGlassContainer({
    super.key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.animationDuration = const Duration(milliseconds: 300),
    this.isHovered = false,
    this.onTap,
  });

  @override
  State<AnimatedGlassContainer> createState() => _AnimatedGlassContainerState();
}

class _AnimatedGlassContainerState extends State<AnimatedGlassContainer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _glowAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));
    
    _glowAnimation = Tween<double>(
      begin: 0.1,
      end: 0.3,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onHoverChanged(bool isHovered) {
    setState(() {
      _isHovered = isHovered;
    });
    
    if (isHovered) {
      _controller.forward();
    } else {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => _onHoverChanged(true),
      onExit: (_) => _onHoverChanged(false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: NeonGlassContainer(
                width: widget.width,
                height: widget.height,
                padding: widget.padding,
                margin: widget.margin,
                glowIntensity: _glowAnimation.value,
                child: widget.child,
              ),
            );
          },
        ),
      ),
    );
  }
} 