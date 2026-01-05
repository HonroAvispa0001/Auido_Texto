# Ultra Whisper Transcriptor 🎙️

<div align="center">

**Herramienta Profesional de Transcripción de Audio**

Una aplicación moderna, eficiente y fácil de usar para transcripción de audio usando la API Whisper de OpenAI con soporte para procesamiento por lotes.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper--1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

</div>

---

## ✨ Características Principales

### 🎨 Interfaz de Usuario Moderna
- **Tema Oscuro** - UI profesional con CustomTkinter y estética moderna
- **Progreso en Tiempo Real** - Actualizaciones de estado en vivo para cada archivo
- **Drag & Drop** - Simplemente arrastra archivos de audio a la aplicación
- **Gestión de Cola** - Agrega, elimina y organiza archivos fácilmente

### ⚡ Alto Rendimiento
- **Procesamiento Multi-hilo** - Procesa hasta 5 archivos simultáneamente
- **Operaciones por Lotes** - Maneja múltiples archivos a la vez
- **Cola Inteligente** - Inicia, detén y gestiona el procesamiento con controles
- **Seguimiento de Progreso** - Ve el estado en tiempo real de cada archivo

### 🎵 Amplio Soporte de Formatos
Soporta **más de 18 formatos de audio** incluyendo:
```
MP3, WAV, M4A, MP4, FLAC, OGG, OGA, OPUS, AAC,
WMA, AIFF, AIF, AMR, WEBM, MPEG, MPGA, 3GP, 3GPP
```

### ⚙️ Configuración Flexible
- **Gestión de API Key** - Almacenamiento seguro de tu API key de OpenAI
- **Selección de Idioma** - Auto-detección o elige entre más de 13 idiomas
- **Opciones de Salida** - Guarda como TXT o JSON
- **Directorio de Salida Personalizado** - Elige dónde guardar las transcripciones
- **Configuración de Workers** - Ajusta el procesamiento concurrente (1-5 workers)

