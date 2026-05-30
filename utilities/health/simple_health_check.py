#!/usr/bin/env python3
"""
🏥 SIMPLE HEALTH CHECK SYSTEM
=============================

Basic health monitoring without dependencies:
- File system checks
- Directory structure
- Basic system info
- Configuration validation
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class SimpleHealthCheck:
    """Basit sağlık kontrol sistemi"""

    def __init__(self):
        self.start_time = datetime.now()
        self.checks = {}

    def check_directories(self) -> Dict[str, Any]:
        """Temel klasör yapısını kontrol et"""
        try:
            required_dirs = ["logs", "sessions", "data", "launchers", "gpt", "core", "utilities"]

            dir_status = {}
            missing_dirs = []

            for dir_name in required_dirs:
                if os.path.exists(dir_name):
                    dir_status[dir_name] = "exists"
                else:
                    dir_status[dir_name] = "missing"
                    missing_dirs.append(dir_name)

            status = "healthy" if not missing_dirs else "warning"

            return {
                "status": status,
                "checked_dirs": len(required_dirs),
                "existing_dirs": len(required_dirs) - len(missing_dirs),
                "missing_dirs": missing_dirs,
                "directory_details": dir_status,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_session_files(self) -> Dict[str, Any]:
        """Session dosyalarını kontrol et"""
        try:
            sessions_dir = Path("sessions")

            if not sessions_dir.exists():
                return {
                    "status": "critical",
                    "message": "Sessions directory not found",
                    "session_count": 0,
                }

            session_files = list(sessions_dir.glob("*.session"))

            if not session_files:
                return {
                    "status": "warning",
                    "message": "No session files found",
                    "session_count": 0,
                }

            # Session dosyalarını analiz et
            valid_sessions = []
            invalid_sessions = []

            for session_file in session_files:
                try:
                    size = session_file.stat().st_size
                    if size > 512:  # En az 512 bytes
                        valid_sessions.append({"file": session_file.name, "size": size})
                    else:
                        invalid_sessions.append(
                            {"file": session_file.name, "size": size, "issue": "too_small"}
                        )
                except Exception as e:
                    invalid_sessions.append({"file": session_file.name, "issue": str(e)})

            total_sessions = len(valid_sessions) + len(invalid_sessions)
            status = (
                "healthy"
                if len(valid_sessions) >= 2
                else "warning"
                if len(valid_sessions) >= 1
                else "critical"
            )

            return {
                "status": status,
                "session_count": total_sessions,
                "valid_sessions": len(valid_sessions),
                "invalid_sessions": len(invalid_sessions),
                "session_details": {"valid": valid_sessions, "invalid": invalid_sessions},
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_logs_system(self) -> Dict[str, Any]:
        """Logs sistemini kontrol et"""
        try:
            logs_dir = Path("logs")

            if not logs_dir.exists():
                return {"status": "warning", "message": "Logs directory not found", "log_count": 0}

            log_files = list(logs_dir.glob("*.log"))

            if not log_files:
                return {"status": "warning", "message": "No log files found", "log_count": 0}

            # Log dosyalarını analiz et
            total_size = 0
            recent_logs = []

            for log_file in log_files:
                try:
                    size = log_file.stat().st_size
                    total_size += size

                    # Son 1 saat içinde değişen dosyalar
                    mod_time = log_file.stat().st_mtime
                    current_time = time.time()

                    if (current_time - mod_time) < 3600:  # 1 saat
                        recent_logs.append(
                            {
                                "file": log_file.name,
                                "size": size,
                                "age_minutes": int((current_time - mod_time) / 60),
                            }
                        )

                except Exception as e:
                    continue

            status = "healthy" if recent_logs else "warning"

            return {
                "status": status,
                "log_count": len(log_files),
                "total_size": total_size,
                "recent_activity": len(recent_logs),
                "size_mb": round(total_size / (1024 * 1024), 2),
                "recent_logs": recent_logs,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_bot_configurations(self) -> Dict[str, Any]:
        """Bot konfigürasyonlarını kontrol et"""
        try:
            # Expected bots
            expected_bots = ["gawatbaba", "yayincilara", "xxxgeisha"]

            # Persona dosyalarını kontrol et
            persona_dir = Path("data/personas")

            if not persona_dir.exists():
                return {
                    "status": "critical",
                    "message": "Personas directory not found",
                    "expected_bots": len(expected_bots),
                    "available_bots": 0,
                }

            available_bots = []
            missing_bots = []

            for bot_name in expected_bots:
                persona_file = persona_dir / f"{bot_name}.json"

                if persona_file.exists():
                    try:
                        with open(persona_file, "r", encoding="utf-8") as f:
                            persona_data = json.load(f)

                        available_bots.append(
                            {
                                "name": bot_name,
                                "file": persona_file.name,
                                "phone": persona_data.get("phone", "unknown"),
                                "display_name": persona_data.get("name", bot_name),
                            }
                        )
                    except Exception as e:
                        missing_bots.append({"name": bot_name, "issue": f"Invalid JSON: {e}"})
                else:
                    missing_bots.append({"name": bot_name, "issue": "File not found"})

            # Master launcher kontrolü
            master_launcher = Path("launchers/gavatcore_master_launcher.py")

            status = (
                "healthy"
                if len(available_bots) >= 2
                else "warning"
                if len(available_bots) >= 1
                else "critical"
            )

            return {
                "status": status,
                "expected_bots": len(expected_bots),
                "available_bots": len(available_bots),
                "missing_bots": len(missing_bots),
                "master_launcher_exists": master_launcher.exists(),
                "bot_details": {"available": available_bots, "missing": missing_bots},
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_core_files(self) -> Dict[str, Any]:
        """Core dosyaları kontrol et"""
        try:
            # Kritik dosyalar
            critical_files = [
                "config.py",
                "launchers/gavatcore_master_launcher.py",
                "test_coin_system_simple.py",
                "test_simple_logs.py",
                "gavatcore_health_check.py",
            ]

            existing_files = []
            missing_files = []

            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        existing_files.append({"file": file_path, "size": size})
                    except:
                        existing_files.append({"file": file_path, "size": 0})
                else:
                    missing_files.append(file_path)

            status = "healthy" if len(existing_files) >= 3 else "warning"

            return {
                "status": status,
                "checked_files": len(critical_files),
                "existing_files": len(existing_files),
                "missing_files": missing_files,
                "file_details": existing_files,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_coin_system(self) -> Dict[str, Any]:
        """Coin sistem dosyalarını kontrol et"""
        try:
            # Coin test dosyası
            coin_file = Path("test_coin_data.json")

            if coin_file.exists():
                try:
                    with open(coin_file, "r", encoding="utf-8") as f:
                        coin_data = json.load(f)

                    users = coin_data.get("users", {})
                    transactions = coin_data.get("transactions", [])

                    return {
                        "status": "healthy",
                        "test_file_exists": True,
                        "users_count": len(users),
                        "transactions_count": len(transactions),
                        "file_size": coin_file.stat().st_size,
                    }
                except Exception as e:
                    return {
                        "status": "warning",
                        "test_file_exists": True,
                        "error": f"Invalid JSON: {e}",
                    }
            else:
                return {
                    "status": "warning",
                    "test_file_exists": False,
                    "message": "Coin test file not found",
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Kapsamlı sağlık kontrolü"""
        start_time = time.time()

        print("🚀 Starting Simple Health Check...")

        # Tüm kontroller
        checks = {
            "directories": self.check_directories(),
            "session_files": self.check_session_files(),
            "logs_system": self.check_logs_system(),
            "bot_configurations": self.check_bot_configurations(),
            "core_files": self.check_core_files(),
            "coin_system": self.check_coin_system(),
        }

        # Sağlık durumu analizi
        healthy_systems = []
        warnings = []
        critical_issues = []

        for system_name, result in checks.items():
            if isinstance(result, dict) and "status" in result:
                if result["status"] == "healthy":
                    healthy_systems.append(system_name)
                elif result["status"] == "warning":
                    warnings.append(system_name)
                elif result["status"] == "critical":
                    critical_issues.append(system_name)

        # Genel sağlık skoru
        total_systems = len(checks)
        health_score = len(healthy_systems) / total_systems * 100

        # Genel durum
        if critical_issues:
            overall_status = "critical"
        elif len(warnings) > len(healthy_systems):
            overall_status = "warning"
        else:
            overall_status = "healthy"

        check_duration = time.time() - start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "health_score": round(health_score, 1),
            "check_duration_ms": round(check_duration * 1000, 2),
            "summary": {
                "total_systems": total_systems,
                "healthy_systems": len(healthy_systems),
                "warnings": len(warnings),
                "critical_issues": len(critical_issues),
            },
            "issues": {
                "healthy": healthy_systems,
                "warnings": warnings,
                "critical": critical_issues,
            },
            "system_details": checks,
        }


