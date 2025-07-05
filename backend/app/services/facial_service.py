"""FacialRecognitionService – revised
-------------------------------------------------
• Uses dlib shape predictor (68 landmarks) for reliable liveness checks.
• Handles both file uploads (bytes) and base64 strings.
• Unified helper for extracting landmarks, no KeyError anymore.
"""

# === Standard library ===
import os
import math
import random
import base64
from io import BytesIO
from PIL import Image

# === Third‑party libs ===
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
        self.actions = ['blink', 'smile']

    # ... (same functions detect_blink / detect_smile / detect_head_pose)
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
            return "left",0.0
        if ar <0.8:
            return "right",0.0
        if h> w*1.3:
            return "up",0.0
        if h< w*0.7:
            return "down",0.0
        return "front",0.0

    # ---------- Encoding with metadata ----------
    @staticmethod
<<<<<<< Updated upstream
    def recognize_face_with_liveness(image_file):
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

        # Truy vấn danh sách nhân viên đã đăng ký khuôn mặt
        employees = Employee.query.all()
=======
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

    # ---------- Liveness ----------
    @staticmethod
    def detect_liveness(img, required_action=None):
        if np.std(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY))<10:
            return False,"Lighting too low"
        landmarks = _extract_landmarks(img)
        if landmarks is None:
            return False,"Unable to detect a single face for liveness check"
        if required_action is None:
            required_action = random.choice(FacialRecognitionService.liveness_checker.actions)
        checker = FacialRecognitionService.liveness_checker
        if required_action=="blink":
            if not checker.detect_blink(landmarks):
                return False,"Please blink for liveness check"
        elif required_action=="smile":
            if not checker.detect_smile(landmarks):
                return False,"Please smile for liveness check"
        elif required_action in {"turn_left","turn_right","nod"}:
            if checker.detect_head_pose(landmarks)!=required_action:
                return False,f"Please {required_action.replace('_',' ')} for liveness check"
        return True,f"Liveness passed ({required_action})"

    # ---------- Recognition ----------
    @staticmethod
    def recognize_face_with_multiple_encodings(img):
        live_ok, live_msg = FacialRecognitionService.detect_liveness(img)
        if not live_ok:
            return False, live_msg, None
        enc = face_recognition.face_encodings(img)
        if not enc:
            return False,"Failed to generate encoding",None
        current = enc[0]
        employees = Employee.query.filter_by(status=True, face_training_completed=True).all()
>>>>>>> Stashed changes
        if not employees:
            return False,"No employees have completed face training yet",None
        best_dist,best_emp = float("inf"),None
        for emp in employees:
            td = FaceTrainingData.get_employee_encodings(emp.employee_id)
            for d in td:
                stored = np.frombuffer(d.face_encoding, dtype=np.float64)
                dist = face_recognition.face_distance([stored], current)[0]
                dist *= (1+(100-d.image_quality_score)/100)
                if dist<best_dist:
                    best_dist,best_emp = dist,emp
        return (True,"Face recognized successfully",best_emp) if best_dist<0.5 else (False,"Face does not match any registered employee",None)

<<<<<<< Updated upstream
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
=======
    @staticmethod
    def recognize_face_with_liveness(img):
        return FacialRecognitionService.recognize_face_with_multiple_encodings(img)

    # ---------- Misc ----------
    @staticmethod
    def get_required_poses():
        return ["front","left","right","up","down"]
>>>>>>> Stashed changes
