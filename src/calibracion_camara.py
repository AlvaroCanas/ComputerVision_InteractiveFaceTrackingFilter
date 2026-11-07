import cv2
import numpy as np
import glob
import os

def calibrar_camara():
    print("[INFO] Iniciando calibración offline...")
    chessboard_shape = (8, 6)
    dx, dy = 30.0, 30.0 # Tamaño de la cuadrícula

    # Puntos 3D anclados al tablero
    objp = np.zeros((chessboard_shape[0] * chessboard_shape[1], 3), np.float32)
    grid = np.mgrid[0:chessboard_shape[0], 0:chessboard_shape[1]].T.reshape(-1, 2)
    objp[:, :2] = grid * np.array([dx, dy], dtype=np.float32)

    objpoints = [] 
    imgpoints = [] 

    # Cambia esto por la ruta donde guardes las fotos del tablero
    images = glob.glob('./patrones_calibracion/*.jpg')
    if not images:
        print("[AVISO] No se encontraron imágenes en './patrones_calibracion/'.")
        return

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_shape, None)
        
        if ret:
            objpoints.append(objp)
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                               (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners_refined)

    if len(objpoints) > 0:
        h, w = gray.shape[::-1]
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (w, h), None, None)
        
        np.savez("parametros_camara.npz", mtx=mtx, dist=dist)
        print(f"[ÉXITO] Calibración completada. Error RMS: {ret:.4f}")
    else:
        print("[ERROR] No se pudo detectar el patrón en ninguna imagen.")

if __name__ == "__main__":
    calibrar_camara()