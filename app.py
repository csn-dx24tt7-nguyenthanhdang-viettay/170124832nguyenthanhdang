import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib.pyplot as plt

class ImageEncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minh họa Kỹ thuật Mã hóa Ảnh - Đồ án Cơ sở ngành CNTT")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")

        self.original_image = None
        self.encrypted_image = None
        self.decrypted_image = None
        self.mask = None

        # Tiêu đề ứng dụng
        title_label = tk.Label(root, text="CHƯƠNG TRÌNH MINH HỌA KỸ THUẬT MÃ HÓA ẢNH", 
                               font=("Arial", 16, "bold"), bg="#003366", fg="white", pady=10)
        title_label.pack(fill=tk.X)

        # Khung điều khiển
        control_frame = tk.Frame(root, bg="#f0f2f5", pady=10)
        control_frame.pack(fill=tk.X, padx=20)

        btn_load = tk.Button(control_frame, text="1. Chọn Ảnh", font=("Arial", 11, "bold"), 
                             bg="#4CAF50", fg="white", padx=10, pady=5, command=self.load_image)
        btn_load.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Số vòng lặp Arnold:", bg="#f0f2f5", font=("Arial", 11)).pack(side=tk.LEFT, padx=(20, 5))
        self.entry_iter = tk.Entry(control_frame, font=("Arial", 11), width=5)
        self.entry_iter.insert(0, "3")
        self.entry_iter.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Khóa (Key):", bg="#f0f2f5", font=("Arial", 11)).pack(side=tk.LEFT, padx=(20, 5))
        self.entry_key = tk.Entry(control_frame, font=("Arial", 11), width=8)
        self.entry_key.insert(0, "12345")
        self.entry_key.pack(side=tk.LEFT, padx=5)

        btn_encrypt = tk.Button(control_frame, text="2. Mã hóa Ảnh", font=("Arial", 11, "bold"), 
                              bg="#2196F3", fg="white", padx=10, pady=5, command=self.encrypt_image)
        btn_encrypt.pack(side=tk.LEFT, padx=15)

        btn_decrypt = tk.Button(control_frame, text="3. Giải mã Khôi phục", font=("Arial", 11, "bold"), 
                              bg="#FF9800", fg="white", padx=10, pady=5, command=self.decrypt_image_func)
        btn_decrypt.pack(side=tk.LEFT, padx=5)

        # Khung hiển thị ảnh (3 ô: Ảnh gốc, Ảnh mã hóa, Ảnh giải mã)
        display_frame = tk.Frame(root, bg="#f0f2f5", pady=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Ô 1: Ảnh gốc
        frame1 = tk.LabelFrame(display_frame, text=" Ảnh Gốc ", font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#003366")
        frame1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_orig = tk.Label(frame1, bg="#e0e0e0")
        self.lbl_orig.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Ô 2: Ảnh mã hóa
        frame2 = tk.LabelFrame(display_frame, text=" Ảnh Đã Mã Hóa ", font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#003366")
        frame2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_enc = tk.Label(frame2, bg="#e0e0e0")
        self.lbl_enc.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Ô 3: Ảnh giải mã
        frame3 = tk.LabelFrame(display_frame, text=" Ảnh Khôi Phục (Giải Mã) ", font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#003366")
        frame3.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.lbl_dec = tk.Label(frame3, bg="#e0e0e0")
        self.lbl_dec.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Thanh thông tin kết quả / trạng thái
        self.status_bar = tk.Label(root, text="Trạng thái: Vui lòng chọn ảnh để bắt đầu thử nghiệm.", 
                                   font=("Arial", 10, "italic"), bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e2e8f0", padx=10, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh thử nghiệm", 
                                                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                messagebox.showerror("Lỗi", "Không thể đọc tệp ảnh!")
                return
            
            # Resize về 256x256 để thuận tiện thuật toán Arnold Cat Map
            img = cv2.resize(img, (256, 256))
            self.original_image = img
            self.encrypted_image = None
            self.decrypted_image = None

            self.display_img(self.original_image, self.lbl_orig)
            self.lbl_enc.config(image='')
            self.lbl_dec.config(image='')
            self.status_bar.config(text=f"Đã nạp ảnh thành công: {file_path} (Kích thước: 256x256)")

    def display_img(self, img_array, label_widget):
        img_pil = Image.fromarray(img_array)
        img_pil = img_pil.resize((220, 220), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        label_widget.config(image=img_tk)
        label_widget.image = img_tk

    def arnold_cat_transform(self, image, iterations, inverse=False):
        h, w = image.shape[:2]
        N = h
        res = image.copy()
        for _ in range(iterations):
            temp = np.zeros_like(res)
            for x in range(N):
                for y in range(N):
                    if not inverse:
                        nx = (2 * x + y) % N
                        ny = (x + y) % N
                    else:
                        nx = (x - y) % N
                        ny = (-x + 2 * y) % N
                    temp[nx, ny] = res[x, y]
            res = temp
        return res

    def encrypt_image(self):
        if self.original_image is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước khi mã hóa!")
            return
        
        try:
            iters = int(self.entry_iter.get())
            key = int(self.entry_key.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số vòng lặp và Khóa phải là số nguyên!")
            return

        # 1. Hoán vị Arnold Cat Map
        permuted = self.arnold_cat_transform(self.original_image, iters, inverse=False)

        # 2. Khuếch tán pixel bằng XOR với key
        np.random.seed(key)
        self.mask = np.random.randint(0, 256, permuted.shape, dtype=np.uint8)
        self.encrypted_image = cv2.bitwise_xor(permuted, self.mask)

        self.display_img(self.encrypted_image, self.lbl_enc)
        self.status_bar.config(text="Đã mã hóa ảnh thành công bằng hoán vị Arnold kết hợp khuếch tán XOR!")

    def decrypt_image_func(self):
        if self.encrypted_image is None or self.mask is None:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh mã hóa để giải mã!")
            return

        try:
            iters = int(self.entry_iter.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số vòng lặp không hợp lệ!")
            return

        # 1. Khử khuếch tán (Inverse Diffusion)
        recovered_permuted = cv2.bitwise_xor(self.encrypted_image, self.mask)

        # 2. Khử hoán vị Arnold (Inverse Arnold Cat Map)
        self.decrypted_image = self.arnold_cat_transform(recovered_permuted, iters, inverse=True)

        self.display_img(self.decrypted_image, self.lbl_dec)
        
        # Tính sai số PSNR để đánh giá
        mse = np.mean((self.original_image.astype(float) - self.decrypted_image.astype(float)) ** 2)
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))

        self.status_bar.config(text=f"Giải mã hoàn tất! Khôi phục ảnh gốc thành công (MSE: {mse:.2f}, PSNR: {psnr:.2f} dB)")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEncryptionApp(root)
    root.mainloop()