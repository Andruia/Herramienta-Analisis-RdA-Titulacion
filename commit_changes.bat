@echo off
echo === COMMIT: Implementacion de Niveles 2 y 4 de Carrera ===

REM Agregar todos los archivos modificados
git add .

REM Realizar commit con mensaje descriptivo
git commit -m "feat: Implementar niveles 2 y 4 de carrera con taxonomia de Bloom" -m "- Expandir APPROPRIATENESS_RULES para niveles 2 y 4 en bloom_analyzer.py" -m "- Actualizar interfaz app.py con selector completo (2,4,6,8)" -m "- Agregar funciones contextuales y recomendaciones inteligentes" -m "- Implementar progresion pedagogica logica desde fundamentos (index=0)" -m "- Resolver problema de N/A en evaluacion de adecuacion" -m "- Agregar documentacion completa y scripts de prueba" -m "" -m "Archivos modificados:" -m "- src/bloom_analyzer.py: Reglas expandidas y funciones contextuales" -m "- src/app.py: Interfaz actualizada con todos los niveles" -m "- docs/niveles_carrera_bloom.md: Documentacion completa" -m "- test_bloom_expansion.py: Script de pruebas basicas" -m "- test_app_integration.py: Pruebas de integracion" -m "- COMMIT_SUMMARY.md: Resumen de cambios" -m "" -m "Fixes: Evaluacion de adecuacion para todos los niveles academicos"

echo === Commit realizado exitosamente ===
echo.
echo Resumen de cambios:
echo ✅ Niveles 2 y 4 implementados en bloom_analyzer.py
echo ✅ Interfaz app.py actualizada con selector (2,4,6,8)
echo ✅ Progresion logica desde nivel basico (index=0)
echo ✅ Problema de 'N/A' en Adecuacion T. resuelto
echo ✅ Documentacion y pruebas agregadas
echo.
echo Proximo paso: streamlit run src/app.py

pause