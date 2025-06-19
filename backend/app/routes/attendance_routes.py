# API chấm công
import cv2
import base64
from flask import Blueprint, request, jsonify
from app.services.facial_service import FacialRecognitionService

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/capture', methods=['POST'])
def capture_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Gọi hàm xử lý ảnh từ FacialRecognitionService
    success, message, processed_image = FacialRecognitionService.preproccess_image(image_file)
    if not success:
        return jsonify({"error": message}), 400
    
    # Lưu tạm ảnh trong request để dùng ở API /api/recognize
    request.imgage_data = processed_image
    return jsonify({"message": "Photo captured, proceeding to recognition"}), 200
    # Nếu nhận diện khuôn mặt thành công, trả lại ảnh đã xử lý (ví dụ: encode Base64 để trả về client)
    # _, encoded_image = cv2.imencode('.jpg', processed_image)
    # base64_image = base64.b64encode(encoded_image).decode('utf-8')

    # # Trả kết quả cho client
    # return jsonify({
    #     "message": "Face detected and image processed successfully",
    #     "image": base64_image  # Trả ảnh đã xử lý dưới dạng Base64
    # }), 200