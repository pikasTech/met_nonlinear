import logging

class SecondsFormatter(logging.Formatter):
    """自定义格式化器，将 relativeCreated (毫秒) 转换为秒数"""
    
    def format(self, record):
        # 将毫秒转换为秒
        record.relative_seconds = record.relativeCreated / 1000.0
        return super().format(record)
