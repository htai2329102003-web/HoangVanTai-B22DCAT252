#!/usr/bin/env python3
"""
webmail.py  |  mail-server : port 5000
BEC + Vendor Phishing Lab — Nền tảng Webmail mô phỏng

Truy cập từ Firefox trên VM: http://172.25.0.2:5000

Tài khoản:
  ceo@company.vn       / ceo123      (attacker — giả mạo CEO)
  vendor@abc-supply.vn / vendor123   (attacker — giả mạo nhà cung cấp)
  finance@company.vn   / finance123  (victim   — nhân viên kế toán)
"""
import sqlite3, os, re
from datetime import datetime
from markupsafe import Markup, escape
from flask import (Flask, render_template_string, request,
                   redirect, session, url_for, abort)

app = Flask(__name__)
# Key ephemeral cho lab cục bộ; không dùng cấu hình này cho production.
app.secret_key = os.environ.get('WEBMAIL_SECRET_KEY') or os.urandom(32)

HOME   = os.path.expanduser('~')
DB     = os.path.join(HOME, 'webmail.db')
WLOG   = os.path.join(HOME, 'webmail.log')
ELOG   = os.path.join(HOME, 'form_events.log')

# ─── Logging ────────────────────────────────────────────────
def log(path, msg):
    ts   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def wlog(msg): log(WLOG, msg)
def elog(msg): log(ELOG, msg)

# ─── Database ────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if os.path.exists(DB):
        return
    db = get_db()
    db.executescript("""
    CREATE TABLE users (
        email        TEXT PRIMARY KEY,
        password     TEXT NOT NULL,
        display_name TEXT NOT NULL,
        role         TEXT NOT NULL
    );
    CREATE TABLE emails (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        from_email TEXT NOT NULL,
        to_email   TEXT NOT NULL,
        subject    TEXT NOT NULL,
        body       TEXT NOT NULL,
        sent_at    TEXT NOT NULL,
        is_draft   INTEGER DEFAULT 0,
        is_read    INTEGER DEFAULT 0
    );
    """)

    now = datetime.now().strftime('%d/%m/%Y %H:%M')

    users = [
        ('ceo@company.vn',       'ceo123',
         'Nguyễn Văn Hùng (CEO)',       'attacker'),
        ('vendor@abc-supply.vn', 'vendor123',
         'ABC Supply Co.',               'attacker'),
        ('finance@company.vn',   'finance123',
         'Trần Thị Lan (Kế toán)',       'victim'),
    ]
    db.executemany(
        "INSERT INTO users VALUES (?,?,?,?)", users)

    CEO_BODY = """\
Anh/Chị phụ trách tài chính,

Do thương vụ đang trong giai đoạn bảo mật tuyệt đối, tôi yêu cầu \
anh/chị thực hiện chuyển khoản NGAY cho đối tác chiến lược theo thông \
tin bên dưới.

  Số tiền  : 450.000.000 VNĐ
  Hạn thực hiện : Trước 17:00 HÔM NAY

Vui lòng xác nhận và hoàn tất thủ tục tại:

  http://172.25.0.2:5000/confirm/ceo

QUAN TRỌNG: Không đề cập vụ này với bất kỳ ai trước khi hoàn tất. \
Tôi đang trong cuộc họp kín, không thể nghe máy.

Nguyễn Văn Hùng
CEO — VNOffice Corporation
"""

    VENDOR_BODY = """\
Kính gửi Phòng Kế toán — VNOffice,

Do thay đổi ngân hàng đối tác, ABC Supply Co. thông báo tài khoản \
nhận thanh toán MỚI có hiệu lực từ 01/08/2024.

Vui lòng cập nhật thông tin ngân hàng tại cổng nhà cung cấp của chúng tôi:

  http://172.25.0.2:5000/confirm/vendor

  Số dư còn nợ  : 125.000.000 VNĐ
  Hạn thanh toán: 15/08/2024

LƯU Ý: Thanh toán vào tài khoản cũ sẽ KHÔNG được xử lý và \
có thể gây trễ hạn hợp đồng.

Trân trọng,
Phòng Kế toán — ABC Supply Co.
accounts@abc-supply.vn  |  ĐT: 028-xxxx-xxxx
"""

    db.executemany(
        """INSERT INTO emails
           (from_email,to_email,subject,body,sent_at,is_draft,is_read)
           VALUES (?,?,?,?,?,?,?)""",
        [
            ('ceo@company.vn', 'finance@company.vn',
             '[KHẨN] Chuyển khoản cho đối tác chiến lược — KHÔNG TIẾT LỘ',
             CEO_BODY, now, 1, 0),
            ('vendor@abc-supply.vn', 'finance@company.vn',
             '[HÓA ĐƠN T8/2024] Cập nhật tài khoản ngân hàng nhà cung cấp',
             VENDOR_BODY, now, 1, 0),
        ]
    )
    db.commit()
    db.close()
    print('[webmail] Database khởi tạo xong.', flush=True)

