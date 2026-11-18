import cv2
import numpy as np
import mediapipe as mp
from sistema_seguridad import SistemaSeguridad
import interfaz as ui
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MASKS_DATA = [
    {"path": os.path.join(SCRIPT_DIR,"../assets/mask_1.png"), "eye_left": (150, 200), "eye_right": (350, 200), "name": "Masc. 1"},
    {"path": os.path.join(SCRIPT_DIR,"../assets/mask_2.png"), "eye_left": (160, 210), "eye_right": (340, 210), "name": "Masc. 2"}
]
loaded_masks = []
for m in MASKS_DATA:
    img = cv2.imread(m["path"], cv2.IMREAD_UNCHANGED)
    if img is not None:
        if img.shape[2] == 3:
            b, g, r = cv2.split(img)
            alpha = np.ones(b.shape, dtype=b.dtype) * 255
            img = cv2.merge((b, g, r, alpha))
        loaded_masks.append({"img": img, "pts_png": np.float32([m["eye_left"], m["eye_right"]]), "name": m["name"]})

def aplicar_mascara_afin(frame, mask_info, eye_left_frame, eye_right_frame):
    pts_src = mask_info["pts_png"]
    pts_dst = np.float32([eye_left_frame, eye_right_frame])
    M, _ = cv2.estimateAffinePartial2D(pts_src, pts_dst)
    if M is None: return frame
    h_f, w_f = frame.shape[:2]
    warped_mask = cv2.warpAffine(mask_info["img"], M, (w_f, h_f), flags=cv2.INTER_LINEAR, borderValue=(0,0,0,0))
    alpha = (warped_mask[:, :, 3] / 255.0)[:, :, np.newaxis]
    frame[:h_f, :w_f] = (alpha * warped_mask[:, :, :3] + (1.0 - alpha) * frame[:h_f, :w_f]).astype(np.uint8)
    return frame

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    seguridad = SistemaSeguridad()
    
    mp_face_mesh = mp.solutions.face_mesh
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    selected_mask_idx = 0
    show_debug_lines = True
    last_touch_time = 0.0

    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh, \
         mp_hands.Hands(max_num_hands=1) as hands:

        while True:
            success, frame = cap.read()
            if not success: break
            frame = cv2.flip(frame, 1)
            h_frame, w_frame = frame.shape[:2]

            if seguridad.bloqueado:
                frame = seguridad.procesar_frame(frame)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 1. Obtenemos botones desde el módulo UI
                buttons = ui.obtener_geometria_botones(w_frame, loaded_masks, show_debug_lines)

                # 2. Extracción de coordenadas de la mano
                hand_res = hands.process(rgb_frame)
                finger_tip = None
                if hand_res.multi_hand_landmarks:
                    for hand_landmarks in hand_res.multi_hand_landmarks:
                        if show_debug_lines:
                            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        ix = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w_frame)
                        iy = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h_frame)
                        finger_tip = (ix, iy)

                # 3. Procesar toques en UI mediante interfaz.py
                selected_mask_idx, show_debug_lines, last_touch_time = ui.procesar_interaccion_botones(
                    finger_tip, buttons, selected_mask_idx, show_debug_lines, last_touch_time
                )

                # 4. Processing Facial y aplicación de la máscara
                face_res = face_mesh.process(rgb_frame)
                if face_res.multi_face_landmarks:
                    for face_landmarks in face_res.multi_face_landmarks:
                        pt_l = face_landmarks.landmark[33]
                        pt_r = face_landmarks.landmark[263]
                        pt_m = face_landmarks.landmark[13]
                        eye_l = (int(pt_l.x * w_frame), int(pt_l.y * h_frame))
                        eye_r = (int(pt_r.x * w_frame), int(pt_r.y * h_frame))
                        mouth = (int(pt_m.x * w_frame), int(pt_m.y * h_frame))
                        
                        xs = [int(lm.x * w_frame) for lm in face_landmarks.landmark]
                        ys = [int(lm.y * h_frame) for lm in face_landmarks.landmark]
                        bbox_face = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

                        if len(loaded_masks) > 0 and selected_mask_idx < len(loaded_masks):
                            frame = aplicar_mascara_afin(frame, loaded_masks[selected_mask_idx], eye_l, eye_r)

                        # Renderizado del modo debug facial mediante interfaz.py
                        if show_debug_lines:
                            frame = ui.renderizar_capa_debug(frame, bbox_face, eye_l, eye_r, mouth)

                # 5. Renderizado final de botones y cursor táctil mediante interfaz.py
                frame = ui.renderizar_ui(frame, buttons, selected_mask_idx, show_debug_lines, finger_tip)

            cv2.imshow('Proyecto Final', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()