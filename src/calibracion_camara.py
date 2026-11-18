import cv2
import numpy as np
import glob
import os

# ==============================================================================
# CONFIGURACIÓN (TABLERO ASIMÉTRICO)
# ==============================================================================

# Definir filas != columnas (ej. 8x6 esquinas internas)
CHESSBOARD_SHAPE = (7, 5)
DX, DY = 16.0, 17.0  # Tamaño del cuadrado en mm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PATRONES_PATH = '../data/patrones_calibracion/*.jpg'
PATRONES_PATH = os.path.join(SCRIPT_DIR, PATRONES_PATH)

OUTPUT_FILE = '../data/parametros_camara.npz'
OUTPUT_FILE = os.path.join(SCRIPT_DIR, OUTPUT_FILE)

SHOW_DEBUG = False # Mostrar las fotos con las detecciones de esquinas

def calibrar_camara():
    print("[INFO] Iniciando calibración para patrón asimétrico...")
    cols, rows = CHESSBOARD_SHAPE

    # 1. Coordenadas 3D del mundo real (Z = 0)
    objp = np.zeros((cols * rows, 3), np.float32)
    grid = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    objp[:, :2] = grid * np.array([DX, DY], dtype=np.float32)

    objpoints = []
    imgpoints = []

    images = glob.glob(PATRONES_PATH)
    if not images:
        print(f"[AVISO] No se encontraron imágenes en '{PATRONES_PATH}'.")
        return

    flags_corners = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SHAPE, flags=flags_corners)

        if ret:
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            objpoints.append(objp)
            imgpoints.append(corners_refined)

        if SHOW_DEBUG:
            if ret:
                img_debug = img.copy()
                cv2.drawChessboardCorners(img_debug, CHESSBOARD_SHAPE, corners_refined, ret)
                cv2.imshow("Verificación de Esquinas", img_debug)
                cv2.waitKey(1200)  # Muestra cada foto durante 1.2 segundos
            cv2.destroyAllWindows()

    # 2. Calibrar
    if len(objpoints) > 0:
        h, w = gray.shape[:2]
        rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (w, h), None, None)
        
        np.savez(OUTPUT_FILE, mtx=mtx, dist=dist)
        print(f"[ÉXITO] Calibrado con {len(objpoints)} fotos. Error RMS: {rms:.4f} px")
    else:
        print("[ERROR] No se pudo detectar el patrón en ninguna imagen.")

if __name__ == "__main__":
    calibrar_camara()