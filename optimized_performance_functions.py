def run_performance_benchmark():
    """Performans benchmark testini çalıştırır."""
    import time
    start = time.time()
    # Basit örnek: 1 milyon toplama işlemi
    total = 0
    for i in range(1000000):
        total += i
    end = time.time()
    return {
        "total": total,
        "elapsed": end - start
    } 