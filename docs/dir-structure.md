gavatcore/
│
├── adminbot/
│   ├── commands.py                 # ✅✅❌ 
│   └── dispatcher.py               # ✅✅❌ 
│
├── core/
│   ├── analytics_logger.py         # ✅✅✅❌
│   ├── controller.py               # ✅✅✅
│   ├── error_tracker.py            # ✅✅✅
│   ├── gavat_client.py             # ✅✅✅
│   ├── license_checker.py          # ✅✅✅ 
│   ├── manual_session_setup.py     # ✅✅✅ 
│   ├── metrics_collector.py        # ✅✅✅
│   ├── onboarding_flow.py          # ✅✅✅
│   ├── profile_generator.py        # ✅✅✅
│   ├── profile_loader.py           # ✅✅✅
│   ├── session_manager.py          # ✅✅✅
│   └── session_watcher.py          # ✅✅✅
│
├── data/
│   ├── personas
│   │    ├── bot_gavatbaba.json     # ✅✅✅
│   │    ├── bot_geishaniz.json     # ✅✅✅
│   │    └── bot_yayincilara.json   # ✅✅✅
│   ├── banks.json                  # ✅✅✅
│   ├── group_spam_messages.json    # ✅✅✅ 
│   ├── licenses.json               # ✅✅✅
│   └── reply_messages.json         # ✅✅✅
│
├── gpt/
│   ├── flirt_agent.py              # ✅✅✅
│   ├── openai_utils.py             # ✅✅✅
│   ├── system_prompt_manager.py    # ✅✅✅   
│   └── user_agent.py               # ✅✅✅  
│
├── handlers/                        
│   ├── dm_handler.py               # ✅✅✅
│   ├── group_handler.py            # ✅✅✅
│   ├── inline_handler.py           # ✅✅✅
│   ├── onboarding_handler.py       # ✅✅✅
│   ├── session_handler.py          # ✅✅✅
│   └── user_commands.py            # ✅✅✅
│
├── logs/
│
├── sessions/                       
│
├── utils/
│   ├── dm_code_callbacks.py        # ✅✅✅
│   ├── file_utils.py               # ✅✅✅
│   ├── log_utils.py                # ✅✅✅
│   ├── payment_utils.py            # ✅✅✅
│   ├── scheduler_utils.py          # ✅✅✅
│   ├── security_utils.py           # ✅✅
│   ├── state_utils.py              # ✅✅
│   └── template_utils.py           # ✅✅
│
├── .env                            # ✅✅
├── .gitignore                      # ✅✅
├── CHANGELOG.md                    # ✅✅
├── config.py                       # ✅
├── dir-structure.md                # ✅✅
├── README.md                       # ✅✅
├── requirements.txt                # ✅✅
├── ROADMAP.md                      # ✅✅
├── run.py                          # ✅✅
└── TODO-bot-commands.md            # ✅




.
├── .env
├── README.md
├── adminbot/
│   ├── commands.py
│   └── dispatcher.py
├── config.py
├── core/
│   ├── controller.py
│   ├── gavat_client.py
│   ├── license_checker.py
│   ├── manual_session_setup.py
│   ├── onboarding_flow.py
│   ├── profile_generator.py
│   ├── profile_loader.py
│   └── session_manager.py
├── data/
│   ├── banks.json
│   ├── group_spam_messages.json
│   ├── licenses.json
│   └── personas/
│       ├── bot_gavatbaba.json
│       ├── bot_geishaniz.json
│       └── bot_yayincilara.json
├── dir-structure.md
├── gpt/
│   ├── flirt_agent.py
│   ├── openai_utils.py
│   ├── system_prompt_manager.py
│   └── user_agent.py
├── handlers/
│   ├── dm_handler.py
│   ├── group_handler.py
│   ├── inline_handler.py
│   ├── session_handler.py
│   └── user_commands.py
├── run.py
└── utils/
    ├── log_utils.py
    ├── payment_utils.py
    ├── scheduler_utils.py
    ├── state_utils.py
    └── template_utils.py

