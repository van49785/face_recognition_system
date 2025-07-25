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
import insightface

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
_face_analyzer = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
_face_analyzer.prepare(ctx_id=0)

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
        # Hàm này không được sử dụng trực tiếp trong liveness check hiện tại, chỉ dùng để minh họa
        # và sẽ không thay đổi để giữ nguyên tên hàm
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
        
        # Sử dụng InsightFace để phát hiện khuôn mặt thay vì face_recognition
        faces = _face_analyzer.get(img)
        if not faces or len(faces) != 1:
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
        """Tính toán điểm chất lượng ảnh dựa trên độ sắc nét và độ tương phản."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
        contrast = gray.std()
        # Công thức heuristic, có thể cần hiệu chỉnh thêm
        return min(100, (sharp/100)*50 + (contrast/50)*50)

    @staticmethod
    def _get_pose_from_angles(pitch, yaw, roll):
        """
        Chuyển đổi các góc pitch, yaw, roll thành các loại pose định tính.
        Dựa trên ngưỡng áng chừng, cần kiểm tra và tinh chỉnh.
        """
        # Ngưỡng (có thể điều chỉnh)
        yaw_threshold = 15 # degrees for left/right
        pitch_threshold = 15 # degrees for up/down

        if yaw > yaw_threshold:
            return "right" # quay sang phải
        elif yaw < -yaw_threshold:
            return "left" # quay sang trái
        elif pitch > pitch_threshold:
            return "down" # nhìn xuống
        elif pitch < -pitch_threshold:
            return "up" # nhìn lên
        else:
            return "front" # chính diện

    @staticmethod
    def detect_face_pose(img, faces): # Thay đổi tham số, nhận directly faces object từ InsightFace
        """
        Xác định loại pose khuôn mặt dựa trên thông tin từ InsightFace.
        """
        if not faces or len(faces) != 1:
            return "unknown", 0.0 # Không phát hiện được hoặc nhiều hơn 1 khuôn mặt

        face = faces[0]
        # InsightFace cung cấp các góc pitch, yaw, roll
        pitch = face.pose[0] # Góc nghiêng lên/xuống
        yaw = face.pose[1]   # Góc quay trái/phải
        roll = face.pose[2]  # Góc nghiêng đầu

        pose_type = FacialRecognitionService._get_pose_from_angles(pitch, yaw, roll)
        
        # Độ tin cậy (có thể là 1 - khoảng cách từ 0,0,0 nếu muốn)
        # Hiện tại trả về 0.0 vì hàm gốc cũng trả về 0.0 cho độ tin cậy.
        return pose_type, 0.0 

    # ---------- NEW: Helper function to check and update training completion ----------
    @staticmethod
    def check_and_update_training_completion(employee_id):
        """Kiểm tra và cập nhật trạng thái training completion sau khi thêm pose mới"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                print(f"⚠️ Không tìm thấy nhân viên với ID: {employee_id}")
                return False
            
            # Kiểm tra đủ pose và chất lượng
            has_sufficient, missing_poses = FaceTrainingData.has_sufficient_poses(
                employee_id, min_quality=35
            )
            
            print(f"🔍 Kiểm tra training completion cho {employee_id}:")
            print(f"   - Đủ pose: {has_sufficient}")
            print(f"   - Pose còn thiếu: {missing_poses}")
            print(f"   - Training completed hiện tại: {employee.face_training_completed}")
            
            if has_sufficient and not employee.face_training_completed:
                print(f"✅ Cập nhật training completion cho {employee_id}")
                employee.complete_face_training()
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật training completion cho {employee_id}: {e}")
            return False

    # ---------- Encoding with metadata (FIXED) ----------
    @staticmethod
    def generate_face_encoding_with_metadata(file_like, pose_type=None, employee_id=None):
        """
        Tiền xử lý ảnh, phát hiện khuôn mặt và sinh ra vector encoding (512D, ArcFace).
        FIXED: Thêm tham số employee_id và logic auto-update training completion
        
        Args:
            file_like: File object chứa ảnh
            pose_type: Loại pose (để tương thích ngược)
            employee_id: ID nhân viên (để cập nhật training completion)
            
        Returns:
            (thành công, thông báo, vector bytes, metadata dict)
        """
        # 1. Đọc ảnh và kiểm tra điều kiện ánh sáng
        img = FacialRecognitionService._bytes_to_image(file_like.read())
        if img is None:
            return False, "Invalid image", None, None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if gray.mean() < 50:
            return False, "Insufficient lighting, please take photo in brighter place", None, None

        # 2. Phát hiện khuôn mặt và sinh encoding bằng InsightFace
        faces = _face_analyzer.get(img)
        if not faces or len(faces) != 1:
            return False, "Please ensure exactly one face is visible", None, None

        face = faces[0]
        embedding = face.embedding.astype(np.float32).tobytes()  # Lưu vector 512D dạng bytes

        # 3. Tính chất lượng ảnh đầu vào
        quality = FacialRecognitionService.calculate_image_quality(img)

        # 4. Tự động xác định pose nếu chưa cung cấp
        # Sử dụng detect_face_pose mới để xác định pose
        auto_detected_pose, _ = FacialRecognitionService.detect_face_pose(img, faces) 
        if not pose_type:
            pose_type = auto_detected_pose

        metadata = {
            "pose_type": pose_type,
            "image_quality_score": quality
        }

        # 5. NEW: Kiểm tra và cập nhật training completion sau khi tạo encoding thành công
        if employee_id:
            print(f"🎯 Đã tạo encoding thành công cho {employee_id}, pose: {pose_type}")
            # Chạy async để không ảnh hưởng đến luồng chính
            try:
                FacialRecognitionService.check_and_update_training_completion(employee_id)
            except Exception as e:
                print(f"⚠️ Lỗi khi cập nhật training completion: {e}")
                # Không return False vì encoding đã tạo thành công

        return True, "Success", embedding, metadata

    # ---------- NEW: Batch update function for existing data ----------
    @staticmethod
    def fix_existing_training_data():
        """
        Khắc phục dữ liệu training cho các nhân viên đã train đủ nhưng chưa được đánh dấu completed
        """
        print("🔧 Bắt đầu khắc phục dữ liệu training hiện có...")
        
        try:
            employees = Employee.query.all()
            updated_count = 0
            
            for emp in employees:
                # Kiểm tra số pose hiện có
                pose_count = FaceTrainingData.get_employee_pose_count(emp.employee_id)
                has_sufficient, missing_poses = FaceTrainingData.has_sufficient_poses(
                    emp.employee_id, min_quality=35
                )
                
                print(f"📊 Nhân viên {emp.employee_id} ({emp.full_name}):")
                print(f"   - Số pose: {pose_count}")
                print(f"   - Đủ pose: {has_sufficient}")
                print(f"   - Training completed: {emp.face_training_completed}")
                
                if has_sufficient and not emp.face_training_completed:
                    print(f"   ✅ Cập nhật training status...")
                    emp.complete_face_training()
                    updated_count += 1
                elif emp.face_training_completed and not has_sufficient:
                    print(f"   ⚠️ Dữ liệu không nhất quán: đã completed nhưng không đủ pose")
                
                print()
            
            print(f"🎉 Hoàn thành! Đã cập nhật {updated_count} nhân viên.")
            return updated_count
            
        except Exception as e:
            print(f"❌ Lỗi khi khắc phục dữ liệu: {e}")
            return 0

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
        landmarks = _extract_landmarks(img) # Vẫn dùng dlib landmarks cho liveness
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
                    # Không break ở đây để vẫn có thể tìm thấy nụ cười trong cùng phiên
            
            for frame_data in session_data['frames_data']:
                if not session_data['smile_detected_in_session'] and checker.detect_smile(frame_data['landmarks']):
                    session_data['smile_detected_in_session'] = True
                    # Không break ở đây để vẫn có thể tìm thấy chớp mắt trong cùng phiên

            # Quyết định liveness: đã phát hiện chớp mắt HOẶC cười
            if session_data['blink_detected_in_session'] or session_data['smile_detected_in_session']:
                session_data['liveness_passed'] = True
                return True, "Kiểm tra sự sống thành công."
            else:
                # Nếu hết 5 giây mà không phát hiện, coi là thất bại
                # Đảm bảo có ít nhất 1 khung hình trong session_data['frames_data'] trước khi truy cập
                if session_data['frames_data'] and (current_time - session_data['frames_data'][0]['timestamp']).total_seconds() > SESSION_TIMEOUT_SECONDS:
                    del LIVENESS_SESSIONS[session_id] # Xóa phiên
                    return False, "No liveness action detected. Please try again and perform a blink or smile."
                return False, "Checking for liveness. Please keep your face clear and blink or smile."
        
        # Nếu liveness đã được xác nhận trong phiên này
        return True, "Liveness check successful."

    # ---------- Recognition ----------
    @staticmethod
    def recognize_face_with_multiple_encodings(img):
        """
        Nhận diện khuôn mặt bằng InsightFace (ArcFace), đã fix chuẩn hóa vector và log chi tiết.
        Bây giờ so sánh với TẤT CẢ các pose đã train của nhân viên.
        """
        # 1. Phát hiện khuôn mặt và lấy embedding
        faces = _face_analyzer.get(img)
        if not faces or len(faces) != 1:
            return False, "Image must contain exactly one face", None

        # 2. Chuẩn hóa vector query
        query_embedding = faces[0].embedding.astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding) # Chuẩn hóa L2

        # 3. Lấy danh sách nhân viên
        # Chỉ lấy nhân viên đang active và đã hoàn tất training
        employees = Employee.query.filter_by(status=True, face_training_completed=True).all()
        if not employees:
            return False, "No employees have completed face training yet", None

        best_match = {
            "distance": float("inf"),
            "employee": None
        }

        for emp in employees:
            training_data_list = FaceTrainingData.get_employee_encodings(emp.employee_id)
            if not training_data_list: # Bỏ qua nếu không có dữ liệu training
                continue

            for d in training_data_list:
                try:
                    stored_embedding = np.frombuffer(d.face_encoding, dtype=np.float32)
                    if stored_embedding.shape[0] != 512: # Đảm bảo đúng kích thước
                        print(f"Lỗi: Kích thước embedding của {emp.employee_id} không đúng (phải là 512).")
                        continue
                    stored_embedding = stored_embedding / np.linalg.norm(stored_embedding) # Chuẩn hóa L2
                except Exception as e:
                    print(f"❌ Lỗi giải mã hoặc chuẩn hóa vector từ DB của {emp.employee_id}: {e}")
                    continue

                # Chỉ lọc dựa trên image_quality_score, không lọc pose_type nữa
                # Lý do: InsightFace mạnh mẽ hơn với các biến thể pose, sử dụng tất cả training data
                # để tìm match tốt nhất sẽ tăng robustness.
                if d.image_quality_score is not None and d.image_quality_score < 35:
                    continue

                # Tính độ tương đồng cosine (cosine distance = 1 - cosine similarity)
                cos_sim = np.dot(query_embedding, stored_embedding)
                pseudo_dist = 1 - cos_sim

                if pseudo_dist < best_match["distance"]:
                    best_match["distance"] = pseudo_dist
                    best_match["employee"] = emp

        # 4. So sánh với ngưỡng
        THRESHOLD = 0.35  # Ngưỡng có thể điều chỉnh sau khi thử nghiệm thực tế.
                          # Khoảng cách nhỏ hơn -> tương đồng cao hơn.
        if best_match["employee"] and best_match["distance"] < THRESHOLD:
            print(f"✅ Tìm thấy khớp: {best_match['employee'].employee_id} – Khoảng cách: {best_match['distance']:.4f}")
            return True, "Face recognized successfully", best_match["employee"]
        else:
            print(f"❌ Không tìm thấy nhân viên phù hợp. Khoảng cách tốt nhất: {best_match['distance']:.4f}")
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