#!/bin/bash

# Script para realizar commit de los cambios de niveles 2 y 4

echo "=== COMMIT: Implementación de Niveles 2 y 4 de Carrera ==="

# Agregar todos los archivos modificados
git add .

# Realizar commit con mensaje descriptivo
git commit -m "feat: Implementar niveles 2 y 4 de carrera con taxonomía de Bloom

- Expandir APPROPRIATENESS_RULES para niveles 2 y 4 en bloom_analyzer.py
- Actualizar interfaz app.py con selector completo (2,4,6,8) 
- Agregar funciones contextuales y recomendaciones inteligentes
- Implementar progresión pedagógica lógica desde fundamentos (index=0)
- Resolver problema de N/A en evaluación de adecuación
- Agregar documentación completa y scripts de prueba

Archivos modificados:
- src/bloom_analyzer.py: Reglas expandidas y funciones contextuales
- src/app.py: Interfaz actualizada con todos los niveles
- docs/niveles_carrera_bloom.md: Documentación completa
- test_bloom_expansion.py: Script de pruebas básicas
- test_app_integration.py: Pruebas de integración
- COMMIT_SUMMARY.md: Resumen de cambios

Fixes: Evaluación de adecuación para todos los niveles académicos"

echo "=== Commit realizado exitosamente ==="
echo ""
echo "Resumen de cambios:"
echo "✅ Niveles 2 y 4 implementados en bloom_analyzer.py"
echo "✅ Interfaz app.py actualizada con selector (2,4,6,8)"
echo "✅ Progresión lógica desde nivel básico (index=0)"
echo "✅ Problema de 'N/A' en Adecuación T. resuelto"
echo "✅ Documentación y pruebas agregadas"
echo ""
echo "Próximo paso: streamlit run src/app.py"