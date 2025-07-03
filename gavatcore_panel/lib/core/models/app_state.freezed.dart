// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AppStateData _$AppStateDataFromJson(Map<String, dynamic> json) {
  return _AppStateData.fromJson(json);
}

/// @nodoc
mixin _$AppStateData {
  int get selectedIndex => throw _privateConstructorUsedError;
  bool get isConnected => throw _privateConstructorUsedError;
  String get theme => throw _privateConstructorUsedError;
  Map<String, dynamic> get userPreferences =>
      throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  String? get errorMessage => throw _privateConstructorUsedError;
  UserAccount? get currentUser => throw _privateConstructorUsedError;

  /// Serializes this AppStateData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AppStateDataCopyWith<AppStateData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AppStateDataCopyWith<$Res> {
  factory $AppStateDataCopyWith(
          AppStateData value, $Res Function(AppStateData) then) =
      _$AppStateDataCopyWithImpl<$Res, AppStateData>;
  @useResult
  $Res call(
      {int selectedIndex,
      bool isConnected,
      String theme,
      Map<String, dynamic> userPreferences,
      bool isLoading,
      String? errorMessage,
      UserAccount? currentUser});

  $UserAccountCopyWith<$Res>? get currentUser;
}

/// @nodoc
class _$AppStateDataCopyWithImpl<$Res, $Val extends AppStateData>
    implements $AppStateDataCopyWith<$Res> {
  _$AppStateDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? selectedIndex = null,
    Object? isConnected = null,
    Object? theme = null,
    Object? userPreferences = null,
    Object? isLoading = null,
    Object? errorMessage = freezed,
    Object? currentUser = freezed,
  }) {
    return _then(_value.copyWith(
      selectedIndex: null == selectedIndex
          ? _value.selectedIndex
          : selectedIndex // ignore: cast_nullable_to_non_nullable
              as int,
      isConnected: null == isConnected
          ? _value.isConnected
          : isConnected // ignore: cast_nullable_to_non_nullable
              as bool,
      theme: null == theme
          ? _value.theme
          : theme // ignore: cast_nullable_to_non_nullable
              as String,
      userPreferences: null == userPreferences
          ? _value.userPreferences
          : userPreferences // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      currentUser: freezed == currentUser
          ? _value.currentUser
          : currentUser // ignore: cast_nullable_to_non_nullable
              as UserAccount?,
    ) as $Val);
  }

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $UserAccountCopyWith<$Res>? get currentUser {
    if (_value.currentUser == null) {
      return null;
    }

    return $UserAccountCopyWith<$Res>(_value.currentUser!, (value) {
      return _then(_value.copyWith(currentUser: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$AppStateDataImplCopyWith<$Res>
    implements $AppStateDataCopyWith<$Res> {
  factory _$$AppStateDataImplCopyWith(
          _$AppStateDataImpl value, $Res Function(_$AppStateDataImpl) then) =
      __$$AppStateDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int selectedIndex,
      bool isConnected,
      String theme,
      Map<String, dynamic> userPreferences,
      bool isLoading,
      String? errorMessage,
      UserAccount? currentUser});

  @override
  $UserAccountCopyWith<$Res>? get currentUser;
}

/// @nodoc
class __$$AppStateDataImplCopyWithImpl<$Res>
    extends _$AppStateDataCopyWithImpl<$Res, _$AppStateDataImpl>
    implements _$$AppStateDataImplCopyWith<$Res> {
  __$$AppStateDataImplCopyWithImpl(
      _$AppStateDataImpl _value, $Res Function(_$AppStateDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? selectedIndex = null,
    Object? isConnected = null,
    Object? theme = null,
    Object? userPreferences = null,
    Object? isLoading = null,
    Object? errorMessage = freezed,
    Object? currentUser = freezed,
  }) {
    return _then(_$AppStateDataImpl(
      selectedIndex: null == selectedIndex
          ? _value.selectedIndex
          : selectedIndex // ignore: cast_nullable_to_non_nullable
              as int,
      isConnected: null == isConnected
          ? _value.isConnected
          : isConnected // ignore: cast_nullable_to_non_nullable
              as bool,
      theme: null == theme
          ? _value.theme
          : theme // ignore: cast_nullable_to_non_nullable
              as String,
      userPreferences: null == userPreferences
          ? _value._userPreferences
          : userPreferences // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      currentUser: freezed == currentUser
          ? _value.currentUser
          : currentUser // ignore: cast_nullable_to_non_nullable
              as UserAccount?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AppStateDataImpl implements _AppStateData {
  const _$AppStateDataImpl(
      {this.selectedIndex = 0,
      this.isConnected = false,
      this.theme = 'light',
      final Map<String, dynamic> userPreferences = const {},
      this.isLoading = false,
      this.errorMessage,
      this.currentUser = null})
      : _userPreferences = userPreferences;

  factory _$AppStateDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$AppStateDataImplFromJson(json);

  @override
  @JsonKey()
  final int selectedIndex;
  @override
  @JsonKey()
  final bool isConnected;
  @override
  @JsonKey()
  final String theme;
  final Map<String, dynamic> _userPreferences;
  @override
  @JsonKey()
  Map<String, dynamic> get userPreferences {
    if (_userPreferences is EqualUnmodifiableMapView) return _userPreferences;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_userPreferences);
  }

  @override
  @JsonKey()
  final bool isLoading;
  @override
  final String? errorMessage;
  @override
  @JsonKey()
  final UserAccount? currentUser;

  @override
  String toString() {
    return 'AppStateData(selectedIndex: $selectedIndex, isConnected: $isConnected, theme: $theme, userPreferences: $userPreferences, isLoading: $isLoading, errorMessage: $errorMessage, currentUser: $currentUser)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AppStateDataImpl &&
            (identical(other.selectedIndex, selectedIndex) ||
                other.selectedIndex == selectedIndex) &&
            (identical(other.isConnected, isConnected) ||
                other.isConnected == isConnected) &&
            (identical(other.theme, theme) || other.theme == theme) &&
            const DeepCollectionEquality()
                .equals(other._userPreferences, _userPreferences) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            (identical(other.currentUser, currentUser) ||
                other.currentUser == currentUser));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      selectedIndex,
      isConnected,
      theme,
      const DeepCollectionEquality().hash(_userPreferences),
      isLoading,
      errorMessage,
      currentUser);

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AppStateDataImplCopyWith<_$AppStateDataImpl> get copyWith =>
      __$$AppStateDataImplCopyWithImpl<_$AppStateDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AppStateDataImplToJson(
      this,
    );
  }
}

abstract class _AppStateData implements AppStateData {
  const factory _AppStateData(
      {final int selectedIndex,
      final bool isConnected,
      final String theme,
      final Map<String, dynamic> userPreferences,
      final bool isLoading,
      final String? errorMessage,
      final UserAccount? currentUser}) = _$AppStateDataImpl;

  factory _AppStateData.fromJson(Map<String, dynamic> json) =
      _$AppStateDataImpl.fromJson;

  @override
  int get selectedIndex;
  @override
  bool get isConnected;
  @override
  String get theme;
  @override
  Map<String, dynamic> get userPreferences;
  @override
  bool get isLoading;
  @override
  String? get errorMessage;
  @override
  UserAccount? get currentUser;

  /// Create a copy of AppStateData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AppStateDataImplCopyWith<_$AppStateDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DashboardStats _$DashboardStatsFromJson(Map<String, dynamic> json) {
  return _DashboardStats.fromJson(json);
}

/// @nodoc
mixin _$DashboardStats {
  int get totalMessages => throw _privateConstructorUsedError;
  int get todayMessages => throw _privateConstructorUsedError;
  int get activeBots => throw _privateConstructorUsedError;
  int get totalBots => throw _privateConstructorUsedError;
  int get apiCalls => throw _privateConstructorUsedError;
  double get successRate => throw _privateConstructorUsedError;
  double get systemLoad => throw _privateConstructorUsedError;
  int get scheduledTasks => throw _privateConstructorUsedError;
  int get queuedMessages => throw _privateConstructorUsedError;
  double get costToday => throw _privateConstructorUsedError;
  double get costTotal => throw _privateConstructorUsedError;
  List<ChartData> get messageChart => throw _privateConstructorUsedError;
  List<ChartData> get botActivityChart => throw _privateConstructorUsedError;

  /// Serializes this DashboardStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DashboardStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DashboardStatsCopyWith<DashboardStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DashboardStatsCopyWith<$Res> {
  factory $DashboardStatsCopyWith(
          DashboardStats value, $Res Function(DashboardStats) then) =
      _$DashboardStatsCopyWithImpl<$Res, DashboardStats>;
  @useResult
  $Res call(
      {int totalMessages,
      int todayMessages,
      int activeBots,
      int totalBots,
      int apiCalls,
      double successRate,
      double systemLoad,
      int scheduledTasks,
      int queuedMessages,
      double costToday,
      double costTotal,
      List<ChartData> messageChart,
      List<ChartData> botActivityChart});
}

/// @nodoc
class _$DashboardStatsCopyWithImpl<$Res, $Val extends DashboardStats>
    implements $DashboardStatsCopyWith<$Res> {
  _$DashboardStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DashboardStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMessages = null,
    Object? todayMessages = null,
    Object? activeBots = null,
    Object? totalBots = null,
    Object? apiCalls = null,
    Object? successRate = null,
    Object? systemLoad = null,
    Object? scheduledTasks = null,
    Object? queuedMessages = null,
    Object? costToday = null,
    Object? costTotal = null,
    Object? messageChart = null,
    Object? botActivityChart = null,
  }) {
    return _then(_value.copyWith(
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
      todayMessages: null == todayMessages
          ? _value.todayMessages
          : todayMessages // ignore: cast_nullable_to_non_nullable
              as int,
      activeBots: null == activeBots
          ? _value.activeBots
          : activeBots // ignore: cast_nullable_to_non_nullable
              as int,
      totalBots: null == totalBots
          ? _value.totalBots
          : totalBots // ignore: cast_nullable_to_non_nullable
              as int,
      apiCalls: null == apiCalls
          ? _value.apiCalls
          : apiCalls // ignore: cast_nullable_to_non_nullable
              as int,
      successRate: null == successRate
          ? _value.successRate
          : successRate // ignore: cast_nullable_to_non_nullable
              as double,
      systemLoad: null == systemLoad
          ? _value.systemLoad
          : systemLoad // ignore: cast_nullable_to_non_nullable
              as double,
      scheduledTasks: null == scheduledTasks
          ? _value.scheduledTasks
          : scheduledTasks // ignore: cast_nullable_to_non_nullable
              as int,
      queuedMessages: null == queuedMessages
          ? _value.queuedMessages
          : queuedMessages // ignore: cast_nullable_to_non_nullable
              as int,
      costToday: null == costToday
          ? _value.costToday
          : costToday // ignore: cast_nullable_to_non_nullable
              as double,
      costTotal: null == costTotal
          ? _value.costTotal
          : costTotal // ignore: cast_nullable_to_non_nullable
              as double,
      messageChart: null == messageChart
          ? _value.messageChart
          : messageChart // ignore: cast_nullable_to_non_nullable
              as List<ChartData>,
      botActivityChart: null == botActivityChart
          ? _value.botActivityChart
          : botActivityChart // ignore: cast_nullable_to_non_nullable
              as List<ChartData>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DashboardStatsImplCopyWith<$Res>
    implements $DashboardStatsCopyWith<$Res> {
  factory _$$DashboardStatsImplCopyWith(_$DashboardStatsImpl value,
          $Res Function(_$DashboardStatsImpl) then) =
      __$$DashboardStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int totalMessages,
      int todayMessages,
      int activeBots,
      int totalBots,
      int apiCalls,
      double successRate,
      double systemLoad,
      int scheduledTasks,
      int queuedMessages,
      double costToday,
      double costTotal,
      List<ChartData> messageChart,
      List<ChartData> botActivityChart});
}

/// @nodoc
class __$$DashboardStatsImplCopyWithImpl<$Res>
    extends _$DashboardStatsCopyWithImpl<$Res, _$DashboardStatsImpl>
    implements _$$DashboardStatsImplCopyWith<$Res> {
  __$$DashboardStatsImplCopyWithImpl(
      _$DashboardStatsImpl _value, $Res Function(_$DashboardStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of DashboardStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMessages = null,
    Object? todayMessages = null,
    Object? activeBots = null,
    Object? totalBots = null,
    Object? apiCalls = null,
    Object? successRate = null,
    Object? systemLoad = null,
    Object? scheduledTasks = null,
    Object? queuedMessages = null,
    Object? costToday = null,
    Object? costTotal = null,
    Object? messageChart = null,
    Object? botActivityChart = null,
  }) {
    return _then(_$DashboardStatsImpl(
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
      todayMessages: null == todayMessages
          ? _value.todayMessages
          : todayMessages // ignore: cast_nullable_to_non_nullable
              as int,
      activeBots: null == activeBots
          ? _value.activeBots
          : activeBots // ignore: cast_nullable_to_non_nullable
              as int,
      totalBots: null == totalBots
          ? _value.totalBots
          : totalBots // ignore: cast_nullable_to_non_nullable
              as int,
      apiCalls: null == apiCalls
          ? _value.apiCalls
          : apiCalls // ignore: cast_nullable_to_non_nullable
              as int,
      successRate: null == successRate
          ? _value.successRate
          : successRate // ignore: cast_nullable_to_non_nullable
              as double,
      systemLoad: null == systemLoad
          ? _value.systemLoad
          : systemLoad // ignore: cast_nullable_to_non_nullable
              as double,
      scheduledTasks: null == scheduledTasks
          ? _value.scheduledTasks
          : scheduledTasks // ignore: cast_nullable_to_non_nullable
              as int,
      queuedMessages: null == queuedMessages
          ? _value.queuedMessages
          : queuedMessages // ignore: cast_nullable_to_non_nullable
              as int,
      costToday: null == costToday
          ? _value.costToday
          : costToday // ignore: cast_nullable_to_non_nullable
              as double,
      costTotal: null == costTotal
          ? _value.costTotal
          : costTotal // ignore: cast_nullable_to_non_nullable
              as double,
      messageChart: null == messageChart
          ? _value._messageChart
          : messageChart // ignore: cast_nullable_to_non_nullable
              as List<ChartData>,
      botActivityChart: null == botActivityChart
          ? _value._botActivityChart
          : botActivityChart // ignore: cast_nullable_to_non_nullable
              as List<ChartData>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DashboardStatsImpl implements _DashboardStats {
  const _$DashboardStatsImpl(
      {this.totalMessages = 0,
      this.todayMessages = 0,
      this.activeBots = 0,
      this.totalBots = 0,
      this.apiCalls = 0,
      this.successRate = 0.0,
      this.systemLoad = 0.0,
      this.scheduledTasks = 0,
      this.queuedMessages = 0,
      this.costToday = 0.0,
      this.costTotal = 0.0,
      final List<ChartData> messageChart = const [],
      final List<ChartData> botActivityChart = const []})
      : _messageChart = messageChart,
        _botActivityChart = botActivityChart;

  factory _$DashboardStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$DashboardStatsImplFromJson(json);

  @override
  @JsonKey()
  final int totalMessages;
  @override
  @JsonKey()
  final int todayMessages;
  @override
  @JsonKey()
  final int activeBots;
  @override
  @JsonKey()
  final int totalBots;
  @override
  @JsonKey()
  final int apiCalls;
  @override
  @JsonKey()
  final double successRate;
  @override
  @JsonKey()
  final double systemLoad;
  @override
  @JsonKey()
  final int scheduledTasks;
  @override
  @JsonKey()
  final int queuedMessages;
  @override
  @JsonKey()
  final double costToday;
  @override
  @JsonKey()
  final double costTotal;
  final List<ChartData> _messageChart;
  @override
  @JsonKey()
  List<ChartData> get messageChart {
    if (_messageChart is EqualUnmodifiableListView) return _messageChart;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_messageChart);
  }

  final List<ChartData> _botActivityChart;
  @override
  @JsonKey()
  List<ChartData> get botActivityChart {
    if (_botActivityChart is EqualUnmodifiableListView)
      return _botActivityChart;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_botActivityChart);
  }

  @override
  String toString() {
    return 'DashboardStats(totalMessages: $totalMessages, todayMessages: $todayMessages, activeBots: $activeBots, totalBots: $totalBots, apiCalls: $apiCalls, successRate: $successRate, systemLoad: $systemLoad, scheduledTasks: $scheduledTasks, queuedMessages: $queuedMessages, costToday: $costToday, costTotal: $costTotal, messageChart: $messageChart, botActivityChart: $botActivityChart)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DashboardStatsImpl &&
            (identical(other.totalMessages, totalMessages) ||
                other.totalMessages == totalMessages) &&
            (identical(other.todayMessages, todayMessages) ||
                other.todayMessages == todayMessages) &&
            (identical(other.activeBots, activeBots) ||
                other.activeBots == activeBots) &&
            (identical(other.totalBots, totalBots) ||
                other.totalBots == totalBots) &&
            (identical(other.apiCalls, apiCalls) ||
                other.apiCalls == apiCalls) &&
            (identical(other.successRate, successRate) ||
                other.successRate == successRate) &&
            (identical(other.systemLoad, systemLoad) ||
                other.systemLoad == systemLoad) &&
            (identical(other.scheduledTasks, scheduledTasks) ||
                other.scheduledTasks == scheduledTasks) &&
            (identical(other.queuedMessages, queuedMessages) ||
                other.queuedMessages == queuedMessages) &&
            (identical(other.costToday, costToday) ||
                other.costToday == costToday) &&
            (identical(other.costTotal, costTotal) ||
                other.costTotal == costTotal) &&
            const DeepCollectionEquality()
                .equals(other._messageChart, _messageChart) &&
            const DeepCollectionEquality()
                .equals(other._botActivityChart, _botActivityChart));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalMessages,
      todayMessages,
      activeBots,
      totalBots,
      apiCalls,
      successRate,
      systemLoad,
      scheduledTasks,
      queuedMessages,
      costToday,
      costTotal,
      const DeepCollectionEquality().hash(_messageChart),
      const DeepCollectionEquality().hash(_botActivityChart));

  /// Create a copy of DashboardStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DashboardStatsImplCopyWith<_$DashboardStatsImpl> get copyWith =>
      __$$DashboardStatsImplCopyWithImpl<_$DashboardStatsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DashboardStatsImplToJson(
      this,
    );
  }
}

abstract class _DashboardStats implements DashboardStats {
  const factory _DashboardStats(
      {final int totalMessages,
      final int todayMessages,
      final int activeBots,
      final int totalBots,
      final int apiCalls,
      final double successRate,
      final double systemLoad,
      final int scheduledTasks,
      final int queuedMessages,
      final double costToday,
      final double costTotal,
      final List<ChartData> messageChart,
      final List<ChartData> botActivityChart}) = _$DashboardStatsImpl;

  factory _DashboardStats.fromJson(Map<String, dynamic> json) =
      _$DashboardStatsImpl.fromJson;

  @override
  int get totalMessages;
  @override
  int get todayMessages;
  @override
  int get activeBots;
  @override
  int get totalBots;
  @override
  int get apiCalls;
  @override
  double get successRate;
  @override
  double get systemLoad;
  @override
  int get scheduledTasks;
  @override
  int get queuedMessages;
  @override
  double get costToday;
  @override
  double get costTotal;
  @override
  List<ChartData> get messageChart;
  @override
  List<ChartData> get botActivityChart;

  /// Create a copy of DashboardStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DashboardStatsImplCopyWith<_$DashboardStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChartData _$ChartDataFromJson(Map<String, dynamic> json) {
  return _ChartData.fromJson(json);
}

/// @nodoc
mixin _$ChartData {
  String get label => throw _privateConstructorUsedError;
  double get value => throw _privateConstructorUsedError;
  String? get color => throw _privateConstructorUsedError;
  DateTime? get timestamp => throw _privateConstructorUsedError;

  /// Serializes this ChartData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChartData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChartDataCopyWith<ChartData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChartDataCopyWith<$Res> {
  factory $ChartDataCopyWith(ChartData value, $Res Function(ChartData) then) =
      _$ChartDataCopyWithImpl<$Res, ChartData>;
  @useResult
  $Res call({String label, double value, String? color, DateTime? timestamp});
}

/// @nodoc
class _$ChartDataCopyWithImpl<$Res, $Val extends ChartData>
    implements $ChartDataCopyWith<$Res> {
  _$ChartDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChartData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? value = null,
    Object? color = freezed,
    Object? timestamp = freezed,
  }) {
    return _then(_value.copyWith(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      color: freezed == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: freezed == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChartDataImplCopyWith<$Res>
    implements $ChartDataCopyWith<$Res> {
  factory _$$ChartDataImplCopyWith(
          _$ChartDataImpl value, $Res Function(_$ChartDataImpl) then) =
      __$$ChartDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String label, double value, String? color, DateTime? timestamp});
}

/// @nodoc
class __$$ChartDataImplCopyWithImpl<$Res>
    extends _$ChartDataCopyWithImpl<$Res, _$ChartDataImpl>
    implements _$$ChartDataImplCopyWith<$Res> {
  __$$ChartDataImplCopyWithImpl(
      _$ChartDataImpl _value, $Res Function(_$ChartDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChartData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? value = null,
    Object? color = freezed,
    Object? timestamp = freezed,
  }) {
    return _then(_$ChartDataImpl(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      color: freezed == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: freezed == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChartDataImpl implements _ChartData {
  const _$ChartDataImpl(
      {required this.label, required this.value, this.color, this.timestamp});

  factory _$ChartDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChartDataImplFromJson(json);

  @override
  final String label;
  @override
  final double value;
  @override
  final String? color;
  @override
  final DateTime? timestamp;

  @override
  String toString() {
    return 'ChartData(label: $label, value: $value, color: $color, timestamp: $timestamp)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChartDataImpl &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.value, value) || other.value == value) &&
            (identical(other.color, color) || other.color == color) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, label, value, color, timestamp);

  /// Create a copy of ChartData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChartDataImplCopyWith<_$ChartDataImpl> get copyWith =>
      __$$ChartDataImplCopyWithImpl<_$ChartDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChartDataImplToJson(
      this,
    );
  }
}

abstract class _ChartData implements ChartData {
  const factory _ChartData(
      {required final String label,
      required final double value,
      final String? color,
      final DateTime? timestamp}) = _$ChartDataImpl;

  factory _ChartData.fromJson(Map<String, dynamic> json) =
      _$ChartDataImpl.fromJson;

  @override
  String get label;
  @override
  double get value;
  @override
  String? get color;
  @override
  DateTime? get timestamp;

  /// Create a copy of ChartData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChartDataImplCopyWith<_$ChartDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

MessageData _$MessageDataFromJson(Map<String, dynamic> json) {
  return _MessageData.fromJson(json);
}

/// @nodoc
mixin _$MessageData {
  String get id => throw _privateConstructorUsedError;
  String get content => throw _privateConstructorUsedError;
  String get originalContent => throw _privateConstructorUsedError;
  String? get enhancedContent => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  String get botId => throw _privateConstructorUsedError;
  String get enhancementType => throw _privateConstructorUsedError;
  bool get isScheduled => throw _privateConstructorUsedError;
  DateTime? get scheduledAt => throw _privateConstructorUsedError;
  DateTime? get sentAt => throw _privateConstructorUsedError;
  String? get targetUserId => throw _privateConstructorUsedError;
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;
  DateTime? get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this MessageData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MessageData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MessageDataCopyWith<MessageData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MessageDataCopyWith<$Res> {
  factory $MessageDataCopyWith(
          MessageData value, $Res Function(MessageData) then) =
      _$MessageDataCopyWithImpl<$Res, MessageData>;
  @useResult
  $Res call(
      {String id,
      String content,
      String originalContent,
      String? enhancedContent,
      String status,
      String botId,
      String enhancementType,
      bool isScheduled,
      DateTime? scheduledAt,
      DateTime? sentAt,
      String? targetUserId,
      Map<String, dynamic> metadata,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class _$MessageDataCopyWithImpl<$Res, $Val extends MessageData>
    implements $MessageDataCopyWith<$Res> {
  _$MessageDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MessageData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? originalContent = null,
    Object? enhancedContent = freezed,
    Object? status = null,
    Object? botId = null,
    Object? enhancementType = null,
    Object? isScheduled = null,
    Object? scheduledAt = freezed,
    Object? sentAt = freezed,
    Object? targetUserId = freezed,
    Object? metadata = null,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      originalContent: null == originalContent
          ? _value.originalContent
          : originalContent // ignore: cast_nullable_to_non_nullable
              as String,
      enhancedContent: freezed == enhancedContent
          ? _value.enhancedContent
          : enhancedContent // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      botId: null == botId
          ? _value.botId
          : botId // ignore: cast_nullable_to_non_nullable
              as String,
      enhancementType: null == enhancementType
          ? _value.enhancementType
          : enhancementType // ignore: cast_nullable_to_non_nullable
              as String,
      isScheduled: null == isScheduled
          ? _value.isScheduled
          : isScheduled // ignore: cast_nullable_to_non_nullable
              as bool,
      scheduledAt: freezed == scheduledAt
          ? _value.scheduledAt
          : scheduledAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      sentAt: freezed == sentAt
          ? _value.sentAt
          : sentAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      targetUserId: freezed == targetUserId
          ? _value.targetUserId
          : targetUserId // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MessageDataImplCopyWith<$Res>
    implements $MessageDataCopyWith<$Res> {
  factory _$$MessageDataImplCopyWith(
          _$MessageDataImpl value, $Res Function(_$MessageDataImpl) then) =
      __$$MessageDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String content,
      String originalContent,
      String? enhancedContent,
      String status,
      String botId,
      String enhancementType,
      bool isScheduled,
      DateTime? scheduledAt,
      DateTime? sentAt,
      String? targetUserId,
      Map<String, dynamic> metadata,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class __$$MessageDataImplCopyWithImpl<$Res>
    extends _$MessageDataCopyWithImpl<$Res, _$MessageDataImpl>
    implements _$$MessageDataImplCopyWith<$Res> {
  __$$MessageDataImplCopyWithImpl(
      _$MessageDataImpl _value, $Res Function(_$MessageDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of MessageData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? content = null,
    Object? originalContent = null,
    Object? enhancedContent = freezed,
    Object? status = null,
    Object? botId = null,
    Object? enhancementType = null,
    Object? isScheduled = null,
    Object? scheduledAt = freezed,
    Object? sentAt = freezed,
    Object? targetUserId = freezed,
    Object? metadata = null,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_$MessageDataImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      originalContent: null == originalContent
          ? _value.originalContent
          : originalContent // ignore: cast_nullable_to_non_nullable
              as String,
      enhancedContent: freezed == enhancedContent
          ? _value.enhancedContent
          : enhancedContent // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      botId: null == botId
          ? _value.botId
          : botId // ignore: cast_nullable_to_non_nullable
              as String,
      enhancementType: null == enhancementType
          ? _value.enhancementType
          : enhancementType // ignore: cast_nullable_to_non_nullable
              as String,
      isScheduled: null == isScheduled
          ? _value.isScheduled
          : isScheduled // ignore: cast_nullable_to_non_nullable
              as bool,
      scheduledAt: freezed == scheduledAt
          ? _value.scheduledAt
          : scheduledAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      sentAt: freezed == sentAt
          ? _value.sentAt
          : sentAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      targetUserId: freezed == targetUserId
          ? _value.targetUserId
          : targetUserId // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MessageDataImpl implements _MessageData {
  const _$MessageDataImpl(
      {required this.id,
      required this.content,
      required this.originalContent,
      this.enhancedContent,
      this.status = 'pending',
      this.botId = 'babagavat',
      this.enhancementType = 'friendly',
      this.isScheduled = false,
      this.scheduledAt,
      this.sentAt,
      this.targetUserId = null,
      final Map<String, dynamic> metadata = const {},
      this.createdAt,
      this.updatedAt})
      : _metadata = metadata;

  factory _$MessageDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$MessageDataImplFromJson(json);

  @override
  final String id;
  @override
  final String content;
  @override
  final String originalContent;
  @override
  final String? enhancedContent;
  @override
  @JsonKey()
  final String status;
  @override
  @JsonKey()
  final String botId;
  @override
  @JsonKey()
  final String enhancementType;
  @override
  @JsonKey()
  final bool isScheduled;
  @override
  final DateTime? scheduledAt;
  @override
  final DateTime? sentAt;
  @override
  @JsonKey()
  final String? targetUserId;
  final Map<String, dynamic> _metadata;
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  @override
  final DateTime? createdAt;
  @override
  final DateTime? updatedAt;

  @override
  String toString() {
    return 'MessageData(id: $id, content: $content, originalContent: $originalContent, enhancedContent: $enhancedContent, status: $status, botId: $botId, enhancementType: $enhancementType, isScheduled: $isScheduled, scheduledAt: $scheduledAt, sentAt: $sentAt, targetUserId: $targetUserId, metadata: $metadata, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MessageDataImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.originalContent, originalContent) ||
                other.originalContent == originalContent) &&
            (identical(other.enhancedContent, enhancedContent) ||
                other.enhancedContent == enhancedContent) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.botId, botId) || other.botId == botId) &&
            (identical(other.enhancementType, enhancementType) ||
                other.enhancementType == enhancementType) &&
            (identical(other.isScheduled, isScheduled) ||
                other.isScheduled == isScheduled) &&
            (identical(other.scheduledAt, scheduledAt) ||
                other.scheduledAt == scheduledAt) &&
            (identical(other.sentAt, sentAt) || other.sentAt == sentAt) &&
            (identical(other.targetUserId, targetUserId) ||
                other.targetUserId == targetUserId) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      content,
      originalContent,
      enhancedContent,
      status,
      botId,
      enhancementType,
      isScheduled,
      scheduledAt,
      sentAt,
      targetUserId,
      const DeepCollectionEquality().hash(_metadata),
      createdAt,
      updatedAt);

  /// Create a copy of MessageData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MessageDataImplCopyWith<_$MessageDataImpl> get copyWith =>
      __$$MessageDataImplCopyWithImpl<_$MessageDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MessageDataImplToJson(
      this,
    );
  }
}

abstract class _MessageData implements MessageData {
  const factory _MessageData(
      {required final String id,
      required final String content,
      required final String originalContent,
      final String? enhancedContent,
      final String status,
      final String botId,
      final String enhancementType,
      final bool isScheduled,
      final DateTime? scheduledAt,
      final DateTime? sentAt,
      final String? targetUserId,
      final Map<String, dynamic> metadata,
      final DateTime? createdAt,
      final DateTime? updatedAt}) = _$MessageDataImpl;

  factory _MessageData.fromJson(Map<String, dynamic> json) =
      _$MessageDataImpl.fromJson;

  @override
  String get id;
  @override
  String get content;
  @override
  String get originalContent;
  @override
  String? get enhancedContent;
  @override
  String get status;
  @override
  String get botId;
  @override
  String get enhancementType;
  @override
  bool get isScheduled;
  @override
  DateTime? get scheduledAt;
  @override
  DateTime? get sentAt;
  @override
  String? get targetUserId;
  @override
  Map<String, dynamic> get metadata;
  @override
  DateTime? get createdAt;
  @override
  DateTime? get updatedAt;

  /// Create a copy of MessageData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MessageDataImplCopyWith<_$MessageDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SchedulerConfig _$SchedulerConfigFromJson(Map<String, dynamic> json) {
  return _SchedulerConfig.fromJson(json);
}

/// @nodoc
mixin _$SchedulerConfig {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get cronExpression => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;
  String get actionType => throw _privateConstructorUsedError;
  Map<String, dynamic> get actionParams => throw _privateConstructorUsedError;
  DateTime? get nextRun => throw _privateConstructorUsedError;
  DateTime? get lastRun => throw _privateConstructorUsedError;
  int get executionCount => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;

  /// Serializes this SchedulerConfig to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SchedulerConfig
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SchedulerConfigCopyWith<SchedulerConfig> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SchedulerConfigCopyWith<$Res> {
  factory $SchedulerConfigCopyWith(
          SchedulerConfig value, $Res Function(SchedulerConfig) then) =
      _$SchedulerConfigCopyWithImpl<$Res, SchedulerConfig>;
  @useResult
  $Res call(
      {String id,
      String name,
      String cronExpression,
      bool isActive,
      String actionType,
      Map<String, dynamic> actionParams,
      DateTime? nextRun,
      DateTime? lastRun,
      int executionCount,
      DateTime? createdAt});
}

/// @nodoc
class _$SchedulerConfigCopyWithImpl<$Res, $Val extends SchedulerConfig>
    implements $SchedulerConfigCopyWith<$Res> {
  _$SchedulerConfigCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SchedulerConfig
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? cronExpression = null,
    Object? isActive = null,
    Object? actionType = null,
    Object? actionParams = null,
    Object? nextRun = freezed,
    Object? lastRun = freezed,
    Object? executionCount = null,
    Object? createdAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      cronExpression: null == cronExpression
          ? _value.cronExpression
          : cronExpression // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      actionType: null == actionType
          ? _value.actionType
          : actionType // ignore: cast_nullable_to_non_nullable
              as String,
      actionParams: null == actionParams
          ? _value.actionParams
          : actionParams // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      nextRun: freezed == nextRun
          ? _value.nextRun
          : nextRun // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastRun: freezed == lastRun
          ? _value.lastRun
          : lastRun // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      executionCount: null == executionCount
          ? _value.executionCount
          : executionCount // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SchedulerConfigImplCopyWith<$Res>
    implements $SchedulerConfigCopyWith<$Res> {
  factory _$$SchedulerConfigImplCopyWith(_$SchedulerConfigImpl value,
          $Res Function(_$SchedulerConfigImpl) then) =
      __$$SchedulerConfigImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String cronExpression,
      bool isActive,
      String actionType,
      Map<String, dynamic> actionParams,
      DateTime? nextRun,
      DateTime? lastRun,
      int executionCount,
      DateTime? createdAt});
}

/// @nodoc
class __$$SchedulerConfigImplCopyWithImpl<$Res>
    extends _$SchedulerConfigCopyWithImpl<$Res, _$SchedulerConfigImpl>
    implements _$$SchedulerConfigImplCopyWith<$Res> {
  __$$SchedulerConfigImplCopyWithImpl(
      _$SchedulerConfigImpl _value, $Res Function(_$SchedulerConfigImpl) _then)
      : super(_value, _then);

  /// Create a copy of SchedulerConfig
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? cronExpression = null,
    Object? isActive = null,
    Object? actionType = null,
    Object? actionParams = null,
    Object? nextRun = freezed,
    Object? lastRun = freezed,
    Object? executionCount = null,
    Object? createdAt = freezed,
  }) {
    return _then(_$SchedulerConfigImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      cronExpression: null == cronExpression
          ? _value.cronExpression
          : cronExpression // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      actionType: null == actionType
          ? _value.actionType
          : actionType // ignore: cast_nullable_to_non_nullable
              as String,
      actionParams: null == actionParams
          ? _value._actionParams
          : actionParams // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      nextRun: freezed == nextRun
          ? _value.nextRun
          : nextRun // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastRun: freezed == lastRun
          ? _value.lastRun
          : lastRun // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      executionCount: null == executionCount
          ? _value.executionCount
          : executionCount // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SchedulerConfigImpl implements _SchedulerConfig {
  const _$SchedulerConfigImpl(
      {required this.id,
      required this.name,
      required this.cronExpression,
      this.isActive = true,
      this.actionType = 'message',
      final Map<String, dynamic> actionParams = const {},
      this.nextRun,
      this.lastRun,
      this.executionCount = 0,
      this.createdAt})
      : _actionParams = actionParams;

  factory _$SchedulerConfigImpl.fromJson(Map<String, dynamic> json) =>
      _$$SchedulerConfigImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String cronExpression;
  @override
  @JsonKey()
  final bool isActive;
  @override
  @JsonKey()
  final String actionType;
  final Map<String, dynamic> _actionParams;
  @override
  @JsonKey()
  Map<String, dynamic> get actionParams {
    if (_actionParams is EqualUnmodifiableMapView) return _actionParams;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_actionParams);
  }

  @override
  final DateTime? nextRun;
  @override
  final DateTime? lastRun;
  @override
  @JsonKey()
  final int executionCount;
  @override
  final DateTime? createdAt;

  @override
  String toString() {
    return 'SchedulerConfig(id: $id, name: $name, cronExpression: $cronExpression, isActive: $isActive, actionType: $actionType, actionParams: $actionParams, nextRun: $nextRun, lastRun: $lastRun, executionCount: $executionCount, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SchedulerConfigImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.cronExpression, cronExpression) ||
                other.cronExpression == cronExpression) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.actionType, actionType) ||
                other.actionType == actionType) &&
            const DeepCollectionEquality()
                .equals(other._actionParams, _actionParams) &&
            (identical(other.nextRun, nextRun) || other.nextRun == nextRun) &&
            (identical(other.lastRun, lastRun) || other.lastRun == lastRun) &&
            (identical(other.executionCount, executionCount) ||
                other.executionCount == executionCount) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      cronExpression,
      isActive,
      actionType,
      const DeepCollectionEquality().hash(_actionParams),
      nextRun,
      lastRun,
      executionCount,
      createdAt);

  /// Create a copy of SchedulerConfig
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SchedulerConfigImplCopyWith<_$SchedulerConfigImpl> get copyWith =>
      __$$SchedulerConfigImplCopyWithImpl<_$SchedulerConfigImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SchedulerConfigImplToJson(
      this,
    );
  }
}

abstract class _SchedulerConfig implements SchedulerConfig {
  const factory _SchedulerConfig(
      {required final String id,
      required final String name,
      required final String cronExpression,
      final bool isActive,
      final String actionType,
      final Map<String, dynamic> actionParams,
      final DateTime? nextRun,
      final DateTime? lastRun,
      final int executionCount,
      final DateTime? createdAt}) = _$SchedulerConfigImpl;

  factory _SchedulerConfig.fromJson(Map<String, dynamic> json) =
      _$SchedulerConfigImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get cronExpression;
  @override
  bool get isActive;
  @override
  String get actionType;
  @override
  Map<String, dynamic> get actionParams;
  @override
  DateTime? get nextRun;
  @override
  DateTime? get lastRun;
  @override
  int get executionCount;
  @override
  DateTime? get createdAt;

  /// Create a copy of SchedulerConfig
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SchedulerConfigImplCopyWith<_$SchedulerConfigImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIPromptData _$AIPromptDataFromJson(Map<String, dynamic> json) {
  return _AIPromptData.fromJson(json);
}

/// @nodoc
mixin _$AIPromptData {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get prompt => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;
  double get temperature => throw _privateConstructorUsedError;
  int get maxTokens => throw _privateConstructorUsedError;
  String get model => throw _privateConstructorUsedError;
  int get usageCount => throw _privateConstructorUsedError;
  double get avgResponseTime => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;
  DateTime? get lastUsed => throw _privateConstructorUsedError;

  /// Serializes this AIPromptData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIPromptData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIPromptDataCopyWith<AIPromptData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIPromptDataCopyWith<$Res> {
  factory $AIPromptDataCopyWith(
          AIPromptData value, $Res Function(AIPromptData) then) =
      _$AIPromptDataCopyWithImpl<$Res, AIPromptData>;
  @useResult
  $Res call(
      {String id,
      String name,
      String prompt,
      String type,
      bool isActive,
      double temperature,
      int maxTokens,
      String model,
      int usageCount,
      double avgResponseTime,
      DateTime? createdAt,
      DateTime? lastUsed});
}

/// @nodoc
class _$AIPromptDataCopyWithImpl<$Res, $Val extends AIPromptData>
    implements $AIPromptDataCopyWith<$Res> {
  _$AIPromptDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIPromptData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? prompt = null,
    Object? type = null,
    Object? isActive = null,
    Object? temperature = null,
    Object? maxTokens = null,
    Object? model = null,
    Object? usageCount = null,
    Object? avgResponseTime = null,
    Object? createdAt = freezed,
    Object? lastUsed = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      prompt: null == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      temperature: null == temperature
          ? _value.temperature
          : temperature // ignore: cast_nullable_to_non_nullable
              as double,
      maxTokens: null == maxTokens
          ? _value.maxTokens
          : maxTokens // ignore: cast_nullable_to_non_nullable
              as int,
      model: null == model
          ? _value.model
          : model // ignore: cast_nullable_to_non_nullable
              as String,
      usageCount: null == usageCount
          ? _value.usageCount
          : usageCount // ignore: cast_nullable_to_non_nullable
              as int,
      avgResponseTime: null == avgResponseTime
          ? _value.avgResponseTime
          : avgResponseTime // ignore: cast_nullable_to_non_nullable
              as double,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastUsed: freezed == lastUsed
          ? _value.lastUsed
          : lastUsed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIPromptDataImplCopyWith<$Res>
    implements $AIPromptDataCopyWith<$Res> {
  factory _$$AIPromptDataImplCopyWith(
          _$AIPromptDataImpl value, $Res Function(_$AIPromptDataImpl) then) =
      __$$AIPromptDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String prompt,
      String type,
      bool isActive,
      double temperature,
      int maxTokens,
      String model,
      int usageCount,
      double avgResponseTime,
      DateTime? createdAt,
      DateTime? lastUsed});
}

/// @nodoc
class __$$AIPromptDataImplCopyWithImpl<$Res>
    extends _$AIPromptDataCopyWithImpl<$Res, _$AIPromptDataImpl>
    implements _$$AIPromptDataImplCopyWith<$Res> {
  __$$AIPromptDataImplCopyWithImpl(
      _$AIPromptDataImpl _value, $Res Function(_$AIPromptDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIPromptData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? prompt = null,
    Object? type = null,
    Object? isActive = null,
    Object? temperature = null,
    Object? maxTokens = null,
    Object? model = null,
    Object? usageCount = null,
    Object? avgResponseTime = null,
    Object? createdAt = freezed,
    Object? lastUsed = freezed,
  }) {
    return _then(_$AIPromptDataImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      prompt: null == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      temperature: null == temperature
          ? _value.temperature
          : temperature // ignore: cast_nullable_to_non_nullable
              as double,
      maxTokens: null == maxTokens
          ? _value.maxTokens
          : maxTokens // ignore: cast_nullable_to_non_nullable
              as int,
      model: null == model
          ? _value.model
          : model // ignore: cast_nullable_to_non_nullable
              as String,
      usageCount: null == usageCount
          ? _value.usageCount
          : usageCount // ignore: cast_nullable_to_non_nullable
              as int,
      avgResponseTime: null == avgResponseTime
          ? _value.avgResponseTime
          : avgResponseTime // ignore: cast_nullable_to_non_nullable
              as double,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastUsed: freezed == lastUsed
          ? _value.lastUsed
          : lastUsed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIPromptDataImpl implements _AIPromptData {
  const _$AIPromptDataImpl(
      {required this.id,
      required this.name,
      required this.prompt,
      this.type = 'persuasive',
      this.isActive = true,
      this.temperature = 0.7,
      this.maxTokens = 150,
      this.model = 'gpt-4o',
      this.usageCount = 0,
      this.avgResponseTime = 0.0,
      this.createdAt,
      this.lastUsed});

  factory _$AIPromptDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIPromptDataImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String prompt;
  @override
  @JsonKey()
  final String type;
  @override
  @JsonKey()
  final bool isActive;
  @override
  @JsonKey()
  final double temperature;
  @override
  @JsonKey()
  final int maxTokens;
  @override
  @JsonKey()
  final String model;
  @override
  @JsonKey()
  final int usageCount;
  @override
  @JsonKey()
  final double avgResponseTime;
  @override
  final DateTime? createdAt;
  @override
  final DateTime? lastUsed;

  @override
  String toString() {
    return 'AIPromptData(id: $id, name: $name, prompt: $prompt, type: $type, isActive: $isActive, temperature: $temperature, maxTokens: $maxTokens, model: $model, usageCount: $usageCount, avgResponseTime: $avgResponseTime, createdAt: $createdAt, lastUsed: $lastUsed)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIPromptDataImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.prompt, prompt) || other.prompt == prompt) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.temperature, temperature) ||
                other.temperature == temperature) &&
            (identical(other.maxTokens, maxTokens) ||
                other.maxTokens == maxTokens) &&
            (identical(other.model, model) || other.model == model) &&
            (identical(other.usageCount, usageCount) ||
                other.usageCount == usageCount) &&
            (identical(other.avgResponseTime, avgResponseTime) ||
                other.avgResponseTime == avgResponseTime) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.lastUsed, lastUsed) ||
                other.lastUsed == lastUsed));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      prompt,
      type,
      isActive,
      temperature,
      maxTokens,
      model,
      usageCount,
      avgResponseTime,
      createdAt,
      lastUsed);

  /// Create a copy of AIPromptData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIPromptDataImplCopyWith<_$AIPromptDataImpl> get copyWith =>
      __$$AIPromptDataImplCopyWithImpl<_$AIPromptDataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIPromptDataImplToJson(
      this,
    );
  }
}

abstract class _AIPromptData implements AIPromptData {
  const factory _AIPromptData(
      {required final String id,
      required final String name,
      required final String prompt,
      final String type,
      final bool isActive,
      final double temperature,
      final int maxTokens,
      final String model,
      final int usageCount,
      final double avgResponseTime,
      final DateTime? createdAt,
      final DateTime? lastUsed}) = _$AIPromptDataImpl;

  factory _AIPromptData.fromJson(Map<String, dynamic> json) =
      _$AIPromptDataImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get prompt;
  @override
  String get type;
  @override
  bool get isActive;
  @override
  double get temperature;
  @override
  int get maxTokens;
  @override
  String get model;
  @override
  int get usageCount;
  @override
  double get avgResponseTime;
  @override
  DateTime? get createdAt;
  @override
  DateTime? get lastUsed;

  /// Create a copy of AIPromptData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIPromptDataImplCopyWith<_$AIPromptDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

LogEntry _$LogEntryFromJson(Map<String, dynamic> json) {
  return _LogEntry.fromJson(json);
}

/// @nodoc
mixin _$LogEntry {
  String get id => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  String get level => throw _privateConstructorUsedError;
  String get source => throw _privateConstructorUsedError;
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String? get botId => throw _privateConstructorUsedError;
  String? get userId => throw _privateConstructorUsedError;
  String? get action => throw _privateConstructorUsedError;

  /// Serializes this LogEntry to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of LogEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $LogEntryCopyWith<LogEntry> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $LogEntryCopyWith<$Res> {
  factory $LogEntryCopyWith(LogEntry value, $Res Function(LogEntry) then) =
      _$LogEntryCopyWithImpl<$Res, LogEntry>;
  @useResult
  $Res call(
      {String id,
      String message,
      String level,
      String source,
      Map<String, dynamic> metadata,
      DateTime timestamp,
      String? botId,
      String? userId,
      String? action});
}

/// @nodoc
class _$LogEntryCopyWithImpl<$Res, $Val extends LogEntry>
    implements $LogEntryCopyWith<$Res> {
  _$LogEntryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of LogEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? message = null,
    Object? level = null,
    Object? source = null,
    Object? metadata = null,
    Object? timestamp = null,
    Object? botId = freezed,
    Object? userId = freezed,
    Object? action = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      level: null == level
          ? _value.level
          : level // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      botId: freezed == botId
          ? _value.botId
          : botId // ignore: cast_nullable_to_non_nullable
              as String?,
      userId: freezed == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String?,
      action: freezed == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$LogEntryImplCopyWith<$Res>
    implements $LogEntryCopyWith<$Res> {
  factory _$$LogEntryImplCopyWith(
          _$LogEntryImpl value, $Res Function(_$LogEntryImpl) then) =
      __$$LogEntryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String message,
      String level,
      String source,
      Map<String, dynamic> metadata,
      DateTime timestamp,
      String? botId,
      String? userId,
      String? action});
}

/// @nodoc
class __$$LogEntryImplCopyWithImpl<$Res>
    extends _$LogEntryCopyWithImpl<$Res, _$LogEntryImpl>
    implements _$$LogEntryImplCopyWith<$Res> {
  __$$LogEntryImplCopyWithImpl(
      _$LogEntryImpl _value, $Res Function(_$LogEntryImpl) _then)
      : super(_value, _then);

  /// Create a copy of LogEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? message = null,
    Object? level = null,
    Object? source = null,
    Object? metadata = null,
    Object? timestamp = null,
    Object? botId = freezed,
    Object? userId = freezed,
    Object? action = freezed,
  }) {
    return _then(_$LogEntryImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      level: null == level
          ? _value.level
          : level // ignore: cast_nullable_to_non_nullable
              as String,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      botId: freezed == botId
          ? _value.botId
          : botId // ignore: cast_nullable_to_non_nullable
              as String?,
      userId: freezed == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String?,
      action: freezed == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$LogEntryImpl implements _LogEntry {
  const _$LogEntryImpl(
      {required this.id,
      required this.message,
      this.level = 'info',
      this.source = 'system',
      final Map<String, dynamic> metadata = const {},
      required this.timestamp,
      this.botId,
      this.userId,
      this.action})
      : _metadata = metadata;

  factory _$LogEntryImpl.fromJson(Map<String, dynamic> json) =>
      _$$LogEntryImplFromJson(json);

  @override
  final String id;
  @override
  final String message;
  @override
  @JsonKey()
  final String level;
  @override
  @JsonKey()
  final String source;
  final Map<String, dynamic> _metadata;
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  @override
  final DateTime timestamp;
  @override
  final String? botId;
  @override
  final String? userId;
  @override
  final String? action;

  @override
  String toString() {
    return 'LogEntry(id: $id, message: $message, level: $level, source: $source, metadata: $metadata, timestamp: $timestamp, botId: $botId, userId: $userId, action: $action)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$LogEntryImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.level, level) || other.level == level) &&
            (identical(other.source, source) || other.source == source) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.botId, botId) || other.botId == botId) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.action, action) || other.action == action));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      message,
      level,
      source,
      const DeepCollectionEquality().hash(_metadata),
      timestamp,
      botId,
      userId,
      action);

  /// Create a copy of LogEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$LogEntryImplCopyWith<_$LogEntryImpl> get copyWith =>
      __$$LogEntryImplCopyWithImpl<_$LogEntryImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$LogEntryImplToJson(
      this,
    );
  }
}

