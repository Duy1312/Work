import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QTabWidget, QComboBox, QCheckBox, QSlider, QSpinBox, 
                             QDoubleSpinBox, QGroupBox, QRadioButton, QScrollArea,
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QDialog,
                             QFormLayout, QSplitter)
from PyQt6.QtCore import Qt, QRect, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np
from pyzbar.pyzbar import decode, Decoded
from PIL import Image
import os
import datetime
import subprocess
import json
import serial  # Thêm thư viện pyserial
import time


class LabelChecker:
    """Class to handle label barcode checking functionality"""
    
    def __init__(self):
        self.last_image = None
    
    def verify_barcode(self, detected_code, expected_code):
        """Verify if detected barcode matches expected value"""
        if not detected_code:
            return False, "No barcode detected"
            
        if detected_code == expected_code:
            return True, "PASS"
        else:
            return False, f"FAIL - Mismatch"


class SerialTriggerWorker(QThread):
    finished = pyqtSignal(bool, str)
    status_update = pyqtSignal(str)

    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate

    def run(self):
        try:
            self.status_update.emit("Đang mở cổng COM...")

            with serial.Serial(self.port, self.baudrate, timeout=5) as ser:
                self.status_update.emit(f"Đã kết nối với {self.port} - đang gửi message 'TRIGGER'...")
                
                command = b"TRIGGER"
                ser.write(command)

                # Đọc phản hồi từ comp4
                response = ser.readline().decode().strip()
                self.finished.emit(True, f"Message 'TRIGGER' đã gửi thành công. Phản hồi: {response}")

        except serial.SerialTimeoutException:
            self.status_update.emit("Timeout khi kết nối serial!")
            self.finished.emit(False, "Kết nối serial timeout")
        except serial.SerialException as e:
            self.status_update.emit(f"Lỗi serial: {str(e)}")
            self.finished.emit(False, f"Lỗi serial: {str(e)}")
        except Exception as e:
            self.status_update.emit(f"Lỗi không xác định: {str(e)}")
            self.finished.emit(False, f"Lỗi không xác định: {str(e)}")