def display_health_report(report: Dict[str, Any]):
    """Health report görüntüle"""
    print("\n🏥 SIMPLE HEALTH CHECK REPORT")
    print("=" * 50)

    # Status emojis
    status_emojis = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}

    # Genel durum
    overall_status = report["overall_status"]
    emoji = status_emojis.get(overall_status, "❓")

    print(f"📊 Overall Status: {emoji} {overall_status.upper()}")
    print(f"🎯 Health Score: {report['health_score']}%")
    print(f"⏱️ Check Duration: {report['check_duration_ms']}ms")
    print(f"📅 Timestamp: {report['timestamp']}")

    # Özet
    summary = report["summary"]
    print(f"\n📋 SUMMARY")
    print(f"✅ Healthy: {summary['healthy_systems']}/{summary['total_systems']}")
    print(f"⚠️ Warnings: {summary['warnings']}")
    print(f"❌ Critical: {summary['critical_issues']}")

    # İssues
    if report["issues"]["critical"]:
        print(f"\n🚨 CRITICAL ISSUES:")
        for issue in report["issues"]["critical"]:
            print(f"   ❌ {issue}")

    if report["issues"]["warnings"]:
        print(f"\n⚠️ WARNINGS:")
        for warning in report["issues"]["warnings"]:
            print(f"   ⚠️ {warning}")

    # Detaylı sistem durumu
    print(f"\n🔍 DETAILED SYSTEM STATUS")
    print("-" * 40)

    for system, details in report["system_details"].items():
        if isinstance(details, dict) and "status" in details:
            status = details["status"]
            emoji = status_emojis.get(status, "❓")

            print(f"{emoji} {system.upper()}: {status}")

            # Önemli detaylar
            if system == "session_files":
                print(f"   📁 Valid Sessions: {details.get('valid_sessions', 0)}")
            elif system == "logs_system":
                print(f"   📄 Log Files: {details.get('log_count', 0)}")
                print(f"   📊 Size: {details.get('size_mb', 0)} MB")
            elif system == "bot_configurations":
                print(f"   🤖 Available Bots: {details.get('available_bots', 0)}")
            elif system == "coin_system":
                print(f"   💰 Users: {details.get('users_count', 0)}")
                print(f"   💱 Transactions: {details.get('transactions_count', 0)}")

            print()


def main():
    """Ana fonksiyon"""
    try:
        health_checker = SimpleHealthCheck()
        report = health_checker.run_comprehensive_check()

        display_health_report(report)

        # Raporu dosyaya kaydet
        report_file = f"simple_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Health report saved: {report_file}")

        # Exit code
        if report["overall_status"] == "critical":
            return 2
        elif report["overall_status"] == "warning":
            return 1
        else:
            return 0

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
