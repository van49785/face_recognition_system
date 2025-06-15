# Nhận diện khuôn mặt
import cv2 
import numpy as np 
import face_recognition

class FacialRecognitionService:
    '''
    Dịch vụ nhận diện khuôn mặt
    '''
    @staticmethod
    def preproccess_image(image_file):
        '''
        Tiền xử lý hình ảnh: kiểm tra ánh sáng, đảm bảo có một khuôn mặt
        Trả về: (bool, str, image) - (thành công, thông điệp lỗi, ảnh đã xử lý)
        '''

        # Đọc ảnh từ file
        image_data = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if image is None:
            return False, "Invalid image", None
        
        # Kiểm tra ánh sáng (dùng độ sáng trung bình của ảnh grayscale)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)

        if mean_brightness < 50: # Ngưỡng ánh sáng tối thiểu
            return False, "Insufficient lighting, please improve lighting", None
        
        # Phát hiện khuôn mặt
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            return False, "No face detected, please ensure a clear face is visible", None
        if len(face_locations) > 1:
            return False, "Multiple faces detected, please ensure only one face is visible", None
        
        return True, "Image processed successfully", image
    
    
