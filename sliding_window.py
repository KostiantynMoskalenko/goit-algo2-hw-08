import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    dictionary = Dict[str, float]
    queue = deque()
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        for record in list(self.queue):
            if user_id in record:
                message_time = record.get(user_id)
                delta = current_time - message_time
                if delta > self.window_size:
                    self.queue.remove(record)

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        for record in list(self.queue):
            if user_id in record:
                message_time = record.get(user_id)
                delta = current_time - message_time
                if message_time != 0 and (delta < self.window_size):
                    return False
        return True

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            now = time.time()
            self.dictionary = {user_id: now}
            self.queue.append(self.dictionary)
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        for record in list(self.queue):
            if user_id in record:
                message_time = record.get(user_id)
                delta = 10 - (current_time - message_time)
                return delta
        else:
            return 0

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()