
import os
import math
import random
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta 

import cv2
import dlib
import numpy as np
import face_recognition

# === Local imports ===
from app.models.employee import Employee
from app.models.face_training_data import FaceTrainingData

# --------------------------------------------------
# Load dlib predictors & detectors once at module import
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../app/services
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "shape_predictor_68_face_landmarks.dat"))
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Landmark model not found at %s" % MODEL_PATH)

_shape_predictor = dlib.shape_predictor(MODEL_PATH)
_face_detector = dlib.get_frontal_face_detector()

# --------------------------------------------------
# Utility – extract 68 landmarks as (68, 2) numpy array
# --------------------------------------------------

def _extract_landmarks(image_bgr: np.ndarray):
    """Return landmarks (68,2) or None if not exactly one face."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    rects = _face_detector(gray, 1)
    if len(rects) != 1:
        return None
    shape = _shape_predictor(gray, rects[0])
    coords = np.zeros((68, 2), dtype="float")
    for i in range(68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

# --------------------------------------------------
# LivenessChecker – unchanged internal logic but expects (68,2)
# --------------------------------------------------
class LivenessChecker:
    def __init__(self):
        # self.actions = ["blink", "smile", "turn_left", "turn_right", "nod"]
        self.actions = ['blink', 'smile'] # Vẫn giữ để sử dụng các hàm con

    def detect_blink(self, landmarks):
        def ear(eye):
            A = np.linalg.norm(eye[1] - eye[5])
            B = np.linalg.norm(eye[2] - eye[4])
            C = np.linalg.norm(eye[0] - eye[3])
            return (A + B) / (2.0 * C)
        left, right = landmarks[36:42], landmarks[42:48]
        return (ear(left) + ear(right)) / 2 < 0.25

    def detect_smile(self, landmarks):
        mouth = landmarks[48:68]
        width = np.linalg.norm(mouth[0] - mouth[6])
        height = np.linalg.norm(mouth[3] - mouth[9])
        ratio = (width / height) if height else 0
        return ratio > 3.0

    def detect_head_pose(self, landmarks):
        nose_tip, chin = landmarks[30], landmarks[8]
        left_eye = landmarks[36:42].mean(axis=0)
        right_eye = landmarks[42:48].mean(axis=0)
        angle_deg = math.degrees(math.atan2(right_eye[1]-left_eye[1], right_eye[0]-left_eye[0]))
        if angle_deg > 15:
            return "turn_left"
        if angle_deg < -15:
            return "turn_right"
        face_center_x = (landmarks[0][0] + landmarks[16][0]) / 2
        if abs(nose_tip[0] - face_center_x) < 5:
            return "nod"
        return "center"

# --------------------------------------------------
# Global Liveness Session Management
# --------------------------------------------------
# Lưu trữ trạng thái liveness cho mỗi phiên (session_id)
# Mỗi phiên sẽ lưu trữ một số khung hình gần nhất và trạng thái liveness
LIVENESS_SESSIONS = {}
SESSION_TIMEOUT_SECONDS = 5 # Thời gian chờ tối đa cho một phiên liveness (ví dụ: 5 giây)
MAX_FRAMES_PER_SESSION = 30 # Số lượng khung hình tối đa được lưu trữ cho mỗi phiên

# --------------------------------------------------
# FacialRecognitionService
# --------------------------------------------------
class FacialRecognitionService:
    liveness_checker = LivenessChecker()

    # ---------- Decoders / preprocess helpers ----------
    @staticmethod
    def _bytes_to_image(image_bytes: bytes):
        arr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    @staticmethod
    def preprocess_image(file_like):
        """Validate lighting & single face."""
        img = FacialRecognitionService._bytes_to_image(file_like.read())
        if img is None:
            return False, "Invalid image", None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if gray.mean() < 50:
            return False, "Insufficient lighting, please take photo in brighter place", None
        if len(face_recognition.face_locations(img)) != 1:
            return False, "Please ensure exactly one face is visible", None
        return True, "OK", img

    @staticmethod
    def decode_base64_image(b64: str):
        try:
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            return FacialRecognitionService._bytes_to_image(base64.b64decode(b64))
        except (ValueError, TypeError, base64.binascii.Error) as e:
            return None

    # ---------- Quality / pose ----------
    @staticmethod
    def calculate_image_quality(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
        contrast = gray.std()
        return min(100, (sharp/100)*50 + (contrast/50)*50)

    @staticmethod
    def detect_face_pose(img, locs):
        if not locs:
            return "unknown", 0.0
        t,r,b,l = locs[0]
        w,h = r-l, b-t
        ar = w / h if h > 0 else 1
        if ar > 1.2:
            return "left",0
        if ar <0.8:
            return "right",0
        if h> w*1.3:
            return "up",0
        if h< w*0.7:
            return "down",0
        return "front",0

    # ---------- Encoding with metadata ----------
    @staticmethod
    def generate_face_encoding_with_metadata(file_like, pose_type=None):
        ok,msg,img = FacialRecognitionService.preprocess_image(file_like)
        if not ok:
            return False,msg,None,None
        locs = face_recognition.face_locations(img)
        enc = face_recognition.face_encodings(img, locs)
        if not enc:
            return False,"Failed to generate encoding",None,None
        quality = FacialRecognitionService.calculate_image_quality(img)
        if not pose_type:
            pose_type,_ = FacialRecognitionService.detect_face_pose(img, locs)
        return True,"Success",enc[0].tobytes(),{"pose_type":pose_type,"image_quality_score":quality}

    # ---------- Liveness (Enhanced for sequence analysis) ----------
    @staticmethod
    def detect_liveness(img, session_id: str):
        # 1. Quản lý và dọn dẹp các phiên cũ
        current_time = datetime.now()
        for sid in list(LIVENESS_SESSIONS.keys()):
            if (current_time - LIVENESS_SESSIONS[sid]['last_update']).total_seconds() > SESSION_TIMEOUT_SECONDS:
                del LIVENESS_SESSIONS[sid]

        # 2. Khởi tạo/Cập nhật phiên hiện tại
        if session_id not in LIVENESS_SESSIONS:
            LIVENESS_SESSIONS[session_id] = {
                'frames_data': [], # Lưu trữ landmarks và timestamp
                'liveness_passed': False,
                'last_update': current_time,
                'blink_detected_in_session': False,
                'smile_detected_in_session': False
            }

        session_data = LIVENESS_SESSIONS[session_id]
        session_data['last_update'] = current_time

        # 3. Kiểm tra ánh sáng
        if np.std(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY))<10:
            # Nếu ánh sáng yếu, xóa phiên và báo lỗi
            if session_id in LIVENESS_SESSIONS:
                del LIVENESS_SESSIONS[session_id]
            return False,"The lighting is too dim, please try again in a brighter location."

        # 4. Trích xuất landmarks và kiểm tra phát hiện khuôn mặt
        landmarks = _extract_landmarks(img)
        if landmarks is None:
            return False,"Unable to detect the face, please look directly into the camera."

        # 5. Thêm dữ liệu khung hình hiện tại vào phiên
        session_data['frames_data'].append({
            'timestamp': current_time,
            'landmarks': landmarks
        })

        # 6. Dọn dẹp khung hình cũ hơn 5 giây
        session_data['frames_data'] = [
            f_data for f_data in session_data['frames_data']
            if (current_time - f_data['timestamp']).total_seconds() <= SESSION_TIMEOUT_SECONDS
        ]

        # Giới hạn số lượng khung hình để tránh tràn bộ nhớ
        if len(session_data['frames_data']) > MAX_FRAMES_PER_SESSION:
            session_data['frames_data'].pop(0)

        # 7. Phân tích chuỗi khung hình để phát hiện liveness
        # Chỉ cần một cái chớp mắt HOẶC một nụ cười
        if not session_data['liveness_passed']:
            checker = FacialRecognitionService.liveness_checker

            for frame_data in session_data['frames_data']:
                if not session_data['blink_detected_in_session'] and checker.detect_blink(frame_data['landmarks']):
                    session_data['blink_detected_in_session'] = True
                    break # Thoát vòng lặp nếu đã phát hiện

            for frame_data in session_data['frames_data']:
                if not session_data['smile_detected_in_session'] and checker.detect_smile(frame_data['landmarks']):
                    session_data['smile_detected_in_session'] = True
                    break # Thoát vòng lặp nếu đã phát hiện

            # Quyết định liveness: đã phát hiện chớp mắt HOẶC cười
            if session_data['blink_detected_in_session'] or session_data['smile_detected_in_session']:
                session_data['liveness_passed'] = True
                return True, "Kiểm tra sự sống thành công."
            else:
                # Nếu hết 5 giây mà không phát hiện, coi là thất bại
                if (current_time - session_data['frames_data'][0]['timestamp']).total_seconds() > SESSION_TIMEOUT_SECONDS:
                    del LIVENESS_SESSIONS[session_id] # Xóa phiên
                    return False, "No liveness action detected. Please try again and perform a blink or smile."
                return False, "Checking for liveness. Please keep your face clear and blink or smile."
        
        # Nếu liveness đã được xác nhận trong phiên này
        return True, "Liveness check successful."

    # ---------- Recognition ----------
    @staticmethod
    def recognize_face_with_multiple_encodings(img):
        """
        So khớp khuôn mặt trong ảnh với danh sách encoding đã lưu.
        Sử dụng chuẩn hóa vector, lọc theo pose và chất lượng ảnh, giới hạn threshold an toàn.
        """
        # 1. Trích xuất encoding từ ảnh mới
        face_locations = face_recognition.face_locations(img)
        if len(face_locations) != 1:
            return False, "Image must contain exactly one face", None

        encodings = face_recognition.face_encodings(img, face_locations)
        if not encodings:
            return False, "Failed to generate encoding", None

        current_encoding = encodings[0]
        current_encoding = current_encoding / np.linalg.norm(current_encoding)  # Normalize

        # 2. Phát hiện pose ảnh hiện tại (nếu có)
        pose_type, _ = FacialRecognitionService.detect_face_pose(img, face_locations)

        # 3. Truy xuất danh sách nhân sự đã training
        employees = Employee.query.filter_by(status=True, face_training_completed=True).all()
        if not employees:
            return False, "No employees have completed face training yet", None

        best_match = {
            "distance": float("inf"),
            "employee": None
        }

        for emp in employees:
            training_data_list = FaceTrainingData.get_employee_encodings(emp.employee_id)
            for d in training_data_list:
                # 3.1 Giải mã encoding & chuẩn hóa
                stored_encoding = np.frombuffer(d.face_encoding, dtype=np.float64)
                stored_encoding = stored_encoding / np.linalg.norm(stored_encoding)

                # 3.2 Lọc theo pose (nếu metadata có)
                if "pose_type" in d.metadata and d.metadata["pose_type"] != pose_type:
                    continue

                # 3.3 Lọc theo chất lượng
                if "image_quality_score" in d.metadata and d.metadata["image_quality_score"] < 35:
                    continue

                # 3.4 Tính khoảng cách cosine (tốt hơn Euclidean)
                dist = np.dot(current_encoding, stored_encoding)
                angle = np.arccos(np.clip(dist, -1.0, 1.0))  # cosine angle

                # 3.5 Chuyển angle thành khoảng cách giả lập để dễ dùng threshold
                pseudo_dist = 1 - dist

                if pseudo_dist < best_match["distance"]:
                    best_match["distance"] = pseudo_dist
                    best_match["employee"] = emp

        # 4. So sánh với ngưỡng chặt chẽ
        THRESHOLD = 0.35  # Có thể điều chỉnh từ 0.30 – 0.40 tùy yêu cầu chính xác
        if best_match["employee"] and best_match["distance"] < THRESHOLD:
            return True, "Face recognized successfully", best_match["employee"]
        else:
            return False, "Face does not match any registered employee", None


    @staticmethod
    def recognize_face_with_liveness(img, session_id: str): # Bổ sung tham số session_id
        live_ok, live_msg = FacialRecognitionService.detect_liveness(img, session_id)
        if not live_ok:
            return False, live_msg, None
        
        # Nếu liveness đã passed, tiếp tục nhận diện
        return FacialRecognitionService.recognize_face_with_multiple_encodings(img)

    # ---------- Misc ----------
    @staticmethod
    def get_required_poses():
        return ["front","left","right","up","down"]