### 🛡️ Production Ready
- **Logging Completo** - Sistema de logging profesional para debugging
- **Manejo Robusto de Errores** - Gestión completa de errores de API, red y archivos
- **Validación de API Key** - Validación básica de formato de API key
- **Mensajes de Error Claros** - Mensajes informativos y accionables
- **Recuperación de Errores** - Continúa procesando otros archivos si uno falla

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8 o superior
- API key de OpenAI ([Obtén una aquí](https://platform.openai.com/api-keys))

### Instalación

#### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### Paso 2: Ejecutar la Aplicación

```bash
python whisper_multi.py
```

### Primera Configuración

1. **Ingresar API Key**: Al iniciar por primera vez, se te pedirá que ingreses tu API key de OpenAI
2. **Configurar Preferencias** (Opcional):
   - Directorio de salida
   - Número de workers concurrentes
   - Idioma preferido
   - Formato de salida (TXT o JSON)

---

## 📖 Guía de Uso

### Agregar Archivos

**Método 1: Botón "Add Files"**
1. Click en el botón "+ Add Files"
2. Selecciona uno o múltiples archivos de audio
3. Click en "Open"

**Método 2: Botón "Add Folder"**
1. Click en el botón "+ Add Folder"
2. Selecciona una carpeta
3. Se agregarán automáticamente todos los archivos de audio soportados

**Método 3: Drag & Drop** (si tkinterdnd2 está instalado)
1. Arrastra archivos o carpetas desde el explorador de archivos
2. Suéltalos en la ventana de la aplicación

### Procesar Archivos

1. Asegúrate de que tu API key esté configurada
2. Los archivos aparecerán en la cola con estado "Pending"
3. Click en el botón "START" para comenzar la transcripción
4. Observa el progreso en tiempo real
5. Los archivos completados mostrarán estado "Complete" en verde

### Detener el Procesamiento

- Click en "Stop" para detener el procesamiento actual
- Los archivos en proceso se marcarán como "Cancelled"
- Los archivos pendientes permanecerán en la cola

### Limpiar la Cola

- **Clear Completed**: Elimina solo los archivos completados y con error
- **Clear All**: Elimina todos los archivos (solo cuando no está procesando)

---

## ⚙️ Configuración

### Panel de Configuración

Accede haciendo click en el botón "Settings" en la esquina superior derecha.

#### OpenAI API Key
- Ingresa tu API key de OpenAI (comienza con `sk-`)
- Usa el checkbox "Show API Key" para ver/ocultar la key
- La key se guarda de forma segura en tu sistema

#### Directorio de Salida
- **Por defecto**: Crea una carpeta `Transcripciones` en el mismo directorio que los archivos de audio
- **Personalizado**: Click en "..." para seleccionar un directorio específico

#### Workers Concurrentes
- Ajusta entre 1-5 workers concurrentes
- Más workers = procesamiento más rápido
- Considera los límites de tu API de OpenAI

#### Idioma
- **auto**: Detección automática (recomendado)
- O selecciona específicamente: en, es, fr, de, it, pt, nl, ja, ko, zh, ru, ar

#### Formato de Salida
- **TXT**: Texto plano simple
- **JSON**: Incluye metadata (archivo origen, timestamp, duración)

---

## 📁 Estructura de Archivos de Salida

### Formato TXT
```
archivo_de_audio_transcript.txt
```
Contiene solo el texto transcrito.

### Formato JSON
```json
{
  "source_file": "C:/path/to/audio.mp3",
  "transcription": "Texto transcrito aquí...",
  "timestamp": "2026-01-05T12:34:56.789012",
  "duration": 123.45
}
```

---

## 🔍 Solución de Problemas

### Error: "Invalid API key"
- Verifica que tu API key sea correcta
- Asegúrate de que comience con `sk-`
- Verifica que tenga permisos activos en OpenAI

### Error: "Rate limited"
- Estás excediendo el límite de requests de tu API
- Reduce el número de workers concurrentes
- Espera unos minutos antes de reintentar

### Error: "Insufficient quota"
- Tu cuenta de OpenAI no tiene créditos suficientes
- Agrega créditos en [OpenAI Billing](https://platform.openai.com/account/billing)

### Error: "File too large"
- El archivo excede el límite de 25 MB de la API de Whisper
- Considera dividir el archivo en partes más pequeñas

### Error: "Network error"
- Verifica tu conexión a internet
- Verifica que no haya firewall bloqueando la conexión
- Intenta de nuevo en unos momentos

### Drag & Drop No Funciona
- Asegúrate de que `tkinterdnd2` esté instalado: `pip install tkinterdnd2`
- Si persiste el error, usa los botones "Add Files" o "Add Folder"

---

## 📊 Logs y Debugging

La aplicación genera logs detallados que puedes revisar si encuentras problemas:

- Los logs se muestran en la consola donde ejecutaste la aplicación
- Nivel de logging: INFO (puedes cambiarlo a DEBUG para más detalle)
- Los logs incluyen:
  - Inicialización de componentes
  - Carga/guardado de configuración
  - Inicio/finalización de transcripciones
  - Errores y advertencias

Para más detalle, modifica el nivel de logging en el código:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambia de INFO a DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🔒 Seguridad y Privacidad

- Tu API key se almacena localmente en: `~/.whisper_transcriptor_config.json`
- No se envía información a ningún servidor excepto la API de OpenAI
- Los archivos de audio se procesan de forma segura
- Las transcripciones se guardan solo en tu computadora

---

## 📦 Dependencias

### Requeridas
- `openai>=1.0.0` - Cliente de la API de OpenAI
- `customtkinter>=5.2.0` - Framework moderno de UI

### Opcionales
- `tkinterdnd2>=0.3.0` - Soporte para drag & drop (recomendado)

**Nota**: tkinter viene incluido con Python, no necesita instalación adicional.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si encuentras un bug o tienes una sugerencia:

1. Abre un issue describiendo el problema o sugerencia
2. Fork el repositorio
3. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
4. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push a la branch (`git push origin feature/AmazingFeature`)
6. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- [OpenAI](https://openai.com/) por la increíble API de Whisper
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) por el framework de UI moderno
- [TkinterDnD2](https://github.com/pmgagne/tkinterdnd2) por el soporte de drag & drop

---

## 📞 Soporte

¿Necesitas ayuda? 

- 📖 Lee esta documentación completa
- 🐛 Reporta bugs en Issues
- 💡 Sugiere features en Issues
- 📧 Contacta al desarrollador

---

<div align="center">

**Hecho con ❤️ para la comunidad**

⭐ Si te gusta este proyecto, considera darle una estrella!

</div>