class LinePacking(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label_checker = LabelChecker()
        self.current_image_path = None
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
        # Cấu hình kết nối serial
        self.serial_port = "COM4"  # Đảm bảo kết nối với COM4
        self.serial_baudrate = 9600
        
        # Biến để theo dõi trạng thái hoạt động
        self.is_running = False
        self.original_pixmap = None  # Để lưu trữ ảnh gốc
        
        self.init_ui()  # Đổi tên từ initUI thành init_ui để tuân theo quy ước Python

        # Tạo timer nhưng chưa khởi động
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_preview)
        # Chỉ bắt đầu khi nhấn nút Start

    # Phương thức này cập nhật trạng thái khi worker gửi tín hiệu
    def update_trigger_status(self, message):
        """Cập nhật trạng thái trong quá trình gửi message 'TRIGGER'"""
        try:
            # Cập nhật giao diện với thông báo từ worker
            self.result_view.setText(f"Trạng thái message 'TRIGGER':\n{message}")
            self.statusBar().showMessage(message)
            QApplication.processEvents()  # Đảm bảo UI được cập nhật ngay lập tức
        except Exception as e:
            print(f"Error updating UI with trigger status: {str(e)}")
            self.result_view.setText(f"Lỗi khi cập nhật trạng thái: {str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")

    def handle_trigger_result(self, success, message):
        """Xử lý kết quả gửi message 'TRIGGER'"""
        try:
            if success:
                self.result_view.setText(f"Message 'TRIGGER' đã gửi thành công!\n{message}")
                self.result_view.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.result_view.setText(f"Message 'TRIGGER' thất bại!\n{message}")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
        except Exception as e:
            print(f"Error in handling trigger result: {str(e)}")
            self.result_view.setText(f"Lỗi khi xử lý kết quả: {str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")

    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước cửa sổ"""
        super().resizeEvent(event)
        # Cập nhật hiển thị ảnh nếu có
        if hasattr(self, 'original_pixmap') and self.original_pixmap and not self.original_pixmap.isNull():
            self.update_image_displays()
    
    def update_image_displays(self):
        """Cập nhật hiển thị ảnh theo kích thước hiện tại của các label"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # Cập nhật camera view
            camera_pixmap = self.original_pixmap.scaled(
                self.camera_label.width(), 
                self.camera_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation  # Sử dụng biến đổi mượt hơn
            )
            self.camera_label.setPixmap(camera_pixmap)
            
            # Cập nhật image view
            image_pixmap = self.original_pixmap.scaled(
                self.image_view.width(), 
                self.image_view.height(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation  # Sử dụng biến đổi mượt hơn
            )
            self.image_view.setPixmap(image_pixmap)

    def init_ui(self):
        # Set window title and size
        self.setWindowTitle('UI Vision in Line Packing RU,OCDU,Acessory')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top section with S/N, Model, Version
        top_frame = QFrame()
        top_frame.setStyleSheet("border: 1px solid orange;")
        top_layout = QHBoxLayout(top_frame)
        
        # S/N input
        top_layout.addWidget(QLabel("S/N"))
        self.sn_input = QLineEdit()
        top_layout.addWidget(self.sn_input)
        
        # Model input
        top_layout.addWidget(QLabel("Model"))
        self.model_input = QLineEdit()
        top_layout.addWidget(self.model_input)
        
        # Version label - Thêm hiển thị tên công đoạn cụ thể
        self.process_name_label = QLabel("Kiểm tra Label v1.0")
        self.process_name_label.setStyleSheet("font-weight: bold; color: blue;")
        self.process_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(self.process_name_label)
        
        main_layout.addWidget(top_frame)
        
        # Auto/Setting buttons
        button_layout = QHBoxLayout()
        self.auto_btn = QPushButton("Auto")
        self.auto_btn.setFixedSize(120, 30)
        self.auto_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold;")
        self.setting_btn = QPushButton("Setting")
        self.setting_btn.setFixedSize(120, 30)
        self.setting_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold;")
        
        button_layout.addWidget(self.auto_btn)
        button_layout.addWidget(self.setting_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Create stacked widget for auto and settings views
        self.main_content = QWidget()
        main_content_layout = QHBoxLayout(self.main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel - Camera view
        self.camera_frame = QFrame()
        self.camera_frame.setStyleSheet("border: 1px solid orange;")
        camera_layout = QVBoxLayout(self.camera_frame)
        
        self.camera_label = QLabel("Camera View Online")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("color: blue; font-weight: bold; font-size: 14px;")
        self.camera_label.setMinimumSize(640, 480)
        camera_layout.addWidget(self.camera_label)
        
        main_content_layout.addWidget(self.camera_frame, 2)  # Takes 2/3 of width
        
        # Right panel - Controls and status
        self.controls_frame = QFrame()
        self.controls_frame.setStyleSheet("border: 1px solid orange;")
        
        # Tạo QSplitter dọc cho bên phải để có thể thay đổi kích thước các thành phần
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        # Đặt thuộc tính để ngăn các thành phần bị thu gọn hoàn toàn
        right_splitter.setChildrenCollapsible(False)
        
        # Status display - Cải thiện hiển thị trạng thái sản lượng
        status_frame = QFrame()
        status_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        status_layout = QVBoxLayout(status_frame)
        
        # Tiêu đề trạng thái
        status_title = QLabel("Hiển thị trạng thái sản lượng")
        status_title.setStyleSheet("font-weight: bold; color: blue;")
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        
        # Bảng thống kê chi tiết
        stats_grid = QGridLayout()
        stats_grid.addWidget(QLabel("OK:"), 0, 0)
        self.ok_count_label = QLabel("0")
        self.ok_count_label.setStyleSheet("font-weight: bold; color: green;")
        stats_grid.addWidget(self.ok_count_label, 0, 1)
        
        stats_grid.addWidget(QLabel("NG:"), 0, 2)
        self.ng_count_label = QLabel("0")
        self.ng_count_label.setStyleSheet("font-weight: bold; color: red;")
        stats_grid.addWidget(self.ng_count_label, 0, 3)
        
        stats_grid.addWidget(QLabel("Total:"), 1, 0)
        self.total_count_label = QLabel("0")
        self.total_count_label.setStyleSheet("font-weight: bold;")
        stats_grid.addWidget(self.total_count_label, 1, 1)
        
        stats_grid.addWidget(QLabel("Rate:"), 1, 2)
        self.rate_label = QLabel("0.0%")
        self.rate_label.setStyleSheet("font-weight: bold; color: blue;")
        stats_grid.addWidget(self.rate_label, 1, 3)
        
        status_layout.addLayout(stats_grid)
        # Đặt chiều cao tối thiểu lớn hơn để không bị thu nhỏ quá
        status_frame.setMinimumHeight(80)
        right_splitter.addWidget(status_frame)
        
        # Control buttons
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        button_frame = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #90EE90; font-weight: bold;")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color: #90EE90; font-weight: bold;")
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet("background-color: #4169E1; color: white; font-weight: bold;")
        self.recheck_btn = QPushButton("Recheck")
        self.recheck_btn.setStyleSheet("background-color: #4169E1; color: white; font-weight: bold;")
        
        button_frame.addWidget(self.start_btn)
        button_frame.addWidget(self.stop_btn)
        button_frame.addWidget(self.reset_btn)
        button_frame.addWidget(self.recheck_btn)
        
        buttons_layout.addLayout(button_frame)
        
        # Image and Result views
        views_layout = QHBoxLayout()
        
        # Left view - Camera image
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        image_layout = QVBoxLayout(self.image_frame)
        
        image_title = QLabel("View ảnh vừa chụp")
        image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_title.setStyleSheet("color: blue; font-weight: bold;")
        image_layout.addWidget(image_title)
        
        self.image_view = QLabel()
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setMinimumSize(300, 220)
        image_layout.addWidget(self.image_view)
        
        views_layout.addWidget(self.image_frame, 2)
        
        # Right view - Results
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        result_layout = QVBoxLayout(self.result_frame)
        
        result_title = QLabel("Trạng thái kết quả")
        result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_title.setStyleSheet("color: blue; font-weight: bold;")
        result_layout.addWidget(result_title)
        
        self.result_view = QLabel("NG/OK/Waiting...")
        self.result_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_view.setStyleSheet("font-size: 14px;")
        self.result_view.setWordWrap(True)
        self.result_view.setMinimumHeight(80)
        self.result_view.setMaximumHeight(80)
        result_layout.addWidget(self.result_view)
        
        views_layout.addWidget(self.result_frame, 1)
        
        buttons_layout.addLayout(views_layout)
        # Đặt chiều cao tối thiểu lớn hơn
        buttons_container.setMinimumHeight(200)
        right_splitter.addWidget(buttons_container)
        
        # Teaching display
        self.teaching_frame = QFrame()
        self.teaching_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        teaching_layout = QVBoxLayout(self.teaching_frame)
        
        teaching_title = QLabel("Hiển thị tool teaching")
        teaching_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        teaching_title.setStyleSheet("color: blue; font-weight: bold;")
        teaching_layout.addWidget(teaching_title)
        
        # Thêm các thành phần hiển thị thông tin teaching
        teaching_grid = QGridLayout()
        
        # Thêm thông tin về model hiện tại
        teaching_grid.addWidget(QLabel("Model:"), 0, 0)
        self.teaching_model_label = QLabel("Not set")
        teaching_grid.addWidget(self.teaching_model_label, 0, 1)
        
        # Thêm thông tin về khu vực kiểm tra
        teaching_grid.addWidget(QLabel("Vùng kiểm tra:"), 1, 0)
        self.teaching_area_label = QLabel("Label area")
        teaching_grid.addWidget(self.teaching_area_label, 1, 1)
        
        # Thêm thông tin về cài đặt vision
        teaching_grid.addWidget(QLabel("Cài đặt vision:"), 2, 0)
        self.teaching_settings_label = QLabel("Barcode Checking")
        teaching_grid.addWidget(self.teaching_settings_label, 2, 1)
        
        # Thêm hiển thị trạng thái teaching
        teaching_grid.addWidget(QLabel("Trạng thái:"), 3, 0)
        self.teaching_status_label = QLabel("Ready")
        self.teaching_status_label.setStyleSheet("color: green; font-weight: bold;")
        teaching_grid.addWidget(self.teaching_status_label, 3, 1)
        
        teaching_layout.addLayout(teaching_grid)
        
        # Thêm nút để mở cấu hình teaching
        self.open_teaching_btn = QPushButton("Mở cấu hình teaching")
        self.open_teaching_btn.clicked.connect(self.open_teaching_config)
        teaching_layout.addWidget(self.open_teaching_btn)
        
        # Đảm bảo luôn có kích thước tối thiểu hiển thị
        self.teaching_frame.setMinimumHeight(130)
        right_splitter.addWidget(self.teaching_frame)
        
        # Log process display
        self.log_frame = QFrame()
        self.log_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        log_layout = QVBoxLayout(self.log_frame)
        
        log_title = QLabel("Show log process theo thời gian")
        log_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_title.setStyleSheet("color: blue; font-weight: bold;")
        log_layout.addWidget(log_title)
        
        # Thêm chi tiết hơn về log
        log_detail = QLabel("SN input/Model/kết quả kiểm tra/Finish")
        log_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_layout.addWidget(log_detail)
        
        # Create log table
        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels(["Time", "S/N", "Model", "Result"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        log_layout.addWidget(self.log_table)
        
        # Đảm bảo luôn có kích thước tối thiểu hiển thị
        self.log_frame.setMinimumHeight(90)
        right_splitter.addWidget(self.log_frame)
        
        # Thêm nút khôi phục kích thước mặc định
        restore_sizes_btn = QPushButton("↺ Khôi phục kích thước mặc định")
        restore_sizes_btn.setStyleSheet("background-color: #FFD700; font-weight: bold;")
        restore_sizes_btn.clicked.connect(lambda: self.restore_default_splitter_sizes(right_splitter))
        
        # Thiết lập kích thước tương đối ban đầu cho các phần tử trong right_splitter
        right_splitter.setSizes([100, 300, 200, 200])
        
        # Tạo layout cho controls_frame để chứa right_splitter và nút khôi phục
        controls_layout = QVBoxLayout(self.controls_frame)
        controls_layout.addWidget(right_splitter)
        controls_layout.addWidget(restore_sizes_btn)
        
        main_content_layout.addWidget(self.controls_frame, 1)
        
        main_layout.addWidget(self.main_content)
        
        # Connect buttons
        self.auto_btn.clicked.connect(self.show_auto_view)
        self.setting_btn.clicked.connect(self.show_settings_view)
        self.start_btn.clicked.connect(self.start_inspection)
        self.stop_btn.clicked.connect(self.stop_inspection)
        self.reset_btn.clicked.connect(self.reset_system)
        self.recheck_btn.clicked.connect(self.recheck)

    def restore_default_splitter_sizes(self, splitter):
        """Khôi phục kích thước mặc định cho splitter"""
        splitter.setSizes([100, 300, 200, 200])

    def update_camera_preview(self):
        if not self.is_running:
            return  # Không cập nhật nếu chưa bắt đầu chạy
            
        result_folder = r"C:\Users\a\Desktop\Work\VisionCheckLabel\image\Result"
        
        # Kiểm tra xem thư mục kết quả có tồn tại không
        if os.path.exists(result_folder):
            # Lấy tất cả các tệp ảnh trong thư mục
            images = [f for f in os.listdir(result_folder) if f.endswith(('.jpg', '.jpeg', '.png', 'bmp'))]
            
            if images:
                # Chọn ảnh mới nhất từ danh sách ảnh
                image_path = os.path.join(result_folder, images[-1])  # Lấy ảnh mới nhất
                
                # Chỉ cập nhật nếu đây là ảnh mới
                if image_path != self.current_image_path:
                    if os.path.exists(image_path):
                        # Lưu đường dẫn ảnh hiện tại
                        self.current_image_path = image_path
                        
                        # Tải ảnh và lưu phiên bản gốc
                        self.original_pixmap = QPixmap(image_path)
                        
                        # Cập nhật hiển thị ảnh
                        self.update_image_displays()
                        
                        # Phân tích kết quả từ barcode trong ảnh nếu có
                        self.process_result_from_image(image_path)
        else:
            print(f"Result folder does not exist: {result_folder}")
            
    def process_result_from_image(self, image_path):
        """Xử lý kết quả từ ảnh đã được xử lý bởi phần mềm thứ 3"""
        try:
            # Đọc ảnh và tìm barcode
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to load image: {image_path}")
                return
                
            # Tìm barcode bằng pyzbar
            barcodes = decode(image)
            
            if barcodes:
                # Lấy barcode đầu tiên
                barcode = barcodes[0]
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                
                # Hiển thị thông tin barcode
                barcode_info = f"Detected: {barcode_data}\nType: {barcode_type}"
                
                # Lấy mã barcode mong đợi (sử dụng S/N)
                expected_barcode = self.sn_input.text()
                
                # Kiểm tra mã barcode
                if barcode_data == expected_barcode:
                    self.result_view.setText(f"PASS\n{barcode_info}")
                    self.result_view.setStyleSheet("color: green; font-weight: bold;")
                    self.pass_count += 1
                    self.teaching_status_label.setText("PASS")
                    self.teaching_status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    self.result_view.setText(f"FAIL - Mismatch\n{barcode_info}")
                    self.result_view.setStyleSheet("color: red; font-weight: bold;")
                    self.fail_count += 1
                    self.teaching_status_label.setText("FAIL")
                    self.teaching_status_label.setStyleSheet("color: red; font-weight: bold;")
                
                # Cập nhật số lần quét và thống kê
                self.scan_count += 1
                self.update_stats()
                
                # Thêm vào log
                self.add_to_log(
                    sn=self.sn_input.text(),
                    model=self.model_input.text(),
                    result=self.result_view.text().split('\n')[0]  # Dòng đầu tiên của kết quả
                )
            else:
                # Không tìm thấy barcode
                self.result_view.setText("FAIL\nNo barcode detected")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
                self.fail_count += 1
                self.teaching_status_label.setText("FAIL")
                self.teaching_status_label.setStyleSheet("color: red; font-weight: bold;")
                
                # Cập nhật số lần quét và thống kê
                self.scan_count += 1
                self.update_stats()
                
                # Thêm vào log
                self.add_to_log(
                    sn=self.sn_input.text(),
                    model=self.model_input.text(),
                    result="FAIL - No barcode"
                )
                
        except Exception as e:
            print(f"Error processing result from image: {str(e)}")
            self.result_view.setText(f"Error: {str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")

    def start_inspection(self):
        """Start the inspection process and send TRIGGER to comp4"""
        try:
            # Check if S/N and Model are entered
            if not self.sn_input.text() or not self.model_input.text():
                self.result_view.setText("Please enter S/N and Model")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
                return

            # Đánh dấu là đã bắt đầu chạy
            self.is_running = True
            
            # Cập nhật giao diện khi bắt đầu quá trình gửi TRIGGER
            self.result_view.setText("Đang gửi message \"TRIGGER\" đến comp4...\nVui lòng đợi...")
            self.result_view.setStyleSheet("color: orange; font-weight: bold;")
            self.teaching_status_label.setText("Processing")
            self.teaching_status_label.setStyleSheet("color: orange; font-weight: bold;")

            # Hiển thị thông báo trên thanh trạng thái
            self.statusBar().showMessage(f"Đang gửi message \"TRIGGER\" qua {self.serial_port} - {self.serial_baudrate} baud")

            QApplication.processEvents()  # Update UI immediately

            # Kiểm tra thư viện PySerial
            try:
                import serial
                print("PySerial đã được cài đặt")
            except ImportError:
                self.result_view.setText("Lỗi: Thư viện PySerial chưa được cài đặt!\nVui lòng cài đặt bằng lệnh:\npip install pyserial")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
                self.statusBar().showMessage("Lỗi: Thư viện PySerial chưa được cài đặt!")
                self.is_running = False
                return

            # Kiểm tra xem đã có serial worker đang chạy chưa
            if hasattr(self, 'trigger_worker') and self.trigger_worker.isRunning():
                self.result_view.setText("Đang xử lý yêu cầu trước đó...\nVui lòng đợi.")
                return

            # Hiển thị debug trên console
            print(f"Bắt đầu gửi message \"TRIGGER\" qua cổng COM4")

            # Thay đổi ở đây: Kết nối với COM4 thay vì COM3
            self.serial_port = "COM4"  # Đảm bảo là COM4

            # Tạo và chạy worker thread để gửi message "TRIGGER" qua serial
            self.trigger_worker = SerialTriggerWorker(self.serial_port, self.serial_baudrate)
            self.trigger_worker.finished.connect(self.handle_trigger_result)
            self.trigger_worker.status_update.connect(self.update_trigger_status)
            self.trigger_worker.start()

            # Hiển thị debug
            print("Đã khởi động thread gửi message \"TRIGGER\"")

            # Thêm vào log
            self.add_to_log(
                sn=self.sn_input.text(),
                model=self.model_input.text(),
                result="TRIGGER Sent"
            )

            # Bây giờ mới bắt đầu camera timer
            self.camera_timer.start(1000)  # Update every second

        except Exception as e:
            self.is_running = False
            import traceback
            traceback.print_exc()  # In stack trace đầy đủ ra console

            self.result_view.setText(f"Lỗi khi khởi động hệ thống:\n{str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")
            self.teaching_status_label.setText("Error")
            self.teaching_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.statusBar().showMessage(f"Lỗi: {str(e)}")

    def stop_inspection(self):
        """Stop the inspection process"""
        self.is_running = False
        self.camera_timer.stop()
        self.result_view.setText("System stopped")
        self.result_view.setStyleSheet("color: blue; font-weight: bold;")

    def reset_system(self):
        """Reset the system to initial state"""
        self.is_running = False
        self.camera_timer.stop()
        self.sn_input.clear()
        self.model_input.clear()
        self.camera_label.setText("Camera View Online")
        self.camera_label.setPixmap(QPixmap())
        self.image_view.setText("View ảnh vừa chụp")
        self.image_view.setPixmap(QPixmap())
        self.result_view.setText("Trạng thái kết quả\nNG/OK/Waiting...")
        self.result_view.setStyleSheet("color: blue;")
        
        # Reset counters
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.update_stats()
        
        # Clear log
        self.log_table.setRowCount(0)
        
        # Reset variables
        self.current_image_path = None
        self.original_pixmap = None
        
        # Reset teaching display
        self.teaching_model_label.setText("Not set")
        self.teaching_area_label.setText("Label area")
        self.teaching_settings_label.setText("Barcode Checking")
        self.teaching_status_label.setText("Ready")
        self.teaching_status_label.setStyleSheet("color: green; font-weight: bold;")

    def recheck(self):
        """Perform a recheck of the current item"""
        try:
            self.result_view.setText("Đang gửi message \"TRIGGER\" để kiểm tra lại...\nVui lòng đợi...")
            self.result_view.setStyleSheet("color: orange; font-weight: bold;")
            self.teaching_status_label.setText("Processing")
            self.teaching_status_label.setStyleSheet("color: orange; font-weight: bold;")
            self.statusBar().showMessage(f"Đang gửi message \"TRIGGER\" để kiểm tra lại qua {self.serial_port}")
            
            QApplication.processEvents()
            
            # Tạo và chạy worker thread để gửi message \"TRIGGER\" qua serial
            self.trigger_worker = SerialTriggerWorker(self.serial_port, self.serial_baudrate)
            self.trigger_worker.finished.connect(self.handle_trigger_result)
            self.trigger_worker.status_update.connect(self.update_trigger_status)
            self.trigger_worker.start()
            
            # Thêm vào log
            self.add_to_log(
                sn=self.sn_input.text(),
                model=self.model_input.text(),
                result="RECHECK Triggered"
            )
            
        except Exception as e:
            self.result_view.setText(f"Lỗi kiểm tra lại:\n{str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")
            self.statusBar().showMessage(f"Lỗi: {str(e)}")

    def add_to_log(self, sn, model, result):
        """Add an entry to the log table"""
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        
        # Add timestamp
        time_item = QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S"))
        self.log_table.setItem(row, 0, time_item)
        
        # Add SN and Model
        self.log_table.setItem(row, 1, QTableWidgetItem(sn))
        self.log_table.setItem(row, 2, QTableWidgetItem(model))
        
        # Add result with color
        result_item = QTableWidgetItem(result)
        if "PASS" in result:
            result_item.setBackground(Qt.GlobalColor.green)
        elif "FAIL" in result:
            result_item.setBackground(Qt.GlobalColor.red)
        self.log_table.setItem(row, 3, result_item)
        
        # Scroll to the latest entry
        self.log_table.scrollToBottom()

    def show_auto_view(self):
        """Switch to auto view"""
        self.auto_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold;")
        self.setting_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold;")

    def show_settings_view(self):
        """Switch to settings view"""
        self.setting_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold;")
        self.auto_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold;")
        # In a real app, you would show a settings panel here

    def get_pass_rate(self):
        """Calculate pass rate percentage"""
        if self.scan_count == 0:
            return "0.0"
        return f"{(self.pass_count / self.scan_count) * 100:.1f}"
        
    def update_stats(self):
        """Update the statistics display with detailed information"""
        self.ok_count_label.setText(str(self.pass_count))
        self.ng_count_label.setText(str(self.fail_count))
        self.total_count_label.setText(str(self.scan_count))
        self.rate_label.setText(f"{self.get_pass_rate()}%")

    def open_teaching_config(self):
        """Open teaching configuration dialog"""
        # Tạo dialog cấu hình teaching
        teaching_dialog = QDialog(self)
        teaching_dialog.setWindowTitle("Cấu hình Teaching")
        teaching_dialog.setFixedSize(800, 600)
        teaching_dialog.setStyleSheet("background-color: #f0f0f0;")
        
        # Layout chính
        main_layout = QVBoxLayout(teaching_dialog)
        
        # Tab widget để tổ chức các phần cấu hình
        tab_widget = QTabWidget()
        
        # Tab 1: Cấu hình chung
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Thông tin model
        model_group = QGroupBox("Thông tin Model")
        model_layout = QFormLayout(model_group)
        
        model_selector = QComboBox()
        model_selector.addItems(["RU Model", "OCDU Model", "Accessory Model"])
        model_layout.addRow("Chọn Model:", model_selector)
        
        model_path = QLineEdit()
        model_path.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(model_path)
        model_path_layout.addWidget(browse_btn)
        model_layout.addRow("Đường dẫn cấu hình:", model_path_layout)
        
        general_layout.addWidget(model_group)
        
        # Thiết lập kiểm tra
        check_group = QGroupBox("Thiết lập kiểm tra")
        check_layout = QFormLayout(check_group)
        
        check_type = QComboBox()
        check_type.addItems(["Barcode 1D", "QR Code", "Data Matrix", "Label Text"])
        check_layout.addRow("Loại kiểm tra:", check_type)
        
        match_mode = QComboBox()
        match_mode.addItems(["Chính xác 100%", "Phần đầu giống nhau", "Chứa chuỗi"])
        check_layout.addRow("Kiểu so sánh:", match_mode)
        
        # Thêm checkbox cho các tùy chọn nâng cao
        enable_preprocessing = QCheckBox("Bật tiền xử lý ảnh")
        check_layout.addRow("Xử lý ảnh:", enable_preprocessing)
        
        timeout_value = QSpinBox()
        timeout_value.setRange(1, 30)
        timeout_value.setValue(5)
        timeout_value.setSuffix(" giây")
        check_layout.addRow("Thời gian timeout:", timeout_value)
        
        general_layout.addWidget(check_group)
        
        # Các nút tác vụ
        action_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu cấu hình")
        test_btn = QPushButton("Kiểm tra")
        reset_config_btn = QPushButton("Đặt lại")
        
        action_layout.addWidget(save_btn)
        action_layout.addWidget(test_btn)
        action_layout.addWidget(reset_config_btn)
        
        general_layout.addLayout(action_layout)
        
        # Tab 2: Thiết lập vùng ảnh
        image_area_tab = QWidget()
        image_area_layout = QVBoxLayout(image_area_tab)
        
        # Hiển thị ảnh mẫu
        image_preview_group = QGroupBox("Xem trước ảnh")
        image_preview_layout = QVBoxLayout(image_preview_group)
        
        image_preview = QLabel("Chưa có ảnh mẫu")
        image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_preview.setStyleSheet("background-color: #e0e0e0; min-height: 300px;")
        image_preview_layout.addWidget(image_preview)
        
        # Các nút điều khiển ảnh
        image_control_layout = QHBoxLayout()
        load_sample_btn = QPushButton("Tải ảnh mẫu")
        capture_sample_btn = QPushButton("Chụp ảnh mẫu")
        clear_sample_btn = QPushButton("Xóa ảnh mẫu")
        
        image_control_layout.addWidget(load_sample_btn)
        image_control_layout.addWidget(capture_sample_btn)
        image_control_layout.addWidget(clear_sample_btn)
        
        image_preview_layout.addLayout(image_control_layout)
        image_area_layout.addWidget(image_preview_group)
        
        # Thiết lập vùng kiểm tra
        roi_group = QGroupBox("Thiết lập vùng ROI")
        roi_layout = QFormLayout(roi_group)
        
        roi_type = QComboBox()
        roi_type.addItems(["Vùng chữ nhật", "Vùng đa giác", "Toàn bộ ảnh"])
        roi_layout.addRow("Kiểu vùng ROI:", roi_type)
        
        roi_edit_btn = QPushButton("Vẽ vùng ROI")
        roi_layout.addRow("Chỉnh sửa ROI:", roi_edit_btn)
        
        # Thêm các tham số của ROI
        roi_params_layout = QHBoxLayout()
        
        # X position
        roi_x = QSpinBox()
        roi_x.setRange(0, 1000)
        roi_x.setSuffix(" px")
        
        # Y position
        roi_y = QSpinBox()
        roi_y.setRange(0, 1000)
        roi_y.setSuffix(" px")
        
        # Width
        roi_width = QSpinBox()
        roi_width.setRange(10, 1000)
        roi_width.setSuffix(" px")
        
        # Height
        roi_height = QSpinBox()
        roi_height.setRange(10, 1000)
        roi_height.setSuffix(" px")
        
        roi_params_layout.addWidget(QLabel("X:"))
        roi_params_layout.addWidget(roi_x)
        roi_params_layout.addWidget(QLabel("Y:"))
        roi_params_layout.addWidget(roi_y)
        roi_params_layout.addWidget(QLabel("W:"))
        roi_params_layout.addWidget(roi_width)
        roi_params_layout.addWidget(QLabel("H:"))
        roi_params_layout.addWidget(roi_height)
        
        roi_layout.addRow("Tọa độ ROI:", roi_params_layout)
        
        image_area_layout.addWidget(roi_group)
        
        # Tab 3: Thiết lập kết nối
        connection_tab = QWidget()
        connection_layout = QVBoxLayout(connection_tab)
        
        # Thiết lập kết nối COM
        com_group = QGroupBox("Thiết lập cổng COM")
        com_layout = QFormLayout(com_group)
        
        com_port = QComboBox()
        com_port.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"])
        com_port.setCurrentText("COM4")  # Default to COM4
        com_layout.addRow("Cổng COM:", com_port)
        
        baudrate = QComboBox()
        baudrate.addItems(["9600", "19200", "38400", "57600", "115200"])
        baudrate.setCurrentText("9600")
        com_layout.addRow("Baudrate:", baudrate)
        
        # Thêm nút kiểm tra kết nối
        test_connection_btn = QPushButton("Kiểm tra kết nối")
        test_connection_btn.clicked.connect(lambda: self.test_connection(com_port.currentText(), int(baudrate.currentText())))
        com_layout.addRow("Kiểm tra:", test_connection_btn)
        
        connection_layout.addWidget(com_group)
        
        # Thiết lập thư mục lưu trữ
        storage_group = QGroupBox("Thiết lập lưu trữ")
        storage_layout = QFormLayout(storage_group)
        
        save_images = QCheckBox("Lưu ảnh kiểm tra")
        save_images.setChecked(True)
        storage_layout.addRow("Lưu ảnh:", save_images)
        
        image_path = QLineEdit(r"C:\Users\a\Desktop\Work\VisionCheckLabel\image\Result")
        browse_image_path_btn = QPushButton("Browse...")
        image_path_layout = QHBoxLayout()
        image_path_layout.addWidget(image_path)
        image_path_layout.addWidget(browse_image_path_btn)
        storage_layout.addRow("Thư mục ảnh:", image_path_layout)
        
        save_results = QCheckBox("Lưu kết quả")
        save_results.setChecked(True)
        storage_layout.addRow("Lưu kết quả:", save_results)
        
        result_path = QLineEdit(r"C:\Users\a\Desktop\Work\VisionCheckLabel\result")
        browse_result_path_btn = QPushButton("Browse...")
        result_path_layout = QHBoxLayout()
        result_path_layout.addWidget(result_path)
        result_path_layout.addWidget(browse_result_path_btn)
        storage_layout.addRow("Thư mục kết quả:", result_path_layout)
        
        connection_layout.addWidget(storage_group)
        
        # Thêm các tab vào tab widget
        tab_widget.addTab(general_tab, "Cấu hình chung")
        tab_widget.addTab(image_area_tab, "Thiết lập vùng ảnh")
        tab_widget.addTab(connection_tab, "Kết nối & Lưu trữ")
        
        main_layout.addWidget(tab_widget)
        
        # Thêm các nút tác vụ cuối cùng
        final_buttons_layout = QHBoxLayout()
        apply_btn = QPushButton("Áp dụng")
        apply_btn.setStyleSheet("background-color: #90EE90; font-weight: bold;")
        cancel_btn = QPushButton("Hủy bỏ")
        
        final_buttons_layout.addWidget(apply_btn)
        final_buttons_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(final_buttons_layout)
        
        # Kết nối các sự kiện
        cancel_btn.clicked.connect(teaching_dialog.reject)
        browse_btn.clicked.connect(lambda: self.browse_file(model_path))
        browse_image_path_btn.clicked.connect(lambda: self.browse_folder(image_path))
        browse_result_path_btn.clicked.connect(lambda: self.browse_folder(result_path))
        apply_btn.clicked.connect(teaching_dialog.accept)
        
        # Thêm sự kiện cho các nút khác
        load_sample_btn.clicked.connect(lambda: self.load_sample_image(image_preview))
        capture_sample_btn.clicked.connect(lambda: self.capture_sample_image(image_preview))
        clear_sample_btn.clicked.connect(lambda: self.clear_sample_image(image_preview))
        roi_edit_btn.clicked.connect(lambda: self.edit_roi(image_preview, roi_x, roi_y, roi_width, roi_height))
        
        # Hiển thị dialog
        if teaching_dialog.exec() == QDialog.DialogCode.Accepted:
            # Cập nhật các thông tin cấu hình
            self.teaching_model_label.setText(model_selector.currentText())
            self.teaching_area_label.setText(f"{roi_type.currentText()}")
            self.teaching_settings_label.setText(f"{check_type.currentText()}")
            
            # Cập nhật cấu hình COM
            self.serial_port = com_port.currentText()
            self.serial_baudrate = int(baudrate.currentText())
            
            # Lưu cấu hình ROI
            self.roi_settings = {
                'type': roi_type.currentText(),
                'x': roi_x.value(),
                'y': roi_y.value(), 
                'width': roi_width.value(),
                'height': roi_height.value()
            }
            
            # Lưu cấu hình đường dẫn
            self.image_folder = image_path.text()
            self.result_folder = result_path.text()
            
            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Cập nhật cấu hình", "Cấu hình teaching đã được cập nhật thành công!")
        
    def test_connection(self, port, baudrate):
        """Kiểm tra kết nối cổng COM"""
        try:
            # Hiển thị thông báo đang kiểm tra
            QMessageBox.information(self, "Đang kiểm tra", f"Đang kiểm tra kết nối với {port} ở baudrate {baudrate}...\nVui lòng đợi.")
            
            # Thử kết nối với cổng COM
            with serial.Serial(port, baudrate, timeout=2) as ser:
                # Nếu mở được cổng COM, hiển thị thông báo thành công
                QMessageBox.information(self, "Kết nối thành công", f"Đã kết nối thành công với {port} ở baudrate {baudrate}!")
        except serial.SerialException as e:
            # Nếu không mở được cổng COM, hiển thị thông báo lỗi
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối với {port}: {str(e)}")
        except Exception as e:
            # Lỗi khác
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
    
    def load_sample_image(self, preview_label):
        """Tải ảnh mẫu từ file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Chọn ảnh mẫu", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
                
            if file_path:
                # Tải và hiển thị ảnh
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # Hiển thị ảnh đã tải lên label
                    pixmap = pixmap.scaled(preview_label.width(), preview_label.height(),
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                    preview_label.setPixmap(pixmap)
                    preview_label.setProperty("image_path", file_path)  # Lưu đường dẫn ảnh
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể tải ảnh đã chọn.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi tải ảnh: {str(e)}")
    
    def capture_sample_image(self, preview_label):
        """Chụp ảnh mẫu từ camera"""
        try:
            # Hiển thị thông báo chức năng chưa khả dụng
            QMessageBox.information(self, "Chức năng chưa khả dụng", 
                                  "Chức năng chụp ảnh mẫu đang được phát triển.\n"
                                  "Vui lòng sử dụng chức năng tải ảnh mẫu.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
    
    def clear_sample_image(self, preview_label):
        """Xóa ảnh mẫu đã tải"""
        try:
            preview_label.setPixmap(QPixmap())  # Xóa pixmap
            preview_label.setText("Chưa có ảnh mẫu")  # Thiết lập lại text
            preview_label.setProperty("image_path", None)  # Xóa đường dẫn ảnh
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi xóa ảnh: {str(e)}")
    
    def edit_roi(self, preview_label, roi_x, roi_y, roi_width, roi_height):
        """Mở công cụ chỉnh sửa ROI"""
        try:
            # Kiểm tra xem đã có ảnh mẫu chưa
            if not preview_label.pixmap() or preview_label.pixmap().isNull():
                QMessageBox.warning(self, "Thiếu ảnh mẫu", "Vui lòng tải ảnh mẫu trước khi thiết lập ROI.")
                return
            
            # Hiển thị thông báo chức năng đang được phát triển
            QMessageBox.information(self, "Chức năng đang phát triển", 
                                   "Công cụ vẽ ROI đang được phát triển.\n"
                                   "Bạn có thể nhập trực tiếp các tọa độ ROI.")
                                   
            # Trong phiên bản đầy đủ, mở cửa sổ vẽ ROI trên ảnh
            # và cập nhật các giá trị roi_x, roi_y, roi_width, roi_height
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi chỉnh sửa ROI: {str(e)}")
        
    def browse_file(self, line_edit):
        """Browse for a file and set the path to the line edit"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file cấu hình", "", "All Files (*);;JSON Files (*.json)")
        if file_path:
            line_edit.setText(file_path)
            
    def browse_folder(self, line_edit):
        """Browse for a folder and set the path to the line edit"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục", "")
        if folder_path:
            line_edit.setText(folder_path)


def main():
    app = QApplication(sys.argv)
    window = LinePacking()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
