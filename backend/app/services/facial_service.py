# Nhận diện khuôn mặt
import cv2 
import numpy as np 
import face_recognition
from app.models.employee import Employee

class FacialRecognitionService:
    '''
    Dịch vụ nhận diện khuôn mặt
    '''

    @staticmethod
    def preprocess_image(image_file):
        '''
        Tiền xử lý hình ảnh: kiểm tra ánh sáng, đảm bảo có một khuôn mặt
        Trả về: (bool, str, image) - (thành công, thông điệp lỗi, ảnh đã xử lý)
        '''

        # Đọc ảnh từ file thành mảng numpy
        image_data = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        # Kiểm tra ảnh có hợp lệ không
        if image is None:
            return False, "Invalid image", None
        
        # Chuyển ảnh sang grayscale để kiểm tra ánh sáng
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)  # Độ sáng trung bình của ảnh

        # Nếu ảnh quá tối
        if mean_brightness < 50:  # Ngưỡng ánh sáng tối thiểu
            return False, "Insufficient lighting, please take a photo in better lighting", None
        
        # Phát hiện vị trí các khuôn mặt trong ảnh
        face_locations = face_recognition.face_locations(image)

        # Không phát hiện khuôn mặt
        if len(face_locations) == 0:
            return False, "No face detected, please ensure your face is clearly visible", None
        
        # Nhiều hơn 1 khuôn mặt
        if len(face_locations) > 1:
            return False, "Multiple faces detected, please ensure only one face is visible", None
        
        # Ảnh hợp lệ và có đúng 1 khuôn mặt
        return True, "Image is valid and has been processed", image
        

    @staticmethod
    def generate_face_encoding(image_file):
        '''
        Tạo face encoding từ ảnh để lưu vào cơ sở dữ liệu
        Trả về: (bool, str, encoding_bytes)
        '''

        # Tiền xử lý ảnh trước
        success, message, processed_image = FacialRecognitionService.preprocess_image(image_file)

        if not success:
            return False, message, None
        
        # Tạo face encoding từ ảnh
        encodings = face_recognition.face_encodings(processed_image)

        if not encodings:
            return False, "Failed to generate face encoding", None
        
        # Trả về encoding dưới dạng bytes
        return True, "Face encoding generated successfully", encodings[0].tobytes()
    

    @staticmethod
    def detect_liveness(image):
        '''
        Phát hiện giả mạo cơ bản dựa trên độ tương phản ảnh
        Trả về: (bool, str)
        '''

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)  # Độ lệch chuẩn ánh sáng

        # Nếu độ lệch chuẩn quá thấp → ảnh phẳng, khả năng cao là ảnh giấy/tĩnh
        if std_brightness < 10:
            return False, "Possible spoof detected, please use a live face in front of the camera"
        
        return True, "Liveness check passed"
    

    @staticmethod
    def recognize_face_with_liveness(processed_image: np.ndarray):
        '''
        Nhận diện khuôn mặt với kiểm tra chống giả mạo
        Đầu vào: ảnh numpy.ndarray đã được xử lý sẵn
        Trả về: (bool, str, employee hoặc None)
        '''

        # Kiểm tra chống giả mạo (phân biệt ảnh thật/giả)
        liveness_success, liveness_message = FacialRecognitionService.detect_liveness(processed_image)
        if not liveness_success:
            return False, liveness_message, None

        # Tạo face encoding từ ảnh
        face_encodings = face_recognition.face_encodings(processed_image)
        if not face_encodings:
            return False, "Failed to generate face encoding", None

        # Lấy danh sách nhân viên đã đăng ký khuôn mặt
        employees = Employee.query.filter_by(status=True).all()
        if not employees:
            return False, "No employees have registered their face yet", None

        best_match_distance = float('inf')
        best_match_employee = None
        face_encoding = face_encodings[0]

        # So sánh encoding với từng nhân viên đã lưu
        for employee in employees:
            if employee.face_encoding:
                stored_encoding = np.frombuffer(employee.face_encoding, dtype=np.float64)
                distances = face_recognition.face_distance([stored_encoding], face_encoding)

                if distances[0] < best_match_distance:
                    best_match_distance = distances[0]
                    best_match_employee = employee

        if best_match_distance < 0.4:
            return True, "Face recognized successfully", best_match_employee

        return False, "Face does not match any registered employee", None

