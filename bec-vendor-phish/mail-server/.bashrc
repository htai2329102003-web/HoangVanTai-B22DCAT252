# .bashrc — mail-server container (bec-vendor-phish)
# Tự động khởi động webmail khi terminal mở lần đầu

export PS1='\[\033[1;32m\][mail-server]\[\033[0m\] \w \$ '

# Khởi động webmail nếu chưa chạy
if ! pgrep -f '[w]ebmail.py' > /dev/null 2>&1; then
    nohup python3 ~/webmail.py > ~/webmail_stdout.log 2>&1 &
    sleep 1
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           WEBMAIL SERVER ĐÃ KHỞI ĐỘNG               ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║  URL    : http://172.25.0.2:5000                      ║"
    echo "║  Log    : ~/webmail.log  (hành vi người dùng)       ║"
    echo "║  Events : ~/form_events.log (chỉ marker nộp form)   ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "  Tài khoản:"
    echo "    ceo@company.vn       / ceo123      (attacker - CEO giả)"
    echo "    vendor@abc-supply.vn / vendor123   (attacker - Vendor giả)"
    echo "    finance@company.vn   / finance123  (victim - Kế toán)"
    echo ""
    echo "  (Lab chỉ ghi sự kiện; không lưu giá trị trong form.)"
    echo "  Theo dõi log theo thời gian thực:"
    echo "    tail -f ~/webmail.log"
    echo "    tail -f ~/form_events.log"
    echo ""
else
    echo "[mail-server] Webmail đang chạy tại http://172.25.0.2:5000"
fi
