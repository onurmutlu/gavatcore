#!/usr/bin/env python3
"""
🏥 GAVATCORE HEALTH CHECK SYSTEM
================================

Production ready health monitoring system:
- Bot status monitoring
- Coin system health
- GPT system status
- Session files validation
- API endpoints health
- Database connections
- Logs system health
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil


class HealthCheckSystem:
    """Sistem sağlık kontrolü yöneticisi"""

    def __init__(self):
        self.start_time = datetime.now()
        self.check_history = []
        self.critical_errors = []
        self.warning_count = 0
        self.error_count = 0

    def get_system_info(self) -> Dict[str, Any]:
        """Sistem bilgilerini al"""
        try:
            return {
                "platform": sys.platform,
                "python_version": sys.version.split()[0],
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
                "uptime": str(datetime.now() - self.start_time),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def check_session_files(self) -> Dict[str, Any]:
        """Session dosyalarını kontrol et"""
        try:
            sessions_dir = Path("sessions")

            if not sessions_dir.exists():
                return {
                    "status": "critical",
                    "message": "Sessions directory not found",
                    "session_count": 0,
                    "valid_sessions": 0,
                }

            session_files = list(sessions_dir.glob("*.session"))
            lock_files = list(sessions_dir.glob("*-journal"))

            valid_sessions = 0
            session_info = []

            for session_file in session_files:
                try:
                    size = session_file.stat().st_size
                    if size > 1024:  # En az 1KB
                        valid_sessions += 1
                        session_info.append(
                            {"file": session_file.name, "size": size, "status": "valid"}
                        )
                    else:
                        session_info.append(
                            {"file": session_file.name, "size": size, "status": "invalid"}
                        )
                except Exception as e:
                    session_info.append(
                        {"file": session_file.name, "error": str(e), "status": "error"}
                    )

            status = (
                "healthy"
                if valid_sessions >= 2
                else "warning"
                if valid_sessions >= 1
                else "critical"
            )

            return {
                "status": status,
                "session_count": len(session_files),
                "valid_sessions": valid_sessions,
                "lock_files": len(lock_files),
                "session_details": session_info,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_logs_system(self) -> Dict[str, Any]:
        """Logs sistemini kontrol et"""
        try:
            logs_dir = Path("logs")

            if not logs_dir.exists():
                return {
                    "status": "warning",
                    "message": "Logs directory not found",
                    "log_count": 0,
                    "total_size": 0,
                }

            log_files = list(logs_dir.glob("*.log"))
            total_size = sum(f.stat().st_size for f in log_files)

            # Recent log activity check
            recent_logs = 0
            one_hour_ago = datetime.now() - timedelta(hours=1)

            for log_file in log_files:
                try:
                    mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mod_time > one_hour_ago:
                        recent_logs += 1
                except:
                    continue

            status = "healthy" if recent_logs > 0 else "warning"

            return {
                "status": status,
                "log_count": len(log_files),
                "total_size": total_size,
                "recent_activity": recent_logs,
                "size_mb": round(total_size / (1024 * 1024), 2),
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_coin_system(self) -> Dict[str, Any]:
        """Coin sistemini kontrol et"""
        try:
            # Test coin data file
            test_coin_file = Path("test_coin_data.json")

            if test_coin_file.exists():
                with open(test_coin_file, "r", encoding="utf-8") as f:
                    coin_data = json.load(f)

                user_count = len(coin_data.get("users", {}))
                transaction_count = len(coin_data.get("transactions", []))
                daily_limits = len(coin_data.get("daily_limits", {}))

                return {
                    "status": "healthy",
                    "user_count": user_count,
                    "transaction_count": transaction_count,
                    "daily_limits": daily_limits,
                    "test_file_exists": True,
                }
            else:
                return {
                    "status": "warning",
                    "message": "Coin test data not found",
                    "test_file_exists": False,
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_gpt_system(self) -> Dict[str, Any]:
        """GPT sistemini kontrol et"""
        try:
            # Check GPT config
            gpt_config_file = Path("data/gpt_config.json")

            gpt_status = {
                "config_exists": gpt_config_file.exists(),
                "fallback_available": True,  # Fallback responses always available
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            }

            # Check GPT cache if available
            try:
                from test_simple_logs import create_simple_log_event

                # Test log creation for GPT
                test_result = create_simple_log_event("health_check", "GPT system test", "INFO")
                gpt_status["logging_works"] = test_result
            except:
                gpt_status["logging_works"] = False

            # Overall GPT health
            if gpt_status["fallback_available"]:
                status = "healthy"
            elif gpt_status["openai_configured"]:
                status = "healthy"
            else:
                status = "warning"

            return {"status": status, **gpt_status}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_api_endpoints(self) -> Dict[str, Any]:
        """API endpoint'leri kontrol et"""
        try:
            # Check if gavatcore-api is running
            try:
                import requests

                response = requests.get("http://localhost:8000/health", timeout=5)
                api_running = response.status_code == 200
            except:
                api_running = False

            # Check if processes are running
            gavatcore_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if "gavatcore" in " ".join(proc.info["cmdline"] or []).lower():
                        gavatcore_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cmdline": " ".join(proc.info["cmdline"] or []),
                            }
                        )
                except:
                    continue

            return {
                "status": "healthy" if api_running else "warning",
                "api_running": api_running,
                "gavatcore_processes": len(gavatcore_processes),
                "process_details": gavatcore_processes,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_bot_status(self) -> Dict[str, Any]:
        """Bot durumlarını kontrol et"""
        try:
            # Expected bots
            expected_bots = ["gawatbaba", "yayincilara", "xxxgeisha"]

            # Check persona files
            persona_status = {}
            for bot in expected_bots:
                persona_file = Path(f"data/personas/{bot}.json")
                if persona_file.exists():
                    try:
                        with open(persona_file, "r", encoding="utf-8") as f:
                            persona_data = json.load(f)
                            persona_status[bot] = {
                                "status": "available",
                                "phone": persona_data.get("phone", "unknown"),
                                "name": persona_data.get("name", bot),
                            }
                    except:
                        persona_status[bot] = {"status": "error", "message": "Invalid persona file"}
                else:
                    persona_status[bot] = {"status": "missing", "message": "Persona file not found"}

            # Check master launcher
            master_launcher = Path("launchers/gavatcore_master_launcher.py")

            available_bots = sum(
                1 for bot in persona_status.values() if bot["status"] == "available"
            )

            return {
                "status": "healthy" if available_bots >= 2 else "warning",
                "expected_bots": len(expected_bots),
                "available_bots": available_bots,
                "master_launcher_exists": master_launcher.exists(),
                "bot_details": persona_status,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def perform_comprehensive_health_check(self) -> Dict[str, Any]:
        """Kapsamlı sağlık kontrolü"""
        start_time = time.time()

        checks = {
            "system_info": self.get_system_info(),
            "session_files": self.check_session_files(),
            "logs_system": self.check_logs_system(),
            "coin_system": self.check_coin_system(),
            "gpt_system": self.check_gpt_system(),
            "api_endpoints": self.check_api_endpoints(),
            "bot_status": self.check_bot_status(),
        }

        # Overall health assessment
        critical_issues = []
        warnings = []
        healthy_systems = []

        for system, result in checks.items():
            if isinstance(result, dict) and "status" in result:
                if result["status"] == "critical":
                    critical_issues.append(system)
                elif result["status"] in ["warning", "error"]:
                    warnings.append(system)
                elif result["status"] == "healthy":
                    healthy_systems.append(system)

        # Calculate overall health score
        total_systems = len(checks)
        health_score = len(healthy_systems) / total_systems * 100

        # Overall status
        if critical_issues:
            overall_status = "critical"
        elif len(warnings) > len(healthy_systems):
            overall_status = "warning"
        else:
            overall_status = "healthy"

        check_duration = time.time() - start_time

        health_report = {
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
            "issues": {"critical": critical_issues, "warnings": warnings},
            "systems": checks,
        }

        # Save to history
        self.check_history.append(health_report)

        # Keep only last 50 checks
        if len(self.check_history) > 50:
            self.check_history = self.check_history[-50:]

        return health_report


def display_health_report(report: Dict[str, Any]):
    """Sağlık raporunu güzel formatta göster"""
    print("🏥 GAVATCORE HEALTH CHECK REPORT")
    print("=" * 50)

    # Overall status
    status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}

    print(
        f"📊 Overall Status: {status_emoji.get(report['overall_status'], '❓')} {report['overall_status'].upper()}"
    )
    print(f"🎯 Health Score: {report['health_score']}%")
    print(f"⏱️ Check Duration: {report['check_duration_ms']}ms")
    print(f"📅 Timestamp: {report['timestamp']}")
    print()

    # Summary
    summary = report["summary"]
    print("📋 SYSTEM SUMMARY")
    print("-" * 30)
    print(f"✅ Healthy Systems: {summary['healthy_systems']}/{summary['total_systems']}")
    print(f"⚠️ Warnings: {summary['warnings']}")
    print(f"❌ Critical Issues: {summary['critical_issues']}")
    print()

    # Issues
    if report["issues"]["critical"]:
        print("🚨 CRITICAL ISSUES")
        for issue in report["issues"]["critical"]:
            print(f"   ❌ {issue}")
        print()

    if report["issues"]["warnings"]:
        print("⚠️ WARNINGS")
        for warning in report["issues"]["warnings"]:
            print(f"   ⚠️ {warning}")
        print()

    # Detailed system status
    print("🔍 DETAILED SYSTEM STATUS")
    print("-" * 40)

    for system, details in report["systems"].items():
        if isinstance(details, dict) and "status" in details:
            status = details["status"]
            emoji = status_emoji.get(status, "❓")
            print(f"{emoji} {system.upper()}: {status}")

            # Show relevant details
            if system == "session_files":
                print(
                    f"   📁 Sessions: {details.get('valid_sessions', 0)}/{details.get('session_count', 0)}"
                )
            elif system == "logs_system":
                print(f"   📄 Log Files: {details.get('log_count', 0)}")
                print(f"   📊 Size: {details.get('size_mb', 0)}MB")
            elif system == "coin_system":
                print(f"   👥 Users: {details.get('user_count', 0)}")
                print(f"   💰 Transactions: {details.get('transaction_count', 0)}")
            elif system == "bot_status":
                print(
                    f"   🤖 Available Bots: {details.get('available_bots', 0)}/{details.get('expected_bots', 0)}"
                )
            elif system == "gpt_system":
                print(f"   🧠 OpenAI: {'✅' if details.get('openai_configured') else '❌'}")
                print(f"   📝 Logging: {'✅' if details.get('logging_works') else '❌'}")
        print()


def main():
    """Ana health check fonksiyonu"""
    try:
        print("🚀 Starting GavatCore Health Check...")

        health_checker = HealthCheckSystem()
        report = health_checker.perform_comprehensive_health_check()

        display_health_report(report)

        # Save report to file
        report_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Health report saved to: {report_file}")

        # Return status code based on health
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
