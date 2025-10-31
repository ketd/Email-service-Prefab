"""
邮件服务预制件

使用 SMTP 协议发送邮件，支持多种配置和附件。
所有敏感信息（SMTP 配置）通过环境变量管理。

📖 完整开发指南请查看：AGENTS.md
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, Any


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    body_type: str = "plain"
) -> Dict[str, Any]:
    """
    发送邮件

    使用 SMTP 协议发送邮件，支持 HTML 内容、抄送、密送和附件。
    SMTP 配置通过环境变量提供，需要在平台上配置相应的 secrets。

    📁 v3.0 文件约定：
    - 附件自动从 data/inputs/attachments/ 目录读取
    - Gateway 会自动下载文件到该目录

    Args:
        to: 收件人邮箱地址，多个地址用逗号分隔
        subject: 邮件主题
        body: 邮件正文内容
        cc: 抄送地址，多个地址用逗号分隔（可选）
        bcc: 密送地址，多个地址用逗号分隔（可选）
        body_type: 邮件正文类型，"plain" 或 "html"，默认 "plain"

    Returns:
        包含发送结果的字典

    Examples:
        >>> send_email(
        ...     to="user@example.com",
        ...     subject="测试邮件",
        ...     body="这是一封测试邮件"
        ... )
        {'success': True, 'message': '邮件发送成功', 'recipients': ['user@example.com']}
    """
    # v3.0: 附件文件路径
    ATTACHMENTS_DIR = Path("data/inputs/attachments")
    try:
        # 获取 SMTP 配置（从环境变量）
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = os.environ.get('SMTP_PORT')
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        smtp_use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'

        # 验证必需的配置
        missing_configs = []
        if not smtp_host:
            missing_configs.append('SMTP_HOST')
        if not smtp_port:
            missing_configs.append('SMTP_PORT')
        if not smtp_username:
            missing_configs.append('SMTP_USERNAME')
        if not smtp_password:
            missing_configs.append('SMTP_PASSWORD')

        if missing_configs:
            return {
                "success": False,
                "error": f"缺少必需的 SMTP 配置: {', '.join(missing_configs)}",
                "error_code": "MISSING_SMTP_CONFIG",
                "missing_configs": missing_configs
            }

        # 验证参数
        if not to or not isinstance(to, str):
            return {
                "success": False,
                "error": "收件人地址 (to) 必须是非空字符串",
                "error_code": "INVALID_RECIPIENT"
            }

        if not subject or not isinstance(subject, str):
            return {
                "success": False,
                "error": "邮件主题 (subject) 必须是非空字符串",
                "error_code": "INVALID_SUBJECT"
            }

        if not body or not isinstance(body, str):
            return {
                "success": False,
                "error": "邮件正文 (body) 必须是非空字符串",
                "error_code": "INVALID_BODY"
            }

        if body_type not in ["plain", "html"]:
            return {
                "success": False,
                "error": "body_type 必须是 'plain' 或 'html'",
                "error_code": "INVALID_BODY_TYPE"
            }

        # 解析收件人地址
        to_addresses = [addr.strip() for addr in to.split(',')]
        cc_addresses = [addr.strip() for addr in cc.split(',')] if cc else []
        bcc_addresses = [addr.strip() for addr in bcc.split(',')] if bcc else []

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = cc

        # 添加邮件正文
        msg.attach(MIMEText(body, body_type, 'utf-8'))

        # v3.0: 添加附件（自动扫描 data/inputs/attachments/ 目录）
        if ATTACHMENTS_DIR.exists():
            attachment_files = list(ATTACHMENTS_DIR.glob("*"))
            # 过滤掉目录，只保留文件
            attachment_files = [f for f in attachment_files if f.is_file()]

            for file_path in attachment_files:
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={file_path.name}'
                        )
                        msg.attach(part)

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"处理附件失败 ({file_path.name}): {str(e)}",
                        "error_code": "ATTACHMENT_ERROR"
                    }

        # 连接 SMTP 服务器并发送邮件
        try:
            port = int(smtp_port)
        except ValueError:
            return {
                "success": False,
                "error": f"SMTP_PORT 必须是数字: {smtp_port}",
                "error_code": "INVALID_PORT"
            }

        # 所有收件人（包括抄送和密送）
        all_recipients = to_addresses + cc_addresses + bcc_addresses

        try:
            if smtp_use_tls:
                # 使用 TLS
                server = smtplib.SMTP(smtp_host, port)
                server.starttls()
            else:
                # 使用 SSL
                server = smtplib.SMTP_SSL(smtp_host, port)

            server.login(smtp_username, smtp_password)
            server.send_message(msg, from_addr=smtp_username, to_addrs=all_recipients)
            server.quit()

            return {
                "success": True,
                "message": "邮件发送成功",
                "recipients": to_addresses,
                "cc": cc_addresses if cc_addresses else None,
                "bcc_count": len(bcc_addresses) if bcc_addresses else 0
            }

        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "SMTP 认证失败，请检查用户名和密码",
                "error_code": "SMTP_AUTH_ERROR"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP 错误: {str(e)}",
                "error_code": "SMTP_ERROR"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"连接 SMTP 服务器失败: {str(e)}",
                "error_code": "SMTP_CONNECTION_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def send_bulk_email(
    recipients: List[str],
    subject: str,
    body: str,
    body_type: str = "plain"
) -> Dict[str, Any]:
    """
    批量发送邮件

    向多个收件人分别发送相同内容的邮件。
    每封邮件独立发送，失败的邮件不会影响其他邮件。

    Args:
        recipients: 收件人邮箱地址列表
        subject: 邮件主题
        body: 邮件正文内容
        body_type: 邮件正文类型，"plain" 或 "html"，默认 "plain"

    Returns:
        包含批量发送结果的字典

    Examples:
        >>> send_bulk_email(
        ...     recipients=["user1@example.com", "user2@example.com"],
        ...     subject="通知",
        ...     body="这是一封通知邮件"
        ... )
        {
            'success': True,
            'total': 2,
            'succeeded': 2,
            'failed': 0,
            'results': [...]
        }
    """
    try:
        # 验证参数
        if not recipients or not isinstance(recipients, list):
            return {
                "success": False,
                "error": "recipients 必须是非空列表",
                "error_code": "INVALID_RECIPIENTS"
            }

        if not subject or not isinstance(subject, str):
            return {
                "success": False,
                "error": "邮件主题 (subject) 必须是非空字符串",
                "error_code": "INVALID_SUBJECT"
            }

        if not body or not isinstance(body, str):
            return {
                "success": False,
                "error": "邮件正文 (body) 必须是非空字符串",
                "error_code": "INVALID_BODY"
            }

        # 逐个发送邮件
        results = []
        succeeded = 0
        failed = 0

        for recipient in recipients:
            result = send_email(
                to=recipient,
                subject=subject,
                body=body,
                body_type=body_type
            )

            if result["success"]:
                succeeded += 1
            else:
                failed += 1

            results.append({
                "recipient": recipient,
                "success": result["success"],
                "error": result.get("error"),
                "error_code": result.get("error_code")
            })

        return {
            "success": failed == 0,
            "total": len(recipients),
            "succeeded": succeeded,
            "failed": failed,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


# 预定义的 HTML 模板
EMAIL_TEMPLATES = {
    "notification": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;
               color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                   padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 30px; }}
        .content h2 {{ color: #667eea; margin-top: 0; }}
        .message {{ background: #f8f9fa; padding: 20px; border-left: 4px solid #667eea;
                    border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666;
                   font-size: 14px; border-top: 1px solid #e0e0e0; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white;
                   text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: 600; }}
        .button:hover {{ background: #5568d3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📢 {title}</h1>
        </div>
        <div class="content">
            <h2>{heading}</h2>
            <div class="message">
                {message}
            </div>
            {button_html}
            {extra_content}
        </div>
        <div class="footer">
            {footer}
        </div>
    </div>
</body>
</html>
""",
    "welcome": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;
               color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white;
                   padding: 40px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; font-weight: 600; }}
        .welcome-icon {{ font-size: 60px; margin-bottom: 10px; }}
        .content {{ padding: 30px; }}
        .welcome-message {{ font-size: 18px; margin: 20px 0; color: #555; }}
        .features {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .feature-item {{ margin: 10px 0; padding-left: 25px; position: relative; }}
        .feature-item:before {{ content: "✓"; position: absolute; left: 0; color: #43e97b;
                                font-weight: bold; }}
        .button {{ display: inline-block; padding: 15px 40px; background: #43e97b; color: white;
                   text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: 600;
                   font-size: 16px; }}
        .button:hover {{ background: #3bd66f; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666;
                   font-size: 14px; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="welcome-icon">🎉</div>
            <h1>{title}</h1>
        </div>
        <div class="content">
            <div class="welcome-message">
                {message}
            </div>
            {features_html}
            {button_html}
            {extra_content}
        </div>
        <div class="footer">
            {footer}
        </div>
    </div>
</body>
</html>
""",
    "alert": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;
               color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;
                   padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
        .alert-icon {{ font-size: 60px; margin-bottom: 10px; }}
        .content {{ padding: 30px; }}
        .alert-box {{ background: #fff3cd; border-left: 4px solid #f5576c; padding: 20px;
                      border-radius: 5px; margin: 20px 0; }}
        .alert-title {{ color: #f5576c; font-weight: 600; font-size: 18px; margin-bottom: 10px; }}
        .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #f5576c; color: white;
                   text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: 600; }}
        .button:hover {{ background: #e04656; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666;
                   font-size: 14px; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="alert-icon">⚠️</div>
            <h1>{title}</h1>
        </div>
        <div class="content">
            <div class="alert-box">
                <div class="alert-title">{alert_title}</div>
                <div>{message}</div>
            </div>
            {details_html}
            {button_html}
            {extra_content}
        </div>
        <div class="footer">
            {footer}
        </div>
    </div>
</body>
</html>
""",
    "report": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;
               color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 10px;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;
                   padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 30px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .summary-title {{ color: #4facfe; font-weight: 600; font-size: 18px; margin-bottom: 15px; }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }}
        .stat-card {{ flex: 1; min-width: 150px; background: white; border: 2px solid #e0e0e0;
                      border-radius: 5px; padding: 15px; text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: 600; color: #4facfe; }}
        .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #4facfe; color: white;
                   text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: 600; }}
        .button:hover {{ background: #3d9ee6; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666;
                   font-size: 14px; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {title}</h1>
        </div>
        <div class="content">
            <div class="summary">
                <div class="summary-title">{summary_title}</div>
                {message}
            </div>
            {stats_html}
            {button_html}
            {extra_content}
        </div>
        <div class="footer">
            {footer}
        </div>
    </div>
</body>
</html>
"""
}


def send_email_with_template(
    to: str,
    subject: str,
    template_type: str,
    template_data: Dict[str, Any],
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用预定义模板发送美观的 HTML 邮件

    提供多种精美的 HTML 模板，让邮件更加专业美观。
    支持的模板类型：notification（通知）、welcome（欢迎）、alert（警告）、report（报告）

    📁 v3.0 文件约定：
    - 附件自动从 data/inputs/attachments/ 目录读取
    - Gateway 会自动下载文件到该目录

    Args:
        to: 收件人邮箱地址，多个地址用逗号分隔
        subject: 邮件主题
        template_type: 模板类型，可选值：notification, welcome, alert, report
        template_data: 模板数据，根据不同模板类型需要提供不同的字段
        cc: 抄送地址，多个地址用逗号分隔（可选）
        bcc: 密送地址，多个地址用逗号分隔（可选）

    模板数据说明：

    notification 模板：
        - title: 标题（必需）
        - heading: 副标题（必需）
        - message: 消息内容（必需）
        - button_text: 按钮文字（可选）
        - button_url: 按钮链接（可选）
        - extra_content: 额外内容（可选）
        - footer: 页脚文字（可选，默认为通用页脚）

    welcome 模板：
        - title: 标题（必需）
        - message: 欢迎消息（必需）
        - features: 功能列表（可选，列表类型）
        - button_text: 按钮文字（可选）
        - button_url: 按钮链接（可选）
        - extra_content: 额外内容（可选）
        - footer: 页脚文字（可选）

    alert 模板：
        - title: 标题（必需）
        - alert_title: 警告标题（必需）
        - message: 警告消息（必需）
        - details: 详细信息（可选，字典类型）
        - button_text: 按钮文字（可选）
        - button_url: 按钮链接（可选）
        - extra_content: 额外内容（可选）
        - footer: 页脚文字（可选）

    report 模板：
        - title: 标题（必需）
        - summary_title: 摘要标题（必需）
        - message: 报告内容（必需）
        - stats: 统计数据（可选，列表类型，每项包含 label 和 value）
        - button_text: 按钮文字（可选）
        - button_url: 按钮链接（可选）
        - extra_content: 额外内容（可选）
        - footer: 页脚文字（可选）

    Returns:
        包含发送结果的字典

    Examples:
        >>> # 发送通知邮件
        >>> send_email_with_template(
        ...     to="user@example.com",
        ...     subject="系统通知",
        ...     template_type="notification",
        ...     template_data={
        ...         "title": "重要通知",
        ...         "heading": "您的账户已激活",
        ...         "message": "恭喜您！您的账户已成功激活，现在可以开始使用我们的服务了。",
        ...         "button_text": "立即开始",
        ...         "button_url": "https://example.com/dashboard"
        ...     }
        ... )

        >>> # 发送欢迎邮件
        >>> send_email_with_template(
        ...     to="newuser@example.com",
        ...     subject="欢迎加入！",
        ...     template_type="welcome",
        ...     template_data={
        ...         "title": "欢迎加入我们的平台",
        ...         "message": "感谢您注册我们的服务！",
        ...         "features": ["功能1：强大的工具", "功能2：实时协作", "功能3：安全可靠"],
        ...         "button_text": "开始使用",
        ...         "button_url": "https://example.com/start"
        ...     }
        ... )
    """
    try:
        # 验证参数
        if not to or not isinstance(to, str):
            return {
                "success": False,
                "error": "收件人地址 (to) 必须是非空字符串",
                "error_code": "INVALID_RECIPIENT"
            }

        if not subject or not isinstance(subject, str):
            return {
                "success": False,
                "error": "邮件主题 (subject) 必须是非空字符串",
                "error_code": "INVALID_SUBJECT"
            }

        if template_type not in EMAIL_TEMPLATES:
            return {
                "success": False,
                "error": f"不支持的模板类型: {template_type}。支持的类型：{', '.join(EMAIL_TEMPLATES.keys())}",
                "error_code": "INVALID_TEMPLATE_TYPE"
            }

        if not template_data or not isinstance(template_data, dict):
            return {
                "success": False,
                "error": "template_data 必须是非空字典",
                "error_code": "INVALID_TEMPLATE_DATA"
            }

        # 准备模板变量
        template_vars = {
            "title": template_data.get("title", ""),
            "heading": template_data.get("heading", ""),
            "message": template_data.get("message", ""),
            "alert_title": template_data.get("alert_title", "重要提示"),
            "summary_title": template_data.get("summary_title", "摘要"),
            "extra_content": template_data.get("extra_content", ""),
            "footer": template_data.get("footer", "此邮件由系统自动发送，请勿回复。")
        }

        # 处理按钮
        button_html = ""
        if template_data.get("button_text") and template_data.get("button_url"):
            button_html = f'<a href="{template_data["button_url"]}" class="button">{template_data["button_text"]}</a>'
        template_vars["button_html"] = button_html

        # 处理特定模板的特殊字段
        if template_type == "welcome" and template_data.get("features"):
            features = template_data["features"]
            features_html = '<div class="features">'
            for feature in features:
                features_html += f'<div class="feature-item">{feature}</div>'
            features_html += '</div>'
            template_vars["features_html"] = features_html
        else:
            template_vars["features_html"] = ""

        if template_type == "alert" and template_data.get("details"):
            details = template_data["details"]
            details_html = '<div class="details">'
            for key, value in details.items():
                details_html += f'<div><strong>{key}:</strong> {value}</div>'
            details_html += '</div>'
            template_vars["details_html"] = details_html
        else:
            template_vars["details_html"] = ""

        if template_type == "report" and template_data.get("stats"):
            stats = template_data["stats"]
            stats_html = '<div class="stats">'
            for stat in stats:
                stats_html += f'''
                <div class="stat-card">
                    <div class="stat-value">{stat.get("value", "N/A")}</div>
                    <div class="stat-label">{stat.get("label", "")}</div>
                </div>
                '''
            stats_html += '</div>'
            template_vars["stats_html"] = stats_html
        else:
            template_vars["stats_html"] = ""

        # 渲染模板
        html_body = EMAIL_TEMPLATES[template_type].format(**template_vars)

        # 使用 send_email 发送（附件会自动从 data/inputs/attachments/ 读取）
        result = send_email(
            to=to,
            subject=subject,
            body=html_body,
            body_type="html",
            cc=cc,
            bcc=bcc
        )

        # 添加模板信息到返回结果
        if result["success"]:
            result["template_type"] = template_type

        return result

    except KeyError as e:
        return {
            "success": False,
            "error": f"模板数据缺少必需字段: {str(e)}",
            "error_code": "MISSING_TEMPLATE_FIELD"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
