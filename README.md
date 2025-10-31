# 📧 邮件服务预制件 (Email Service Prefab)

[![Build and Release](https://github.com/your-org/email-service-prefab/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/your-org/email-service-prefab/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/managed%20by-uv-F67909.svg)](https://github.com/astral-sh/uv)

> **基于 SMTP 协议的邮件发送服务，支持 HTML 内容、抄送、密送和附件。**

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [API 文档](#api-文档)
- [常见邮件服务商配置](#常见邮件服务商配置)
- [开发与测试](#开发与测试)
- [常见问题](#常见问题)

## 功能特性

- ✅ **SMTP 发送**: 支持标准 SMTP 协议
- 📝 **多种格式**: 支持纯文本和 HTML 邮件
- 🎨 **精美模板**: 4种预定义的响应式 HTML 模板（通知、欢迎、警告、报告）
- 📎 **附件支持**: 可添加多个附件文件
- 👥 **多收件人**: 支持抄送（CC）和密送（BCC）
- 🔒 **安全连接**: 支持 TLS/SSL 加密
- 🔐 **密钥管理**: 所有敏感信息通过环境变量管理
- 🚀 **批量发送**: 支持批量发送邮件功能
- 🧪 **完整测试**: 包含全面的单元测试（27个测试用例）

## 快速开始

### 1. 配置环境变量

在使用前，需要配置以下环境变量：

```bash
export SMTP_HOST="smtp.example.com"        # SMTP 服务器地址
export SMTP_PORT="587"                     # SMTP 端口（587 for TLS, 465 for SSL）
export SMTP_USERNAME="your@email.com"      # 邮箱地址
export SMTP_PASSWORD="your-password"       # 密码或授权码
export SMTP_USE_TLS="true"                 # 是否使用 TLS（true/false）
```

### 2. 发送第一封邮件

```python
from src.main import send_email

result = send_email(
    to="recipient@example.com",
    subject="测试邮件",
    body="这是一封测试邮件"
)

if result["success"]:
    print(f"邮件发送成功！收件人: {result['recipients']}")
else:
    print(f"发送失败: {result['error']}")
```

### 3. 发送 HTML 邮件

```python
html_content = """
<html>
  <body>
    <h1>欢迎使用邮件服务</h1>
    <p>这是一封 <strong>HTML 格式</strong>的邮件。</p>
  </body>
</html>
"""

result = send_email(
    to="recipient@example.com",
    subject="HTML 邮件示例",
    body=html_content,
    body_type="html"
)
```

## 配置说明

### 必需的环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SMTP_HOST` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `587` (TLS) 或 `465` (SSL) |
| `SMTP_USERNAME` | 邮箱地址 | `your@email.com` |
| `SMTP_PASSWORD` | 密码或授权码 | `your-app-password` |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SMTP_USE_TLS` | 是否使用 TLS | `true` |

> **注意**: 某些邮件服务商（如 Gmail、QQ 邮箱）需要使用**应用专用密码或授权码**，而不是账户登录密码。

## 使用示例

### 1. 发送带抄送和密送的邮件

```python
result = send_email(
    to="recipient1@example.com,recipient2@example.com",
    subject="通知",
    body="这是一封重要通知",
    cc="manager@example.com",
    bcc="admin@example.com"
)
```

### 2. 发送带附件的邮件

```python
result = send_email(
    to="recipient@example.com",
    subject="报告",
    body="请查收附件中的报告",
    attachments=[
        "/path/to/report.pdf",
        "/path/to/data.xlsx"
    ]
)

if result["success"]:
    print(f"已发送附件: {result['attachments']}")
```

### 3. 批量发送邮件

```python
from src.main import send_bulk_email

recipients = [
    "user1@example.com",
    "user2@example.com",
    "user3@example.com"
]

result = send_bulk_email(
    recipients=recipients,
    subject="通知",
    body="这是群发邮件的内容"
)

print(f"总数: {result['total']}")
print(f"成功: {result['succeeded']}")
print(f"失败: {result['failed']}")
```

### 4. 使用预定义模板发送美观邮件 ✨

使用精美的 HTML 模板让邮件更专业：

#### 4.1 通知模板（Notification）

```python
from src.main import send_email_with_template

result = send_email_with_template(
    to="user@example.com",
    subject="系统通知",
    template_type="notification",
    template_data={
        "title": "重要通知",
        "heading": "您的账户已激活",
        "message": "恭喜您！您的账户已成功激活，现在可以开始使用我们的服务了。",
        "button_text": "立即开始",
        "button_url": "https://example.com/dashboard"
    }
)
```

#### 4.2 欢迎模板（Welcome）

```python
result = send_email_with_template(
    to="newuser@example.com",
    subject="欢迎加入我们的平台！",
    template_type="welcome",
    template_data={
        "title": "欢迎加入",
        "message": "感谢您注册我们的服务！以下是您可以使用的功能：",
        "features": [
            "🚀 强大的工具和功能",
            "👥 实时团队协作",
            "🔒 企业级安全保护",
            "📊 详细的数据分析"
        ],
        "button_text": "开始探索",
        "button_url": "https://example.com/getting-started"
    }
)
```

#### 4.3 警告模板（Alert）

```python
result = send_email_with_template(
    to="admin@example.com",
    subject="安全警告",
    template_type="alert",
    template_data={
        "title": "安全警告",
        "alert_title": "检测到异常登录",
        "message": "我们在您的账户中检测到异常登录活动，请立即检查。",
        "details": {
            "时间": "2024-01-15 10:30:00",
            "IP地址": "192.168.1.100",
            "位置": "北京",
            "设备": "Chrome on Windows"
        },
        "button_text": "查看详情",
        "button_url": "https://example.com/security/login-history"
    }
)
```

#### 4.4 报告模板（Report）

```python
result = send_email_with_template(
    to="manager@example.com",
    subject="月度数据报告",
    template_type="report",
    template_data={
        "title": "2024年1月运营报告",
        "summary_title": "本月亮点",
        "message": "本月我们取得了显著的增长，以下是关键指标：",
        "stats": [
            {"label": "新增用户", "value": "1,234"},
            {"label": "总收入", "value": "$56,789"},
            {"label": "增长率", "value": "+15%"},
            {"label": "客户满意度", "value": "98%"}
        ],
        "button_text": "查看完整报告",
        "button_url": "https://example.com/reports/2024-01"
    }
)
```

**支持的模板类型：**
- `notification` - 通知模板（紫色渐变）
- `welcome` - 欢迎模板（绿色渐变）
- `alert` - 警告模板（粉红色渐变）
- `report` - 报告模板（蓝色渐变）

所有模板都是**响应式设计**，在手机和桌面设备上都能完美显示！

## API 文档

### `send_email()`

发送单封邮件。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `to` | string | ✅ | 收件人邮箱，多个地址用逗号分隔 |
| `subject` | string | ✅ | 邮件主题 |
| `body` | string | ✅ | 邮件正文 |
| `cc` | string | ❌ | 抄送地址，多个地址用逗号分隔 |
| `bcc` | string | ❌ | 密送地址，多个地址用逗号分隔 |
| `body_type` | string | ❌ | 正文类型，`plain` 或 `html`，默认 `plain` |
| `attachments` | list[string] | ❌ | 附件文件路径列表 |

**返回值：**

```python
{
    "success": true,
    "message": "邮件发送成功",
    "recipients": ["user@example.com"],
    "cc": ["cc@example.com"],      # 可选
    "bcc_count": 1,                # 可选
    "attachments": ["file.pdf"]    # 可选
}
```

**错误码：**

- `MISSING_SMTP_CONFIG`: 缺少必需的 SMTP 配置
- `INVALID_RECIPIENT`: 收件人地址无效
- `INVALID_SUBJECT`: 邮件主题无效
- `INVALID_BODY`: 邮件正文无效
- `INVALID_BODY_TYPE`: 正文类型无效
- `ATTACHMENT_NOT_FOUND`: 附件文件不存在
- `ATTACHMENT_ERROR`: 处理附件失败
- `INVALID_PORT`: SMTP 端口无效
- `SMTP_AUTH_ERROR`: SMTP 认证失败
- `SMTP_ERROR`: SMTP 错误
- `SMTP_CONNECTION_ERROR`: 连接 SMTP 服务器失败
- `UNEXPECTED_ERROR`: 未预期的错误

### `send_bulk_email()`

批量发送邮件，向多个收件人分别发送相同内容的邮件。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `recipients` | list[string] | ✅ | 收件人邮箱地址列表 |
| `subject` | string | ✅ | 邮件主题 |
| `body` | string | ✅ | 邮件正文 |
| `body_type` | string | ❌ | 正文类型，`plain` 或 `html`，默认 `plain` |

**返回值：**

```python
{
    "success": true,
    "total": 3,
    "succeeded": 3,
    "failed": 0,
    "results": [
        {
            "recipient": "user1@example.com",
            "success": true
        },
        {
            "recipient": "user2@example.com",
            "success": true
        },
        ...
    ]
}
```

### `send_email_with_template()`

使用预定义模板发送美观的 HTML 邮件。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `to` | string | ✅ | 收件人邮箱，多个地址用逗号分隔 |
| `subject` | string | ✅ | 邮件主题 |
| `template_type` | string | ✅ | 模板类型：`notification`, `welcome`, `alert`, `report` |
| `template_data` | dict | ✅ | 模板数据，详见下方说明 |
| `cc` | string | ❌ | 抄送地址，多个地址用逗号分隔 |
| `bcc` | string | ❌ | 密送地址，多个地址用逗号分隔 |
| `attachments` | list[string] | ❌ | 附件文件路径列表 |

**模板数据说明：**

**notification 模板：**
- `title` ✅ - 标题
- `heading` ✅ - 副标题
- `message` ✅ - 消息内容
- `button_text` ❌ - 按钮文字
- `button_url` ❌ - 按钮链接
- `extra_content` ❌ - 额外内容
- `footer` ❌ - 页脚文字

**welcome 模板：**
- `title` ✅ - 标题
- `message` ✅ - 欢迎消息
- `features` ❌ - 功能列表（数组）
- `button_text` ❌ - 按钮文字
- `button_url` ❌ - 按钮链接
- `extra_content` ❌ - 额外内容
- `footer` ❌ - 页脚文字

**alert 模板：**
- `title` ✅ - 标题
- `alert_title` ✅ - 警告标题
- `message` ✅ - 警告消息
- `details` ❌ - 详细信息（字典）
- `button_text` ❌ - 按钮文字
- `button_url` ❌ - 按钮链接
- `extra_content` ❌ - 额外内容
- `footer` ❌ - 页脚文字

**report 模板：**
- `title` ✅ - 标题
- `summary_title` ✅ - 摘要标题
- `message` ✅ - 报告内容
- `stats` ❌ - 统计数据（数组，每项包含 `label` 和 `value`）
- `button_text` ❌ - 按钮文字
- `button_url` ❌ - 按钮链接
- `extra_content` ❌ - 额外内容
- `footer` ❌ - 页脚文字

**返回值：**

```python
{
    "success": true,
    "message": "邮件发送成功",
    "recipients": ["user@example.com"],
    "template_type": "notification",  # 使用的模板类型
    "cc": ["cc@example.com"],         # 可选
    "bcc_count": 1,                   # 可选
    "attachments": ["file.pdf"]       # 可选
}
```

**错误码：**

除了 `send_email()` 的所有错误码外，还包括：
- `INVALID_TEMPLATE_TYPE`: 不支持的模板类型
- `INVALID_TEMPLATE_DATA`: 模板数据无效
- `MISSING_TEMPLATE_FIELD`: 缺少必需的模板字段

## 常见邮件服务商配置

### Gmail

```bash
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="your@gmail.com"
SMTP_PASSWORD="your-app-password"  # 需要生成应用专用密码
SMTP_USE_TLS="true"
```

**获取应用专用密码：**
1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 启用"两步验证"
3. 生成"应用专用密码"

### QQ 邮箱

```bash
SMTP_HOST="smtp.qq.com"
SMTP_PORT="587"
SMTP_USERNAME="your@qq.com"
SMTP_PASSWORD="authorization-code"  # 需要生成授权码
SMTP_USE_TLS="true"
```

**获取授权码：**
1. 登录 QQ 邮箱
2. 设置 → 账户
3. 开启 SMTP 服务，生成授权码

### 网易邮箱（163）

```bash
SMTP_HOST="smtp.163.com"
SMTP_PORT="465"
SMTP_USERNAME="your@163.com"
SMTP_PASSWORD="authorization-code"  # 需要生成授权码
SMTP_USE_TLS="false"  # 使用 SSL
```

### Outlook / Office 365

```bash
SMTP_HOST="smtp.office365.com"
SMTP_PORT="587"
SMTP_USERNAME="your@outlook.com"
SMTP_PASSWORD="your-password"
SMTP_USE_TLS="true"
```

### 自定义 SMTP 服务器

```bash
SMTP_HOST="mail.yourdomain.com"
SMTP_PORT="587"
SMTP_USERNAME="your@yourdomain.com"
SMTP_PASSWORD="your-password"
SMTP_USE_TLS="true"
```

## 开发与测试

### 安装开发依赖

```bash
# 安装 uv（如果尚未安装）
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
uv sync --dev
```

### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_main.py::TestSendEmail -v

# 查看测试覆盖率
uv run pytest tests/ --cov=src --cov-report=html
```

### 代码质量检查

```bash
# Flake8 代码风格检查
uv run flake8 src/ --max-line-length=120

# 验证 manifest 一致性
uv run python scripts/validate_manifest.py

# 一键运行所有验证
uv run python scripts/quick_start.py
```

### 安装 Git Hooks

安装 pre-commit hooks 后，每次提交代码前会自动运行质量检查：

```bash
uv run pre-commit install
```

## 常见问题

### Q: 发送邮件时提示认证失败？

**A:** 检查以下几点：
1. 确认 SMTP 用户名和密码是否正确
2. 某些邮件服务商需要使用**应用专用密码或授权码**，而不是账户登录密码
3. 检查邮箱是否开启了 SMTP 服务

### Q: 支持哪些邮件服务商？

**A:** 支持所有遵循标准 SMTP 协议的邮件服务商，包括但不限于：
- Gmail
- QQ 邮箱
- 网易邮箱（163、126）
- Outlook / Office 365
- 阿里云企业邮箱
- 自建 SMTP 服务器

### Q: TLS 和 SSL 有什么区别？

**A:**
- **TLS (端口 587)**: 先建立普通连接，再升级为加密连接（`SMTP_USE_TLS=true`）
- **SSL (端口 465)**: 直接建立加密连接（`SMTP_USE_TLS=false`）

大多数现代邮件服务商推荐使用 TLS（端口 587）。

### Q: 如何发送给多个收件人？

**A:** 有两种方式：
1. **单封邮件多个收件人**: 使用逗号分隔地址
   ```python
   send_email(to="user1@example.com,user2@example.com", ...)
   ```
2. **批量发送**: 每个收件人收到独立的邮件
   ```python
   send_bulk_email(recipients=["user1@example.com", "user2@example.com"], ...)
   ```

### Q: 可以发送多大的附件？

**A:** 附件大小限制取决于：
1. SMTP 服务器的限制（通常为 10-25 MB）
2. 收件人邮箱的限制

建议单封邮件的附件总大小不超过 10 MB。

### Q: 如何处理发送失败的邮件？

**A:** 查看返回结果中的 `error` 和 `error_code` 字段：

```python
result = send_email(...)
if not result["success"]:
    print(f"错误: {result['error']}")
    print(f"错误码: {result['error_code']}")
    
    # 根据错误码进行处理
    if result["error_code"] == "SMTP_AUTH_ERROR":
        print("请检查用户名和密码")
    elif result["error_code"] == "SMTP_CONNECTION_ERROR":
        print("请检查网络连接和 SMTP 服务器地址")
```

## 项目结构

```
email-service-prefab/
├── src/                          # 源代码
│   ├── __init__.py              # 模块导出
│   └── main.py                  # 核心邮件发送逻辑
├── tests/                       # 测试
│   └── test_main.py            # 单元测试
├── scripts/                     # 辅助脚本
│   ├── validate_manifest.py    # Manifest 验证
│   ├── version_bump.py         # 版本管理
│   └── quick_start.py          # 快速验证
├── prefab-manifest.json         # 函数元数据
├── pyproject.toml              # 项目配置
└── README.md                   # 文档（本文件）
```

## 贡献

欢迎提交 Issue 和 Pull Request！

在提交 PR 前，请确保：
- ✅ 所有测试通过
- ✅ 代码风格检查通过
- ✅ Manifest 验证通过
- ✅ 添加了相应的测试用例

## 许可证

[MIT License](LICENSE)

---

**📚 更多文档**: [AI 助手开发指南](AGENTS.md) | [贡献指南](CONTRIBUTING.md)
