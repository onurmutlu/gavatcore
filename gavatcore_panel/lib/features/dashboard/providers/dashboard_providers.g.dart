// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dashboard_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$dashboardStatsHash() => r'a420fbba789a39de903b2cd30fd01104893e458f';

/// See also [DashboardStats].
@ProviderFor(DashboardStats)
final dashboardStatsProvider = AutoDisposeAsyncNotifierProvider<DashboardStats,
    DashboardStatsData>.internal(
  DashboardStats.new,
  name: r'dashboardStatsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$dashboardStatsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$DashboardStats = AutoDisposeAsyncNotifier<DashboardStatsData>;
String _$realTimeUpdatesHash() => r'd73e7963b0f761c184d073f17df38e2bbd527abb';

/// See also [RealTimeUpdates].
@ProviderFor(RealTimeUpdates)
final realTimeUpdatesProvider = AutoDisposeStreamNotifierProvider<
    RealTimeUpdates, Map<String, dynamic>>.internal(
  RealTimeUpdates.new,
  name: r'realTimeUpdatesProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$realTimeUpdatesHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$RealTimeUpdates = AutoDisposeStreamNotifier<Map<String, dynamic>>;
String _$systemStatusHash() => r'1aa396a730ed87ae48e9688b593ccb6dee0d4154';

/// See also [SystemStatus].
@ProviderFor(SystemStatus)
final systemStatusProvider =
    AutoDisposeNotifierProvider<SystemStatus, Map<String, dynamic>>.internal(
  SystemStatus.new,
  name: r'systemStatusProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$systemStatusHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$SystemStatus = AutoDisposeNotifier<Map<String, dynamic>>;
String _$quickActionsHash() => r'e2d09c1f48003ac95fa3c527203b39206b5a9dd9';

/// See also [QuickActions].
@ProviderFor(QuickActions)
final quickActionsProvider =
    AutoDisposeNotifierProvider<QuickActions, bool>.internal(
  QuickActions.new,
  name: r'quickActionsProvider',
  debugGetCreateSourceHash:
      const bool.fromEnvironment('dart.vm.product') ? null : _$quickActionsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$QuickActions = AutoDisposeNotifier<bool>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
