import cv2
import time

# --- CONFIGURACIÓN DE ESTILOS Y COLORES (Ajusta aquí tu diseño) ---
COLOR_BOTON_ACTIVO = (0, 180, 0)      # Verde
COLOR_BOTON_INACTIVO = (70, 70, 70)   # Gris oscuro
COLOR_TEXTO = (255, 255, 255)         # Blanco
COLOR_BORDER = (255, 255, 255)        # Blanco
COLOR_DEBUG_FACE = (255, 255, 0)      # Cian
COLOR_DEBUG_LINES = (255, 0, 0)       # Azul
COLOR_FINGER = (0, 255, 255)          # Amarillo

def obtener_geometria_botones(w_frame, loaded_masks, show_debug_lines):
    """Genera la lista de regiones e información visual de los botones."""
    btn_w, btn_h = 110, 45
    buttons = []
    
    # Botones dinámicos para cada máscara cargada
    for idx, mask_info in enumerate(loaded_masks):
        x1 = 20 + idx * (btn_w + 10)
        y1 = 20
        buttons.append({
            "rect": (x1, y1, x1 + btn_w, y1 + btn_h),
            "label": mask_info["name"],
            "action": "SELECT_MASK",
            "val": idx
        })
        
    # Botón Toggle Debug
    buttons.append({
        "rect": (w_frame - 160, 20, w_frame - 20, 20 + btn_h),
        "label": f"Debug: {'ON' if show_debug_lines else 'OFF'}",
        "action": "TOGGLE_DEBUG",
        "val": None
    })
    
    return buttons

def procesar_interaccion_botones(finger_tip, buttons, selected_mask_idx, show_debug_lines, last_touch_time):
    """Evalúa si la punta del dedo colisiona con algún botón y aplica la acción."""
    if not finger_tip:
        return selected_mask_idx, show_debug_lines, last_touch_time

    ix, iy = finger_tip
    curr_time = time.time()

    if curr_time - last_touch_time > 0.5: # Antirrebote de 0.5s
        for btn in buttons:
            x1, y1, x2, y2 = btn["rect"]
            if x1 <= ix <= x2 and y1 <= iy <= y2:
                last_touch_time = curr_time
                if btn["action"] == "SELECT_MASK":
                    selected_mask_idx = btn["val"]
                elif btn["action"] == "TOGGLE_DEBUG":
                    show_debug_lines = not show_debug_lines
                break

    return selected_mask_idx, show_debug_lines, last_touch_time

def renderizar_ui(frame, buttons, selected_mask_idx, show_debug_lines, finger_tip):
    """Dibuja los botones de la interfaz y el puntero táctil del dedo."""
    for btn in buttons:
        x1, y1, x2, y2 = btn["rect"]
        is_active = (btn["action"] == "SELECT_MASK" and btn["val"] == selected_mask_idx) or \
                    (btn["action"] == "TOGGLE_DEBUG" and show_debug_lines)
        
        color_bg = COLOR_BOTON_ACTIVO if is_active else COLOR_BOTON_INACTIVO
        
        # Renderizado de cajas y textos
        cv2.rectangle(frame, (x1, y1), (x2, y2), color_bg, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_BORDER, 1)
        cv2.putText(frame, btn["label"], (x1 + 10, y1 + 28), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXTO, 1)

    # Dibujar puntero del dedo en pantalla
    if finger_tip:
        cv2.circle(frame, finger_tip, 8, COLOR_FINGER, -1)
        cv2.circle(frame, finger_tip, 12, (255, 0, 255), 2)

    return frame

def renderizar_capa_debug(frame, bbox_face, eye_l, eye_r, mouth):
    """Dibuja la superposición de líneas de tracking facial y cajas de debug."""
    if bbox_face:
        bx, by, bw, bh = bbox_face
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), COLOR_DEBUG_FACE, 2)
    
    if eye_l and eye_r and mouth:
        overlay = frame.copy()
        cv2.line(overlay, eye_l, eye_r, COLOR_DEBUG_LINES, 3)
        cv2.line(overlay, eye_l, mouth, (0, 255, 255), 2)
        cv2.line(overlay, eye_r, mouth, (0, 255, 255), 2)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    return frame