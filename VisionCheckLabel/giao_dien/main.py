import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QTabWidget, QComboBox, QCheckBox, QSlider, QSpinBox, 
                             QDoubleSpinBox, QGroupBox, QRadioButton, QScrollArea,
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QDialog,
                             QFormLayout)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np
from pyzbar.pyzbar import decode, Decoded
from PIL import Image
import os
import datetime
import subprocess
import json


class LabelChecker:
    """Class to handle label barcode checking functionality"""
    
    def __init__(self):
        self.last_image = None
        self.last_processed_image = None
    
    def process_image(self, image_path):
        """Process an image to detect barcodes"""
        # Load and store the original image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
            
        self.last_image = image.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Store the processed image
        self.last_processed_image = thresh.copy()
        
        # Try to decode barcodes from the processed image
        decode_objects = decode(thresh)
        
        # If no barcodes found, try with the original image
        if not decode_objects:
            decode_objects = decode(Image.open(image_path))
        
        return decode_objects
    
    def draw_barcode_locations(self, image, decode_objects):
        """Draw boxes around detected barcodes"""
        result_image = image.copy()
        
        for obj in decode_objects:
            # Get the barcode polygon points
            points = obj.polygon
            
            if points:
                # Convert points to numpy array
                pts = np.array([(p.x, p.y) for p in points], np.int32)
                pts = pts.reshape((-1, 1, 2))
                
                # Draw the polygon
                cv2.polylines(result_image, [pts], True, (0, 255, 0), 2)
                
                # Draw the barcode data
                x = points[0].x
                y = points[0].y
                cv2.putText(result_image, obj.data.decode('utf-8'), (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
        return result_image
    
    def verify_barcode(self, detected_code, expected_code):
        """Verify if detected barcode matches expected value"""
        if not detected_code:
            return False, "No barcode detected"
            
        if detected_code == expected_code:
            return True, "PASS"
        else:
            return False, f"FAIL - Mismatch"

class VisionMasterInterface:
    """Interface to communicate with Vision Master through the UPDATE.sol file"""
    
    def __init__(self, sol_file_path=None):
        self.sol_file_path = sol_file_path
        self.config = {}
        
    def load_sol_file(self, file_path=None):
        """Load and parse the UPDATE.sol file"""
        if file_path:
            self.sol_file_path = file_path
            
        if not self.sol_file_path or not os.path.exists(self.sol_file_path):
            raise FileNotFoundError(f"SOL file not found: {self.sol_file_path}")
            
        try:
            # Đọc file .sol - Điều chỉnh phương thức đọc tùy theo định dạng thực tế
            with open(self.sol_file_path, 'r') as f:
                # Giả định file có cấu trúc đơn giản như text hoặc JSON
                content = f.read()
                
                # Nếu file là JSON
                try:
                    self.config = json.loads(content)
                except json.JSONDecodeError:
                    # Nếu không phải JSON, xử lý như file văn bản thông thường
                    self.parse_sol_content(content)
                    
            return True
        except Exception as e:
            print(f"Error loading SOL file: {str(e)}")
            return False
    
    def parse_sol_content(self, content):
        """Parse the content of the SOL file if it's not a JSON format"""
        # Điều chỉnh parser này tùy theo cấu trúc thực tế của file .sol
        lines = content.strip().split('\n')
        self.config = {}
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                # Đây là tiêu đề section
                current_section = line[1:-1]
                self.config[current_section] = {}
            elif '=' in line and current_section:
                # Đây là cặp key-value
                key, value = line.split('=', 1)
                self.config[current_section][key.strip()] = value.strip()
    
    def process_image(self, image_path):
        """Process image using the Vision Master configuration"""
        if not self.config:
            raise ValueError("No configuration loaded. Please load the SOL file first.")
            
        # Phương pháp 1: Sử dụng thông tin từ file .sol để xử lý ảnh trong Python
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
                
            # Thực hiện xử lý ảnh dựa trên config từ file .sol
            # Đây là phần bạn cần điều chỉnh dựa trên cấu trúc thực tế của file .sol
            processed_image = self.apply_vision_processing(image)
            
            return processed_image, True, "Success"
        except Exception as e:
            return None, False, str(e)
    
    def apply_vision_processing(self, image):
        """Apply vision processing based on the loaded configuration"""
        # Điều chỉnh hàm này tùy theo nội dung thực tế của file .sol
        # Ví dụ về một số xử lý cơ bản:
        
        processed = image.copy()
        
        # Áp dụng các bước xử lý từ config
        if 'ProcessingSteps' in self.config:
            steps = self.config.get('ProcessingSteps', {})
            
            # Ví dụ: Chuyển đổi sang grayscale
            if steps.get('ConvertGrayscale') == 'True':
                processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                # Chuyển lại sang BGR để các xử lý khác hoạt động đúng
                if len(processed.shape) == 2:
                    processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            
            # Ví dụ: Áp dụng Gaussian blur
            if 'GaussianBlur' in steps:
                ksize = int(steps.get('GaussianBlurKernelSize', '3'))
                if ksize % 2 == 0:
                    ksize += 1  # Đảm bảo kích thước kernel là số lẻ
                sigma = float(steps.get('GaussianBlurSigma', '0'))
                processed = cv2.GaussianBlur(processed, (ksize, ksize), sigma)
            
            # Ví dụ: Phát hiện cạnh với Canny
            if steps.get('CannyEdgeDetection') == 'True':
                threshold1 = float(steps.get('CannyThreshold1', '100'))
                threshold2 = float(steps.get('CannyThreshold2', '200'))
                edges = cv2.Canny(processed, threshold1, threshold2)
                # Chuyển lại sang BGR
                processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                
        return processed
    
    def run_external_vision_process(self, image_path, output_path=None):
        """Run the external Vision Master program using subprocess"""
        # Phương pháp 2: Gọi chương trình vision master thông qua subprocess
        
        # Đường dẫn đến chương trình vision master
        vision_master_exe = self.config.get('System', {}).get('ExecutablePath', 'vision_master.exe')
        
        # Tham số dòng lệnh
        command = [
            vision_master_exe,
            '-config', self.sol_file_path,
            '-input', image_path
        ]
        
        if output_path:
            command.extend(['-output', output_path])
            
        try:
            # Chạy lệnh
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Process error: {e.stderr}"
        except Exception as e:
            return False, f"Error running vision process: {str(e)}"

class LinePacking(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label_checker = LabelChecker()
        self.vision_master = VisionMasterInterface()
        self.current_image_path = None
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.sol_file_loaded = False
        self.initUI()
        
    def initUI(self):
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
        controls_layout = QVBoxLayout(self.controls_frame)
        
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
        controls_layout.addWidget(status_frame)
        
        # Control buttons
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
        
        controls_layout.addLayout(button_frame)
        
        # Image and Result views
        views_layout = QHBoxLayout()
        
        # Left view - Camera image - Tăng kích thước
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("border: 1px solid orange; background-color: white;")
        self.image_frame.setMinimumHeight(250)  # Tăng chiều cao tối thiểu
        image_layout = QVBoxLayout(self.image_frame)
        
        image_title = QLabel("View ảnh vừa chụp")
        image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_title.setStyleSheet("color: blue; font-weight: bold;")
        image_layout.addWidget(image_title)
        
        self.image_view = QLabel()
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setMinimumSize(300, 220)  # Thiết lập kích thước tối thiểu
        image_layout.addWidget(self.image_view)
        
        views_layout.addWidget(self.image_frame, 2)  # Tăng tỷ lệ cho phần ảnh
        
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
        result_layout.addWidget(self.result_view)
        
        views_layout.addWidget(self.result_frame, 1)  # Để 1 cho phần kết quả
        
        controls_layout.addLayout(views_layout)
        
        # Teaching display - Cải thiện hiển thị tool teaching
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
        
        controls_layout.addWidget(self.teaching_frame)
        
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
        
        controls_layout.addWidget(self.log_frame)
        
        main_content_layout.addWidget(self.controls_frame, 1)  # Takes 1/3 of width
        
        main_layout.addWidget(self.main_content)
        
        # Connect buttons
        self.auto_btn.clicked.connect(self.show_auto_view)
        self.setting_btn.clicked.connect(self.show_settings_view)
        self.start_btn.clicked.connect(self.start_inspection)
        self.stop_btn.clicked.connect(self.stop_inspection)
        self.reset_btn.clicked.connect(self.reset_system)
        self.recheck_btn.clicked.connect(self.recheck)
        
        # Setup a timer for simulating camera preview
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_preview)
        
        # Thêm nút Load SOL File trong phần Setting
        self.load_sol_btn = QPushButton("Load SOL File")
        self.load_sol_btn.clicked.connect(self.load_sol_file)
        # Thêm nút này vào giao diện setting
        
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
        
    def update_camera_preview(self):
        """Update the camera preview with simulated feed"""
        try:
            # For simulation, we'll rotate through a set of test images if available
            test_dir = "test_images"
            if os.path.exists(test_dir):
                images = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    image_path = os.path.join(test_dir, images[int(datetime.datetime.now().timestamp()) % len(images)])
                    if os.path.exists(image_path):
                        self.current_image_path = image_path
                        pixmap = QPixmap(image_path)
                        pixmap = pixmap.scaled(self.camera_label.width(), self.camera_label.height(), 
                                             Qt.AspectRatioMode.KeepAspectRatio)
                        self.camera_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Camera preview error: {str(e)}")

    def start_inspection(self):
        """Start the inspection process"""
        try:
            # Check if S/N and Model are entered
            if not self.sn_input.text() or not self.model_input.text():
                self.result_view.setText("Please enter S/N and Model")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
                return
                
            # Update UI to show processing state
            self.result_view.setText("Processing...\nWaiting for capture...")
            self.result_view.setStyleSheet("color: orange; font-weight: bold;")
            
            # Update teaching model with current model
            self.teaching_model_label.setText(self.model_input.text())
            self.teaching_status_label.setText("Processing")
            self.teaching_status_label.setStyleSheet("color: orange; font-weight: bold;")
            
            QApplication.processEvents()  # Update UI immediately
            
            # Start camera preview timer
            self.camera_timer.start(500)  # Update every 500ms
            
            # For testing with a file dialog:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Test Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_path:
                self.process_captured_image(file_path)
            
        except Exception as e:
            self.result_view.setText(f"Error starting system:\n{str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")
            self.teaching_status_label.setText("Error")
            self.teaching_status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def process_captured_image(self, image_path):
        """Process a captured or selected image"""
        try:
            # Stop camera preview
            self.camera_timer.stop()
            
            # Update UI
            self.result_view.setText("Processing image...\nPlease wait...")
            self.result_view.setStyleSheet("color: orange; font-weight: bold;")
            QApplication.processEvents()
            
            # Load and display the image
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Display in image view
                pixmap_small = pixmap.scaled(self.image_view.width(), self.image_view.height(),
                                          Qt.AspectRatioMode.KeepAspectRatio)
                self.image_view.setPixmap(pixmap_small)
                
                # Xử lý ảnh với Vision Master nếu đã load file .sol
                use_vision_master = self.sol_file_loaded
                
                if use_vision_master:
                    # Sử dụng Vision Master để xử lý
                    processed_image, success, message = self.vision_master.process_image(image_path)
                    
                    if success and processed_image is not None:
                        # Hiển thị ảnh đã xử lý
                        height, width, channel = processed_image.shape
                        bytes_per_line = 3 * width
                        qimg = QImage(processed_image.data, width, height, 
                                     bytes_per_line, QImage.Format.Format_BGR888)
                        pixmap = QPixmap.fromImage(qimg)
                        pixmap = pixmap.scaled(
                            self.camera_label.width(), 
                            self.camera_label.height(),
                            Qt.AspectRatioMode.KeepAspectRatio
                        )
                        self.camera_label.setPixmap(pixmap)
                        
                        # Tiếp tục với phát hiện barcode
                        decode_objects = decode(processed_image)
                    else:
                        # Nếu xử lý bằng Vision Master thất bại, thông báo lỗi và sử dụng xử lý mặc định
                        self.result_view.setText(f"Vision Master processing failed:\n{message}\nFalling back to default processing")
                        self.result_view.setStyleSheet("color: orange; font-weight: bold;")
                        QApplication.processEvents()
                        decode_objects = self.label_checker.process_image(image_path)
                else:
                    # Sử dụng xử lý mặc định
                    decode_objects = self.label_checker.process_image(image_path)
                
                # Update result based on barcode detection
                if decode_objects:
                    # Get the first barcode
                    barcode = decode_objects[0]
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    # Display detected barcode and type
                    barcode_info = f"Detected: {barcode_data}\nType: {barcode_type}"
                    
                    # Get expected barcode (using S/N for simplicity)
                    expected_barcode = self.sn_input.text()
                    
                    # Verify the barcode
                    success, message = self.label_checker.verify_barcode(barcode_data, expected_barcode)
                    
                    # Update result
                    if success:
                        self.result_view.setText(f"PASS\n{barcode_info}")
                        self.result_view.setStyleSheet("color: green; font-weight: bold;")
                        self.pass_count += 1
                    else:
                        self.result_view.setText(f"FAIL - Mismatch\n{barcode_info}")
                        self.result_view.setStyleSheet("color: red; font-weight: bold;")
                        self.fail_count += 1
                    
                    # Draw the barcode on the original image
                    marked_image = self.label_checker.draw_barcode_locations(
                        self.label_checker.last_image, decode_objects)
                    
                    # Convert to QPixmap and display
                    height, width, channel = marked_image.shape
                    bytes_per_line = 3 * width
                    qimg = QImage(marked_image.data, width, height, 
                                 bytes_per_line, QImage.Format.Format_BGR888)
                    pixmap = QPixmap.fromImage(qimg)
                    pixmap = pixmap.scaled(
                        self.camera_label.width(), 
                        self.camera_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                    self.camera_label.setPixmap(pixmap)
                    
                else:
                    # No barcode detected
                    self.result_view.setText("FAIL\nNo barcode detected")
                    self.result_view.setStyleSheet("color: red; font-weight: bold;")
                    self.fail_count += 1
                
                # Update scan count and stats
                self.scan_count += 1
                self.update_stats()
                
                # Add to log
                self.add_to_log(
                    sn=self.sn_input.text(),
                    model=self.model_input.text(),
                    result=self.result_view.text().split('\n')[0]  # First line of result
                )
                
                # Update teaching status
                if success:
                    self.teaching_status_label.setText("PASS")
                    self.teaching_status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    self.teaching_status_label.setText("FAIL")
                    self.teaching_status_label.setStyleSheet("color: red; font-weight: bold;")
                
            else:
                self.result_view.setText("Error loading image")
                self.result_view.setStyleSheet("color: red; font-weight: bold;")
                
        except Exception as e:
            self.result_view.setText(f"Error processing image:\n{str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")

    def stop_inspection(self):
        """Stop the inspection process"""
        self.camera_timer.stop()
        self.result_view.setText("System stopped")
        self.result_view.setStyleSheet("color: blue; font-weight: bold;")

    def reset_system(self):
        """Reset the system to initial state"""
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
        
        # Stop camera timer
        self.camera_timer.stop()
        
        # Reset teaching display
        self.teaching_model_label.setText("Not set")
        self.teaching_area_label.setText("Label area")
        self.teaching_settings_label.setText("Barcode Checking")
        self.teaching_status_label.setText("Ready")
        self.teaching_status_label.setStyleSheet("color: green; font-weight: bold;")

    def recheck(self):
        """Perform a recheck of the current item"""
        try:
            if self.current_image_path and os.path.exists(self.current_image_path):
                self.process_captured_image(self.current_image_path)
            else:
                self.result_view.setText("No image available for recheck")
                self.result_view.setStyleSheet("color: orange; font-weight: bold;")
        except Exception as e:
            self.result_view.setText(f"Recheck error:\n{str(e)}")
            self.result_view.setStyleSheet("color: red; font-weight: bold;")

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

    def load_sol_file(self):
        """Load the UPDATE.sol file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select SOL Config File", "", "SOL Files (*.sol)"
        )
        
        if file_path:
            try:
                success = self.vision_master.load_sol_file(file_path)
                if success:
                    self.sol_file_loaded = True
                    QMessageBox.information(self, "Success", "SOL file loaded successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to load SOL file")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading SOL file: {str(e)}")

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
        
        expected_value = QLineEdit()
        check_layout.addRow("Giá trị mong đợi:", expected_value)
        
        match_type = QComboBox()
        match_type.addItems(["Exact Match", "Contains", "Starts With", "Ends With", "Regex"])
        check_layout.addRow("Kiểu so khớp:", match_type)
        
        general_layout.addWidget(check_group)
        
        # Thêm các thông số timeout và retry
        timeout_group = QGroupBox("Thiết lập thời gian")
        timeout_layout = QFormLayout(timeout_group)
        
        timeout_spin = QSpinBox()
        timeout_spin.setRange(1, 30)
        timeout_spin.setValue(5)
        timeout_spin.setSuffix(" seconds")
        timeout_layout.addRow("Timeout:", timeout_spin)
        
        retry_spin = QSpinBox()
        retry_spin.setRange(0, 5)
        retry_spin.setValue(2)
        timeout_layout.addRow("Số lần thử lại:", retry_spin)
        
        general_layout.addWidget(timeout_group)
        
        # Thêm tab vào tab widget
        tab_widget.addTab(general_tab, "Cấu hình chung")
        
        # Tab 2: Cấu hình vùng ROI
        roi_tab = QWidget()
        roi_layout = QVBoxLayout(roi_tab)
        
        # Preview hình ảnh và vùng ROI
        preview_group = QGroupBox("Preview và chọn vùng ROI")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview image placeholder
        preview_label = QLabel("Hình ảnh preview")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("background-color: black; color: white;")
        preview_label.setMinimumSize(600, 400)
        preview_layout.addWidget(preview_label)
        
        # ROI controls
        roi_controls = QHBoxLayout()
        roi_controls.addWidget(QLabel("X:"))
        roi_x = QSpinBox()
        roi_x.setRange(0, 1000)
        roi_controls.addWidget(roi_x)
        
        roi_controls.addWidget(QLabel("Y:"))
        roi_y = QSpinBox()
        roi_y.setRange(0, 1000)
        roi_controls.addWidget(roi_y)
        
        roi_controls.addWidget(QLabel("Width:"))
        roi_width = QSpinBox()
        roi_width.setRange(10, 1000)
        roi_width.setValue(200)
        roi_controls.addWidget(roi_width)
        
        roi_controls.addWidget(QLabel("Height:"))
        roi_height = QSpinBox()
        roi_height.setRange(10, 1000)
        roi_height.setValue(100)
        roi_controls.addWidget(roi_height)
        
        preview_layout.addLayout(roi_controls)
        
        # Capture test image button
        capture_test_btn = QPushButton("Chụp ảnh test")
        capture_test_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        preview_layout.addWidget(capture_test_btn)
        
        roi_layout.addWidget(preview_group)
        
        tab_widget.addTab(roi_tab, "Cấu hình vùng ROI")
        
        # Tab 3: Cấu hình xử lý ảnh
        image_proc_tab = QWidget()
        image_proc_layout = QVBoxLayout(image_proc_tab)
        
        preprocessing_group = QGroupBox("Tiền xử lý ảnh")
        preprocessing_layout = QVBoxLayout(preprocessing_group)
        
        # Các checkbox cho preprocessing
        grayscale_check = QCheckBox("Chuyển đổi sang ảnh xám")
        grayscale_check.setChecked(True)
        preprocessing_layout.addWidget(grayscale_check)
        
        blur_check = QCheckBox("Áp dụng Gaussian Blur")
        blur_check.setChecked(True)
        preprocessing_layout.addWidget(blur_check)
        
        # Blur settings
        blur_settings = QHBoxLayout()
        blur_settings.addWidget(QLabel("Kernel Size:"))
        blur_kernel = QComboBox()
        blur_kernel.addItems(["3x3", "5x5", "7x7", "9x9"])
        blur_settings.addWidget(blur_kernel)
        blur_settings.addStretch()
        preprocessing_layout.addLayout(blur_settings)
        
        threshold_check = QCheckBox("Áp dụng Adaptive Threshold")
        threshold_check.setChecked(True)
        preprocessing_layout.addWidget(threshold_check)
        
        # Threshold settings
        threshold_settings = QHBoxLayout()
        threshold_settings.addWidget(QLabel("Block Size:"))
        block_size = QComboBox()
        block_size.addItems(["3", "5", "7", "9", "11", "13"])
        block_size.setCurrentText("11")
        threshold_settings.addWidget(block_size)
        
        threshold_settings.addWidget(QLabel("C:"))
        c_value = QSpinBox()
        c_value.setRange(-10, 10)
        c_value.setValue(2)
        threshold_settings.addWidget(c_value)
        threshold_settings.addStretch()
        preprocessing_layout.addLayout(threshold_settings)
        
        image_proc_layout.addWidget(preprocessing_group)
        
        # Advanced options
        advanced_group = QGroupBox("Tùy chọn nâng cao")
        advanced_layout = QVBoxLayout(advanced_group)
        
        advanced_check = QCheckBox("Sử dụng cài đặt Vision Master (.sol)")
        advanced_layout.addWidget(advanced_check)
        
        sol_path = QLineEdit()
        sol_path.setReadOnly(True)
        sol_path.setPlaceholderText("Đường dẫn đến file .sol")
        sol_browse_btn = QPushButton("Browse...")
        sol_path_layout = QHBoxLayout()
        sol_path_layout.addWidget(sol_path)
        sol_path_layout.addWidget(sol_browse_btn)
        advanced_layout.addLayout(sol_path_layout)
        
        image_proc_layout.addWidget(advanced_group)
        
        tab_widget.addTab(image_proc_tab, "Xử lý ảnh")
        
        # Thêm tab widget vào layout chính
        main_layout.addWidget(tab_widget)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_btn = QPushButton("Test")
        test_btn.setStyleSheet("background-color: #008CBA; color: white; font-weight: bold;")
        button_layout.addWidget(test_btn)
        
        save_btn = QPushButton("Lưu cấu hình")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Hủy")
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect buttons
        cancel_btn.clicked.connect(teaching_dialog.reject)
        
        # Show the dialog
        teaching_dialog.exec()

def main():
    app = QApplication(sys.argv)
    window = LinePacking()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