abstract class _LogEntry implements LogEntry {
  const factory _LogEntry(
      {required final String id,
      required final String message,
      final String level,
      final String source,
      final Map<String, dynamic> metadata,
      required final DateTime timestamp,
      final String? botId,
      final String? userId,
      final String? action}) = _$LogEntryImpl;

  factory _LogEntry.fromJson(Map<String, dynamic> json) =
      _$LogEntryImpl.fromJson;

  @override
  String get id;
  @override
  String get message;
  @override
  String get level;
  @override
  String get source;
  @override
  Map<String, dynamic> get metadata;
  @override
  DateTime get timestamp;
  @override
  String? get botId;
  @override
  String? get userId;
  @override
  String? get action;

  /// Create a copy of LogEntry
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$LogEntryImplCopyWith<_$LogEntryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UserAccount _$UserAccountFromJson(Map<String, dynamic> json) {
  return _UserAccount.fromJson(json);
}

/// @nodoc
mixin _$UserAccount {
  String get id => throw _privateConstructorUsedError;
  String get email => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get role => throw _privateConstructorUsedError;
  String get plan => throw _privateConstructorUsedError;
  double get balance => throw _privateConstructorUsedError;
  double get monthlyUsage => throw _privateConstructorUsedError;
  double get monthlyLimit => throw _privateConstructorUsedError;
  Map<String, dynamic> get settings => throw _privateConstructorUsedError;
  DateTime? get createdAt => throw _privateConstructorUsedError;
  DateTime? get lastLogin => throw _privateConstructorUsedError;
  bool get isActive => throw _privateConstructorUsedError;

  /// Serializes this UserAccount to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UserAccount
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserAccountCopyWith<UserAccount> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserAccountCopyWith<$Res> {
  factory $UserAccountCopyWith(
          UserAccount value, $Res Function(UserAccount) then) =
      _$UserAccountCopyWithImpl<$Res, UserAccount>;
  @useResult
  $Res call(
      {String id,
      String email,
      String name,
      String role,
      String plan,
      double balance,
      double monthlyUsage,
      double monthlyLimit,
      Map<String, dynamic> settings,
      DateTime? createdAt,
      DateTime? lastLogin,
      bool isActive});
}

/// @nodoc
class _$UserAccountCopyWithImpl<$Res, $Val extends UserAccount>
    implements $UserAccountCopyWith<$Res> {
  _$UserAccountCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UserAccount
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = null,
    Object? name = null,
    Object? role = null,
    Object? plan = null,
    Object? balance = null,
    Object? monthlyUsage = null,
    Object? monthlyLimit = null,
    Object? settings = null,
    Object? createdAt = freezed,
    Object? lastLogin = freezed,
    Object? isActive = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      plan: null == plan
          ? _value.plan
          : plan // ignore: cast_nullable_to_non_nullable
              as String,
      balance: null == balance
          ? _value.balance
          : balance // ignore: cast_nullable_to_non_nullable
              as double,
      monthlyUsage: null == monthlyUsage
          ? _value.monthlyUsage
          : monthlyUsage // ignore: cast_nullable_to_non_nullable
              as double,
      monthlyLimit: null == monthlyLimit
          ? _value.monthlyLimit
          : monthlyLimit // ignore: cast_nullable_to_non_nullable
              as double,
      settings: null == settings
          ? _value.settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastLogin: freezed == lastLogin
          ? _value.lastLogin
          : lastLogin // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UserAccountImplCopyWith<$Res>
    implements $UserAccountCopyWith<$Res> {
  factory _$$UserAccountImplCopyWith(
          _$UserAccountImpl value, $Res Function(_$UserAccountImpl) then) =
      __$$UserAccountImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String email,
      String name,
      String role,
      String plan,
      double balance,
      double monthlyUsage,
      double monthlyLimit,
      Map<String, dynamic> settings,
      DateTime? createdAt,
      DateTime? lastLogin,
      bool isActive});
}

/// @nodoc
class __$$UserAccountImplCopyWithImpl<$Res>
    extends _$UserAccountCopyWithImpl<$Res, _$UserAccountImpl>
    implements _$$UserAccountImplCopyWith<$Res> {
  __$$UserAccountImplCopyWithImpl(
      _$UserAccountImpl _value, $Res Function(_$UserAccountImpl) _then)
      : super(_value, _then);

  /// Create a copy of UserAccount
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? email = null,
    Object? name = null,
    Object? role = null,
    Object? plan = null,
    Object? balance = null,
    Object? monthlyUsage = null,
    Object? monthlyLimit = null,
    Object? settings = null,
    Object? createdAt = freezed,
    Object? lastLogin = freezed,
    Object? isActive = null,
  }) {
    return _then(_$UserAccountImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      plan: null == plan
          ? _value.plan
          : plan // ignore: cast_nullable_to_non_nullable
              as String,
      balance: null == balance
          ? _value.balance
          : balance // ignore: cast_nullable_to_non_nullable
              as double,
      monthlyUsage: null == monthlyUsage
          ? _value.monthlyUsage
          : monthlyUsage // ignore: cast_nullable_to_non_nullable
              as double,
      monthlyLimit: null == monthlyLimit
          ? _value.monthlyLimit
          : monthlyLimit // ignore: cast_nullable_to_non_nullable
              as double,
      settings: null == settings
          ? _value._settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastLogin: freezed == lastLogin
          ? _value.lastLogin
          : lastLogin // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UserAccountImpl implements _UserAccount {
  const _$UserAccountImpl(
      {required this.id,
      required this.email,
      required this.name,
      this.role = 'user',
      this.plan = 'free',
      this.balance = 0.0,
      this.monthlyUsage = 0.0,
      this.monthlyLimit = 100.0,
      final Map<String, dynamic> settings = const {},
      this.createdAt,
      this.lastLogin,
      this.isActive = true})
      : _settings = settings;

  factory _$UserAccountImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserAccountImplFromJson(json);

  @override
  final String id;
  @override
  final String email;
  @override
  final String name;
  @override
  @JsonKey()
  final String role;
  @override
  @JsonKey()
  final String plan;
  @override
  @JsonKey()
  final double balance;
  @override
  @JsonKey()
  final double monthlyUsage;
  @override
  @JsonKey()
  final double monthlyLimit;
  final Map<String, dynamic> _settings;
  @override
  @JsonKey()
  Map<String, dynamic> get settings {
    if (_settings is EqualUnmodifiableMapView) return _settings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_settings);
  }

  @override
  final DateTime? createdAt;
  @override
  final DateTime? lastLogin;
  @override
  @JsonKey()
  final bool isActive;

  @override
  String toString() {
    return 'UserAccount(id: $id, email: $email, name: $name, role: $role, plan: $plan, balance: $balance, monthlyUsage: $monthlyUsage, monthlyLimit: $monthlyLimit, settings: $settings, createdAt: $createdAt, lastLogin: $lastLogin, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserAccountImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.plan, plan) || other.plan == plan) &&
            (identical(other.balance, balance) || other.balance == balance) &&
            (identical(other.monthlyUsage, monthlyUsage) ||
                other.monthlyUsage == monthlyUsage) &&
            (identical(other.monthlyLimit, monthlyLimit) ||
                other.monthlyLimit == monthlyLimit) &&
            const DeepCollectionEquality().equals(other._settings, _settings) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.lastLogin, lastLogin) ||
                other.lastLogin == lastLogin) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      email,
      name,
      role,
      plan,
      balance,
      monthlyUsage,
      monthlyLimit,
      const DeepCollectionEquality().hash(_settings),
      createdAt,
      lastLogin,
      isActive);

  /// Create a copy of UserAccount
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserAccountImplCopyWith<_$UserAccountImpl> get copyWith =>
      __$$UserAccountImplCopyWithImpl<_$UserAccountImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UserAccountImplToJson(
      this,
    );
  }
}

