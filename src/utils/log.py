"""
日志配置模块 (Log Configuration Module)

功能描述:
    本模块负责配置全局日志记录器，提供控制台输出（使用 rich 库美化）和文件记录功能。
    旨在为应用程序提供统一、格式规范的日志服务，便于开发调试和生产环境监控。

实现细节:
    1. 使用 Python 标准库 `logging` 作为基础日志框架。
    2. 引入 `rich.logging.RichHandler` 作为控制台处理器，提供带颜色和格式的高亮日志输出。
    3. 使用 `logging.FileHandler` 将日志写入指定文件，格式包含时间、文件名、行号、日志级别和消息。
    4. 设置全局日志级别为 INFO。

依赖关系:
    - Python 标准库: logging
    - 第三方库: rich (需安装 rich 库)

使用方法:
    在应用入口或需要使用日志的地方导入 `logger` 对象即可直接使用。
    >>> from src.utils.log import logger
    >>> logger.info("This is an info message")
    >>> logger.error("This is an error message")

因果约束:
    - 默认日志文件路径为 ".log/app.log"。
    - 模块加载时会自动创建日志目录，若创建失败可能会抛出 OSError。
    - 全局 logger 单例模式，多次调用 setup_logger 可能会导致 handler 重复添加。
"""

import logging
import os
from rich.logging import RichHandler


def setup_logger(log_file: str = ".log/app.log"):
    """
    配置并返回根日志记录器。

    功能:
        初始化根 logger，添加 RichHandler (控制台) 和 FileHandler (文件)。
        会自动创建日志文件所在的目录。

    参数:
        log_file (str): 日志文件的保存路径。默认为 ".log/app.log"。

    返回:
        logging.Logger: 配置好的根日志记录器实例。

    实现逻辑:
        1. 获取 root logger (`logging.getLogger()`)。
        2. 设置级别为 INFO。
        3. 检查并创建日志文件目录。
        4. 配置 RichHandler 用于控制台输出。
        5. 配置 FileHandler 用于文件记录，并设置详细的格式 (时间、文件名、行号、级别、消息)。
        6. 将 handlers 添加到 logger。
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    console_log = RichHandler(log_time_format="%Y-%m-%d %H:%M:%S")
    file_log = logging.FileHandler(filename=log_file, encoding="utf-8")
    file_log.setFormatter(
        logging.Formatter(
            "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
        )
    )

    logger.addHandler(console_log)
    logger.addHandler(file_log)

    return logger


logger = setup_logger()


if __name__ == "__main__":
    # Test cases to verify logger functionality
    logger.info("Logger initialized successfully.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Captured an exception:")
