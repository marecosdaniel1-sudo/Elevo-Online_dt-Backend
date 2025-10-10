"""
Script para iniciar el servidor de desarrollo de Elevo Online
"""
import uvicorn
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True
):
    """
    Inicia el servidor FastAPI
    
    Args:
        host: Dirección IP del host (default: 0.0.0.0 para todas las interfaces)
        port: Puerto del servidor (default: 8000)
        reload: Activar hot-reload para desarrollo (default: True)
    """
    print("🚀 Iniciando servidor Elevo Online...")
    print(f"📍 URL: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"📚 Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"🔄 Hot-reload: {'Activado' if reload else 'Desactivado'}")
    print("\n⏳ Cargando aplicación...\n")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Puedes cambiar estos valores según necesites
    start_server(
        host="0.0.0.0",
        port=8000,
        reload=True  # Cambiar a False para producción
    )
