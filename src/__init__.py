"""
邮件服务预制件模块导出

这个文件定义了预制件对外暴露的函数列表。
"""

from .main import send_email, send_bulk_email, send_email_with_template

__all__ = [
    "send_email",
    "send_bulk_email",
    "send_email_with_template",
]
