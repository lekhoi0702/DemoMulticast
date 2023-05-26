import socket
import struct
import tkinter as tk
from tkinter import messagebox
import threading
# Hàm gửi dữ liệu
def send_data():
    # Lấy địa chỉ multicast group, port, và dữ liệu từ giao diện người dùng
    group = group_entry.get()
    port = port_entry.get()
    data = data_entry.get()

    try:
        # Kiểm tra địa chỉ multicast group và port
        socket.inet_aton(group)
        port = int(port)
    except (socket.error, ValueError):
        messagebox.showerror("Lỗi", "Địa chỉ multicast group hoặc port không hợp lệ!")
        return

    # Tạo socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)
    # Tắt chế độ lặp lại gói tin trên địa chỉ multicast group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

   # sock.setsockopt(socket.IPPROTO_UDP, socket.IP_MULTICAST_TTL, 2)

    # Gửi dữ liệu qua multicast
    sock.sendto(data.encode(), (group, port))


#  trạng thái nhận dữ liệu
receiving = False
# Khai báo biến global sock
sock = None
# Hàm nhận dữ liệu
def start_receiver():
    global receiving
    global sock
    # Kiểm tra có đang nhận DL k
    if receiving:
        messagebox.showinfo("Thông báo", "Đang trong quá trình nhận dữ liệu!")
        return
    # Lấy địa chỉ multicast group và port từ giao diện người dùng
    group = group_entry.get()
    port = port_entry.get()

    try:
        # Kiểm tra địa chỉ multicast group và port
        socket.inet_aton(group)
        port = int(port)
    except (socket.error, ValueError):
        messagebox.showerror("Lỗi", "Địa chỉ multicast group hoặc port không hợp lệ!")
        return

    # Tạo socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP)
    # Tắt chế độ lặp lại gói tin trên địa chỉ multicast group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind địa chỉ và port cho socket
    sock.bind(('', port))

    # Chuyển đổi địa chỉ multicast group sang dạng binary
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)

    # Tham gia vào multicast group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    #sock.setsockopt(socket.IPPROTO_UDP, socket.IP_ADD_MEMBERSHIP, mreq)
    # Cập nhật trạng thái của biến receiving
    receiving = True

    # Hàm nhận dữ liệu từ multicast group
    def receive_data():
        global receiving, sock
        while receiving:
            # Nhận dữ liệu từ multicast group
            # Kiểm tra giá trị của biến sock trước khi nhận dữ liệu
            if sock is not None:
                data, addr = sock.recvfrom(10240)
                #message_text.insert(tk.END, data.decode())
                message_text.insert(tk.END, "Nhận từ {}: {}\n".format(addr[0], data.decode()))

            else:
                # Nếu giá trị của sock là None, dừng vòng lặp để kết thúc luồng nhận dữ liệu
                receiving = False

    # Tạo một thread mới để chạy hàm receive_data()
    receiver_thread = threading.Thread(target=receive_data)
    # Đánh dấu thread là daemon, để khi chương trình chạy xong, thread này cũng sẽ tự động kết thúc
    receiver_thread.daemon = True
    # Bắt đầu chạy thread
    receiver_thread.start()


# Hàm dừng nhận dữ liệu
def stop_receive():
    global receiving, sock
    if receiving:
        receiving = False
        # Thông báo đã dừng nhận dữ liệu
        messagebox.showinfo("Thông báo", "Đã dừng nhận dữ liệu!")
        # Kiểm tra giá trị của biến sock trước khi đóng socket
        if sock is not None:
            sock.close()
# Tạo giao diện đồ họa
root = tk.Tk()
root.title("Multicast App")


group_label = tk.Label(root, text="Địa chỉ multicast group:")
group_label.pack()
group_entry = tk.Entry(root)
group_entry.pack()

port_label = tk.Label(root, text="Port:")
port_label.pack()
port_entry = tk.Entry(root)
port_entry.pack()

data_label = tk.Label(root, text="Nội dung dữ liệu:")
data_label.pack()
data_entry = tk.Entry(root)
data_entry.pack()

send_button = tk.Button(root, text="Gửi", command=send_data)
send_button.pack()

start_button = tk.Button(root, text="Bắt đầu nhận", command=start_receiver)
start_button.pack()

message_label = tk.Label(root, text="Dữ liệu nhận được:")
message_label.pack()
message_text = tk.Text(root)
message_text.pack()


stop_button = tk.Button(root, text="Ngừng nhận", command=stop_receive)
stop_button.pack()

root.mainloop()