# ─── Auth helpers ────────────────────────────────────────────
def current_user():
    return session.get('user')

def require_login():
    if not current_user():
        return redirect(url_for('login'))
    return None

def require_victim():
    """Các landing/submit chỉ được ghi nhận khi tài khoản kế toán đăng nhập."""
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if user.get('role') != 'victim' or user.get('email') != 'finance@company.vn':
        abort(403)
    return None

# ─── URL auto-linkify an toàn cho email mô phỏng ─────────────
# Chỉ biến hai đường dẫn landing cục bộ thành liên kết; phần còn lại escape HTML.
_LOCAL_LANDING_RE = re.compile(r'(http://172\.25\.0\.2:5000/confirm/(?:ceo|vendor)(?=$|[\s.,;)]))')
def linkify(text):
    escaped_text = str(escape(text))
    linked = _LOCAL_LANDING_RE.sub(
        r'<a href="\1" rel="noopener">\1</a>', escaped_text
    )
    return Markup(linked)

# ─── Routes ─────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pw    = request.form.get('password', '').strip()
        db    = get_db()
        user  = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, pw)).fetchone()
        db.close()
        if user:
            session.clear()
            # Do not place the password column in the signed client-side session.
            session['user'] = {
                'email': email,
                'display_name': user['display_name'],
                'role': user['role'],
            }
            wlog(f"LOGIN user={email}")
            return redirect(url_for('inbox'))
        error = 'Email hoặc mật khẩu không đúng.'
    return render_template_string(LOGIN_TMPL, error=error)

@app.route('/logout')
def logout():
    u = current_user()
    if u:
        wlog(f"LOGOUT user={u['email']}")
    session.clear()
    return redirect(url_for('login'))

@app.route('/inbox')
def inbox():
    r = require_login()
    if r: return r
    u  = current_user()
    db = get_db()
    rows = db.execute(
        "SELECT * FROM emails WHERE to_email=? AND is_draft=0 ORDER BY id DESC",
        (u['email'],)).fetchall()
    db.close()
    unread = sum(1 for e in rows if not e['is_read'])
    return render_template_string(INBOX_TMPL, emails=rows, user=u,
                                  folder='inbox', unread=unread)

@app.route('/drafts')
def drafts():
    r = require_login()
    if r: return r
    u  = current_user()
    db = get_db()
    rows = db.execute(
        "SELECT * FROM emails WHERE from_email=? AND is_draft=1 ORDER BY id DESC",
        (u['email'],)).fetchall()
    db.close()
    return render_template_string(INBOX_TMPL, emails=rows, user=u,
                                  folder='drafts', unread=0)

@app.route('/sent')
def sent():
    r = require_login()
    if r: return r
    u  = current_user()
    db = get_db()
    rows = db.execute(
        "SELECT * FROM emails WHERE from_email=? AND is_draft=0 ORDER BY id DESC",
        (u['email'],)).fetchall()
    db.close()
    return render_template_string(INBOX_TMPL, emails=rows, user=u,
                                  folder='sent', unread=0)