abstract class _UserAccount implements UserAccount {
  const factory _UserAccount(
      {required final String id,
      required final String email,
      required final String name,
      final String role,
      final String plan,
      final double balance,
      final double monthlyUsage,
      final double monthlyLimit,
      final Map<String, dynamic> settings,
      final DateTime? createdAt,
      final DateTime? lastLogin,
      final bool isActive}) = _$UserAccountImpl;

  factory _UserAccount.fromJson(Map<String, dynamic> json) =
      _$UserAccountImpl.fromJson;

  @override
  String get id;
  @override
  String get email;
  @override
  String get name;
  @override
  String get role;
  @override
  String get plan;
  @override
  double get balance;
  @override
  double get monthlyUsage;
  @override
  double get monthlyLimit;
  @override
  Map<String, dynamic> get settings;
  @override
  DateTime? get createdAt;
  @override
  DateTime? get lastLogin;
  @override
  bool get isActive;

  /// Create a copy of UserAccount
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserAccountImplCopyWith<_$UserAccountImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SystemStatus _$SystemStatusFromJson(Map<String, dynamic> json) {
  return _SystemStatus.fromJson(json);
}

/// @nodoc
mixin _$SystemStatus {
  String get status => throw _privateConstructorUsedError;
  double get cpuUsage => throw _privateConstructorUsedError;
  double get memoryUsage => throw _privateConstructorUsedError;
  double get diskUsage => throw _privateConstructorUsedError;
  int get activeConnections => throw _privateConstructorUsedError;
  int get queueLength => throw _privateConstructorUsedError;
  bool get maintenanceMode => throw _privateConstructorUsedError;
  DateTime? get lastRestart => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;

  /// Serializes this SystemStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SystemStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SystemStatusCopyWith<SystemStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SystemStatusCopyWith<$Res> {
  factory $SystemStatusCopyWith(
          SystemStatus value, $Res Function(SystemStatus) then) =
      _$SystemStatusCopyWithImpl<$Res, SystemStatus>;
  @useResult
  $Res call(
      {String status,
      double cpuUsage,
      double memoryUsage,
      double diskUsage,
      int activeConnections,
      int queueLength,
      bool maintenanceMode,
      DateTime? lastRestart,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class _$SystemStatusCopyWithImpl<$Res, $Val extends SystemStatus>
    implements $SystemStatusCopyWith<$Res> {
  _$SystemStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SystemStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? cpuUsage = null,
    Object? memoryUsage = null,
    Object? diskUsage = null,
    Object? activeConnections = null,
    Object? queueLength = null,
    Object? maintenanceMode = null,
    Object? lastRestart = freezed,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_value.copyWith(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      cpuUsage: null == cpuUsage
          ? _value.cpuUsage
          : cpuUsage // ignore: cast_nullable_to_non_nullable
              as double,
      memoryUsage: null == memoryUsage
          ? _value.memoryUsage
          : memoryUsage // ignore: cast_nullable_to_non_nullable
              as double,
      diskUsage: null == diskUsage
          ? _value.diskUsage
          : diskUsage // ignore: cast_nullable_to_non_nullable
              as double,
      activeConnections: null == activeConnections
          ? _value.activeConnections
          : activeConnections // ignore: cast_nullable_to_non_nullable
              as int,
      queueLength: null == queueLength
          ? _value.queueLength
          : queueLength // ignore: cast_nullable_to_non_nullable
              as int,
      maintenanceMode: null == maintenanceMode
          ? _value.maintenanceMode
          : maintenanceMode // ignore: cast_nullable_to_non_nullable
              as bool,
      lastRestart: freezed == lastRestart
          ? _value.lastRestart
          : lastRestart // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SystemStatusImplCopyWith<$Res>
    implements $SystemStatusCopyWith<$Res> {
  factory _$$SystemStatusImplCopyWith(
          _$SystemStatusImpl value, $Res Function(_$SystemStatusImpl) then) =
      __$$SystemStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String status,
      double cpuUsage,
      double memoryUsage,
      double diskUsage,
      int activeConnections,
      int queueLength,
      bool maintenanceMode,
      DateTime? lastRestart,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class __$$SystemStatusImplCopyWithImpl<$Res>
    extends _$SystemStatusCopyWithImpl<$Res, _$SystemStatusImpl>
    implements _$$SystemStatusImplCopyWith<$Res> {
  __$$SystemStatusImplCopyWithImpl(
      _$SystemStatusImpl _value, $Res Function(_$SystemStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of SystemStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? cpuUsage = null,
    Object? memoryUsage = null,
    Object? diskUsage = null,
    Object? activeConnections = null,
    Object? queueLength = null,
    Object? maintenanceMode = null,
    Object? lastRestart = freezed,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_$SystemStatusImpl(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      cpuUsage: null == cpuUsage
          ? _value.cpuUsage
          : cpuUsage // ignore: cast_nullable_to_non_nullable
              as double,
      memoryUsage: null == memoryUsage
          ? _value.memoryUsage
          : memoryUsage // ignore: cast_nullable_to_non_nullable
              as double,
      diskUsage: null == diskUsage
          ? _value.diskUsage
          : diskUsage // ignore: cast_nullable_to_non_nullable
              as double,
      activeConnections: null == activeConnections
          ? _value.activeConnections
          : activeConnections // ignore: cast_nullable_to_non_nullable
              as int,
      queueLength: null == queueLength
          ? _value.queueLength
          : queueLength // ignore: cast_nullable_to_non_nullable
              as int,
      maintenanceMode: null == maintenanceMode
          ? _value.maintenanceMode
          : maintenanceMode // ignore: cast_nullable_to_non_nullable
              as bool,
      lastRestart: freezed == lastRestart
          ? _value.lastRestart
          : lastRestart // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SystemStatusImpl implements _SystemStatus {
  const _$SystemStatusImpl(
      {this.status = 'running',
      this.cpuUsage = 0.0,
      this.memoryUsage = 0.0,
      this.diskUsage = 0.0,
      this.activeConnections = 0,
      this.queueLength = 0,
      this.maintenanceMode = false,
      this.lastRestart,
      final List<String> errors = const [],
      final List<String> warnings = const []})
      : _errors = errors,
        _warnings = warnings;

  factory _$SystemStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$SystemStatusImplFromJson(json);

  @override
  @JsonKey()
  final String status;
  @override
  @JsonKey()
  final double cpuUsage;
  @override
  @JsonKey()
  final double memoryUsage;
  @override
  @JsonKey()
  final double diskUsage;
  @override
  @JsonKey()
  final int activeConnections;
  @override
  @JsonKey()
  final int queueLength;
  @override
  @JsonKey()
  final bool maintenanceMode;
  @override
  final DateTime? lastRestart;
  final List<String> _errors;
  @override
  @JsonKey()
  List<String> get errors {
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errors);
  }

  final List<String> _warnings;
  @override
  @JsonKey()
  List<String> get warnings {
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warnings);
  }

  @override
  String toString() {
    return 'SystemStatus(status: $status, cpuUsage: $cpuUsage, memoryUsage: $memoryUsage, diskUsage: $diskUsage, activeConnections: $activeConnections, queueLength: $queueLength, maintenanceMode: $maintenanceMode, lastRestart: $lastRestart, errors: $errors, warnings: $warnings)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SystemStatusImpl &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.cpuUsage, cpuUsage) ||
                other.cpuUsage == cpuUsage) &&
            (identical(other.memoryUsage, memoryUsage) ||
                other.memoryUsage == memoryUsage) &&
            (identical(other.diskUsage, diskUsage) ||
                other.diskUsage == diskUsage) &&
            (identical(other.activeConnections, activeConnections) ||
                other.activeConnections == activeConnections) &&
            (identical(other.queueLength, queueLength) ||
                other.queueLength == queueLength) &&
            (identical(other.maintenanceMode, maintenanceMode) ||
                other.maintenanceMode == maintenanceMode) &&
            (identical(other.lastRestart, lastRestart) ||
                other.lastRestart == lastRestart) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      status,
      cpuUsage,
      memoryUsage,
      diskUsage,
      activeConnections,
      queueLength,
      maintenanceMode,
      lastRestart,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings));

  /// Create a copy of SystemStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SystemStatusImplCopyWith<_$SystemStatusImpl> get copyWith =>
      __$$SystemStatusImplCopyWithImpl<_$SystemStatusImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SystemStatusImplToJson(
      this,
    );
  }
}

abstract class _SystemStatus implements SystemStatus {
  const factory _SystemStatus(
      {final String status,
      final double cpuUsage,
      final double memoryUsage,
      final double diskUsage,
      final int activeConnections,
      final int queueLength,
      final bool maintenanceMode,
      final DateTime? lastRestart,
      final List<String> errors,
      final List<String> warnings}) = _$SystemStatusImpl;

  factory _SystemStatus.fromJson(Map<String, dynamic> json) =
      _$SystemStatusImpl.fromJson;

  @override
  String get status;
  @override
  double get cpuUsage;
  @override
  double get memoryUsage;
  @override
  double get diskUsage;
  @override
  int get activeConnections;
  @override
  int get queueLength;
  @override
  bool get maintenanceMode;
  @override
  DateTime? get lastRestart;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;

  /// Create a copy of SystemStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SystemStatusImplCopyWith<_$SystemStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
