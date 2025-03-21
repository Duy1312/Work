

def explain_camera_parameters():
    """
    Hàm giải thích về các hệ số biến dạng D và cách đọc thông số camera
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Rectangle
    
    print("=== THÔNG TIN VỀ CÁC HỆ SỐ BIẾN DẠNG VÀ THÔNG SỐ CAMERA ===")
    
    # Hiển thị thông tin về các hệ số biến dạng
    print("\n1. CÁC HỆ SỐ BIẾN DẠNG (DISTORTION COEFFICIENTS):")
    print("---------------------------------------------------")
    print("Trong OpenCV, ma trận biến dạng D thường gồm 5 thông số: (k1, k2, p1, p2, k3)")
    print("- k1, k2, k3: Các hệ số biến dạng hướng tâm (radial distortion)")
    print("- p1, p2: Các hệ số biến dạng tiếp tuyến (tangential distortion)")
    
    # Thêm công thức toán học của biến dạng
    print("\nCông thức toán học của biến dạng hướng tâm:")
    print("x_distorted = x(1 + k1*r² + k2*r⁴ + k3*r⁶)")
    print("y_distorted = y(1 + k1*r² + k2*r⁴ + k3*r⁶)")
    print("Trong đó r là khoảng cách từ điểm đến tâm ảnh: r² = x² + y²")
    
    print("\nCông thức toán học của biến dạng tiếp tuyến:")
    print("x_distorted = x + [2*p1*x*y + p2*(r² + 2*x²)]")
    print("y_distorted = y + [p1*(r² + 2*y²) + 2*p2*x*y]")
    
    # Tạo hình minh họa về biến dạng hướng tâm
    plt.figure(figsize=(15, 5))
    
    # Hình 1: Biến dạng hướng tâm (Radial Distortion)
    plt.subplot(1, 3, 1)
    
    # Tạo lưới điểm ban đầu
    x = np.linspace(-1, 1, 11)
    y = np.linspace(-1, 1, 11)
    X, Y = np.meshgrid(x, y)
    
    # Vẽ lưới điểm không biến dạng
    plt.scatter(X, Y, color='blue', s=10, label='Không biến dạng')
    
    # Tạo biến dạng hướng tâm
    r = np.sqrt(X**2 + Y**2)
    k1 = 0.5  # Hệ số biến dạng dương (pincushion)
    X_distorted = X * (1 + k1 * r**2)
    Y_distorted = Y * (1 + k1 * r**2)
    
    # Vẽ lưới điểm biến dạng
    plt.scatter(X_distorted, Y_distorted, color='red', s=10, label='Biến dạng gối (k1 > 0)')
    
    # Tạo biến dạng hướng tâm ngược
    k1_neg = -0.5  # Hệ số biến dạng âm (barrel)
    X_barrel = X * (1 + k1_neg * r**2)
    Y_barrel = Y * (1 + k1_neg * r**2)
    
    # Vẽ lưới điểm biến dạng thùng
    plt.scatter(X_barrel, Y_barrel, color='green', s=10, label='Biến dạng thùng (k1 < 0)')
    
    plt.title('Biến dạng hướng tâm (Radial Distortion)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Hình 2: Biến dạng tiếp tuyến (Tangential Distortion)
    plt.subplot(1, 3, 2)
    
    # Vẽ lưới điểm không biến dạng
    plt.scatter(X, Y, color='blue', s=10, label='Không biến dạng')
    
    # Tạo biến dạng tiếp tuyến
    p1, p2 = 0.1, 0.1
    X_tan_dist = X + (2 * p1 * X * Y + p2 * (r**2 + 2 * X**2))
    Y_tan_dist = Y + (p1 * (r**2 + 2 * Y**2) + 2 * p2 * X * Y)
    
    # Vẽ lưới điểm biến dạng tiếp tuyến
    plt.scatter(X_tan_dist, Y_tan_dist, color='red', s=10, label='Biến dạng tiếp tuyến')
    
    plt.title('Biến dạng tiếp tuyến (Tangential Distortion)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Hình 3: Ví dụ thực tế từ ảnh bàn cờ bị biến dạng
    plt.subplot(1, 3, 3)
    
    # Tạo minh họa biến dạng trên ảnh
    fig = plt.gcf()
    ax = plt.gca()
    
    # Hình bàn cờ bị biến dạng
    ax.add_patch(Rectangle((0.1, 0.1), 0.8, 0.8, fill=False, color='black', linewidth=1))
    
    # Vẽ đường thẳng kỳ vọng
    plt.plot([0.1, 0.9], [0.1, 0.1], 'r-', linewidth=2, label='Đường thẳng kỳ vọng')
    plt.plot([0.1, 0.9], [0.9, 0.9], 'r-', linewidth=2)
    plt.plot([0.1, 0.1], [0.1, 0.9], 'r-', linewidth=2)
    plt.plot([0.9, 0.9], [0.1, 0.9], 'r-', linewidth=2)
    
    # Vẽ đường cong thực tế (biến dạng thùng)
    x = np.linspace(0.1, 0.9, 100)
    y_bottom = 0.1 - 0.05*np.sin(np.pi*(x-0.1)/(0.9-0.1))
    y_top = 0.9 + 0.05*np.sin(np.pi*(x-0.1)/(0.9-0.1))
    
    x_left = np.linspace(0.1, 0.9, 100)
    y_left = 0.1 + 0.8*x_left/0.8
    x_left = 0.1 - 0.05*np.sin(np.pi*(y_left-0.1)/(0.9-0.1))
    
    x_right = np.linspace(0.1, 0.9, 100)
    y_right = 0.1 + 0.8*x_right/0.8
    x_right = 0.9 + 0.05*np.sin(np.pi*(y_right-0.1)/(0.9-0.1))
    
    plt.plot(x, y_bottom, 'g-', linewidth=2, label='Đường cong thực tế')
    plt.plot(x, y_top, 'g-', linewidth=2)
    plt.plot(x_left, y_left, 'g-', linewidth=2)
    plt.plot(x_right, y_right, 'g-', linewidth=2)
    
    plt.title('Biến dạng bàn cờ thực tế')
    plt.legend(loc='lower right')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Giải thích về các thông số camera
    print("\n2. CÁCH ĐỌC THÔNG SỐ CAMERA:")
    print("-----------------------------")
    print("Các thông số thường thấy trên camera:")
    
    print("\na) Tiêu cự (Focal Length) - ví dụ: '16mm'")
    print("   - Là khoảng cách từ tâm quang học của ống kính đến mặt phẳng cảm biến")
    print("   - Tiêu cự càng lớn, góc nhìn càng hẹp (zoom xa)")
    print("   - Tiêu cự càng nhỏ, góc nhìn càng rộng (góc rộng)")
    print("   - Ảnh hưởng trực tiếp đến ma trận camera trong hiệu chỉnh")
    
    print("\nb) Khẩu độ (Aperture) - ví dụ: '1:2.4' hoặc 'f/2.4'")
    print("   - Tỷ lệ giữa tiêu cự và đường kính ống kính")
    print("   - f/2.4 nghĩa là đường kính ống kính = tiêu cự / 2.4")
    print("   - Số càng nhỏ, khẩu độ càng lớn, thu được nhiều ánh sáng hơn")
    print("   - Ảnh hưởng đến độ sáng và độ sâu trường ảnh")
    
    print("\nc) Kích thước cảm biến - ví dụ: '1.2\"' (1.2 inch)")
    print("   - Đường chéo của cảm biến, thường được tính bằng inch")
    print("   - Cảm biến càng lớn, chất lượng hình ảnh càng tốt (đặc biệt trong điều kiện ánh sáng yếu)")
    print("   - Các kích thước phổ biến: 1/4\", 1/3\", 1/2.3\", 1/1.7\", 1\", APS-C, Full-frame")
    
    print("\nd) Số lượng điểm ảnh - ví dụ: '20MP'")
    print("   - Số điểm ảnh trên cảm biến, thường được tính bằng megapixel (triệu điểm ảnh)")
    print("   - Ảnh hưởng đến độ phân giải của hình ảnh")
    
    # Thêm phần nội dung mới về QUY TRÌNH HIỆU CHỈNH CAMERA
    print("\n3. QUY TRÌNH HIỆU CHỈNH CAMERA (CAMERA CALIBRATION):")
    print("---------------------------------------------------")
    print("Mục tiêu: Tìm các thông số nội tại (intrinsic) và ngoại tại (extrinsic) của camera")
    print("  - Thông số nội tại: Ma trận camera (camera matrix)")
    print("  - Thông số ngoại tại: Vector quay (rotation) và dịch chuyển (translation)")
    print("  - Hệ số biến dạng: (k1, k2, p1, p2, k3)")
    
    print("\nQuy trình hiệu chỉnh:")
    print("1. Chụp nhiều ảnh của mẫu có cấu trúc đã biết (bàn cờ hoặc lưới tròn) ở các góc độ khác nhau")
    print("2. Tìm các góc (cho bàn cồ) hoặc tâm (cho lưói tròn) trong các ảnh")
    print("3. Tính ma trận camera và hệ số biến dạng từ các tọa độ này")
    print("4. Sử dụng để hiệu chỉnh ảnh bị biến dạng")
    
    print("\nCác thuật toán hiệu chỉnh ảnh:")
    print("A. Sử dụng cv.undistort() (đơn giản nhất)")
    print("   cv.undistort(img, mtx, dist, None, newcameramtx)")
    
    print("\nB. Sử dụng remapping (linh hoạt hơn)")
    print("   mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)")
    print("   dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)")
    
    print("\nĐánh giá kết quả hiệu chỉnh:")
    print("- Lỗi tái chiếu (Re-projection error): Là sự khác biệt giữa tọa độ tái chiếu và tọa độ thực")
    print("- Lỗi càng gần 0, kết quả hiệu chỉnh càng chính xác")
    print("- Công thức: error = cv.norm(imgpoints, projectedPoints, cv.NORM_L2)/len(projectedPoints)")
    
    # Mối quan hệ giữa thông số camera và thông số hiệu chỉnh
    print("\n4. MỐI QUAN HỆ GIỮA THÔNG SỐ CAMERA VÀ THÔNG SỐ HIỆU CHỈNH:")
    print("-------------------------------------------------------------")
    print("a) Ma trận camera (Camera Matrix) - K:")
    print("   [fx  0  cx]")
    print("   [ 0 fy  cy]")
    print("   [ 0  0   1]")
    print("   Trong đó:")
    print("   - fx, fy: Tiêu cự theo đơn vị pixel theo trục x, y")
    print("   - cx, cy: Tọa độ tâm quang học (điểm chính) theo pixel")
    
    print("\nb) Các hệ số biến dạng (Distortion Coefficients) - D:")
    print("   [k1, k2, p1, p2, k3, ...]")
    print("   Trong đó:")
    print("   - k1, k2, k3: Hệ số biến dạng hướng tâm")
    print("   - p1, p2: Hệ số biến dạng tiếp tuyến")
    
    print("\nc) Các vector quay và dịch chuyển (Rotation and Translation Vectors):")
    print("   - rvecs: Vector quay - mô tả hướng của camera")
    print("   - tvecs: Vector dịch chuyển - mô tả vị trí của camera")
    
    print("\nd) Mối liên hệ với thông số physical camera:")
    print("   - fx = F * sx (F: tiêu cự thật, sx: kích thước pixel theo x)")
    print("   - fy = F * sy (F: tiêu cự thật, sy: kích thước pixel theo y)")
    print("   - Góc nhìn rộng (wide-angle) thường có k1 < 0 (biến dạng thùng)")
    print("   - Góc nhìn hẹp (telephoto) thường có k1 > 0 (biến dạng gối)")
    
    # Tạo hình minh họa về mối quan hệ giữa các thông số
    plt.figure(figsize=(15, 5))
    
    # Minh họa tiêu cự
    plt.subplot(1, 3, 1)
    
    # Vẽ minh họa ống kính
    rect = Rectangle((0.3, 0.4), 0.4, 0.2, fill=True, color='gray')
    ax = plt.gca()
    ax.add_patch(rect)
    
    # Vẽ cảm biến
    sensor = Rectangle((0.8, 0.3), 0.02, 0.4, fill=True, color='blue')
    ax.add_patch(sensor)
    
    # Vẽ tiêu cự
    plt.arrow(0.5, 0.5, 0.3, 0, head_width=0.02, head_length=0.02, fc='red', ec='red')
    plt.text(0.65, 0.53, 'Tiêu cự (mm)', color='red', fontsize=12)
    
    # Thêm minh họa đường đi của ánh sáng
    plt.plot([0.1, 0.5, 0.8], [0.7, 0.5, 0.35], 'y--', alpha=0.7)
    plt.plot([0.1, 0.5, 0.8], [0.3, 0.5, 0.65], 'y--', alpha=0.7)
    
    plt.title('Tiêu cự (focal length)\nVí dụ: 16mm, 50mm, 200mm')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # Minh họa khẩu độ
    plt.subplot(1, 3, 2)
    
    # Vẽ ống kính với khẩu độ khác nhau
    circle_outer = plt.Circle((0.5, 0.5), 0.3, fill=False, color='black', linewidth=2)
    ax = plt.gca()
    ax.add_patch(circle_outer)
    
    # Khẩu độ lớn f/1.4
    circle_f14 = plt.Circle((0.5, 0.5), 0.25, fill=True, color='yellow', alpha=0.3)
    ax.add_patch(circle_f14)
    plt.text(0.5, 0.8, 'Khẩu độ lớn (f/1.4)', ha='center', fontsize=10)
    
    # Khẩu độ nhỏ f/16
    circle_f16 = plt.Circle((0.5, 0.5), 0.1, fill=True, color='orange', alpha=0.7)
    ax.add_patch(circle_f16)
    plt.text(0.5, 0.2, 'Khẩu độ nhỏ (f/16)', ha='center', fontsize=10)
    
    # Công thức khẩu độ
    plt.text(0.5, 0.35, 'f/N = tiêu cự / đường kính', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
    
    plt.title('Khẩu độ (aperture)\nVí dụ: f/1.4, f/2.8, f/16')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # Minh họa kích thước cảm biến
    plt.subplot(1, 3, 3)
    
    # Vẽ các loại cảm biến phổ biến
    sizes = [
        ('Full Frame\n36x24mm (1")', 0.9, 0.6, 'red'),
        ('APS-C\n23.6×15.7mm (2/3")', 0.65, 0.43, 'green'),
        ('1/1.7"\n7.6x5.7mm', 0.35, 0.23, 'blue'),
        ('1/2.3"\n6.17x4.55mm', 0.25, 0.18, 'purple')
    ]
    
    for name, w, h, color in sizes:
        sensor = Rectangle((0.5-w/2, 0.5-h/2), w, h, fill=False, edgecolor=color, linewidth=2)
        ax = plt.gca()
        ax.add_patch(sensor)
        
        # Chỉ thêm nhãn cho 2 cảm biến lớn nhất
        if w > 0.5:
            plt.text(0.5, 0.5-h/2-0.05, name, ha='center', color=color, fontsize=10)
    
    # Thêm đường chéo minh họa cách đo kích thước
    plt.arrow(0.5-0.9/2, 0.5-0.6/2, 0.9, 0.6, head_width=0.02, head_length=0.02, fc='black', ec='black', linestyle='--')
    plt.text(0.5+0.05, 0.5+0.05, 'Đường chéo', rotation=45, fontsize=9)
    
    plt.title('Kích thước cảm biến\nVí dụ: 1/2.3", 1", Full Frame')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Thêm minh họa về quy trình hiệu chỉnh camera
    plt.figure(figsize=(15, 10))
    
    # 1. Ảnh bàn cờ gốc
    plt.subplot(2, 3, 1)
    # Vẽ bàn cờ
    for i in range(7):
        for j in range(6):
            if (i + j) % 2 == 0:
                rect = Rectangle((i/7, j/6), 1/7, 1/6, fill=True, color='black')
                ax = plt.gca()
                ax.add_patch(rect)
    
    plt.title('1. Chụp ảnh bàn cờ\nở nhiều góc khác nhau')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 2. Phát hiện góc
    plt.subplot(2, 3, 2)
    # Vẽ bàn cờ
    for i in range(7):
        for j in range(6):
            if (i + j) % 2 == 0:
                rect = Rectangle((i/7, j/6), 1/7, 1/6, fill=True, color='black')
                ax = plt.gca()
                ax.add_patch(rect)
    
    # Vẽ các góc phát hiện được
    for i in range(1, 7):
        for j in range(1, 6):
            plt.plot(i/7, j/6, 'ro', markersize=5)
    
    plt.title('2. Phát hiện các góc bàn cờ\ncv.findChessboardCorners()')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 3. Tính toán ma trận camera
    plt.subplot(2, 3, 3)
    plt.text(0.5, 0.7, 'Ma trận camera K:', ha='center', fontsize=12)
    plt.text(0.5, 0.5, '[[fx  0  cx]\n [ 0 fy  cy]\n [ 0  0   1]]', ha='center', fontsize=12)
    
    plt.text(0.5, 0.3, 'Hệ số biến dạng D:', ha='center', fontsize=12)
    plt.text(0.5, 0.2, '[k1, k2, p1, p2, k3]', ha='center', fontsize=12)
    
    plt.title('3. Tính toán các tham số\ncv.calibrateCamera()')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 4. Ảnh bị biến dạng
    plt.subplot(2, 3, 4)
    # Vẽ lưới bị biến dạng
    x = np.linspace(0, 1, 11)
    y = np.linspace(0, 1, 11)
    X, Y = np.meshgrid(x, y)
    
    r = np.sqrt((X-0.5)**2 + (Y-0.5)**2)
    k1 = -0.5
    
    X_dist = X + (X-0.5) * k1 * r**2
    Y_dist = Y + (Y-0.5) * k1 * r**2
    
    for i in range(11):
        plt.plot(X_dist[i,:], Y_dist[i,:], 'b-', linewidth=1)
        plt.plot(X_dist[:,i], Y_dist[:,i], 'b-', linewidth=1)
    
    plt.title('4. Ảnh bị biến dạng\nCác đường thẳng bị cong')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 5. Hiệu chỉnh ảnh
    plt.subplot(2, 3, 5)
    # Vẽ lưới không bị biến dạng
    for i in range(11):
        plt.plot([0, 1], [i/10, i/10], 'g-', linewidth=1)
        plt.plot([i/10, i/10], [0, 1], 'g-', linewidth=1)
    
    plt.title('5. Hiệu chỉnh ảnh\ncv.undistort()')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 6. Đánh giá kết quả
    plt.subplot(2, 3, 6)
    plt.text(0.5, 0.7, 'Lỗi tái chiếu (Re-projection Error):', ha='center', fontsize=10)
    plt.text(0.5, 0.6, 'error = ||imgPoints - projectedPoints||', ha='center', fontsize=10)
    plt.text(0.5, 0.5, 'Lỗi thấp = Hiệu chỉnh chính xác', ha='center', fontsize=10)
    
    plt.text(0.5, 0.3, 'Ví dụ lỗi tốt: < 0.5 pixel', ha='center', fontsize=10, color='green')
    plt.text(0.5, 0.2, 'Ví dụ lỗi kém: > 1.0 pixel', ha='center', fontsize=10, color='red')
    
    plt.title('6. Đánh giá kết quả\nTính lỗi tái chiếu')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Hiển thị ma trận hiệu chỉnh đã tính
    try:
        mtx = np.load('hikrobot_camera_matrix.npy')
        dist = np.load('hikrobot_dist_coeffs.npy')
        
        print("\n5. THÔNG SỐ HIỆU CHỈNH ĐÃ TÍNH TOÁN CHO CAMERA HIỆN TẠI:")
        print("------------------------------------------------------------")
        print(f"Ma trận camera (Camera Matrix):")
        print(mtx)
        print(f"\nCác hệ số biến dạng (Distortion Coefficients):")
        print(dist)
        
        # Giải thích ý nghĩa của các giá trị
        fx, fy = mtx[0,0], mtx[1,1]
        cx, cy = mtx[0,2], mtx[1,2]
        
        print(f"\nTiêu cự theo pixel: fx = {fx:.2f}, fy = {fy:.2f}")
        print(f"Tâm quang học: cx = {cx:.2f}, cy = {cy:.2f}")
        
        if len(dist) >= 5:
            k1, k2, p1, p2, k3 = dist[:5]
            print(f"\nCác hệ số biến dạng hướng tâm: k1 = {k1:.6f}, k2 = {k2:.6f}, k3 = {k3:.6f}")
            print(f"Các hệ số biến dạng tiếp tuyến: p1 = {p1:.6f}, p2 = {p2:.6f}")
            
            # Phân tích loại biến dạng
            if k1 < 0:
                print("\nCamera có biến dạng thùng (barrel distortion) do k1 < 0")
                print("→ Thường thấy ở ống kính góc rộng, các đường thẳng bị cong ra phía ngoài")
            elif k1 > 0:
                print("\nCamera có biến dạng gối (pincushion distortion) do k1 > 0")
                print("→ Thường thấy ở ống kính tele, các đường thẳng bị cong vào trong")
            else:
                print("\nCamera có ít biến dạng hướng tâm")
                
            if abs(p1) > 0.001 or abs(p2) > 0.001:
                print("\nCamera có biến dạng tiếp tuyến đáng kể")
                print("→ Có thể do ống kính không lắp hoàn toàn song song với cảm biến")
            else:
                print("\nCamera có ít biến dạng tiếp tuyến")
    except:
        print("\n5. KHÔNG TÌM THẤY THÔNG SỐ HIỆU CHỈNH ĐÃ LƯU")
        print("Vui lòng chạy hiệu chỉnh camera trước khi xem thông số")

# Gọi hàm giải thích các thông số camera
explain_camera_parameters()

