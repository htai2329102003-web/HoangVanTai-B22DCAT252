# Hướng dẫn build, publish và test — bec-vendor-phish

## 0. Phân biệt 2 phần phát hành

`dist/imodule.tar` cung cấp runtime config/instructions cho lệnh `imodule`; archive này
không chứa Dockerfiles. Docker images phải được build và publish riêng trên Docker Hub
trước khi người học khởi động lab. Đây là cơ chế IModule của Labtainers: gói archive
đưa các file lab vào thư mục labs, còn image layers được kéo từ Docker Hub.

## 1. Kiểm tra môi trường phát triển

Labtainers README hiện hành ghi rằng bản cài student thông thường không bao gồm đầy đủ
tool phát triển; chạy `update-designer.sh` từ `labtainer/trunk/setup_scripts` để cài phần
designer. Hãy sao lưu VM trước khi thay đổi môi trường.

```bash
cd ~/labtainer/trunk/setup_scripts
./update-designer.sh
```

Đường dẫn thực tế phụ thuộc nơi bạn giải nén Labtainers. Đảm bảo lab source nằm trong
`trunk/labs/bec-vendor-phish` khi dùng designer toolchain. Không chạy quy trình build
trên máy sinh viên; build/publish bằng VM phát triển riêng.

## 2. Kiểm tra config/source

```bash
python3 -m py_compile ~/labtainer/trunk/labs/bec-vendor-phish/mail-server/webmail.py
```

Dùng `checklab.py bec-vendor-phish` nếu công cụ này có trong bản designer bạn cài.
Kiểm tra cả hai Dockerfiles có sử dụng đúng base image được Labtainers cung cấp.

## 3. Build và publish Docker images

1. Đăng nhập Docker Hub từ VM phát triển: `docker login`.
2. Dùng quy trình build/publish đi kèm phiên bản Labtainers Designer đã cài để build
   image từ hai Dockerfiles trong `dockerfiles/`.
3. `REGISTRY_ID meme2003` trong `config/start.config` xác định namespace publish. Dùng `publish.py` của đúng phiên bản designer để build/tag/push; dự kiến repository name là `bec-vendor-phish.mail-server.student` và `bec-vendor-phish.victim-pc.student` trong namespace `meme2003`. Xác minh tên thực tế do tool in ra trước khi chia sẻ.
4. Xác nhận hai repository/image là public nếu muốn người học pull mà không cần đăng nhập.

Không tự suy đoán cú pháp của `build.py`/`publish.py`: chúng thay đổi theo bản designer.
Chạy `-h` trên tool trong đúng thư mục để lấy syntax đúng phiên bản. Không publish image
cho tới khi `checklab.py` và test nội bộ vượt qua.

## 4. Tạo IModule archive

Archive `dist/imodule.tar` được tạo từ runtime files của lab, đặt đường dẫn nội bộ bắt
đầu bằng `bec-vendor-phish/`, theo quy ước IModule. Không đưa Dockerfiles vào archive
runtime; các file đó chỉ cần ở bản source của maintainer.

Khi cập nhật runtime files, tạo lại archive từ thư mục source (thư mục cha của lab):

```bash
cd /path/to/source-parent
rm -f dist/imodule.tar
mkdir -p dist
# Chỉ đóng gói các file runtime đã thay đổi/mới cần cho người chạy lab.
tar -cf dist/imodule.tar \
  bec-vendor-phish/config/start.config \
  bec-vendor-phish/config/about.txt \
  bec-vendor-phish/instr_config/goals.config \
  bec-vendor-phish/instr_config/results.config \
  bec-vendor-phish/mail-server/.bashrc \
  bec-vendor-phish/mail-server/webmail.py \
  bec-vendor-phish/victim-pc/.bashrc \
  bec-vendor-phish/docs/lab_instructions.txt
```

Chú ý: lệnh mẫu giả định `dist/` nằm ngoài thư mục lab. Nếu dùng layout khác, điều chỉnh
đường dẫn output nhưng giữ nguyên prefix đường dẫn `bec-vendor-phish/` trong tar.

## 5. Test IModule trên VM sạch

1. Copy `dist/imodule.tar` vào một VM Labtainers khác, không phải VM phát triển.
2. Từ terminal `labtainer-student`, import archive qua file URL:

```bash
imodule file:///home/student/imodules/imodule.tar
```

Thay đường dẫn bằng vị trí tuyệt đối thật của `imodule.tar`. Sau khi import, xác minh lab xuất hiện rồi chạy:

```bash
labtainer bec-vendor-phish
```

Nếu `imodule` báo lỗi parse/config, dừng phát hành và kiểm tra log Labtainers. Nếu báo
không pull được image, xác minh Docker Hub repos/tags và `REGISTRY_ID meme2003` trong `start.config`.

## 6. Đưa archive lên mạng để người học import

Đặt `imodule.tar` ở GitHub Release hoặc một URL HTTPS tải file trực tiếp, công khai, không
cần cookie/đăng nhập. Khi có URL tải trực tiếp, người học dùng:

```bash
imodule https://example.org/path/to/imodule.tar
```

URL trên chỉ là ví dụ, chưa phải URL phát hành thực tế. Thử URL đó từ VM sạch trước khi
gửi lớp học. Khi cập nhật archive, người học có thể chạy `imodule -u` theo tài liệu
Labtainers để đồng bộ lại các IModule đã đăng ký.

## 7. Kiểm thử chức năng (manual checklist)

- [ ] Trang login mở được ở `http://172.25.0.2:5000` từ Firefox trong VM.
- [ ] Có đúng ba tài khoản demo và hai email nháp ở trạng thái ban đầu.
- [ ] CEO gửi thư, vendor gửi thư, hai thư đến inbox finance.
- [ ] Finance đọc từng thư; 2 marker `EMAIL_READ` xuất hiện.
- [ ] Finance click 2 landing; 2 marker `LINK_CLICK user=finance@company.vn` xuất hiện.
- [ ] POST submit khi chưa login chuyển về login; attacker account bị 403.
- [ ] Finance submit hai form; file `form_events.log` chỉ có marker, không chứa giá trị nhập.
- [ ] Thử nhập email nhận ngoài danh sách — app từ chối gửi.
- [ ] `checkwork` cho thấy 7 goal và `lab_complete` TRUE sau khi làm đủ.
- [ ] `labtainer bec-vendor-phish -r` tạo trạng thái lab mới theo cách xử lý của bản Labtainers đã cài.
- [ ] VM sạch khác đã import và chạy lab thành công.

## 8. Cấu hình mạng và lưu ý dữ liệu

Không cấu hình host port-forward/NAT cho cổng 5000. Flask lắng nghe trên mạng BEC_LAN tại `172.25.0.2:5000`; Firefox trên host VM truy cập `http://172.25.0.2:5000`. Nếu bản Labtainers của bạn cô lập route host-to-container, mở Firefox trong một container có X11 hoặc điều chỉnh bằng công cụ Designer chính thức; không mở cổng ra LAN/Internet. App không gửi email ra ngoài và không lưu
trường form vào database/log. Dữ liệu tài khoản hiển thị trong lab là credential demo cố
định, không phải tài khoản bảo mật.

## Nguồn Labtainers
- README / phiên bản: https://github.com/mfthomps/Labtainers
- IModules: https://nps.edu/web/c3o/imodules
- Lab Designer User Guide: https://nps.edu/documents/107523844/117289221/labdesigner.pdf/9ab93fc3-7cfe-48f4-987b-2efda8d99346