@app.route('/email/<int:eid>')
def read_email(eid):
    r = require_login()
    if r: return r
    u  = current_user()
    db = get_db()
    em = db.execute("SELECT * FROM emails WHERE id=?", (eid,)).fetchone()

    # Chỉ người nhận hoặc người gửi được đọc thư đã gửi; draft chỉ qua giao diện Drafts.
    if not em or em['is_draft'] or u['email'] not in (em['from_email'], em['to_email']):
        db.close()
        return redirect(url_for('inbox'))

    if em['to_email'] == u['email']:
        db.execute("UPDATE emails SET is_read=1 WHERE id=?", (eid,))
        db.commit()
        wlog(f"EMAIL_READ user={u['email']} from={em['from_email']} id={eid}")

    db.close()
    body_html = linkify(em['body'])
    return render_template_string(EMAIL_TMPL, email=em, user=u,
                                  body_html=body_html)

@app.route('/compose', methods=['GET'])
def compose():
    r = require_login()
    if r: return r
    u  = current_user()
    # Pre-fill từ draft nếu có tham số ?draft=id
    draft_id = request.args.get('draft')
    draft    = None
    if draft_id:
        db    = get_db()
        draft = db.execute(
            "SELECT * FROM emails WHERE id=? AND from_email=? AND is_draft=1",
            (draft_id, u['email'])).fetchone()
        db.close()
    return render_template_string(COMPOSE_TMPL, user=u, draft=draft, msg='')

@app.route('/send', methods=['POST'])
def send_email():
    r = require_login()
    if r: return r
    u       = current_user()
    to      = request.form.get('to', '').strip()
    subject = request.form.get('subject', '').strip()
    body    = request.form.get('body', '').strip()
    now     = datetime.now().strftime('%d/%m/%Y %H:%M')

    if not to or not subject or not body:
        draft = None
        return render_template_string(COMPOSE_TMPL, user=u, draft=draft,
                                      msg='Vui lòng điền đầy đủ thông tin.')

    # Mô phỏng không gửi email ra Internet: người nhận phải là tài khoản lab đã seed.
    db = get_db()
    recipient = db.execute("SELECT email FROM users WHERE email=?", (to,)).fetchone()
    if not recipient:
        db.close()
        return render_template_string(COMPOSE_TMPL, user=u, draft=None,
                                      msg='Lab chỉ cho phép gửi tới tài khoản nội bộ được định nghĩa sẵn.')

    # Nếu gửi từ draft, chỉ xoá draft do tài khoản hiện tại sở hữu.
    draft_id = request.form.get('draft_id')
    if draft_id:
        db.execute("DELETE FROM emails WHERE id=? AND from_email=? AND is_draft=1",
                   (draft_id, u['email']))

    db.execute(
        """INSERT INTO emails (from_email,to_email,subject,body,sent_at,is_draft,is_read)
           VALUES (?,?,?,?,?,0,0)""",
        (u['email'], to, subject, body, now))
    db.commit()
    db.close()

    # Không đưa subject/body vào log để tránh log injection hoặc lưu nội dung không cần thiết.
    wlog(f"EMAIL_SENT from={u['email']} to={to}")
    return render_template_string(COMPOSE_TMPL, user=u, draft=None,
                                  msg=f'✓ Email đã gửi thành công tới {to}')

# ─── Landing pages mô phỏng + logging chỉ ghi sự kiện ─────────
@app.route('/confirm/ceo')
def confirm_ceo():
    guard = require_victim()
    if guard is not None:
        return guard
    u = current_user()
    wlog(f"LINK_CLICK user={u['email']} type=ceo")
    return render_template_string(CEO_LANDING_TMPL)

@app.route('/confirm/vendor')
def confirm_vendor():
    guard = require_victim()
    if guard is not None:
        return guard
    u = current_user()
    wlog(f"LINK_CLICK user={u['email']} type=vendor")
    return render_template_string(VENDOR_LANDING_TMPL)

