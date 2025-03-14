import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QTabWidget, QComboBox, QCheckBox, QSlider, QSpinBox, 
                             QDoubleSpinBox, QGroupBox, QRadioButton, QScrollArea)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont

class LinePacking(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window title and size
        self.setWindowTitle('UI Vision in Line Packing RU,OCDU,Acessory')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: white;")
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title label with dark blue background
        self.title_label = QLabel('UI Vision in Line Packing RU,OCDU,Acessory')
        self.title_label.setStyleSheet("background-color: #000080; color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        self.main_layout.addWidget(self.title_label)
        
        # Top form layout (S/N, Model, Version)
        self.top_form = QFrame()
        self.top_form.setFrameShape(QFrame.Shape.Box)
        self.top_form.setStyleSheet("border: 1px solid orange;")
        top_form_layout = QHBoxLayout(self.top_form)
        
        sn_label = QLabel('S/N')
        self.sn_input = QLineEdit()
        self.sn_input.setFixedHeight(25)
        self.sn_input.setFixedWidth(200)
        self.sn_input.setStyleSheet("border: 1px solid black;")
        
        model_label = QLabel('Model')
        self.model_input = QLineEdit()
        self.model_input.setFixedHeight(25)
        self.model_input.setFixedWidth(200)
        self.model_input.setStyleSheet("border: 1px solid black;")
        
        version_label = QLabel('Tên công đoạn, ver')
        
        top_form_layout.addWidget(sn_label)
        top_form_layout.addWidget(self.sn_input)
        top_form_layout.addSpacing(20)
        top_form_layout.addWidget(model_label)
        top_form_layout.addWidget(self.model_input)
        top_form_layout.addSpacing(20)
        top_form_layout.addWidget(version_label)
        top_form_layout.addStretch()
        
        self.main_layout.addWidget(self.top_form)
        
        # Mode buttons
        mode_layout = QHBoxLayout()
        self.auto_btn = QPushButton('Auto')
        self.auto_btn.setFixedWidth(80)
        self.auto_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold; border: 1px solid black;")
        self.setting_btn = QPushButton('Setting')
        self.setting_btn.setFixedWidth(80)
        self.setting_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold; border: 1px solid black;")
        
        mode_layout.addWidget(self.auto_btn)
        mode_layout.addWidget(self.setting_btn)
        mode_layout.addStretch()
        
        self.main_layout.addLayout(mode_layout)
        
        # Create stacked layout for Auto and Setting views
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.main_layout.addWidget(self.content_container)
        
        # Create Auto View (default)
        self.auto_view = QWidget()
        self.auto_layout = QVBoxLayout(self.auto_view)
        
        # Middle section with camera view and controls
        middle_section = QHBoxLayout()
        
        # Camera view frame
        camera_frame = QFrame()
        camera_frame.setFrameShape(QFrame.Shape.Box)
        camera_frame.setStyleSheet("border: 1px solid orange;")
        camera_layout = QVBoxLayout(camera_frame)
        
        camera_label = QLabel('Camera View Online')
        camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_label.setStyleSheet("color: blue; font-weight: bold; font-size: 14px;")
        camera_layout.addWidget(camera_label)
        camera_layout.addStretch()
        
        # Controls panel
        controls_panel = QVBoxLayout()
        
        # Status display - made smaller to match the image
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.Box)
        status_frame.setFixedHeight(80)
        status_frame.setStyleSheet("border: 1px solid orange;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        status_label = QLabel('Hiển thị trạng thái sản lượng (OK? ON? Total? Rate?)')
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_label)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_btn = QPushButton('Start')
        self.start_btn.setStyleSheet("background-color: #66CC00; color: white; font-weight: bold;")
        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setStyleSheet("background-color: #99CC66; font-weight: bold;")
        self.reset_btn = QPushButton('Reset')
        self.reset_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        self.recheck_btn = QPushButton('Recheck')
        self.recheck_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.recheck_btn)
        
        status_layout.addLayout(buttons_layout)
        controls_panel.addWidget(status_frame)
        
        # Image and result display - now with actual display areas
        image_result_layout = QHBoxLayout()
        
        # Image frame - includes an empty white area for the image
        img_frame = QFrame()
        img_frame.setFrameShape(QFrame.Shape.Box)
        img_frame.setFixedHeight(150)
        img_frame.setStyleSheet("border: 1px solid orange;")
        img_layout = QVBoxLayout(img_frame)
        
        img_label = QLabel('View ảnh vừa chụp')
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("color: blue; font-weight: bold;")
        
        img_view = QFrame()
        img_view.setStyleSheet("background-color: white;")
        
        img_layout.addWidget(img_label)
        img_layout.addWidget(img_view)
        
        # Result frame - includes an empty white area for the result
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.Shape.Box)
        result_frame.setFixedHeight(150)
        result_frame.setStyleSheet("border: 1px solid orange;")
        result_layout = QVBoxLayout(result_frame)
        
        result_label = QLabel('Trạng thái kết quả\nNG/OK/Waiting...')
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_label.setStyleSheet("color: blue; font-weight: bold;")
        
        result_view = QFrame()
        result_view.setStyleSheet("background-color: white;")
        
        result_layout.addWidget(result_label)
        result_layout.addWidget(result_view)
        
        image_result_layout.addWidget(img_frame)
        image_result_layout.addWidget(result_frame)
        
        controls_panel.addLayout(image_result_layout)
        
        # Teaching tool display
        teaching_frame = QFrame()
        teaching_frame.setFrameShape(QFrame.Shape.Box)
        teaching_frame.setFixedHeight(180)
        teaching_frame.setStyleSheet("border: 1px solid orange;")
        teaching_layout = QVBoxLayout(teaching_frame)
        
        teaching_label = QLabel('Hiển thị tool teaching:\nshow teaching ban đầu / kết quả vision check thực tế/ Kết quả')
        teaching_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        teaching_label.setStyleSheet("color: blue; font-weight: bold;")
        
        teaching_view = QFrame()
        teaching_view.setStyleSheet("background-color: white;")
        
        teaching_layout.addWidget(teaching_label)
        teaching_layout.addWidget(teaching_view)
        
        controls_panel.addWidget(teaching_frame)
        
        # Log display
        log_frame = QFrame()
        log_frame.setFrameShape(QFrame.Shape.Box)
        log_frame.setFixedHeight(80)
        log_frame.setStyleSheet("border: 1px solid orange;")
        log_layout = QVBoxLayout(log_frame)
        
        log_label = QLabel('Show log process theo thời gian:\n- SN input/Model/kết quả kiểm tra/Finish')
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_label.setStyleSheet("color: blue; font-weight: bold;")
        
        log_view = QFrame()
        log_view.setStyleSheet("background-color: white;")
        
        log_layout.addWidget(log_label)
        log_layout.addWidget(log_view)
        
        controls_panel.addWidget(log_frame)
        
        # Add camera and controls to middle section
        middle_section.addWidget(camera_frame, 2)  # Camera takes 2/3 of width
        middle_section.addLayout(controls_panel, 1)  # Controls take 1/3 of width
        
        self.auto_layout.addLayout(middle_section)

        # Create Settings View
        self.settings_view = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_view)
        
        # Create tab widget for different setting categories
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid orange; }")
        
        # Camera Settings Tab
        camera_tab = QWidget()
        camera_tab_layout = QVBoxLayout(camera_tab)
        
        # Camera Connection Group
        camera_connection = QGroupBox("Camera Connection")
        camera_connection.setStyleSheet("QGroupBox { font-weight: bold; }")
        camera_conn_layout = QGridLayout(camera_connection)
        
        camera_conn_layout.addWidget(QLabel("Camera Model:"), 0, 0)
        camera_model = QComboBox()
        camera_model.addItems(["Basler acA1920-40gm", "HIKVISION MV-CA016-10GM", "Custom..."])
        camera_conn_layout.addWidget(camera_model, 0, 1)
        
        camera_conn_layout.addWidget(QLabel("Camera IP:"), 1, 0)
        camera_ip = QLineEdit("192.168.1.10")
        camera_conn_layout.addWidget(camera_ip, 1, 1)
        
        camera_conn_layout.addWidget(QLabel("Connection Type:"), 2, 0)
        conn_type = QComboBox()
        conn_type.addItems(["GigE Vision", "USB3 Vision", "CameraLink"])
        camera_conn_layout.addWidget(conn_type, 2, 1)
        
        test_conn_btn = QPushButton("Test Connection")
        test_conn_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        camera_conn_layout.addWidget(test_conn_btn, 3, 0, 1, 2)
        
        camera_tab_layout.addWidget(camera_connection)
        
        # Camera Properties Group
        camera_properties = QGroupBox("Camera Properties")
        camera_properties.setStyleSheet("QGroupBox { font-weight: bold; }")
        camera_prop_layout = QGridLayout(camera_properties)
        
        camera_prop_layout.addWidget(QLabel("Exposure (ms):"), 0, 0)
        exposure = QDoubleSpinBox()
        exposure.setRange(0.1, 1000.0)
        exposure.setValue(10.0)
        camera_prop_layout.addWidget(exposure, 0, 1)
        
        camera_prop_layout.addWidget(QLabel("Gain:"), 1, 0)
        gain = QDoubleSpinBox()
        gain.setRange(0.0, 24.0)
        gain.setValue(5.0)
        camera_prop_layout.addWidget(gain, 1, 1)
        
        camera_prop_layout.addWidget(QLabel("Trigger Mode:"), 2, 0)
        trigger_mode = QComboBox()
        trigger_mode.addItems(["Continuous", "External Trigger", "Software Trigger"])
        camera_prop_layout.addWidget(trigger_mode, 2, 1)
        
        camera_tab_layout.addWidget(camera_properties)
        camera_tab_layout.addStretch()
        
        # Vision Settings Tab
        vision_tab = QWidget()
        vision_tab_layout = QVBoxLayout(vision_tab)
        
        # Algorithm Settings
        algorithm_settings = QGroupBox("Algorithm Settings")
        algorithm_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        algorithm_layout = QGridLayout(algorithm_settings)
        
        algorithm_layout.addWidget(QLabel("Detection Method:"), 0, 0)
        detection_method = QComboBox()
        detection_method.addItems(["Contour Detection", "Pattern Matching", "Feature Extraction", "Deep Learning"])
        algorithm_layout.addWidget(detection_method, 0, 1)
        
        algorithm_layout.addWidget(QLabel("Threshold (0-255):"), 1, 0)
        threshold = QSlider(Qt.Orientation.Horizontal)
        threshold.setRange(0, 255)
        threshold.setValue(127)
        threshold_value = QLabel("127")
        algorithm_layout.addWidget(threshold, 1, 1)
        algorithm_layout.addWidget(threshold_value, 1, 2)
        
        algorithm_layout.addWidget(QLabel("Minimum Area (px):"), 2, 0)
        min_area = QSpinBox()
        min_area.setRange(10, 10000)
        min_area.setValue(100)
        algorithm_layout.addWidget(min_area, 2, 1)
        
        algorithm_layout.addWidget(QLabel("Match Score (%):"), 3, 0)
        match_score = QSlider(Qt.Orientation.Horizontal)
        match_score.setRange(50, 100)
        match_score.setValue(80)
        match_value = QLabel("80")
        algorithm_layout.addWidget(match_score, 3, 1)
        algorithm_layout.addWidget(match_value, 3, 2)
        
        vision_tab_layout.addWidget(algorithm_settings)
        
        # ROI Settings
        roi_settings = QGroupBox("Region of Interest (ROI)")
        roi_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        roi_layout = QGridLayout(roi_settings)
        
        roi_layout.addWidget(QLabel("Enable Multiple ROIs:"), 0, 0)
        enable_roi = QCheckBox()
        enable_roi.setChecked(True)
        roi_layout.addWidget(enable_roi, 0, 1)
        
        roi_layout.addWidget(QLabel("ROI Type:"), 1, 0)
        roi_type = QComboBox()
        roi_type.addItems(["Rectangle", "Circle", "Polygon", "Automatic"])
        roi_layout.addWidget(roi_type, 1, 1)
        
        draw_roi_btn = QPushButton("Draw/Edit ROIs")
        draw_roi_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        roi_layout.addWidget(draw_roi_btn, 2, 0, 1, 2)
        
        vision_tab_layout.addWidget(roi_settings)
        vision_tab_layout.addStretch()
        
        # System Settings Tab
        system_tab = QWidget()
        system_tab_layout = QVBoxLayout(system_tab)
        
        # Save/Load Settings
        save_settings = QGroupBox("Save/Load Configuration")
        save_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        save_layout = QGridLayout(save_settings)
        
        save_layout.addWidget(QLabel("Configuration Name:"), 0, 0)
        config_name = QLineEdit("Default_Config")
        save_layout.addWidget(config_name, 0, 1)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.setStyleSheet("background-color: #66CC00; color: white; font-weight: bold;")
        save_layout.addWidget(save_btn, 1, 0)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        save_layout.addWidget(load_btn, 1, 1)
        
        system_tab_layout.addWidget(save_settings)
        
        # Data Storage Settings
        storage_settings = QGroupBox("Data Storage Settings")
        storage_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        storage_layout = QGridLayout(storage_settings)
        
        storage_layout.addWidget(QLabel("Save Images:"), 0, 0)
        save_images = QCheckBox()
        save_images.setChecked(True)
        storage_layout.addWidget(save_images, 0, 1)
        
        storage_layout.addWidget(QLabel("Image Format:"), 1, 0)
        image_format = QComboBox()
        image_format.addItems(["PNG", "JPEG", "BMP", "TIFF"])
        storage_layout.addWidget(image_format, 1, 1)
        
        storage_layout.addWidget(QLabel("Save Path:"), 2, 0)
        save_path = QLineEdit("D:/Vision_Data/")
        storage_layout.addWidget(save_path, 2, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold;")
        storage_layout.addWidget(browse_btn, 2, 2)
        
        storage_layout.addWidget(QLabel("Log Level:"), 3, 0)
        log_level = QComboBox()
        log_level.addItems(["Info", "Warning", "Error", "Debug"])
        storage_layout.addWidget(log_level, 3, 1)
        
        system_tab_layout.addWidget(storage_settings)
        
        # Network Settings
        network_settings = QGroupBox("Network Settings")
        network_settings.setStyleSheet("QGroupBox { font-weight: bold; }")
        network_layout = QGridLayout(network_settings)
        
        network_layout.addWidget(QLabel("Enable PLC Connection:"), 0, 0)
        enable_plc = QCheckBox()
        enable_plc.setChecked(True)
        network_layout.addWidget(enable_plc, 0, 1)
        
        network_layout.addWidget(QLabel("PLC IP Address:"), 1, 0)
        plc_ip = QLineEdit("192.168.1.5")
        network_layout.addWidget(plc_ip, 1, 1)
        
        network_layout.addWidget(QLabel("Protocol:"), 2, 0)
        protocol = QComboBox()
        protocol.addItems(["Modbus TCP", "Ethernet/IP", "Profinet", "TCP/IP"])
        network_layout.addWidget(protocol, 2, 1)
        
        test_network_btn = QPushButton("Test Connection")
        test_network_btn.setStyleSheet("background-color: #3399FF; font-weight: bold;")
        network_layout.addWidget(test_network_btn, 3, 0, 1, 2)
        
        system_tab_layout.addWidget(network_settings)
        system_tab_layout.addStretch()
        
        # Add tabs to the tab widget
        self.settings_tabs.addTab(camera_tab, "Camera")
        self.settings_tabs.addTab(vision_tab, "Vision")
        self.settings_tabs.addTab(system_tab, "System")
        
        # Add settings save/cancel buttons
        settings_actions = QHBoxLayout()
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setStyleSheet("background-color: #66CC00; color: white; font-weight: bold;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold;")
        
        settings_actions.addStretch()
        settings_actions.addWidget(apply_btn)
        settings_actions.addWidget(cancel_btn)
        
        self.settings_layout.addWidget(self.settings_tabs)
        self.settings_layout.addLayout(settings_actions)
        
        # Initially show the auto view
        self.content_layout.addWidget(self.auto_view)
        self.settings_view.hide()
        self.content_layout.addWidget(self.settings_view)
        
        # Footer
        footer_layout = QHBoxLayout()
        page_label = QLabel('0')
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        project_label = QLabel('SEV/NW E04/P_2025_Project report')
        project_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        footer_layout.addStretch()
        footer_layout.addWidget(page_label)
        footer_layout.addStretch()
        footer_layout.addWidget(project_label)
        
        self.main_layout.addLayout(footer_layout)
        
        # Connect buttons to switch between views
        self.auto_btn.clicked.connect(self.show_auto_view)
        self.setting_btn.clicked.connect(self.show_settings_view)
    
    def show_auto_view(self):
        self.auto_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold; border: 1px solid black;")
        self.setting_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold; border: 1px solid black;")
        self.settings_view.hide()
        self.auto_view.show()
    
    def show_settings_view(self):
        self.setting_btn.setStyleSheet("background-color: #CCFF99; font-weight: bold; border: 1px solid black;")
        self.auto_btn.setStyleSheet("background-color: #D3D3D3; font-weight: bold; border: 1px solid black;")
        self.auto_view.hide()
        self.settings_view.show()

def main():
    app = QApplication(sys.argv)
    window = LinePacking()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()