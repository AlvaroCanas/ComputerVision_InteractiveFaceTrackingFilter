import cv2
import numpy as np

COLOR_RANGES = {
    "ROJO": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (180, 255, 255))],
    "VERDE": [((40, 50, 50), (80, 255, 255))],
    "AZUL": [((95, 120, 50), (135, 255, 255))]
}
SECUENCIA_OBJETIVO = ["ROJO", "VERDE", "AZUL"]

class SistemaSeguridad:
    def __init__(self):
        self.paso_actual = 0
        self.bloqueado = True
        self.esperando_retirada = False

    def procesar_frame(self, frame_bgr):
        # Si ya se ha superado la secuencia o el sistema está desbloqueado, retornar directamente
        if not self.bloqueado or self.paso_actual >= len(SECUENCIA_OBJETIVO):
            self.bloqueado = False
            return frame_bgr

        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        target_color = SECUENCIA_OBJETIVO[self.paso_actual]
        
        mask_combined = None
        for (lower, upper) in COLOR_RANGES[target_color]:
            m = cv2.inRange(frame_hsv, np.array(lower), np.array(upper))
            mask_combined = m if mask_combined is None else cv2.bitwise_or(mask_combined, m)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detectado = False
        
        if contours:
            c_max = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c_max) > 2500:
                detectado = True
                x, y, w, h = cv2.boundingRect(c_max)
                
                # Feedback de Interfaz
                color_bgr = (0, 0, 255) if target_color == "ROJO" else (0, 255, 0) if target_color == "VERDE" else (255, 0, 0)
                cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), color_bgr, 3)
                cv2.putText(frame_bgr, f"{target_color} OK - RETIRE BOLA", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
                
                if not self.esperando_retirada:
                    self.esperando_retirada = True

        # Lógica para avanzar de estado
        if not detectado and self.esperando_retirada:
            self.paso_actual += 1
            self.esperando_retirada = False
            if self.paso_actual >= len(SECUENCIA_OBJETIVO):
                self.bloqueado = False
                return frame_bgr

        # Dibujar interfaz de bloqueo si continúa bloqueado
        if self.bloqueado:
            cv2.rectangle(frame_bgr, (0, 0), (frame_bgr.shape[1], 80), (30, 30, 30), -1)
            msg = f"ESPERANDO {target_color}" if not self.esperando_retirada else f"RETIRE {target_color}"
            cv2.putText(frame_bgr, f"SEGURIDAD: {msg}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame_bgr, f"Progreso: {self.paso_actual}/{len(SECUENCIA_OBJETIVO)}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return frame_bgr