@app.route('/submit/ceo', methods=['POST'])
def submit_ceo():
    guard = require_victim()
    if guard is not None:
        return guard
    u = current_user()
    # Không đọc/ghi giá trị form. Chỉ lưu marker để checkwork chấm được.
    elog(f"FORM_SUBMIT type=ceo user={u['email']}")
    return render_template_string(SUCCESS_TMPL,
        msg="Đã ghi nhận thao tác trong bài lab.",
        sub="Đây là mô phỏng cục bộ. Giá trị đã nhập không được lưu hoặc ghi vào log.")

@app.route('/submit/vendor', methods=['POST'])
def submit_vendor():
    guard = require_victim()
    if guard is not None:
        return guard
    u = current_user()
    # Không đọc/ghi giá trị form. Chỉ lưu marker để checkwork chấm được.
    elog(f"FORM_SUBMIT type=vendor user={u['email']}")
    return render_template_string(SUCCESS_TMPL,
        msg="Đã ghi nhận thao tác trong bài lab.",
        sub="Đây là mô phỏng cục bộ. Giá trị đã nhập không được lưu hoặc ghi vào log.")

# ════════════════════════════════════════════════════════════
#  HTML TEMPLATES
# ════════════════════════════════════════════════════════════
_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f4ff;color:#111}
a{text-decoration:none;color:inherit}

/* ── Topbar ── */
.topbar{background:#1a56db;color:#fff;height:52px;display:flex;
  align-items:center;padding:0 20px;gap:16px;
  box-shadow:0 2px 6px rgba(0,0,0,.25)}
.topbar .logo{font-size:18px;font-weight:700;letter-spacing:.5px;flex:1}
.topbar .uname{font-size:13px;opacity:.85}
.topbar a.logout{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);
  color:#fff;padding:4px 12px;border-radius:4px;font-size:12px}

/* ── Layout ── */
.wrap{display:flex;height:calc(100vh - 52px)}
.sidebar{width:200px;background:#fff;border-right:1px solid #e2e8f0;
  padding:14px 0;flex-shrink:0;display:flex;flex-direction:column;gap:2px}
.compose-btn{display:block;margin:0 14px 14px;padding:9px 18px;
  background:#1a56db;color:#fff;border-radius:20px;font-size:13px;
  font-weight:700;text-align:center}
