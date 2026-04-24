import threading
import time
import sys
from queue import Queue


class ScrollingLogHandler(threading.Thread):
    def __init__(self, log_queue: Queue):
        # Keep the log refresher from pinning the whole CLI process on
        # unexpected training exceptions.
        super().__init__(daemon=True)
        self.log_queue = log_queue
        self.print_queue = Queue()
        self.current_log = ""
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def run(self):
        while not self.stop_event.is_set():
            try:
                # 优先处理打印消息
                try:
                    message = self.print_queue.get_nowait()
                    with self.lock:
                        # 回到行首
                        sys.stdout.write('\r')
                        # 打印消息
                        print(message, end='', flush=True)
                        # 向后清除多余字符
                        sys.stdout.write('\x1b[K')
                        # 换行
                        print()
                        print(self.current_log, end='', flush=True)
                except:
                    pass

                # 处理滚动日志更新
                log_info = self.log_queue.get(timeout=0.1)
                with self.lock:
                    self.current_log = log_info
                    # 移动到行首
                    sys.stdout.write('\r')
                    print(self.current_log, end='', flush=True)
                    # 向后清除多余字符
                    sys.stdout.write('\x1b[K')
            except:
                continue

    def update_log(self, log_info: str):
        self.log_queue.put(log_info)

    def print_message(self, message: str):
        self.print_queue.put(message)

    def stop(self):
        self.stop_event.set()


# 测试代码
def test_scrolling_log_handler():
    log_queue = Queue()
    sleep = 0.1

    # 创建滚动日志处理器并启动
    scrolling_log_handler = ScrollingLogHandler(log_queue)
    scrolling_log_handler.start()

    # 模拟更新日志内容
    for i in range(1, 6):
        log_msg = f"Log message {i}"
        scrolling_log_handler.update_log(log_msg)
        time.sleep(sleep)

    # 打印一条额外的信息
    scrolling_log_handler.print_message("This is a special message! xxxxxx")

    # 模拟继续更新日志
    for i in range(6, 11):
        log_msg = f"Log message {i} qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
        scrolling_log_handler.update_log(log_msg)
        time.sleep(sleep)

    scrolling_log_handler.print_message("This is a special message2!")

    for i in range(11, 16):
        log_msg = f"Log message {i}"
        scrolling_log_handler.update_log(log_msg)
        time.sleep(0.1)

    # 停止滚动日志处理器
    scrolling_log_handler.stop()
    scrolling_log_handler.join()


if __name__ == "__main__":
    test_scrolling_log_handler()
