# Sistema de Filtros AR y Control Gestual con Seguridad Óptica

**Asignatura:** Visión por Ordenador I  
**Grado:** Ingeniería Matemática — Comillas ICAI  
**Curso:** 2026/2027  

---

## 📌 Descripción del Proyecto

Este proyecto implementa una aplicación interactiva en tiempo real utilizando OpenCV y MediaPipe. El sistema se compone de dos bloques principales:

1. **Sistema de Seguridad (Decodificador de Patrones Ópticos):**  
   Máquina de estados de acceso que valida la entrada mediante la detección y retirada secuencial de 3 patrones de color (**ROJO**, **VERDE** y **AZUL**) procesados en el espacio de color HSV.

2. **Sistema Propuesto (Tracker Facial AR e Interfaz Táctil Air-Touch):**  
   - **Tracker Facial Adaptativo:** Ajuste de posición, rotación y escala de máscaras AR mediante transformaciones afines de 2D (`cv2.estimateAffinePartial2D` y `cv2.warpAffine`) basadas en puntos de anclaje de ojos con MediaPipe Face Mesh.
   - **Interfaz Virtual Air-Touch:** Control por gestos táctiles mediante el seguimiento del dedo índice con MediaPipe Hands, permitiendo conmutar entre diferentes máscaras y activar/desactivar la capa de supervisión en tiempo real (*modo debug*).

---

## 🏗️ Arquitectura del Proyecto

```text
.
├── calibracion_camara.py    # Módulo de calibración offline mediante tablero de ajedrez
├── sistema_seguridad.py     # Lógica de la máquina de estados y segmentación HSV
├── interfaz.py              # Geometría de UI, detección de toques virtuales y debug
├── main.py                  # Bucle principal de ejecución e integración MediaPipe
├── Proyecto/                # Recursos gráficos (imágenes PNG de máscaras con canal Alfa)
│   ├── mask_1.png
│   └── mask_2.png
├── patrones_calibracion/    # Imágenes del tablero para calibración offline (excluidas en .gitignore)
│   └── .gitkeep             # Archivo para conservar la estructura de carpetas en Git
├── requirements.txt         # Dependencias ancladas del entorno
├── .gitignore               # Exclusiones de Git
└── README.md                # Documentación del repositorio
```

---

## ⚙️ Requisitos e Instalación

### Requisitos previos
- Python 3.9 (Recomendado)
- Cámara web integrada o USB

### Instalación de dependencias
Para instalar el entorno utilizando `uv` o `pip` sin alterar la compatibilidad con NumPy 1.26 y OpenCV 4.8:

```bash
# Crear e inicializar el entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
.venv\Scripts\activate     # Windows

# Instalación de paquetes fijados
uv pip install -r requirements.txt
# o alternativamente:
pip install -r requirements.txt
```

---

## 🚀 Guía de Uso Paso a Paso

### Paso 1: Calibración de la Cámara (Fase Offline)
1. Captura entre 10 y 20 fotos a un tablero de ajedrez ($8 \times 6$ esquinas internas, cuadrícula de $30\text{ mm} \times 30\text{ mm}$) en distintas posiciones y orientaciones utilizando **tu propia cámara**.
2. Guarda las imágenes en formato `.jpg` dentro de la carpeta `./patrones_calibracion/`.
3. Ejecuta el script de calibración offline:

```bash
python calibracion_camara.py
```

El script procesará los patrones, refinará la detección de esquinas a nivel subpíxel (`cv2.cornerSubPix`) y generará el archivo `parametros_camara.npz` mostrando por consola el error RMS obtenido.

### Paso 2: Ejecución de la Aplicación Principal

Lanza la aplicación interactiva:

```bash
python main.py
```

#### Flujo de Funcionamiento:
1. **Desbloqueo del Sistema de Seguridad:**
   - La pantalla mostrará el mensaje `SEGURIDAD: ESPERANDO ROJO`. Presenta un objeto o pelota **ROJA** frente a la cámara.
   - Cuando el sistema reconozca el objeto, mostrará un recuadro con el mensaje `RETIRE BOLA`. Retira el objeto del campo de visión para confirmar la lectura y avanzar de paso.
   - Repite el proceso para los colores **VERDE** y **AZUL**.
2. **Acceso al Sistema AR y Control Táctil:**
   - Al completar la secuencia, el sistema desbloqueará la interfaz principal y superpondrá la máscara AR adaptada a tu rostro.
   - Mueve tu mano frente a la cámara: pasa el puntero del dedo índice sobre los botones superiores para seleccionar distintas máscaras o alternar el modo `Debug: ON/OFF`.
3. **Salida:** Presiona la tecla `q` para cerrar la ventana y finalizar la ejecución.

---

## 📊 Métricas y Parámetros del Sistema

- **Patrón de Calibración:** Tablero de ajedrez de $8 \times 6$ esquinas internas, cuadrículas de $30\text{ mm} \times 30\text{ mm}$.
- **Modelo de Cámara:** Proyección Central Pin-hole con corrección de distorsión radial y tangencial ($k_1, k_2, p_1, p_2, k_3$).
- **Frecuencia de Refresco:** Ejecución en tiempo real en GPU/CPU manteniendo procesamiento de vídeo continuo.