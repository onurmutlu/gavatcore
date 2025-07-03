Cevap: Bot Sistemi Nasıl Çalışır?
run.py sadece API'leri ve Lara bot'unu başlatır. Tüm botları çalıştırmak için:
Manuel olarak:

   python -m services.telegram.bot_manager.bot_system

Import ederek:

   from services.telegram.bot_manager import bot_system
   bot_system.run_all_bots()

Eski launcher ile (hala çalışır):

   python launchers/gavatcore_ultimate_launcher.py


README.md artık tüm bu bilgileri içeriyor ve yeni yapıyı açıklıyor! 🚀