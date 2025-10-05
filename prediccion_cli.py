#!/usr/bin/env python3
"""
Script de línea de comandos para el Sistema de Predicción de Calidad del Aire
con NASA TEMPO + LSTM

Uso:
    python prediccion_cli.py --lat 19.4326 --lon -99.1332 --horas 6
    python prediccion_cli.py --ubicacion "Ciudad de México" --alertas
    python prediccion_cli.py --entrenar
"""

import argparse
import sys
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(
        description='Sistema de Predicción de Calidad del Aire con NASA TEMPO + LSTM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos de uso:
  
  Predicción para una ubicación:
    python prediccion_cli.py --lat 19.4326 --lon -99.1332 --horas 6
  
  Generar alertas:
    python prediccion_cli.py --lat 19.4326 --lon -99.1332 --alertas
  
  Informe completo:
    python prediccion_cli.py --lat 19.4326 --lon -99.1332 --informe
  
  Entrenar modelo:
    python prediccion_cli.py --entrenar --dias 365
  
  Actualizar datos de TEMPO:
    python prediccion_cli.py --actualizar --lat 19.4326 --lon -99.1332
        '''
    )
    
    # Argumentos de ubicación
    parser.add_argument('--lat', type=float, help='Latitud (-90 a 90)')
    parser.add_argument('--lon', type=float, help='Longitud (-180 a 180)')
    parser.add_argument('--ubicacion', type=str, help='Nombre de la ubicación')
    
    # Argumentos de predicción
    parser.add_argument('--horas', type=int, nargs='+', 
                       default=[3, 6, 12, 24],
                       help='Horizontes de predicción (ej: 3 6 24)')
    
    # Modos de operación
    parser.add_argument('--predecir', action='store_true',
                       help='Realizar predicción')
    parser.add_argument('--alertas', action='store_true',
                       help='Generar alertas si hay riesgo')
    parser.add_argument('--informe', action='store_true',
                       help='Generar informe completo')
    parser.add_argument('--entrenar', action='store_true',
                       help='Entrenar nuevo modelo')
    parser.add_argument('--actualizar', action='store_true',
                       help='Actualizar datos de TEMPO')
    
    # Argumentos de entrenamiento
    parser.add_argument('--dias', type=int, default=365,
                       help='Días de datos para entrenamiento (default: 365)')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Épocas de entrenamiento (default: 100)')
    
    # Argumentos de configuración
    parser.add_argument('--username', type=str,
                       help='Usuario de NASA Earthdata')
    parser.add_argument('--password', type=str,
                       help='Contraseña de NASA Earthdata')
    parser.add_argument('--modelo', type=str, default='modelos/modelo_lstm_calidad_aire.h5',
                       help='Ruta al modelo entrenado')
    
    # Argumentos de salida
    parser.add_argument('--json', action='store_true',
                       help='Salida en formato JSON')
    parser.add_argument('--guardar', type=str,
                       help='Guardar resultado en archivo')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verbose')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.predecir or args.alertas or args.informe or args.actualizar:
        if args.lat is None or args.lon is None:
            parser.error("Se requiere --lat y --lon para esta operación")
    
    # Banner
    if not args.json:
        print("="*70)
        print("🛰️  SISTEMA DE PREDICCIÓN DE CALIDAD DEL AIRE")
        print("    NASA TEMPO + LSTM")
        print("="*70)
        print()
    
    # Ejecutar modo seleccionado
    if args.entrenar:
        entrenar_modelo(args)
    elif args.actualizar:
        actualizar_datos(args)
    elif args.alertas:
        generar_alertas(args)
    elif args.informe:
        generar_informe(args)
    else:
        # Por defecto, hacer predicción
        realizar_prediccion(args)

def realizar_prediccion(args):
    """Realiza predicción de calidad del aire"""
    print(f"🔮 Realizando predicción para:")
    print(f"   📍 Ubicación: {args.ubicacion or f'({args.lat}, {args.lon})'}")
    print(f"   ⏰ Horizontes: {args.horas} horas")
    print()
    
    # TODO: Implementar lógica de predicción
    # 1. Cargar modelo
    # 2. Obtener datos TEMPO
    # 3. Realizar predicción
    # 4. Mostrar resultados
    
    print("⚠️  Implementación pendiente: carga del modelo y predicción")
    print("💡 Ejecuta el notebook PRUEBAS.ipynb primero para entrenar el modelo")

def generar_alertas(args):
    """Genera alertas de calidad del aire"""
    print(f"🚨 Generando alertas para:")
    print(f"   📍 {args.ubicacion or f'({args.lat}, {args.lon})'}")
    print()
    
    # TODO: Implementar lógica de alertas
    print("⚠️  Implementación pendiente")

def generar_informe(args):
    """Genera informe completo"""
    print(f"📊 Generando informe para:")
    print(f"   📍 {args.ubicacion or f'({args.lat}, {args.lon})'}")
    print(f"   📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # TODO: Implementar lógica de informe
    print("⚠️  Implementación pendiente")

def entrenar_modelo(args):
    """Entrena un nuevo modelo"""
    print(f"🧠 Entrenando modelo LSTM:")
    print(f"   📊 Días de datos: {args.dias}")
    print(f"   🔄 Épocas: {args.epochs}")
    print()
    
    # TODO: Implementar lógica de entrenamiento
    print("⚠️  Implementación pendiente")
    print("💡 Por ahora, usa el notebook PRUEBAS.ipynb para entrenar el modelo")

def actualizar_datos(args):
    """Actualiza datos de TEMPO"""
    print(f"🔄 Actualizando datos de TEMPO:")
    print(f"   📍 {args.lat}, {args.lon}")
    print()
    
    # TODO: Implementar lógica de actualización
    print("⚠️  Implementación pendiente")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
