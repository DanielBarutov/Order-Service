import functools
import asyncio


def retry_on_error(max_retries: int = 3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"Ошибка при выполнении функции {func.__name__}: {e}")
                    await asyncio.sleep(1)

        return wrapper

    return decorator