.compose-btn:hover{background:#1e40af}
.nav a{display:flex;align-items:center;gap:10px;padding:8px 20px;
  font-size:13px;color:#374151}
.nav a:hover{background:#f3f4f6}
.nav a.active{background:#dbeafe;color:#1a56db;font-weight:700}
.badge{background:#1a56db;color:#fff;border-radius:10px;
  padding:1px 7px;font-size:11px;margin-left:auto}
.main{flex:1;overflow-y:auto;background:#f8fafc}

/* ── Email list ── */
.list-header{padding:14px 20px;background:#fff;
  border-bottom:1px solid #e5e7eb;font-size:15px;font-weight:700}
table.elist{width:100%;border-collapse:collapse}
table.elist tr{border-bottom:1px solid #f0f0f0;cursor:pointer}
table.elist tr:hover{background:#f0f6ff}
table.elist tr.unread{background:#fff;font-weight:700}
table.elist td{padding:11px 16px;font-size:13px}
.col-from{width:200px;color:#111}
.col-subj{color:#333}
.col-date{width:110px;color:#9ca3af;font-size:12px;text-align:right}
.unread-dot{width:8px;height:8px;background:#1a56db;border-radius:50%;
  display:inline-block;margin-right:6px}
.draft-tag{background:#fef3c7;color:#92400e;font-size:11px;
  padding:1px 7px;border-radius:10px;margin-left:6px}
.empty{text-align:center;padding:60px;color:#9ca3af;font-size:14px}

/* ── Email detail ── */
.email-wrap{padding:24px 36px;max-width:800px}
.back-link{display:inline-flex;align-items:center;gap:6px;
  color:#6b7280;font-size:13px;margin-bottom:16px}
.back-link:hover{color:#111}
.email-subject{font-size:22px;font-weight:700;color:#111;margin-bottom:16px}
.email-meta{border-bottom:1px solid #e5e7eb;padding-bottom:14px;margin-bottom:20px}
.meta-row{font-size:13px;color:#6b7280;margin-bottom:4px}
.meta-row b{color:#374151}
.email-body{background:#fff;border:1px solid #e5e7eb;border-radius:8px;
  padding:24px;font-size:14px;line-height:1.9;white-space:pre-wrap;color:#1f2937}
.email-body a{color:#1a56db;text-decoration:underline}
.action-bar{display:flex;gap:10px;margin-top:16px}
.btn-send-this{padding:9px 22px;background:#1a56db;color:#fff;
  border:none;border-radius:6px;font-size:13px;cursor:pointer;font-weight:700}
.btn-send-this:hover{background:#1e40af}

/* ── Compose ── */
.compose-wrap{padding:24px 36px;max-width:720px}
.compose-wrap h2{font-size:17px;font-weight:700;margin-bottom:20px}
.field{margin-bottom:14px}
.field label{display:block;font-size:11px;font-weight:700;
  text-transform:uppercase;color:#6b7280;margin-bottom:4px}
.field input,.field textarea,.field select{
  width:100%;padding:9px 12px;border:1px solid #d1d5db;
  border-radius:6px;font-size:14px;font-family:inherit}
.field textarea{height:280px;resize:vertical;line-height:1.7}
.btn-submit{padding:10px 28px;background:#1a56db;color:#fff;
  border:none;border-radius:6px;font-size:14px;cursor:pointer;font-weight:700}
.btn-submit:hover{background:#1e40af}
.flash{padding:10px 14px;border-radius:6px;margin-bottom:16px;font-size:13px}
.flash.ok{background:#d1fae5;color:#065f46}
.flash.err{background:#fee2e2;color:#991b1b}
"""

_SIDEBAR = """
<div class="sidebar">
  <a class="compose-btn" href="/compose">✏ Soạn thư</a>
  <nav class="nav">
    <a href="/inbox"  class="{{ 'active' if folder=='inbox'  else '' }}">
      📥 Hộp thư đến
      {% if unread %}<span class="badge">{{ unread }}</span>{% endif %}
    </a>
    <a href="/drafts" class="{{ 'active' if folder=='drafts' else '' }}">📄 Thư nháp</a>
    <a href="/sent"   class="{{ 'active' if folder=='sent'   else '' }}">📤 Đã gửi</a>
  </nav>
</div>
"""

LOGIN_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>VNOffice Mail — Đăng nhập</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;
  background:linear-gradient(135deg,#1a56db 0%,#0e2a6e 100%);
  min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#fff;border-radius:12px;padding:40px;width:380px;
  box-shadow:0 8px 32px rgba(0,0,0,.2)}
.logo{text-align:center;margin-bottom:28px}
.logo-icon{font-size:40px}
.logo-name{font-size:24px;font-weight:800;color:#1a56db;margin-top:6px}
.logo-sub{font-size:12px;color:#9ca3af;margin-top:2px}
label{display:block;font-size:11px;font-weight:700;
  text-transform:uppercase;color:#6b7280;margin-bottom:4px}
input{width:100%;padding:10px 12px;border:1px solid #d1d5db;
  border-radius:6px;font-size:14px;margin-bottom:14px}
input:focus{outline:none;border-color:#1a56db;
  box-shadow:0 0 0 2px rgba(26,86,219,.15)}
.btn{width:100%;padding:11px;background:#1a56db;color:#fff;
  border:none;border-radius:6px;font-size:15px;font-weight:700;cursor:pointer}
.btn:hover{background:#1e40af}
.err{background:#fee2e2;color:#991b1b;padding:9px 12px;
  border-radius:6px;font-size:13px;margin-bottom:14px}
.hint{font-size:11px;color:#9ca3af;margin-top:16px;line-height:1.6}
</style></head><body>
<div class="card">
  <div class="logo">
    <div class="logo-icon">📧</div>
    <div class="logo-name">VNOffice Mail</div>
    <div class="logo-sub">Hệ thống email nội bộ doanh nghiệp</div>
  </div>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST">
    <label>Địa chỉ email</label>
    <input type="email" name="email" placeholder="ten@company.vn" required autofocus>
    <label>Mật khẩu</label>
    <input type="password" name="password" placeholder="••••••••" required>
    <button class="btn" type="submit">Đăng nhập</button>
  </form>
  <div class="hint">
    <b>Tài khoản demo:</b><br>
    ceo@company.vn / ceo123<br>
    vendor@abc-supply.vn / vendor123<br>
    finance@company.vn / finance123
  </div>
</div>
</body></html>"""

INBOX_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>VNOffice Mail</title>
<style>{{ css }}</style></head>
<body>
<div class="topbar">
  <span class="logo">📧 VNOffice Mail</span>
  <span class="uname">{{ user.display_name }}</span>
  <a class="logout" href="/logout">Đăng xuất</a>
</div>
<div class="wrap">
  """ + _SIDEBAR + """
  <div class="main">
    <div class="list-header">
      {% if folder=='inbox' %}📥 Hộp thư đến
      {% elif folder=='drafts' %}📄 Thư nháp
      {% else %}📤 Đã gửi{% endif %}
    </div>
    {% if emails %}
    <table class="elist">
      {% for e in emails %}
      <tr class="{{ 'unread' if (not e.is_read and folder=='inbox') else '' }}"
          onclick="location.href='/{% if folder=='drafts' %}compose?draft={{ e.id }}{% else %}email/{{ e.id }}{% endif %}'">
        <td class="col-from">
          {% if not e.is_read and folder=='inbox' %}<span class="unread-dot"></span>{% endif %}
          {% if folder=='drafts' or folder=='sent' %}{{ e.to_email }}{% else %}{{ e.from_email }}{% endif %}
        </td>
        <td class="col-subj">
          {{ e.subject }}
          {% if folder=='drafts' %}<span class="draft-tag">Nháp</span>{% endif %}
        </td>
        <td class="col-date">{{ e.sent_at }}</td>
      </tr>
      {% endfor %}
    </table>
    {% else %}
    <div class="empty">Không có thư nào.</div>
    {% endif %}
  </div>
</div>
</body></html>"""

EMAIL_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>{{ email.subject }} — VNOffice Mail</title>
<style>{{ css }}</style></head>
<body>
<div class="topbar">
  <span class="logo">📧 VNOffice Mail</span>
  <span class="uname">{{ user.display_name }}</span>
  <a class="logout" href="/logout">Đăng xuất</a>
</div>
<div class="wrap">
  """ + _SIDEBAR + """
  <div class="main">
    <div class="email-wrap">
      <a class="back-link" href="/inbox">← Quay lại hộp thư</a>
      <div class="email-subject">{{ email.subject }}</div>
      <div class="email-meta">
        <div class="meta-row"><b>Từ:</b> {{ email.from_email }}</div>
        <div class="meta-row"><b>Đến:</b> {{ email.to_email }}</div>
        <div class="meta-row"><b>Ngày:</b> {{ email.sent_at }}</div>
      </div>
      <div class="email-body">{{ body_html|safe }}</div>
    </div>
  </div>
</div>
</body></html>"""

COMPOSE_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Soạn thư — VNOffice Mail</title>
<style>{{ css }}</style></head>
<body>
<div class="topbar">
  <span class="logo">📧 VNOffice Mail</span>
  <span class="uname">{{ user.display_name }}</span>
  <a class="logout" href="/logout">Đăng xuất</a>
</div>
<div class="wrap">
  """ + _SIDEBAR + """
  <div class="main">
    <div class="compose-wrap">
      <h2>✏ {% if draft %}Gửi thư nháp{% else %}Soạn thư mới{% endif %}</h2>
      {% if msg %}
      <div class="flash {{ 'ok' if msg.startswith('✓') else 'err' }}">{{ msg }}</div>
      {% endif %}
      <form method="POST" action="/send">
        {% if draft %}<input type="hidden" name="draft_id" value="{{ draft.id }}">{% endif %}
        <div class="field">
          <label>Đến</label>
          <input name="to" type="email" value="{{ draft.to_email if draft else '' }}"
                 placeholder="nguoi@nhan.vn" required>
        </div>
        <div class="field">
          <label>Tiêu đề</label>
          <input name="subject" value="{{ draft.subject if draft else '' }}"
                 placeholder="Tiêu đề email" required>
        </div>
        <div class="field">
          <label>Nội dung</label>
          <textarea name="body" required>{{ draft.body if draft else '' }}</textarea>
        </div>
        <button class="btn-submit" type="submit">📤 Gửi email</button>
      </form>
    </div>
  </div>
</div>
</body></html>"""

# ── Phishing landing pages ───────────────────────────────────
_LANDING_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#f1f5f9}
.alert-bar{background:#dc2626;color:#fff;text-align:center;
  padding:8px;font-size:12px;font-weight:700}
.card{max-width:580px;margin:40px auto;background:#fff;
  border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,.12);overflow:hidden}
.card-header{background:#1e3a5f;color:#fff;padding:24px 32px}
.card-header h1{font-size:19px;font-weight:700}
.card-header p{font-size:12px;opacity:.75;margin-top:4px}
.card-body{padding:28px 32px}
.warn-box{background:#fef3c7;border-left:4px solid #f59e0b;
  padding:12px 16px;font-size:13px;color:#92400e;
  margin-bottom:22px;border-radius:0 6px 6px 0}
.field{margin-bottom:16px}
label{display:block;font-size:12px;font-weight:700;
  color:#374151;margin-bottom:5px;text-transform:uppercase}
input,select{width:100%;padding:10px 12px;border:1px solid #d1d5db;
  border-radius:6px;font-size:14px}
.submit{width:100%;padding:12px;background:#dc2626;color:#fff;
  border:none;border-radius:6px;font-size:15px;font-weight:700;
  cursor:pointer;margin-top:6px}
.submit:hover{background:#b91c1c}
.security{text-align:center;font-size:11px;color:#9ca3af;margin-top:14px}
"""

CEO_LANDING_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Xác nhận Lệnh Chuyển Khoản — Hệ thống Nội bộ</title>
<style>""" + _LANDING_CSS + """</style></head><body>
<div class="alert-bar">MÔ PHỎNG ĐÀO TẠO — CHỈ NHẬP DỮ LIỆU GIẢ</div>
<div class="alert-bar">⚠ PHÂN LOẠI: NỘI BỘ — BẢO MẬT CAO</div>
<div class="card">
  <div class="card-header">
    <h1>🏦 Xác nhận Lệnh Chuyển Khoản</h1>
    <p>Cổng phê duyệt tài chính nội bộ — VNOffice Treasury</p>
  </div>
  <div class="card-body">
    <div class="warn-box">
      ⚠ Lệnh chuyển khoản khẩn cấp theo chỉ đạo Ban Điều hành.
      Vui lòng xác nhận thông tin tài khoản thụ hưởng trước 17:00.
    </div>
    <form method="POST" action="/submit/ceo" autocomplete="off">
      <div class="field">
        <label>Số tài khoản thụ hưởng</label>
        <input name="bank_no" type="text" placeholder="VD: 0123456789" required>
      </div>
      <div class="field">
        <label>Ngân hàng</label>
        <select name="bank_name" required>
          <option value="">-- Chọn ngân hàng --</option>
          <option>Vietcombank</option><option>VietinBank</option>
          <option>BIDV</option><option>Agribank</option>
          <option>Techcombank</option><option>MB Bank</option>
          <option>ACB</option><option>VPBank</option>
          <option>Khác</option>
        </select>
      </div>
      <div class="field">
        <label>Số tiền (VNĐ)</label>
        <input name="amount" type="text" value="450,000,000" required>
      </div>
      <button class="submit" type="submit">✓ Xác nhận và Phê duyệt Chuyển khoản</button>
    </form>
    <p class="security">🔒 Kết nối bảo mật SSL 256-bit | VNOffice Internal System v4.2</p>
  </div>
</div>
</body></html>"""

VENDOR_LANDING_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Cập nhật Tài khoản Ngân hàng — Cổng Nhà Cung Cấp</title>
<style>""" + _LANDING_CSS + """</style></head><body>
<div class="alert-bar">MÔ PHỎNG ĐÀO TẠO — CHỈ NHẬP DỮ LIỆU GIẢ</div>
<div class="alert-bar">🔒 ABC Supply Co. — Supplier Portal</div>
<div class="card">
  <div class="card-header">
    <h1>🏢 Cập nhật Tài khoản Ngân hàng</h1>
    <p>Cổng quản lý thông tin nhà cung cấp — ABC Supply Co.</p>
  </div>
  <div class="card-body">
    <div class="warn-box">
      ⚠ Vui lòng cập nhật thông tin ngân hàng mới trước 15/08/2024.
      Thanh toán vào tài khoản cũ sẽ không được xử lý.
    </div>
    <form method="POST" action="/submit/vendor" autocomplete="off">
      <div class="field">
        <label>Tên công ty / đơn vị</label>
        <input name="company" type="text" placeholder="Tên doanh nghiệp" required>
      </div>
      <div class="field">
        <label>Số tài khoản ngân hàng MỚI</label>
        <input name="bank_no" type="text" placeholder="VD: 9876543210" required>
      </div>
      <div class="field">
        <label>Ngân hàng</label>
        <select name="bank_name" required>
          <option value="">-- Chọn ngân hàng --</option>
          <option>Vietcombank</option><option>VietinBank</option>
          <option>BIDV</option><option>Agribank</option>
          <option>Techcombank</option><option>MB Bank</option>
          <option>ACB</option><option>VPBank</option>
          <option>Khác</option>
        </select>
      </div>
      <div class="field">
        <label>Email liên hệ xác nhận</label>
        <input name="contact" type="email" placeholder="ke-toan@abc-supply.vn" required>
      </div>
      <button class="submit" type="submit">💾 Cập nhật Thông tin Ngân hàng</button>
    </form>
    <p class="security">🔒 Supplier Portal Security v2.1 | ABC Supply Co.</p>
  </div>
</div>
</body></html>"""

SUCCESS_TMPL = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8"><title>Xử lý thành công</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#f1f5f9;display:flex;
  align-items:center;justify-content:center;min-height:100vh}
.card{background:#fff;border-radius:10px;padding:48px;text-align:center;
  max-width:440px;box-shadow:0 4px 16px rgba(0,0,0,.1)}
.icon{font-size:56px;margin-bottom:16px}
h2{font-size:20px;color:#065f46;margin-bottom:10px}
p{font-size:14px;color:#6b7280;line-height:1.7}
.back{display:inline-block;margin-top:24px;padding:10px 24px;
  background:#1a56db;color:#fff;border-radius:6px;font-size:14px}
</style></head><body>
<div class="card">
  <div class="icon">✅</div>
  <h2>{{ msg }}</h2>
  <p>{{ sub }}</p>
  <a class="back" href="/">Quay về Webmail</a>
</div>
</body></html>"""

# ─── Context processor để inject CSS vào tất cả template ────
@app.context_processor
def inject_globals():
    return dict(css=_CSS, folder='inbox', unread=0)

# ─── Entrypoint ─────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print('[webmail] Khởi động tại http://0.0.0.0:5000', flush=True)
    print('[webmail] Truy cập từ Firefox trong VM: http://172.25.0.2:5000', flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
