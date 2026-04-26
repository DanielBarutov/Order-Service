import functools
import asyncio

import logging

logger = logging.getLogger(__name__)


def retry_on_error(max_retries: int = 3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        "Retry#: %s. Ошибка при retry в функции %s ::: %s",
                        _,
                        func.__name__,
                        e,
                    )
                    await asyncio.sleep(3)

        return wrapper

    return decorator
