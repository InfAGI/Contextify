import asyncio
import concurrent.futures


def run_async_in_thread(async_func, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If we are in a running loop, run in a separate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return executor.submit(asyncio.run, async_func(*args, **kwargs)).result()
    else:
        return asyncio.run(async_func(*args, **kwargs))
