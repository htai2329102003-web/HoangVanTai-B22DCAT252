"""
delay_logic.py
---------------
SINH VIEN HOAN THIEN HAM decide_destination() BEN DUOI (Buoc 2 trong bai lab).

Muc tieu: phan biet giua "sandbox/bot" (thuong truy cap ngay sau khi link
duoc tao) va "nguoi dung that" (truy cap sau khi da vuot qua mot khoang
thoi gian tre DELAY_THRESHOLD), de quyet dinh dieu huong sang trang
"decoy" (vo hai) hay trang "payload" (mo phong muc tieu, chi dung de
minh hoa trong lab - khong chua noi dung doc hai).
"""


def decide_destination(elapsed_seconds: float, user_agent: str, delay_threshold: int) -> str:
    """
    elapsed_seconds : so giay da troi qua ke tu lan truy cap DAU TIEN vao link nay
    user_agent      : chuoi User-Agent cua trinh duyet/bot dang truy cap
    delay_threshold : nguong thoi gian (giay) - chi sau moc nay moi tra ve "payload"

    Tra ve: "decoy" hoac "payload"
    """
    # TODO (Buoc 2):
    # 1) Neu elapsed_seconds < delay_threshold:
    #       -> tra ve "decoy"   (day co the la sandbox/bot quet som)
    # 2) Nguoc lai (da vuot nguong thoi gian):
    #       -> tra ve "payload" (coi nhu nguoi dung that)
    #
    # Goi y nang cao (khong bat buoc, lam them de hieu sau hon):
    #   - Ket hop kiem tra chuoi user_agent (vi du cac tu khoa thuong gap
    #     trong UA cua trinh quet tu dong) de tang do chinh xac phan biet.
    #
    # Xoa dong raise ben duoi sau khi ban da viet xong logic.
    raise NotImplementedError("Hay hoan thien ham decide_destination() theo huong dan o tren")
