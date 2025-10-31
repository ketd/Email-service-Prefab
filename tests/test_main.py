"""
邮件服务预制件核心函数测试

测试所有暴露给 AI 的函数，确保它们按预期工作。
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.main import send_bulk_email, send_email


class TestSendEmail:
    """测试单封邮件发送功能"""

    @pytest.fixture
    def smtp_env(self, monkeypatch):
        """设置 SMTP 环境变量"""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")
        monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "test-password")
        monkeypatch.setenv("SMTP_USE_TLS", "true")

    def test_send_email_missing_config(self, monkeypatch):
        """测试缺少 SMTP 配置"""
        # 清除所有 SMTP 环境变量
        monkeypatch.delenv("SMTP_HOST", raising=False)
        monkeypatch.delenv("SMTP_PORT", raising=False)
        monkeypatch.delenv("SMTP_USERNAME", raising=False)
        monkeypatch.delenv("SMTP_PASSWORD", raising=False)

        result = send_email(
            to="user@example.com",
            subject="Test",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "MISSING_SMTP_CONFIG"
        assert "missing_configs" in result
        assert len(result["missing_configs"]) == 4

    def test_send_email_invalid_recipient(self, smtp_env):
        """测试无效的收件人"""
        result = send_email(
            to="",
            subject="Test",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_RECIPIENT"

    def test_send_email_invalid_subject(self, smtp_env):
        """测试无效的主题"""
        result = send_email(
            to="user@example.com",
            subject="",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_SUBJECT"

    def test_send_email_invalid_body(self, smtp_env):
        """测试无效的正文"""
        result = send_email(
            to="user@example.com",
            subject="Test",
            body=""
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_BODY"

    def test_send_email_invalid_body_type(self, smtp_env):
        """测试无效的正文类型"""
        result = send_email(
            to="user@example.com",
            subject="Test",
            body="Test body",
            body_type="markdown"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_BODY_TYPE"

    @patch('smtplib.SMTP')
    def test_send_email_success_plain(self, mock_smtp, smtp_env):
        """测试成功发送纯文本邮件"""
        # Mock SMTP 服务器
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email(
            to="user@example.com",
            subject="Test Email",
            body="This is a test email"
        )

        assert result["success"] is True
        assert result["message"] == "邮件发送成功"
        assert result["recipients"] == ["user@example.com"]
        assert mock_server.starttls.called
        assert mock_server.login.called
        assert mock_server.send_message.called
        assert mock_server.quit.called

    @patch('smtplib.SMTP')
    def test_send_email_success_html(self, mock_smtp, smtp_env):
        """测试成功发送 HTML 邮件"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email(
            to="user@example.com",
            subject="Test Email",
            body="<h1>Hello</h1><p>This is HTML</p>",
            body_type="html"
        )

        assert result["success"] is True
        assert result["message"] == "邮件发送成功"

    @patch('smtplib.SMTP')
    def test_send_email_with_cc_bcc(self, mock_smtp, smtp_env):
        """测试带抄送和密送的邮件"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email(
            to="user1@example.com",
            subject="Test Email",
            body="Test body",
            cc="user2@example.com,user3@example.com",
            bcc="user4@example.com"
        )

        assert result["success"] is True
        assert result["recipients"] == ["user1@example.com"]
        assert result["cc"] == ["user2@example.com", "user3@example.com"]
        assert result["bcc_count"] == 1

    @patch('smtplib.SMTP')
    def test_send_email_multiple_recipients(self, mock_smtp, smtp_env):
        """测试多个收件人"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email(
            to="user1@example.com,user2@example.com,user3@example.com",
            subject="Test Email",
            body="Test body"
        )

        assert result["success"] is True
        assert len(result["recipients"]) == 3
        assert "user1@example.com" in result["recipients"]
        assert "user2@example.com" in result["recipients"]
        assert "user3@example.com" in result["recipients"]

    @patch('smtplib.SMTP_SSL')
    def test_send_email_with_ssl(self, mock_smtp_ssl, monkeypatch):
        """测试使用 SSL 连接"""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "465")
        monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "test-password")
        monkeypatch.setenv("SMTP_USE_TLS", "false")

        mock_server = Mock()
        mock_smtp_ssl.return_value = mock_server

        result = send_email(
            to="user@example.com",
            subject="Test Email",
            body="Test body"
        )

        assert result["success"] is True
        assert mock_smtp_ssl.called
        # SSL 不需要 starttls
        assert not mock_server.starttls.called

    @patch('smtplib.SMTP')
    def test_send_email_auth_error(self, mock_smtp, smtp_env):
        """测试认证失败"""
        mock_server = Mock()
        mock_server.login.side_effect = Exception("Authentication failed")
        mock_smtp.return_value = mock_server

        result = send_email(
            to="user@example.com",
            subject="Test Email",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "SMTP_CONNECTION_ERROR"

    def test_send_email_invalid_port(self, monkeypatch):
        """测试无效的端口"""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "invalid")
        monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "test-password")

        result = send_email(
            to="user@example.com",
            subject="Test Email",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_PORT"


class TestSendBulkEmail:
    """测试批量邮件发送功能"""

    @pytest.fixture
    def smtp_env(self, monkeypatch):
        """设置 SMTP 环境变量"""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")
        monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "test-password")
        monkeypatch.setenv("SMTP_USE_TLS", "true")

    def test_send_bulk_email_invalid_recipients(self, smtp_env):
        """测试无效的收件人列表"""
        result = send_bulk_email(
            recipients=[],
            subject="Test",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_RECIPIENTS"

    def test_send_bulk_email_invalid_subject(self, smtp_env):
        """测试无效的主题"""
        result = send_bulk_email(
            recipients=["user@example.com"],
            subject="",
            body="Test body"
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_SUBJECT"

    def test_send_bulk_email_invalid_body(self, smtp_env):
        """测试无效的正文"""
        result = send_bulk_email(
            recipients=["user@example.com"],
            subject="Test",
            body=""
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_BODY"

    @patch('smtplib.SMTP')
    def test_send_bulk_email_success(self, mock_smtp, smtp_env):
        """测试批量发送成功"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        recipients = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com"
        ]

        result = send_bulk_email(
            recipients=recipients,
            subject="Bulk Test",
            body="This is a bulk test email"
        )

        assert result["success"] is True
        assert result["total"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0
        assert len(result["results"]) == 3

        for r in result["results"]:
            assert r["success"] is True
            assert r["recipient"] in recipients

    @patch('src.main.send_email')
    def test_send_bulk_email_partial_failure(self, mock_send_email, smtp_env):
        """测试部分失败的批量发送"""
        # 模拟第二封邮件发送失败
        def side_effect(to, subject, body, body_type):
            if to == "user2@example.com":
                return {
                    "success": False,
                    "error": "SMTP error",
                    "error_code": "SMTP_ERROR"
                }
            return {
                "success": True,
                "message": "邮件发送成功",
                "recipients": [to]
            }

        mock_send_email.side_effect = side_effect

        recipients = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com"
        ]

        result = send_bulk_email(
            recipients=recipients,
            subject="Bulk Test",
            body="This is a bulk test email"
        )

        assert result["success"] is False  # 有失败的邮件
        assert result["total"] == 3
        assert result["succeeded"] == 2
        assert result["failed"] == 1

        # 检查结果详情
        failed_results = [r for r in result["results"] if not r["success"]]
        assert len(failed_results) == 1
        assert failed_results[0]["recipient"] == "user2@example.com"

    @patch('smtplib.SMTP')
    def test_send_bulk_email_html(self, mock_smtp, smtp_env):
        """测试批量发送 HTML 邮件"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_bulk_email(
            recipients=["user1@example.com", "user2@example.com"],
            subject="HTML Test",
            body="<h1>Hello</h1>",
            body_type="html"
        )

        assert result["success"] is True
        assert result["total"] == 2
        assert result["succeeded"] == 2


class TestSendEmailWithTemplate:
    """测试模板邮件发送功能"""

    @pytest.fixture
    def smtp_env(self, monkeypatch):
        """设置 SMTP 环境变量"""
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")
        monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "test-password")
        monkeypatch.setenv("SMTP_USE_TLS", "true")

    def test_send_template_email_invalid_recipient(self, smtp_env):
        """测试无效的收件人"""
        from src.main import send_email_with_template

        result = send_email_with_template(
            to="",
            subject="Test",
            template_type="notification",
            template_data={"title": "Test"}
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_RECIPIENT"

    def test_send_template_email_invalid_template_type(self, smtp_env):
        """测试无效的模板类型"""
        from src.main import send_email_with_template

        result = send_email_with_template(
            to="user@example.com",
            subject="Test",
            template_type="invalid_template",
            template_data={"title": "Test"}
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_TEMPLATE_TYPE"

    def test_send_template_email_invalid_template_data(self, smtp_env):
        """测试无效的模板数据"""
        from src.main import send_email_with_template

        result = send_email_with_template(
            to="user@example.com",
            subject="Test",
            template_type="notification",
            template_data=None
        )

        assert result["success"] is False
        assert result["error_code"] == "INVALID_TEMPLATE_DATA"

    @patch('smtplib.SMTP')
    def test_send_notification_template(self, mock_smtp, smtp_env):
        """测试发送通知模板邮件"""
        from src.main import send_email_with_template

        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email_with_template(
            to="user@example.com",
            subject="系统通知",
            template_type="notification",
            template_data={
                "title": "重要通知",
                "heading": "您的账户已激活",
                "message": "恭喜您！",
                "button_text": "立即开始",
                "button_url": "https://example.com"
            }
        )

        assert result["success"] is True
        assert result["template_type"] == "notification"
        assert mock_server.send_message.called

    @patch('smtplib.SMTP')
    def test_send_welcome_template(self, mock_smtp, smtp_env):
        """测试发送欢迎模板邮件"""
        from src.main import send_email_with_template

        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email_with_template(
            to="user@example.com",
            subject="欢迎加入",
            template_type="welcome",
            template_data={
                "title": "欢迎加入我们",
                "message": "感谢您注册！",
                "features": ["功能1", "功能2", "功能3"],
                "button_text": "开始使用",
                "button_url": "https://example.com"
            }
        )

        assert result["success"] is True
        assert result["template_type"] == "welcome"

    @patch('smtplib.SMTP')
    def test_send_alert_template(self, mock_smtp, smtp_env):
        """测试发送警告模板邮件"""
        from src.main import send_email_with_template

        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email_with_template(
            to="user@example.com",
            subject="安全警告",
            template_type="alert",
            template_data={
                "title": "安全警告",
                "alert_title": "检测到异常登录",
                "message": "请立即检查您的账户安全",
                "details": {
                    "时间": "2024-01-01 10:00",
                    "IP地址": "192.168.1.1"
                },
                "button_text": "查看详情",
                "button_url": "https://example.com/security"
            }
        )

        assert result["success"] is True
        assert result["template_type"] == "alert"

    @patch('smtplib.SMTP')
    def test_send_report_template(self, mock_smtp, smtp_env):
        """测试发送报告模板邮件"""
        from src.main import send_email_with_template

        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email_with_template(
            to="user@example.com",
            subject="月度报告",
            template_type="report",
            template_data={
                "title": "2024年1月报告",
                "summary_title": "本月摘要",
                "message": "以下是本月的关键指标",
                "stats": [
                    {"label": "用户数", "value": "1,234"},
                    {"label": "收入", "value": "$56,789"},
                    {"label": "增长率", "value": "+15%"}
                ],
                "button_text": "查看完整报告",
                "button_url": "https://example.com/report"
            }
        )

        assert result["success"] is True
        assert result["template_type"] == "report"

    @patch('smtplib.SMTP')
    def test_send_template_with_cc_bcc(self, mock_smtp, smtp_env):
        """测试发送带抄送和密送的模板邮件"""
        from src.main import send_email_with_template

        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = send_email_with_template(
            to="user@example.com",
            subject="通知",
            template_type="notification",
            template_data={
                "title": "通知",
                "heading": "重要通知",
                "message": "这是一封重要通知"
            },
            cc="manager@example.com",
            bcc="admin@example.com"
        )

        assert result["success"] is True
        assert result["cc"] == ["manager@example.com"]
        assert result["bcc_count"] == 1
