#!/usr/bin/env python3
"""
Servicio de Actualización Automática de Papers
Automatic Paper Update Service
Author: SPINOR Technologies
Date: August 6, 2025
"""

import schedule
import time
import logging
from datetime import datetime
import os
import sys

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_papers import RealTimePaperFetcher

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_updates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoPaperUpdateService:
    """Servicio de actualización automática de papers."""
    
    def __init__(self):
        self.fetcher = RealTimePaperFetcher()
        logger.info("🤖 Servicio de actualización automática iniciado")
    
    def daily_update(self):
        """Actualización diaria de papers."""
        logger.info("📅 Iniciando actualización diaria de papers...")
        try:
            self.fetcher.fetch_and_update(days_back=2, max_papers=10)
            logger.info("✅ Actualización diaria completada")
        except Exception as e:
            logger.error(f"❌ Error en actualización diaria: {e}")
    
    def weekly_update(self):
        """Actualización semanal más completa."""
        logger.info("📅 Iniciando actualización semanal completa...")
        try:
            self.fetcher.fetch_and_update(days_back=7, max_papers=20)
            logger.info("✅ Actualización semanal completada")
        except Exception as e:
            logger.error(f"❌ Error en actualización semanal: {e}")
    
    def start_scheduler(self):
        """Inicia el programador de tareas."""
        print("🚀 SERVICIO DE ACTUALIZACIÓN AUTOMÁTICA DE PAPERS")
        print("🚀 AUTOMATIC PAPER UPDATE SERVICE")
        print("="*60)
        print("⏰ Programación configurada:")
        print("   📅 Actualización diaria: 08:00 AM")
        print("   📅 Actualización semanal: Domingos 10:00 AM")
        print("   📊 Papers por actualización diaria: ~10")
        print("   📊 Papers por actualización semanal: ~20")
        print("="*60)
        print()
        
        # Programar tareas
        schedule.every().day.at("08:00").do(self.daily_update)
        schedule.every().sunday.at("10:00").do(self.weekly_update)
        
        # Ejecutar una actualización inicial
        print("🔄 Ejecutando actualización inicial...")
        self.daily_update()
        
        print("✅ Servicio iniciado. Presiona Ctrl+C para detener.")
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            print("\n👋 Servicio detenido por el usuario")
            logger.info("Servicio de actualización automática detenido")


def main():
    """Función principal."""
    try:
        service = AutoPaperUpdateService()
        
        print("\n📋 Opciones de ejecución:")
        print("1. Iniciar servicio automático (recomendado)")
        print("2. Actualización única ahora")
        print("3. Configurar horarios personalizados")
        
        choice = input("\n🔢 Selecciona opción (1-3): ").strip()
        
        if choice == "1":
            service.start_scheduler()
        elif choice == "2":
            print("🔄 Ejecutando actualización única...")
            service.daily_update()
            print("✅ Actualización completada")
        elif choice == "3":
            print("⚙️ Configuración personalizada:")
            hour = input("🕐 Hora para actualización diaria (HH:MM): ")
            try:
                schedule.every().day.at(hour).do(service.daily_update)
                print(f"✅ Actualización programada para las {hour} diariamente")
                service.start_scheduler()
            except:
                print("❌ Formato de hora inválido")
        else:
            print("🔄 Ejecutando actualización por defecto...")
            service.daily_update()
            
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
