class LaraConfig:
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

def get_lara_stats() -> dict:
    return {
        "total_messages": 100,
        "success_rate": 0.95,
        "average_response_time": 1.5
    } 