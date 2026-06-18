import sentry_sdk
from sentry_sdk import capture_exception, capture_message, set_tag, set_user, push_scope
import logging
import os

# -------------------------------------------------------
# Инициализация SDK с использованием переменных окружения
# -------------------------------------------------------
SENTRY_DSN = os.environ.get("SENTRY_DSN", "http://e65de544436e3c53bc234892e1e8a847@192.168.100.2:9000/3")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Процент performance-трассировок
    traces_sample_rate=0.5,
    # Отправляем все ошибки (по умолчанию 1.0)
    sample_rate=1.0,
    # Окружение и версия релиза
    environment=os.environ.get("APP_ENV", "development"),
    release="demo-app@1.0.0",
    # Игнорируем безобидные исключения
    ignore_errors=[KeyboardInterrupt],
    # Максимальное количество breadcrumbs
    max_breadcrumbs=50,
    # Таймаут на отправку событий при аварийном завершении (сек)
    shutdown_timeout=2,
    # Хук before_send для модификации/отбрасывания событий
    before_send=lambda event, hint: event if event.get("level") != "debug" else None,
)

# -------------------------------------------------------
# Демонстрация различных способов отправки событий
# -------------------------------------------------------

# 1. Исключение с автоматическим захватом контекста
try:
    result = 1 / 0
except ZeroDivisionError as e:
    # Захватываем текущее исключение
    capture_exception(e)
    # Также можно использовать стандартный логгинг
    logging.error("Обнаружено деление на ноль", exc_info=True)

# 2. Сообщение с уровнем warning
capture_message("Начало выполнения сложной операции", level="info")

# 3. Обогащение глобального скоупа (теперь все события будут иметь этот тег)
set_tag("feature", "payment")
set_user({"id": "user_42", "email": "user@example.com"})

# 4. Локальный скоуп с дополнительными данными
with push_scope() as scope:
    scope.set_tag("order_id", "12345")
    scope.set_extra("order_amount", 999.99)
    scope.add_breadcrumb(
        message="Отправка запроса в платёжный шлюз",
        category="http",
        data={"url": "https://api.bank.com/v1/charge", "method": "POST"},
    )
    # Имитация ошибки
    try:
        raise ValueError("Недостаточно средств")
    except ValueError as exc:
        capture_exception(exc)

# 5. Группировка событий по кастомному ключу
with push_scope() as scope:
    scope.fingerprint = ["insufficient_funds_group"]
    capture_message("Ошибка оплаты: недостаточно средств", level="error")

# 6. Performance-трассировка (для демонстрации мониторинга производительности)
from sentry_sdk import start_transaction
with start_transaction(op="script", name="demo_script"):
    # Имитируем какую-то работу
    import time
    time.sleep(0.2)
    # Внутри транзакции можно добавлять дочерние спаны (spans), если требуется

print("События успешно отправлены в Sentry. Проверьте панель управления.")