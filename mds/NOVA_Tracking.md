# NOVA — Tracking de desarrollo

> Parte de la especificación de **NOVA**. Documento maestro: [NOVA_GameDesign_Spec.md](./NOVA_GameDesign_Spec.md).
> **Sección T.** Este archivo es el estado vivo del proyecto. Se actualiza en cada tarea completada.
>
> Cubre **solo desarrollo**. El arte se sigue en [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md) y no se planifica aquí.

---

## T.1 Prompt de continuación

Pega esto en un chat nuevo junto con los siete archivos `.md` del proyecto:

```
Estoy desarrollando NOVA, un juego 2D en Unity. Toda la especificación está en
los archivos adjuntos:

- NOVA_GameDesign_Spec.md       reglas, economía, poderes, niveles, UI, arquitectura
- NOVA_Nodos.md                 los 4 tipos de nodo
- NOVA_IA_Algoritmos.md         algoritmos del Enemigo
- NOVA_Estados_Animaciones.md   estados y animaciones
- NOVA_Assets_Diseno.md         inventario de arte y su estado
- NOVA_Arte_Tecnica.md          contrato del pipeline: primitivas y reglas
- NOVA_Tracking.md              estado del desarrollo (este es el que manda)

El arte se genera con Python (NumPy + Pillow). Las primitivas estan en
tools/nova_core.py, la paleta en tools/nova_paleta.py y un generador por
propuesta en tools/gen_<nodo>_v<n>.py. Los PNG viven en
art/nodes/<nodo>/v<n>/ y son salida derivada: no se editan a mano. Un nodo
puede tener varias versiones conviviendo; la elegida la marca la columna
"Archivos" de NOVA_Assets_Diseno.md, no la carpeta.

Tu tarea:
0. Mira T.7 y T.8. Hay decisiones abiertas; la de T.8 (escala del tablero) hay
   que cerrarla ANTES de disenar las coordenadas de los 9 niveles. Si la tarea
   que toca depende de una decision abierta, dilo antes de empezar.
1. Lee T.3 y T.4 de NOVA_Tracking.md y dime cuál es la SIGUIENTE tarea pendiente,
   respetando el orden de fases y las dependencias.
2. Antes de proponerla, comprueba su columna "Arte" en T.4. Si depende de un
   ART-* que no está ✅ en NOVA_Assets_Diseno.md, NO la propongas: decláralo
   BLOQUEADA, dime exactamente qué asset falta, y pasa a la siguiente tarea
   desbloqueada. Nunca sustituyas arte pendiente por arte improvisado.
3. Implementa esa tarea completa: los scripts de C# que pide, respetando la
   arquitectura de la sección 15 y el glosario de la sección 2.
4. Al terminar, dame la línea actualizada de T.4 y del registro T.5 para que
   yo la pegue en el archivo.

Reglas:
- Una sola tarea por respuesta. No adelantes trabajo de tareas posteriores.
- No inventes reglas de juego. Si la especificación no cubre un caso, para y
  pregúntame.
- Todo número de balance va en un ScriptableObject, nunca escrito en el código.
- Nombra las clases y variables exactamente como el glosario de la sección 2.

Empieza diciéndome cuál es la siguiente tarea y por qué.
```

---

## T.2 Reglas del ciclo de trabajo

| # | Regla |
|---|---|
| 1 | **Una tarea por sesión.** Terminar, marcar ✅ y actualizar T.5 antes de abrir la siguiente. |
| 2 | **El orden de fases es obligatorio.** No se empieza una fase sin cumplir el criterio de salida de la anterior (T.6). Dentro de una fase, se respetan las dependencias de T.4. |
| 3 | **Bloqueo por arte.** Una tarea con `ART-*` en su columna *Arte* solo se inicia si ese asset está ✅ en [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md). Si no lo está, se marca 🔴 BLOQUEADA y se salta. |
| 4 | **Primitivas en fases 1–5.** Círculos de color y texto plano son válidos para probar lógica. No cuentan como arte y no se marcan ✅ en el inventario. |
| 5 | **Fase 6 es solo integración de arte.** Si su asset falta, la tarea no existe todavía. No se improvisa. |
| 6 | **La especificación manda.** Si el código y el `.md` se contradicen, se corrige el código. Si el `.md` está mal, se corrige el `.md` primero y se anota en T.5. |
| 7 | **Definición de hecho:** compila sin errores, sus tests pasan, no rompe los criterios de salida anteriores, y T.4 + T.5 están actualizados. |

Estados: ⬜ pendiente · 🟨 en curso · ✅ hecha · 🔴 bloqueada.

---

## T.3 Estado global

| Fase | Nombre | Tareas | ✅ | Estado | Criterio de salida |
|---|---|---|---|---|---|
| 1 | Núcleo jugable | 12 | 0 | ⬜ | Capturar un Asteroide, encenderlo como Estrella y tomar un nodo enemigo |
| 2 | Tipos y defensa | 8 | 0 | ⬜ | Los cuatro tipos funcionan y el nivel 3 es jugable |
| 3 | Poderes | 7 | 0 | ⬜ | Los tres poderes funcionan y pasan los casos 8–14 de la sección 17 |
| 4 | IA | 6 | 0 | ⬜ | La IA del mapa 3 vence a un jugador descuidado |
| 5 | Flujo y contenido | 7 | 0 | ⬜ | Los 9 niveles son completables de principio a fin |
| 6 | Presentación | 10 | 0 | 🔴 | 49 de 95 assets listos. **`T6-01`, `T6-02` y `T6-03` ya no están bloqueadas por arte**; las otras siete sí ([A.7](./NOVA_Assets_Diseno.md#a7-resumen-de-progreso)) |
| | **Total** | **50** | **0** | | |

**Siguiente tarea:** `T1-01`.

---

## T.4 Tareas

`Arte` = dependencia bloqueante de [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md). `Ref` = sección de la especificación que define la tarea.

### Fase 1 — Núcleo jugable

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T1-01 | Enums de `Core`: `Faction`, `NodeType`, `NodeState`, `PowerType`, `ImpactResult` | [15.3](./NOVA_GameDesign_Spec.md#153-core--reglas-puras-sin-monobehaviour) | — | No | ⬜ |
| T1-02 | `EnergyMath` + tests: multiplicadores, redondeos, coste efectivo de captura | [6.2](./NOVA_GameDesign_Spec.md#62-resolución-de-impacto), [6.4](./NOVA_GameDesign_Spec.md#64-casos-de-captura-por-tipo) | T1-01 | No | ⬜ |
| T1-03 | `ImpactResolver` + tests: absorción, daño, captura, resistencia ×2 | [6.2](./NOVA_GameDesign_Spec.md#62-resolución-de-impacto) | T1-02 | No | ⬜ |
| T1-04 | `ConversionRules` + tests: validez y coste de encendido, mejora, reconversión | [8](./NOVA_GameDesign_Spec.md#8-reconversión), [16.2](./NOVA_GameDesign_Spec.md#162-costes-de-nivel) | T1-01 | No | ⬜ |
| T1-05 | ScriptableObjects `NodeDefinition`, `NodeLevelData`, `BalanceConfig` + assets con los valores de la sección 16 | [15.4](./NOVA_GameDesign_Spec.md#154-data--scriptableobjects), [16](./NOVA_GameDesign_Spec.md#16-tablas-de-balance-consolidadas) | T1-01 | No | ⬜ |
| T1-06 | `NodeController` + `NodeIdentity`, `NodeOwnership`, `NodeEnergy` | [15.5](./NOVA_GameDesign_Spec.md#155-gameplay--componentes-de-nodo) | T1-05 | No | ⬜ |
| T1-07 | `NodeLevelComponent` y `NodeStateMachine` (solo `Normal`, `Dormido`, `SinEncender`) | [14.1](./NOVA_Estados_Animaciones.md#141-estados-del-nodo) | T1-06 | No | ⬜ |
| T1-08 | `StarGenerator`: +1 de Energía por intervalo, tope 50, parada al llenarse | [4.2](./NOVA_Nodos.md#42-estrella) | T1-06 | No | ⬜ |
| T1-09 | `ProtonLauncher`, `Proton`, `ProtonPool`: envío 50 % / 100 %, velocidad 2.5 u/s | [5.2](./NOVA_GameDesign_Spec.md#52-envío), [6.1](./NOVA_GameDesign_Spec.md#61-el-protón) | T1-03, T1-06 | No | ⬜ |
| T1-10 | `NodeRegistry` y `ProtonRegistry` + orden de ejecución de 15.10 | [15.6](./NOVA_GameDesign_Spec.md#156-systems--escena), [15.10](./NOVA_GameDesign_Spec.md#1510-orden-de-ejecución) | T1-06 | No | ⬜ |
| T1-11 | `InputRouter`, `SelectionManager`, `PlayerCommandIssuer` con buffer de doble clic de 0.25 s | [13.1](./NOVA_GameDesign_Spec.md#131-ratón), [13.2](./NOVA_GameDesign_Spec.md#132-resolución-del-doble-clic) | T1-09 | No | ⬜ |
| T1-12 | Escena de prueba con 3 nodos: capturar, encender y tomar un nodo enemigo | — | T1-11 | No | ⬜ |

### Fase 2 — Tipos y defensa

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T2-01 | `NodeIgnition`: Asteroide propio con 10 de Energía → nivel 1 con 0 | [4.1](./NOVA_Nodos.md#41-asteroide-nivel-0) | T1-12 | No | ⬜ |
| T2-02 | `IgnitionMenu` radial de 3 opciones | [13.3](./NOVA_GameDesign_Spec.md#133-panel-de-clic-derecho) | T2-01 | No | ⬜ |
| T2-03 | Mejoras de nivel y `NodeInfoPanel` de clic derecho, con botón deshabilitado y coste en rojo | [13.3](./NOVA_GameDesign_Spec.md#133-panel-de-clic-derecho), [13.4](./NOVA_GameDesign_Spec.md#134-traducción-de-velocidad-de-ataque) | T2-01 | No | ⬜ |
| T2-04 | `MagnetarTurret`: radio, cadencia, objetivo más cercano al centro, −2 de Carga | [4.4](./NOVA_Nodos.md#44-magnetar), [6.3](./NOVA_GameDesign_Spec.md#63-efecto-del-magnetar-sobre-protones) | T1-12 | No | ⬜ |
| T2-05 | Resistencia ×2 en impactos hostiles y 1:1 en refuerzos aliados | [5.3](./NOVA_GameDesign_Spec.md#53-recepción), [6.2](./NOVA_GameDesign_Spec.md#62-resolución-de-impacto) | T2-04 | No | ⬜ |
| T2-06 | Magnetar neutral disparando a ambos bandos | [3.2](./NOVA_GameDesign_Spec.md#32-nota-sobre-el-magnetar-neutral), [4.4](./NOVA_Nodos.md#44-magnetar) | T2-04 | No | ⬜ |
| T2-07 | `NodeConverter`: reconversión de 3 s con ventana de vulnerabilidad | [8.1](./NOVA_GameDesign_Spec.md#81-reglas) | T1-04, T2-03 | No | ⬜ |
| T2-08 | `ThreatCalculator` + estado `Asustado` | [14.2](./NOVA_Estados_Animaciones.md#142-animación-de-susto) | T1-10 | No | ⬜ |

### Fase 3 — Poderes

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T3-01 | `PowerDefinition` + assets de los tres poderes | [16.3](./NOVA_GameDesign_Spec.md#163-poderes) | T2-08 | No | ⬜ |
| T3-02 | `PulsarCaster`: carga acoplada a la Energía, pausa, cancelación con devolución del 50 % | [7.1](./NOVA_GameDesign_Spec.md#71-regla-de-carga) | T3-01 | No | ⬜ |
| T3-03 | `PowerProjectile`: 6 u/s, no derribable, alcance y objetivos válidos | [7.2](./NOVA_GameDesign_Spec.md#72-tabla-de-poderes) | T3-02 | No | ⬜ |
| T3-04 | Cero Absoluto: congelación, deshielo invertido, auto-deshielo de 30 s | [7.3](./NOVA_GameDesign_Spec.md#73-cero-absoluto) | T3-03 | No | ⬜ |
| T3-05 | Decaimiento: −2 E/s, permanencia en 0, cura, no acumulable | [7.4](./NOVA_GameDesign_Spec.md#74-decaimiento) | T3-03 | No | ⬜ |
| T3-06 | Agujero de Gusano: captura íntegra, ignora ×2, robo de carga en sus 3 ventanas | [7.5](./NOVA_GameDesign_Spec.md#75-agujero-de-gusano) | T3-03 | No | ⬜ |
| T3-07 | `PulsarPowerWheel` + barra de carga visible también en el Púlsar enemigo | [13.5](./NOVA_GameDesign_Spec.md#135-rueda-de-poderes-del-púlsar) | T3-06 | No | ⬜ |

### Fase 4 — IA

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T4-01 | `AIProfile` + los tres assets de perfil | [12.5](./NOVA_IA_Algoritmos.md#125-perfiles-por-mapa) | T3-07 | No | ⬜ |
| T4-02 | `AIEvaluator` + los 5 tests de 12.7 | [12.3](./NOVA_IA_Algoritmos.md#123-función-de-puntuación-atacar), [12.7](./NOVA_IA_Algoritmos.md#127-contrato-de-implementación) | T4-01 | No | ⬜ |
| T4-03 | `EnemyCommandIssuer` sobre `INodeCommandIssuer` | [12.7](./NOVA_IA_Algoritmos.md#127-contrato-de-implementación), [15.1](./NOVA_GameDesign_Spec.md#151-principios) | T4-01 | No | ⬜ |
| T4-04 | `EnemyBrain`: ciclo de decisión, una acción por ciclo, ruido con semilla | [12.1](./NOVA_IA_Algoritmos.md#121-ciclo-de-decisión), [12.2](./NOVA_IA_Algoritmos.md#122-acciones-candidatas) | T4-02, T4-03 | No | ⬜ |
| T4-05 | `AIThreatResponder`: refuerzo, congelación y evacuación | [12.4](./NOVA_IA_Algoritmos.md#124-detección-de-amenaza-y-defensa) | T4-04 | No | ⬜ |
| T4-06 | Verificación de las prohibiciones de 12.6 | [12.6](./NOVA_IA_Algoritmos.md#126-prohibiciones) | T4-05 | No | ⬜ |

### Fase 5 — Flujo y contenido

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T5-01 | `LevelDefinition`, `NodeSpawnData` y `LevelLoader` | [15.4](./NOVA_GameDesign_Spec.md#154-data--scriptableobjects) | T4-06 | No | ⬜ |
| T5-02 | Los 9 assets de nivel con la tabla de 11.2 | [11.2](./NOVA_GameDesign_Spec.md#112-diseño-de-niveles) | T5-01 | No | ⬜ |
| T5-03 | `WinConditionChecker`: victoria, aniquilación, estancamiento, cascada de conquista | [10](./NOVA_GameDesign_Spec.md#10-condiciones-de-victoria-y-derrota) | T5-01 | No | ⬜ |
| T5-04 | `PowerUpSpawner` + `FactionBuffs` con el calendario de 9.3 | [9](./NOVA_GameDesign_Spec.md#9-power-ups-del-cielo) | T5-01 | No | ⬜ |
| T5-05 | `GameManager`, pausa, reinicio de nivel, `EndLevelScreen` | [10.3](./NOVA_GameDesign_Spec.md#103-fin-de-nivel) | T5-03 | No | ⬜ |
| T5-06 | `ProgressSaver` y pantalla de selección de nivel | [1.2](./NOVA_GameDesign_Spec.md#12-alcance-cerrado) | T5-05 | No | ⬜ |
| T5-07 | Suite de aceptación con los 26 casos de la sección 17 | [17](./NOVA_GameDesign_Spec.md#17-casos-borde-y-reglas-de-resolución) | T5-06 | No | ⬜ |

### Fase 6 — Presentación 🔴

Ninguna tarea de esta fase puede iniciarse hoy. Se desbloquean una a una según avance [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md).

> **`ART-NOD-*` está completo: 34 de 34.** Los cuatro tipos de nodo tienen sus sprites, así que `T6-01` deja de estar 🔴 y pasa a ⬜: lo único que la retiene ya es su dependencia de código (`T5-07`), como cualquier otra tarea. Es la primera tarea de la fase 6 que existe de verdad.
>
> **`ART-ST-*` está completo: 9 de 9.** Con A.2 y A.3 cerradas, `T6-02` y `T6-03` dejan de estar bloqueadas por arte y pasan a ⬜: lo único que las retiene ya es la cadena de código `T6-01 → T6-02 → T6-03`. Son las tres primeras tareas de la fase 6 que existen de verdad.
>
> Las otras siete siguen 🔴, y el orden en que se desbloquean lo marca [A.7](./NOVA_Assets_Diseno.md#a7-resumen-de-progreso). Lo siguiente que más desbloquea es A.4.1 (el radio del Magnetar, que abre `T6-05` y es además legibilidad de fase 2) y A.4.2 (el protón, que abre `T6-04`).

| ID | Tarea | Ref | Depende de | Arte | Estado |
|---|---|---|---|---|---|
| T6-01 | `NodeVisual`: sprite por tipo, nivel y facción | [15.8](./NOVA_GameDesign_Spec.md#158-presentation) | T5-07 | `ART-NOD-*` **34/34 ✅** | ⬜ |
| T6-02 | `NodeAnimator`: estados de 14.1 | [14.1](./NOVA_Estados_Animaciones.md#141-estados-del-nodo) | T6-01 | `ART-ST-*` **9/9 ✅** | ⬜ |
| T6-03 | Animación de susto sobre los tres bandos | [14.2](./NOVA_Estados_Animaciones.md#142-animación-de-susto) | T6-02 | `ART-ST-SCARE` ✅ | ⬜ |
| T6-04 | `ProtonVisual`: número de Carga y escala | [14.3](./NOVA_Estados_Animaciones.md#143-protón) | T6-01 | `ART-WLD-PRO-*` | 🔴 |
| T6-05 | Radio del Magnetar en pantalla | [A.4.1](./NOVA_Assets_Diseno.md#a41-radio-de-alcance-del-magnetar) | T6-01 | `ART-WLD-RAD-*` | 🔴 |
| T6-06 | Feedback de selección, lazo y apuntado | [13.1](./NOVA_GameDesign_Spec.md#131-ratón) | T6-01 | `ART-WLD-SEL`, `ART-WLD-LASSO`, `ART-WLD-AIM`, `ART-WLD-RANGE` | 🔴 |
| T6-07 | `VFXPool` con las 15 animaciones puntuales | [14.5](./NOVA_Estados_Animaciones.md#145-animaciones-puntuales-sin-estado) | T6-02 | `ART-FX-*` (15) | 🔴 |
| T6-08 | `PowerBarUI` y HUD permanente | [13.6](./NOVA_GameDesign_Spec.md#136-hud-permanente) | T5-07 | `ART-UI-POWERBAR`, `ART-UI-TOPBAR` | 🔴 |
| T6-09 | Skin final de paneles, rueda de poderes y pantallas de fin | [13.3](./NOVA_GameDesign_Spec.md#133-panel-de-clic-derecho) | T6-08 | `ART-UI-*` (13) | 🔴 |
| T6-10 | `AudioDirector` y `CameraShake` | [15.8](./NOVA_GameDesign_Spec.md#158-presentation) | T6-07 | Audio (sin inventariar) | 🔴 |

---

## T.5 Registro

Una línea por tarea completada. La más reciente arriba.

| Fecha | Tarea | Resultado | Notas / desviaciones de la spec |
|---|---|---|---|
| 2026-09-19 | Arte: `ART-ST-BUFF` (v1 elegida) | «El galón» desde `tools/gen_state_buff_v1.py` → `art/states/buff/v1/`. **Dos archivos de 1 frame**, uno por power-up: un galón de dos chevrones en la esquina libre de la celda. Se descartaron dos propuestas completas («El temblor» y «El sobrecalentado»), que se conservan. **Cierra A.3: 9 de 9** | A.3 completa. `T6-02` y `T6-03` dejan de estar bloqueadas por arte. Desviaciones 71–75 abajo |
| 2026-09-19 | Arte: `ART-ST-CAP` (v2 elegida) | «El relevo» desde `tools/gen_state_cap_v2.py` → `art/states/cap/v2/`. **Una hoja de 5 frames 480×96**: dos anillos blancos que se cruzan en el frame central, uno entrando y otro saliendo. Sin variante de facción. Se descartaron dos propuestas completas («El fogonazo» y «El sello»), que se conservan | A.3 pasa de 7 a 8 de 9. Desviaciones 66–70 abajo |
| 2026-09-19 | Arte: `ART-ST-CONV` (v2 elegida) | «La colada» desde `tools/gen_state_conv_v2.py` → `art/states/conv/v2/`. **Dos hojas de 36 frames 3456×96**, una por facción: el primer asset de A.3 que no es un estado sino un tránsito de 3.0 s. Se descartaron dos propuestas completas («El torno» y «El apagón»), que se conservan | A.3 pasa de 6 a 7 de 9. Desviaciones 60–65 abajo |
| 2026-09-19 | Arte: `ART-ST-DECAY` (v2 elegida) | «El miasma» desde `tools/gen_state_decay_v2.py` → `art/states/decay/v2/`. **Hoja de 16 frames 1536×96**, el primer tinte animado: nube con cizalla sesgada hacia abajo más cinco gotas. Se descartaron dos propuestas completas («El goteo» y «El enjambre»), que se conservan | A.3 pasa de 5 a 6 de 9. Desviaciones 55–59 abajo |
| 2026-09-19 | Arte: `ART-ST-FROZEN` (v3 elegida) | «El vidrio» desde `tools/gen_state_frozen_v3.py` → `art/states/frozen/v3/`. **Un archivo de 1 frame**: una red de 13 segmentos que cruza el nodo, con la escarcha brotando de la propia grieta, verificado sobre los 13 congelables con la vara nueva `verifica_tinte`. Se descartaron dos propuestas completas («La escarcha» y «El bloque»), que se conservan. **«El bloque» llegó a estar elegida y documentada**; se cambió el mismo día por ser la primera figura de contorno recto y regular dentro del tablero | A.3 pasa de 4 a 5 de 9. Desviaciones 48–54 abajo |
| 2026-09-18 | Arte: `ART-ST-SCARE` (v1 elegida) | «Los ojos como platos» desde `tools/gen_state_scare_v1.py` → `art/states/scare/v1/`. **Dos archivos de 1 frame** —un ojo en dos tallas— que cubren los 14 nodos con la tabla de anclaje de `nova_estados.OJOS`. Se descartó una v2 completa («La pupila dilatada»), que se conserva | A.3 pasa de 3 a 4 de 9. Desviaciones 43–47 abajo |
| 2026-09-18 | Arte: `ART-ST-IGN` + `ART-ST-READY` (v2 elegida) | «El pedernal» desde `tools/gen_state_ign_v2.py` → `art/states/ign/v2/`. **Cuatro archivos**: dos lecturas (`energy < 10` / `>= 10`) × dos facciones. Se descartó una v1 completa («El interruptor»), que se conserva | A.3 pasa de 8 IDs a 9 y de 1 a 3 hechos. Desviaciones 38–42 abajo |
| 2026-09-18 | Arte: `ART-ST-SLEEP` (v2 elegida) | Primer asset de A.3. Hoja de 16 frames 1536×96 desde `tools/gen_state_sleep_v2.py`, hoy en `art/states/sleep/v2/` (la carpeta se movió el mismo día, desviación 40). Se descartó una v1 completa («La escalera»), que se conserva | A.3 estaba entonces en 1 de 8. Desviaciones 33–37 abajo, con la 33 corregida |
| 2026-09-18 | Arte: Magnetar, vuelta a la v1 | El diseño cerrado pasa de «La Botella» (`v2`) a **«El Yunque»** (`tools/gen_magnetar_v1.py` → `art/nodes/magnetar/v1/`). Los 15 `ART-NOD-MAG-*` siguen en 15: mismos IDs, mismos nombres de archivo, otra carpeta. La v2 se conserva descartada | Revierte la desviación 11 y corrige la 23. Desviaciones 29–32 abajo |
| 2026-09-18 | Arte: los 3 assets de power-up | `ART-UI-PU-RAY`, `ART-UI-PU-HYD` y `ART-WLD-DROP-HALO` desde `tools/gen_powerups_v1.py`. A.4.4 cerrada. Estrena `anillo`, la última primitiva sin usar | Pedidos para la sección ITEMS de la plantilla de GDD. Cierra T.7 #11 |
| 2026-09-18 | Arte: los 3 fondos de mapa | `ART-BG-01/02/03`, 2048×1152, desde `tools/gen_fondos_v1.py` sobre un módulo nuevo `tools/nova_fondo.py`. A.4.5 cerrada | Pedidos fuera de orden para una entrega de documento. Desviaciones 24–28 abajo |
| 2026-09-18 | Arte: Asteroide (v1 elegida) | Los 3 sprites de `ART-NOD-AST-00*` desde `tools/gen_asteroide_v1.py`. Se descartó una v2 completa, que se conserva. **Con esto `ART-NOD-*` queda completo: 34/34** | A.2.1 pasa de tabla vacía a diseño cerrado y `T6-01` se desbloquea. Desviaciones 18–23 abajo |
| 2026-09-18 | Arte: Magnetar (v2 elegida) | Los 15 sprites de `ART-NOD-MAG-*`, tres facciones, desde `tools/gen_magnetar_v2.py`, más sus 15 hojas de idle de 16 frames. Se descartó una v1 completa, que se conserva. **Entrada histórica: la elección se revirtió el mismo día, ver la fila de arriba** | A.2.4 pasa de tabla vacía a diseño cerrado. Desviaciones 11–17 abajo, con la 11 revertida y la 23 corregida |
| 2026-09-18 | Arte: Púlsar (v2 elegida) | Los 6 sprites de `ART-NOD-PUL-*` desde `tools/gen_pulsar_v2.py`. Se descartó una v1 completa, que se conserva | A.2.3 pasa de boceto a diseño cerrado. Desviaciones 7–10 abajo |
| 2026-09-18 | Arte: paleta, pipeline y Estrella | 20 rampas, 8 primitivas y los 10 sprites de `ART-NOD-STR-*` | Ver abajo. No es una tarea de T.4: el arte no se planifica aquí. |
| — | — | Proyecto de código sin iniciar | — |

**Desviaciones introducidas al cerrar `ART-ST-BUFF` (2026-09-19).** Noveno y
último overlay de A.3. Tres propuestas completas; gana la v1. Detalle en
[A.3.8](./NOVA_Assets_Diseno.md#a38-art-st-buff--power-up-activo).

71. **El buff no es un tinte: es un glifo, y A.3 y 14.7 se contradecían.**
    A.3 lo clasificaba entre los que cubren el cuerpo y por tanto se traman;
    14.7 lo tenía en la **capa 4, con el `zzz` y la brasa**. Gana 14.7. La
    tabla de casos de A.3 pasa de tres a cuatro: hay un cuarto sitio donde
    puede vivir un overlay, que es **la esquina de la celda**.
72. **El cuadrado libre de la esquina son 23 px** en los catorce nodos, y 33
    si solo se cuentan Magnetar y Púlsar. A.3.1 midió 20 y concluyó que ahí
    no cabe un `zzz` de 33×16, que es cierto; lo que no dijo es que sí cabe
    una marca. Queda como dato reutilizable.
73. **`FX-BUFF` no va sobre todos los nodos de la facción**, aunque el
    efecto sí. 9.2 dice a qué afecta cada power-up: Rayo a Magnetar y
    Púlsar, Hidrógeno a Estrella. El Asteroide no gana nada con ninguno y
    marcarlo prometería una ventaja que no tiene (A.2.1). Corregido en 14.5.
    Consecuencia gratis: **ningún nodo lleva nunca los dos buffs**, aunque
    9.1 permita que los dos estén activos, así que el overlay no se apila
    consigo mismo.
74. **Segundo asset que llega con «16 frames, bucle» y sale estático.** El
    galón da **7 frames distintos de 16** en 23 px, la misma pared que dejó
    `ART-ST-SCARE` en un frame. Regla nueva en el contrato: **el número de
    frames se mide, no se planifica.** Y con ella un caso que no era obvio:
    **doblar la frecuencia de un latido divide por dos los frames
    distintos** —un seno de periodo 1/2 sobre 16 frames repite a los 8—, y
    se compensa sumando un canal de periodo completo. Salió midiendo «El
    sobrecalentado», que acabó descartada.
75. **El color de un overlay de power-up es el del power-up, no el de la
    facción**, y es lo contrario de lo que decidió A.4.4 para el halo del
    drop. Allí el icono flotante dice cuál es; sobre un nodo buffeado no
    flota nada, así que el overlay es lo único que puede decirlo. Lleva
    `#FFD23F` y `#FF8FD0` literales de 14.4.

**Desviaciones introducidas al cerrar `ART-ST-CAP` (2026-09-19).** Sexto
overlay de A.3 y el más corto: 5 frames, 0.4 s. Tres propuestas completas;
gana la v2. Detalle en
[A.3.7](./NOVA_Assets_Diseno.md#a37-art-st-cap--capturado).

66. **La geometría no cambia con la facción en ninguno de los catorce
    nodos**, comprobado byte a byte sobre los 34 sprites. 14.0 #3 lo decía y
    A.2.1 lo repetía para el Asteroide, pero nadie lo había medido. La
    consecuencia es de diseño, no de trámite: `ChangeFaction()` es un
    recoloreado en el sitio y **no deja ningún corte que tapar**, al revés
    que `Reconvirtiendo`. `ART-ST-CAP` no necesita ocluir nada, así que se
    queda en un pico de tapado del 18–30 % en vez del 69–85 % que costaba la
    propuesta con fogonazo.
67. **La desviación 63 se parte en dos.** Decía que un efecto con duración
    «entra desde nada y sale a nada». Salir a nada lo cumplen los dos, pero
    **entrar desde nada solo vale para un efecto que se prepara**. Uno que
    se dispara arranca en su pico: el suceso ya ha ocurrido y el sprite ya
    ha cambiado de paleta en ese frame. Con 5 frames, exigirle entrada sería
    gastar el 20 % del asset. Corregida la regla del contrato y añadido
    `entra_de_nada` a `verifica_tinte`, que en ese modo cuenta también el
    frame 0 entre los distintos.
68. **El blanco puro se cobra.** La desviación 65 lo reservó para este
    asset; aquí se usa, y queda anotado que el índice 0 de toda rampa está
    reservado al especular (contrato, *Paleta*) y que este es el **único
    overlay del proyecto que lo usa como color propio**.
69. **14.1 se precisa, no se corrige.** Pedía «flash blanco, onda
    expansiva». La versión elegida conserva el blanco y conserva la onda que
    sale; lo que quita es el relleno del flash y lo que añade es un segundo
    anillo que entra. La propuesta que sí habría obligado a **cambiar el
    texto** —«El sello», un aro que solo se cierra, sin expansión ninguna—
    se descartó por eso y por poco más: es la que menos tapa de las tres.
70. **`FX-CAP` deja de ser el efecto genérico y pasa a ser el específico.**
    A.5 tiene quince VFX por diseñar y al menos cuatro son destellos cortos
    sobre un nodo (`FX-DMG`, `FX-ABS`, `FX-KILL`, `FX-UPG`). Gastar «flash
    blanco + onda expansiva» en la captura habría dejado a los otros catorce
    sin el gesto del que tenían que diferenciarse. Anotado en 14.5: **los
    que quedan se diferencian de `FX-CAP`, no al revés.**

**Desviaciones introducidas al cerrar `ART-ST-CONV` (2026-09-19).** Quinto
overlay de A.3 y **el primero que no es un estado sino un tránsito**: 3.0 s
exactos, 36 frames, no cierra. Tres propuestas completas; gana la v2.
Detalle en [A.3.6](./NOVA_Assets_Diseno.md#a36-art-st-conv--reconvirtiendo).

60. **«Silueta neutra» de 14.1 quiere decir sin tipo, no sin bando, o el
    texto contradice a 8.1.** Durante los 3 s el nodo sigue siendo de su
    dueño —tanto que puede ser capturado, y entonces la reconversión se
    cancela—. Leído como «gris `#8A93A6`», el overlay le diría al jugador
    que el nodo no es de nadie justo en su momento más vulnerable. Corregido
    en 14.1 y recogido en A.8.
61. **`ART-ST-CONV` lleva variante de facción**, y es el segundo overlay que
    la lleva tras `ART-ST-IGN`, pero por un motivo distinto: aquel marca
    posesión porque el sprite no lo hace; este la marca porque **no puede
    dejar de marcarla**. La fila de A.8 que decía «solo `ART-ST-IGN` y
    `ART-ST-READY`» queda ampliada.
62. **Un overlay aditivo no puede dibujar un colapso, y hay que decirlo en
    el contrato.** Con alfa binario solo suma píxeles. La silueta nueva la
    pone el animador **cambiando de sprite** —el nodo acaba siendo otro tipo
    y de nivel 1 (8.1)— y el asset solo **tapa el corte**. Medido: un disco
    de radio **45** cubre la unión de los trece sprites reconvertibles
    (`x 6-92, y 10-88`, 3956 px) sin dejar un píxel fuera y sin tocar el
    borde. Regla nueva en *Reglas de trabajo*.
63. **`verifica_tinte` gana un modo transitorio.** Un efecto con duración no
    se juzga por si cierra, sino por si **entra desde nada y sale a nada**;
    sus frames distintos se cuentan sin los dos vacíos; y de la cara no
    importa *si* la tapa sino **cuántos frames** la deja ciega, porque la
    unión de 36 frames no dice nada útil de un efecto que barre. Regla nueva
    en el contrato.
64. **Primera y única exención al contador de nivel.** Los tintes tienen
    prohibido tapar esquirlas y frentes (A.8 #2), pero aquí el nivel **está
    cambiando**: acaba en N1 del tipo nuevo. La exención la tiene este asset
    porque su duración coincide exactamente con la del cambio, y **no se
    hereda**.
65. **El blanco puro queda reservado a `FX-CAP`.** 14.5 le da a la captura
    «flash blanco + onda», y 8.1 permite que capturen un nodo mientras se
    reconvierte: los dos eventos pueden coincidir sobre el mismo sprite y no
    pueden empezar igual. El frame de corte de la reconversión lleva la
    **banda 3**, donde vive el ancla de 14.4. Anotado en 14.5 como punto de
    partida de `ART-ST-CAP`.

**Desviaciones introducidas al cerrar `ART-ST-DECAY` (2026-09-19).** Cuarto
overlay de A.3, segundo tinte y **primer tinte animado**. Tres propuestas
completas; gana la v2. Detalle en
[A.3.5](./NOVA_Assets_Diseno.md#a35-art-st-decay--infectado).

55. **El cuerpo común a los trece nodos son 505 px, y la cara se come casi
    todo.** Medido: la intersección de los trece es un bulto de radio ≤ 19.9
    en `x 36-60, y 30-60`; quitando la caja de la cara quedan **228 px**, y
    **195 de esos 228 están debajo de la cara**. «Pintar sobre el cuerpo» y
    «pintar en los trece» solo son compatibles en una franja estrecha bajo
    los ojos. No lo dice ningún documento y condiciona a los tres tintes que
    faltan.
56. **La desviación 49 se queda corta: un tinte registra con TRES cosas**, no
    con dos. La tercera son **los otros tintes**. 14.6 marca `Congelado` +
    `Infectado` como «Sí», los dos son trama, y dos campos de Bayer apilados
    pueden acabar en una mancha donde no se lee ninguno de los dos.
57. **`verifica_tinte` gana tres medidas**, y las tres las pidió este asset:
    cierre del bucle, **frames distintos de verdad** —la regla del contrato
    que dejó `ART-ST-SCARE` en un frame, aquí aplicada a uno que sí se anima:
    16 de 16— y **convivencia con otro overlay**.
58. **Y una cuarta, porque una de las que había estaba midiendo otra cosa.**
    La columna *contraste* promedia solo donde el overlay cae encima del
    nodo. «El miasma» toca entre el 1.3 % y el 10.9 % del sprite, así que
    sacaba el peor contraste de las nueve propuestas de A.3 (25.8 sobre un
    Magnetar N1) siendo la que mejor se ve sobre ese nodo: el 98 % de su nube
    está en el aire, compitiendo con el fondo `#0B0E1A` y no con la roca. Se
    añade el **reparto aire/cuerpo por nodo**, para que el contraste se lea
    junto al tamaño de la muestra de la que sale.
59. **Regla nueva del contrato: el ciclo de un aura es radial, no
    giratorio.** Hacer viajar la fase de la onda angular no cierra el bucle
    salvo dando una vuelta entera, y una vuelta en 16 frames a 12 fps es
    1.3 s por revolución: un aura que gira, que es lo que la regla 6 quiere
    evitar. El ciclo va en el radio y en la densidad, desfasados entre sí.

**Desviaciones introducidas al cerrar `ART-ST-FROZEN` (2026-09-19).** Tercer
overlay de A.3 y primero de los que **cubren el cuerpo**. Tres propuestas
completas, las tres verificadas sobre los trece nodos congelables; gana la v2.
Detalle en [A.3.4](./NOVA_Assets_Diseno.md#a34-art-st-frozen--congelado).

48. **`Congelado` va sobre trece sprites, no catorce.** 14.1 lo limita a nodos
    encendidos y el Asteroide nunca lo está: encenderlo lo convierte en otro
    tipo (4.1). Vale igual para `Infectado` y el buff; `Reconvirtiendo` son
    doce, porque además tiene que ser propio. A.3 decía «va sobre los cuatro».
    Corregido en A.3, en 14.1 y en `tools/nova_estados.py` (`CONGELABLES`).
49. **La desviación 47 era falsa a medias, y se corrige.** Decía que los cinco
    que faltaban de A.3 «no tienen que registrar con nada». Un tinte sí
    registra, solo que no con una pieza del sprite sino con dos lecturas que
    no puede tapar: la **cara**, porque 14.6 lo hace convivir con `Asustado`,
    y el **contador de nivel**, porque A.8 #2 lo dejó solo en el sprite. En
    los tres nodos congelables esas dos ocupan entre las dos **todos** los
    radios de 13 a 40 px, así que no hay ningún anillo libre donde poner
    material denso. El grupo que quedaba no era el fácil, era otro difícil.
50. **Tercera vara de verificación:** `verifica_tinte`, junto a `verifica`
    (glifos) y `verifica_ojos` (susto). Mide cara libre, supervivencia del
    contador de nivel y **contraste** contra el nodo de debajo. La vara de un
    glifo —cero píxeles sobre el cuerpo, capa `glow` limpia— suspendería a un
    tinte por hacer exactamente su trabajo. (Al cerrar `ART-ST-DECAY` se le
    añadieron tres medidas más: cierre del bucle, frames distintos de verdad
    y convivencia con otro overlay. Ver la desviación 57.)
51. **Regla nueva del contrato: nada que se dibuje encima de otro dibujo lleva
    contorno.** Medido en la propuesta «El bloque», que acabó descartada: sus
    doce aristas con `veta` se comían el 71 % de un frente de onda del Púlsar
    —33 px de relleno y 35 de contorno sobre una pieza de 142—. Dentro de un
    sprite el contorno separa; sobre un sprite ajeno, tacha. Es el mismo
    argumento que la regla 7 da para la capa `glow`. El número sobrevive a la
    propuesta que lo produjo, y la que quedó elegida es casi toda línea.
52. **Dos primitivas nuevas**, que suben el catálogo implementado a 18:
    `tramar` (el paso de dithering que `halo_trama` y `cono_trama` tenían
    cableado cada una dentro de su propia geometría, sacado aparte para que
    una forma nueva no traiga su propio dither y para que dos propuestas del
    mismo asset se midan igual) y `veta_luz` (la línea de la desviación 51).
53. **El ancla funcional no siempre está en el índice 3.** `#B8F0FF` vive en
    `hielo[2]`, porque por encima de ese tono al hielo solo le quedan el
    blanco y el especular. El contrato decía «índice 3» sin excepción;
    `nova_paleta.py` ya lo admitía en su docstring. Se corrige el contrato, no
    la paleta.
54. **14.7 no cambia, y conviene saber por qué.** Un tinte de la capa 2 va por
    encima de los ojos, así que un nodo congelado y asustado no podría avisar.
    No se arregla reordenando capas —dos ojos flotando sobre un bloque de
    hielo es peor—: se arregla en la geometría del tinte. Queda anotado en
    14.7 como obligación para los tres tintes que faltan.

**Desviaciones introducidas al cerrar `ART-ST-SCARE` (2026-09-18).**

43. **Un overlay puede tener geometría fija y posición variable.** `Asustado`
    es el primero que va sobre los cuatro tipos y tiene que **aterrizar en la
    cara**. Medido en los 34 sprites: el centro en x está registrado
    (47.0–47.5) pero la separación entre ojos va de 9.5 a 16.0 px. Ningún
    overlay de posición fija aterriza, y escalarlo lo prohíbe el pixel-perfect.
    Se resuelve con **tallas discretas más desplazamiento entero**, la misma
    decisión que el protón (A.4.2), y con el asset siendo **un ojo y no un
    par**: se instancia dos veces. Dos archivos cubren los 14 nodos.
44. **La tabla de anclaje es un entregable, no un comentario.** Vive en
    `tools/nova_estados.OJOS` y la leen el generador y su verificación; A.3.3
    la reproduce. Es la primera vez que un asset de este proyecto necesita
    **datos** además de píxeles.
45. **Regla nueva del contrato: una hoja cuyos frames no son distintos no es
    una animación.** Medido antes de decidir: a 6×8 px, desplazar la pupila da
    7–9 frames distintos de 16, contraerla 5–8 y pulsar la esclerótica 2–8.
    `ART-ST-SCARE` es de **un frame**, y el motivo es la rejilla, no el coste.
46. **Regla nueva del contrato: lo que no cabe en una escala cabe en tallas
    discretas más desplazamiento entero.** Estaba implícita en el protón y
    ahora tiene un segundo usuario, así que sube a *Reglas de trabajo*.
47. **A.3 termina de partirse en tres casos**, y queda escrito en su cabecera:
    los que solo van sobre el Asteroide y se colocan al lado, el que va sobre
    los cuatro y aterriza en la cara, y los cinco que faltan, que cubren el
    cuerpo y no tienen que registrar con nada. El grupo difícil ya está hecho.
    ⚠️ **La última frase la desmintió el primero de esos cinco**: ver la
    desviación 49.

**Desviaciones introducidas al cerrar `ART-ST-IGN` (2026-09-18).**

38. **`SinEncender` pasa a tener dos lecturas, y A.3 gana un ID.** 14.1
    disparaba el estado con `faction != Neutral` a secas, pero 4.1 solo deja
    encender con 10 de Energía: el icono prometía algo que el jugador no
    siempre podía cobrar. Ahora son `ART-ST-IGN` (apagado, 1 frame, estático)
    y `ART-ST-READY` (encendible, 16 frames, bucle). **No es un estado nuevo:**
    el animador elige leyendo `energy >= 10` (14.0 #1), así que `NodeState`,
    `NodeStateMachine` y la matriz de 14.6 no se tocan. A.3 pasa de 8 a 9 IDs
    y el total de A.7 de 94 a 95.
39. **El *parpadeo* de 14.1 se reasigna.** Lo pedía para todo `SinEncender`;
    pasa a ser la firma de la lectura accionable, y la pasiva es estática.
40. **`art/states/v<n>/` no aguantaba el segundo overlay** y pasa a
    `art/states/<estado>/v<n>/`: con el esquema anterior la v1 de `sleep` y la
    v1 de `ign` caían en la misma carpeta. `dir_estado()` toma ahora
    `(estado, version)`. **Corrige las rutas escritas en A.3.1 el mismo día.**
41. **Las comprobaciones de overlay salen a `tools/nova_estados.py`** y las
    usan los cuatro generadores. Un asset se comprueba contra lo que va a
    tener al lado, no contra sí mismo, y con la misma vara en todas las
    propuestas. El generador **falla** si algo no pasa. Recogido en el contrato.
42. **Regla nueva: entre dos lecturas del mismo overlay, la accionable nunca
    puede pesar menos que la pasiva.** Se encontró contando, no mirando: una
    versión intermedia dejaba el icono «encendible» en 120 px en el valle del
    parpadeo contra 156 px del «apagado». El suelo del parpadeo lo fija esa
    desigualdad. Cerrado en A.8.

**Desviaciones introducidas al cerrar `ART-ST-SLEEP` (2026-09-18).**

33. **La convención de propuestas deja de ser solo de nodos.** ~~`art/states/v<n>/`~~
    y `dir_estado()` en `tools/nova_core.py`, con el generador declarando
    `ESTADO` y `VERSION` en vez de `NODO` y `VERSION`. Recogido en A.1, A.3 y
    en el contrato. **Corregida por la desviación 40:** la ruta lleva el nombre
    del overlay antes de la versión, `art/states/<estado>/v<n>/`, y
    `dir_estado()` toma `(estado, version)`.
34. **La regla de tramado de A.3 se parte en dos.** Se traman los overlays que
    **cubren el cuerpo** —tintes y auras: `Congelado`, `Infectado`, buff—,
    porque tienen que dejarlo ver. Un **glifo** de estado no cubre nada:
    compite con el fondo y va sólido con contorno. El alfa binario no cambia;
    cambia contra qué se compite. En A.3.1 y en el contrato.
35. **«Los overlays son independientes del tipo» se matiza, y con medidas.** La
    unión de los cuatro nodos vivos ocupa `y 10-88, x 6-92` de la celda: el
    mayor hueco libre en esquina son 20 px y un `zzz` legible necesita 33×16.
    `Dormido` y `SinEncender` solo se aplican al Asteroide (14.1), así que se
    colocan contra **su** silueta. La regla sigue entera para los otros cuatro.
36. **La capa 4 de 14.7 pasa a llamarse «Glifos y overlays»** y se documenta que
    un glifo de estado no pisa un solo píxel del sprite: vive en el hueco que
    el nodo deja dentro de su celda. Es lo que hace que la capa 6 —el número de
    Energía, que nunca se oculta— no entre en conflicto con él.
37. **Un asset de A.3 se verifica contra el sprite de verdad**, no contra una
    suposición: el generador abre el PNG del Asteroide y mide el solape. Y para
    un glifo contable se añade una comprobación que los nodos no necesitaban:
    **que las piezas no se toquen entre ellas** en ningún frame. Tres Z pegadas
    no se cuentan, y un `zzz` que no se cuenta no dice «duerme».

**Desviaciones introducidas al volver el Magnetar a la v1 (2026-09-18).**

29. **El Magnetar vuelve a transform en el reparto del idle**, y con eso la
    desviación 11 queda revertida. El motivo de la regla —«los que tienen que
    mover algo interno llevan hoja»— no le aplica a un cuerpo tallado con
    esquirlas capturadas. **Las 15 hojas `mag_lvl<n>_<faccion>_sheet.png` se
    quedan en `v2/` con la propuesta descartada y salen del inventario
    pendiente** (T.7 #6). Recogido en el contrato, en 14.0 #4 y en A.2.4.
30. **El contador de nivel del Magnetar pasa a ser posicional.** La escalera
    sigue siendo aditiva —N4 es N3 más una pieza—, pero el elemento es la
    esquirla capturada y su sitio lo reparte el ángulo áureo. **Efecto lateral
    documentado:** la huella deja de ser monótona (0.64 / 0.94 / 0.94 / 1.05 /
    1.05 u), porque la extensión la fija la pieza más excéntrica y no la
    última añadida. El contador sigue siendo exacto; lo que no crece en todos
    los escalones es el rectángulo que lo contiene.
31. **La tabla de ejes de A.8 deja de ser disjunta**, y corrige la desviación
    23. El Magnetar y el Asteroide comparten ahora *simetría* («ninguna») e
    *idle* (transform), y *espacio interior* pasa a **macizo en los cuatro**:
    el calado se va con la v2. Los dos siguen separados por material, cuerpo y
    rampa. **`calado` queda como valor de eje libre** para el primer nodo que
    lo necesite.
32. **Se invierte qué primitivas están en uso.** `poliedro` y `veta` pasan de
    «propuesta descartada» a ejercitadas por el nodo vivo; `linea_dipolar` y
    el `esferoide` del núcleo y los yugos pasan al otro lado. El catálogo no
    se toca: lo que se descarta es un diseño, no una herramienta (A.7).

**Desviaciones introducidas al cerrar los fondos (2026-09-18).**

24. **Módulo nuevo `tools/nova_fondo.py`**, con 7 primitivas de fondo. El
    contrato decía que las primitivas viven en `nova_core.py`; los fondos son
    una familia con reglas distintas —campos de densidad de 2048×1152 en vez
    de cuerpos en una celda de 96— y solo comparten paleta y matriz de Bayer.
    El contrato ya las separaba en su sección de Resolución.
25. **Tres rampas nuevas**, la paleta pasa de 20 a **22**: `bg_s1`, `bg_s2` y
    `bg_s3`. Existen porque **todas las demás rampas significan algo** y un
    fondo pintado con una de ellas le miente al jugador durante toda la
    partida. `gusano`, `hielo`, `decaimiento`, `rayo` e `hidrogeno` quedan
    expresamente prohibidas en un fondo.
26. **Presupuesto de contraste**, calculado de la paleta y verificado sobre el
    PNG: la media de cualquier ventana de 96×96 por debajo del tono más
    oscuro de un cuerpo de nodo. **Se corrigió una vez**: la primera versión
    puso la cota en la luminancia de `CONTORNO` razonando que el perfilado
    dejaría de leerse, y es falso —el contorno nunca fue un perfilado de alto
    contraste contra el cielo—. Con esa cota los tres fondos salían correctos
    y vacíos.
27. **En un fondo se modula la cobertura, no el tono.** Si una banda cubre el
    100 % de una ventana, esa ventana ya está por encima del presupuesto por
    oscura que sea. La cobertura máxima de cada banda se despeja de la cota.
28. **Regla nueva: nada del fondo puede medir lo que mide un nodo** (0.6–1.2
    u). Lo que caiga en esa franja es un nodo a ojos del jugador hasta que
    intente clicarlo, y eso es peor que un fondo feo.

**Desviaciones introducidas al cerrar el Asteroide (2026-09-18).**

18. **Cuatro primitivas nuevas**, que suben el catálogo implementado a **16**:
    `bulto` (contorno orgánico por armónicos, con el sombreado en el radio
    normalizado), `crater` (depresión cóncava con reborde), `esquirla`
    (contorno recto con sombreado curvo) y `estratos` (capas paralelas sin
    centro). Las dos últimas salieron de la propuesta descartada y **no se
    retiran**, igual que `poliedro`.
19. **La concavidad entra en el contrato** como material propio, no como un
    ajuste. Con ella, contorno y sombreado quedan como dos ejes
    independientes y las tres combinaciones vivas —`poliedro`, `bulto`,
    `esquirla`— están documentadas en *Los tres cuerpos*.
20. **Regla nueva: un accidente de superficie modula la banda que hay, no la
    sustituye**, y su desplazamiento va acotado y simétrico. Pintado en
    absoluto, un hoyo en la mitad en sombra se lee como un bulto. Afecta a
    `crater` y a `estratos`.
21. **El especular se puede apagar.** Es la única excepción viva a la regla
    3 del contrato: una roca mate no es material pulido. Va por parámetro
    explícito. Y en un cuerpo alargado el brillo va en una arista, no en la
    superficie, porque el punto se estira hasta ser un manchón.
22. **A.2.1 se corrige.** Pedía «marca de posesión» en el sprite del
    Jugador, lo que contradice 14.0 #3 —una variante de facción es la misma
    geometría con otra rampa—. La posesión la marca el overlay `ART-ST-IGN`,
    que 4.1 ya obliga a mostrar. Ninguna geometría cambia entre facciones.
23. **La partición de materiales queda cerrada** con el cuarto valor:
    Asteroide = materia que **solo refleja**, sin una sola fuente de luz
    propia. Y la tabla de ejes de A.8 pasa de lista de huecos libres a
    registro completo. ~~Los cuatro nodos no comparten ni una casilla.~~
    **Corregida por la desviación 31:** con el Magnetar en «El Yunque»
    comparte *simetría* e *idle* con el Asteroide, y *espacio interior* pasa a
    macizo en los cuatro.

**Desviaciones introducidas al cerrar el Magnetar (2026-09-18).**

11. ~~**El Magnetar cambia de lado en el reparto del idle**: pasa de transform
    a **hoja de 16 frames**.~~ **Revertida por la desviación 29:** la excepción
    se abrió para «La Botella» y se cierra con ella. Lo que sí queda en pie de
    aquí es la regla que la justificaba: **el criterio es el motivo, no la
    lista**. Recogido en el contrato, en 14.0 #4 y en A.2.4.
12. **Tres primitivas nuevas**, que suben el catálogo implementado a 12:
    `poliedro` (cuerpo de caras planas: la regla 1 muestreada por cara y no
    por píxel, con `sesgo_mesa` y especular de esquina), `veta` (fractura
    sólida de banda constante) y `linea_dipolar` (línea de campo cerrada
    `r = R·sin²t`, con el grosor siguiendo a `|B|` acotado, escala anisótropa
    y onda viajera). Las dos primeras salieron de la propuesta descartada y
    **no se retiran**: son materiales que el catálogo no tenía.
13. **La partición de materiales pasa a ser regla del contrato**: Estrella
    luz continua, Púlsar luz tramada, Magnetar materia. Es un eje de
    separación de primer orden, como la silueta o la simetría.
14. **Dos reglas de trabajo nuevas**: un nodo no se construye con las piezas
    de otro —reutilizar primitivas es obligatorio, heredar el reparto de
    primitivas del vecino es lo contrario—, y el material es un eje de
    separación de primer orden.
15. **A.7 queda desmentida en su propia predicción.** Daba por hecho que el
    Magnetar heredaría `anillo` y `anillo_orbital`. No heredó ninguna de las
    dos, y fue lo mejor que le pasó al diseño. `anillo` sigue sin estrenar.
16. **Tabla de ejes de diseño ocupados** en A.8, para consultarla *antes* de
    empezar un nodo. Sale de que esta es la tercera vez que el proyecto
    descubre lo mismo por las malas.
17. **Restricción geométrica documentada** (ver T.7 #9): cara grande y cinco
    lazos anidados no caben juntos en la celda de 96.

**Desviaciones introducidas al cerrar el Púlsar (2026-09-18).**

7. **`art/nodes/` pasa a tener una carpeta por nodo y una subcarpeta por
   propuesta**, `art/nodes/<nodo>/v<n>/`, y todo generador pasa a llamarse
   `gen_<nodo>_v<n>.py` con el sufijo de versión siempre presente. La
   convención anterior era plana y sin versionar. Motivo: el Púlsar necesitó
   dos diseños completos vivos a la vez para poder compararlos, y una versión
   descartada no se borra. Recogido en A.1.
8. **Dos primitivas nuevas**, que suben el catálogo implementado a 9:
   `esferoide` (cuerpo elipsoidal inclinado; `esfera` pasa a delegar en ella,
   verificado pixel a pixel sobre los 16 sprites que ya existían) y
   `cono_trama` (haz cónico de luz por trama Bayer sobre `glow`).
9. **Dos reglas de trabajo nuevas en el contrato:** dos nodos no se separan
   repintándolos, y una huella se mide sobre el ciclo entero y no sobre el
   frame 0.
10. **`elipse_base_plana` está en el contrato pero nunca se implementó.**
    Detectado al cerrar esta tarea. No se ha tocado; ver T.7 #7.

**Desviaciones introducidas el 2026-09-18 (paleta, pipeline y Estrella).** Todas están ya volcadas a los documentos correspondientes; se listan aquí porque contradicen texto anterior:

1. **PPU 64, no 96.** La celda de 96 px pasa a valer 1.5 u. El contrato decía "PPU igual al ancho de celda".
2. **12 fps fijo.** Sustituye al "por defecto 16 frames" del contrato. A.3 y A.5 recalculadas; los valores viejos implicaban entre 4 y 15 fps según el efecto.
3. **El protón no escala de forma continua.** Tres sprites discretos. Anula la fórmula de 14.3 y sube el inventario de 90 a 94 assets.
4. **`✅` cambia de significado** en A.0: "generado y disponible en `art/`", no "integrado en Unity". La definición anterior era circular con la regla de bloqueo T.2 #3.
5. **Cuatro primitivas nuevas** en el contrato: cizalla de corona, trama Bayer sobre una capa `glow`, tubo de grosor constante y anillo orbital con profundidad. El catálogo de código deja de estar copiado en el `.md` y pasa a `tools/`.
6. **A.2.2 reescrita.** La Estrella ya no es "corona + protuberancias" sino cuerpo + atmósfera de dos capas con cizalla.

---

## T.6 Criterios de salida por fase

Copiados de la [sección 19](./NOVA_GameDesign_Spec.md#19-checklist-de-implementación-por-fases) del maestro. Una fase no se cierra sin cumplirlos.

| Fase | Criterio |
|---|---|
| 1 | Se puede capturar un Asteroide, encenderlo como Estrella y tomar un nodo enemigo |
| 2 | Los cuatro tipos son funcionales y el nivel 3 es jugable |
| 3 | Los tres poderes funcionan y pasan los casos 8–14 de la sección 17 |
| 4 | La IA del mapa 3 vence a un jugador descuidado |
| 5 | Los 9 niveles son completables de principio a fin |
| 6 | Todos los assets de [A.7](./NOVA_Assets_Diseno.md#a7-resumen-de-progreso) están ✅ e integrados |

---

## T.7 Pendientes abiertos

| # | Asunto | Dónde se resuelve |
|---|---|---|
| 1 | ~~5 decisiones de diseño visual sin cerrar~~ | ✅ Cerradas el 2026-09-18. [A.8](./NOVA_Assets_Diseno.md#a8-decisiones-de-diseño-cerradas) |
| 2 | Coordenadas exactas de los 9 niveles | Apéndice del maestro. Sin empezar |
| 3 | Audio: no hay inventario equivalente al de A | Pendiente de crear |
| 4 | Estilo de la UI: paneles, botones y estados | Hay paleta y tipografía, falta el lenguaje visual. Bloquea A.6 |
| 5 | Empaquetado en atlas | El pivote está decidido; el atlas no |
| 6 | Hojas de idle sin ID de inventario | Quedan **dos** familias, no tres: Estrella y Púlsar tienen el idle diseñado y sus generadores animan por `t`, pero falta volcarlas a `_sheet.png` y ninguna tiene ID. El Magnetar sale de este pendiente: resuelve su idle por transform (A.2.4) y las 15 hojas generadas son de la v2 descartada |
| 7 | `elipse_base_plana` documentada y no implementada | Está en el catálogo de [NOVA_Arte_Tecnica.md](./NOVA_Arte_Tecnica.md) pero no en `tools/nova_core.py`. Ningún asset la ha necesitado: en NOVA nada se apoya en un suelo. Decidir si se implementa o si sale del contrato |
| 8 | Versiones descartadas | Púlsar v1; **Magnetar v2 («La Botella»)**; Asteroide v2 («El Fragmento»); **`ART-ST-SLEEP` v1 («La escalera»)** en `art/states/sleep/v1/`; **`ART-ST-IGN` v1 («El interruptor»)** en `art/states/ign/v1/`; **`ART-ST-SCARE` v2 («La pupila dilatada»)** en `art/states/scare/v2/`; **`ART-ST-FROZEN` v1 («La escarcha») y v2 («El bloque»)** en `art/states/frozen/v1/` y `v2/`; **`ART-ST-DECAY` v1 («El goteo») y v3 («El enjambre»)** en `art/states/decay/v1/` y `v3/`; **`ART-ST-CONV` v1 («El torno») y v3 («El apagón»)** en `art/states/conv/v1/` y `v3/`; **`ART-ST-CAP` v1 («El fogonazo») y v3 («El sello»)** en `art/states/cap/v1/` y `v3/`; **`ART-ST-BUFF` v2 («El temblor») y v3 («El sobrecalentado»)** en `art/states/buff/v2/` y `v3/`. Cada una con su carpeta y su generador. **Son catorce propuestas descartadas en total**, todas con su generador y su PNG. Se conservan por A.1. Borrarlas es una decisión pendiente, no un olvido |
| 9 | ~~Cara grande XOR cinco lazos anidados~~ | ✅ **Deja de aplicar al nodo vivo.** La desigualdad sigue siendo cierta —cinco lazos necesitan ~4 px de separación, 16 px de radio para los cuatro huecos, y con el exterior topado en 38 px (1.2 u) el interior no pasa de 22 px, lo que deja el cuerpo en ≤ 14 px de semieje—, pero quien la pagaba era la v2. «El Yunque» no anida nada y su cuerpo llega a 17.5 px de semieje horizontal. Vuelve a la mesa solo si vuelve la v2 (#14) |
| 10 | Asteroide v2, reabrible bajo condición | Perdió porque `L` es global: sus estratos salen a la misma diagonal en todos los asteroides de la pantalla y ocho iguales leen como papel pintado. Vuelve a la mesa si 11.2 acaba colocando dos o tres asteroides por nivel en vez de ocho, o si se aceptan varias variantes de estratificación **como sprites distintos** (A.2.1 pasaría de 3 archivos a 6 o 9) |
| 11 | ~~Iconos de los dos power-ups~~ | ✅ Cerrado el 2026-09-18. [A.4.4](./NOVA_Assets_Diseno.md#a44-power-ups--9) |
| 12 | **Escala del tablero: 32×18 u es demasiado grande** | Un nodo ocupa el 4.7 % del ancho. **Análisis completo y decisión en [T.8](#t8-decisión-abierta-escala-del-tablero).** Hay que cerrarla ANTES que #2 |
| 13 | El documento no tiene número de versión | La plantilla de GDD exige un campo *Versión* y un *Historial de versiones*, y pide explícitamente **un número, no una fecha**. El proyecto lleva el registro T.5 pero no numera los `.md`. Decidir el esquema (`0.x` mientras no haya build jugable) y dónde vive: cabecera del maestro |
| 14 | Magnetar v2, reabrible bajo condición | «El Yunque» cuenta mal a 1× a partir de tres esquirlas: son el elemento más pequeño del sprite (A.2.4, *Lo que se paga*). La segunda lectura del nivel es el radio de A.4.1, siempre visible en neutrales y enemigos. **Si con el radio en pantalla el nivel sigue sin contarse en juego**, la v2 está entera en `art/nodes/magnetar/v2/` y vuelve a la mesa con su coste conocido: la cara más pequeña de los cuatro (#9) y 15 hojas de idle que producir |
| 15 | `ART-ST-SLEEP` v1, reabrible bajo condición | «El vaivén» no cuenta una historia: tres glifos que solo cabecean pueden leerse como un cartel pegado encima en vez de como el bicho respirando ([A.3.1](./NOVA_Assets_Diseno.md#a31-art-st-sleep--dormido)). **Si en juego el `zzz` parece UI y no aliento**, la v1 («La escalera», con relevo y traslación) está entera en `art/states/sleep/v1/`, con su coste conocido: apaga un glifo de golpe una vez por vuelta y por Z |
| 16 | `ART-ST-IGN` v1, reabrible bajo condición | «El pedernal» pesa la mitad que «El interruptor» —143–196 px contra 306 constantes— y una chispa se acerca más a la firma de la Estrella que un anillo ([A.3.2](./NOVA_Assets_Diseno.md#a32-art-st-ign-y-art-st-ready--sinencender)). **Si entre ocho asteroides el icono no se ve o se confunde con una Estrella pequeña**, la v1 está entera en `art/states/ign/v1/`, con su coste conocido: sería el primer símbolo de interfaz dentro del tablero |
| 17 | `ART-ST-SCARE` v2, reabrible bajo condición | «Los ojos como platos» pone mucha esclerótica y poca pupila, y eso empuja al bicho hacia el dibujo animado ([A.3.3](./NOVA_Assets_Diseno.md#a33-art-st-scare--asustado)). **Si en juego los cuatro nodos asustados parecen de otra serie**, la v2 («La pupila dilatada») está entera en `art/states/scare/v2/`: mismo anclaje, mismas tallas, misma quietud, solo cambia la pupila |

| 18 | `ART-ST-FROZEN` v1, reabrible bajo condición | «La escarcha» es la propuesta más barata en huella —317 px— y la única que deja la cara **entera** en los trece. Pierde porque sus agujas blancas alrededor del Magnetar se confunden con una esquirla más, y una esquirla es el contador de nivel de ese nodo. Está entera en `art/states/frozen/v1/` |
| 19 | **`ART-ST-FROZEN` v2, reabrible bajo condición** | «El bloque» es un prisma de seis caras, y es **la más legible de las tres a 1×**: 91.5 de contraste sobre la Estrella N5, contra 73.4 de la elegida. Llegó a estar elegida y documentada. Pierde por ser la primera figura de contorno **recto y regular** dentro del tablero, que es el argumento con el que se descartó la v1 de `ART-ST-IGN` ([A.3.4](./NOVA_Assets_Diseno.md#a34-art-st-frozen--congelado)). **Si en juego «El vidrio» no se ve sobre una Estrella grande, o se confunde con las vetas del Magnetar**, la v2 está entera en `art/states/frozen/v2/`, con su coste conocido: 1278 px de huella y el riesgo de leerse como un recuadro de UI |
| 20 | `ART-ST-DECAY` v1, reabrible bajo condición | «El goteo» no le pone aura al nodo: le pone una costra en la franja común bajo la cara y siete gotas cayendo. Es la más barata (460 px), la que mejor convive con el hielo y la que menos se parece a una corona de Estrella. Pierde por presencia: es una mancha discreta y `Infectado` es un estado indefinido que el jugador tiene que ver para curarlo. **Si «El miasma» resulta ruidoso junto al hielo o se confunde con la corona de la Estrella**, está entera en `art/states/decay/v1/` |
| 22 | `ART-ST-CONV` v1, reabrible bajo condición | «El torno» desmonta el nodo con tres anillos que caen hacia el centro y salen después. Es el gesto que 14.1 describe palabra por palabra —colapso a un punto y reencendido desde él— y deja la cara ciega 5–6 frames, uno menos que la elegida. Pierde por composición: anillos concéntricos son **simetría radial *n*-fold centrada**, la firma de la Estrella, y una de cada tres reconversiones acaba en Estrella. **Si en juego «La colada» se lee como un efecto de menú**, está entera en `art/states/conv/v1/` |
| 24 | `ART-ST-CAP` v1, reabrible bajo condición | «El fogonazo» es la lectura literal de 14.1: núcleo blanco que llena el nodo y onda que sale. Es **con diferencia la más contundente en visión periférica**, que es lo que pide el suceso más importante que le puede pasar a un nodo. Pierde por dos cosas medidas: tapa el sprite al 69–85 % y deja la cara ciega 2 frames de 5 —en el Asteroide se lo come entero—, y gasta en la captura el gesto genérico que los otros catorce VFX de A.5 iban a necesitar. **Si en juego la captura pasa desapercibida**, está entera en `art/states/cap/v1/` |
| 26 | `ART-ST-BUFF` v2, reabrible bajo condición | «El temblor» son seis trazos horizontales que corren a los lados del nodo. Es la única de las tres que **dice tempo**, que es lo que un +50 % de cadencia significa, y usa el eje horizontal, que no ocupa ningún nodo ni ningún otro overlay. Da 16 frames distintos de 16. Pierde porque sus trazos viven en la franja donde el Magnetar guarda sus esquirlas y porque cuesta 228 px contra 87. **Si en juego el galón parece UI y no estado**, está entera en `art/states/buff/v2/` |
| 27 | `ART-ST-BUFF` v3, descartada por medida | «El sobrecalentado» es la lectura que A.3 daba por hecha: un aura tramada pegada al cuerpo que late al doble. **No es reabrible sin rediseñarla:** sobre un nodo infectado y buffeado a la vez, su aro punteado y la nube de `Infectado` se funden en un moteado único (`art/_preview/estados/buff_vs_infectado.png`). Es la misma construcción con otro color. Se conserva en `art/states/buff/v3/` por A.1, y por la medida que salió de ella (desviación 74) |
| 25 | `ART-ST-CAP` v3, reabrible bajo condición | «El sello» es un solo anillo que se cierra sobre el nodo y engorda al llegar. Es la que menos tapa (39–47 %) y **la única que no deja la cara ciega ni un frame**, y el gesto «algo se cierra sobre un nodo» no lo ocupa nada más en el proyecto. Pierde porque **contradice 14.1**: no tiene expansión ninguna, y elegirla obligaría a cambiar el texto en vez de precisarlo. Está entera en `art/states/cap/v3/` |
| 23 | `ART-ST-CONV` v3, reabrible bajo condición | «El apagón» es la lectura literal de 14.1: el nodo se apaga a gris y vuelve. Es **la más barata de las tres** —una sola hoja en vez de dos, y solo **2 frames de cara ciega** de 36—. Pierde porque durante casi tres segundos el nodo parece Neutral y no lo es (desviación 60). Si algún día se acepta esa lectura, está entera en `art/states/conv/v3/` |
| 21 | `ART-ST-DECAY` v3, reabrible bajo condición | «El enjambre» son trece motas cayendo por carriles, sin campo continuo: el **mejor contraste de las nueve propuestas de A.3** (74.9–121.1) y el que menos contador de nivel se lleva (95.6 %). Pierde porque a 1× hay que ir a buscarlo, y porque sus motas de 3 px se pierden dentro de la trama del hielo. Está entera en `art/states/decay/v3/` |

---

## T.8 Decisión abierta: escala del tablero

> Abierta el 2026-09-18. **Hay que cerrarla antes que T.7 #2** (las coordenadas de los 9 niveles).
> Comparación montada: `art/_preview/escala/32u_vs_20u.png`.

### El diagnóstico

Los nodos se leen pequeños. **No es un problema de resolución, es una proporción en unidades de mundo:** el tablero mide 32 u y un nodo mide ~1 u, así que ocupa el **4.7 % del ancho**. Subir la resolución del arte no cambia eso — solo lo haría más nítido, igual de pequeño.

### Por qué escalar en Unity no lo arregla

1. **Un zoom no cambia una proporción.** Escalando nodos y fondo por el mismo factor, el nodo sigue siendo el 4.7 % del ancho. El zoom mueve todo a la vez; lo que molesta es una relación, y una relación es invariante al zoom.
2. **Escalar solo los nodos rompe la rejilla.** Con `Filter Mode: Point` una escala no entera produce filas de píxeles de distinto grosor dentro del mismo sprite. **Ya pasó en este proyecto:** es exactamente por lo que el protón dejó de escalar de forma continua y pasó a tres sprites discretos ([A.4.2](./NOVA_Assets_Diseno.md#a42-protón-y-proyectiles--143), que anula la fórmula de 14.3). Y aun a escala entera, un nodo de píxeles 2×2 sobre un fondo de píxeles 1×1 se ve mal: el grano del cielo mediría la mitad.
3. **La salida legítima acaba en el mismo sitio.** Bajar el PPU de los nodos *es* escalar en Unity y es gratis para el arte, pero obliga a regenerar el fondo para compartir rejilla. **Ninguna ruta evita regenerar el fondo**, que por suerte es una constante.

Lo que sí conviene hacer con la escala de Unity: **probar**. En la escena de `T1-12`, subir el Transform de los nodos a 1.5× o 2× y mirar. No es *shippable* y desalinea la rejilla, pero dice en dos minutos qué proporción gusta, y esa es la que luego se hornea en unidades.

### Las tres opciones

| | Qué se hace | Coste de arte | Riesgo |
|---|---|---|---|
| **A** *(recomendada)* | Encoger el tablero en unidades | Regenerar los 3 fondos: **una constante**. Cero cambios en sprites de nodo | Cambia el balance relativo (ver abajo). **No toca A.8 #4** |
| **B** | Bajar el PPU, dejar el tablero en 32 u | Regenerar los 3 fondos igualmente | **Rompe [A.8 #4](./NOVA_Assets_Diseno.md#a8-decisiones-de-diseño-cerradas)**: el anillo de un Magnetar N1 apenas sobresaldría de su propio sprite. Arrastra rebalanceo de 4.4 y 16 |
| **C** | Regenerar los sprites en celda mayor (192 px) | Rehacer 34 sprites y 15 hojas | **No cambia la proporción**, solo la nitidez. Descartada |

### Tamaños candidatos

El ancho del tablero decide además a qué pantallas se escala sin temblor. A PPU 64:

| Tablero | Arte | 1080p | 1440p | 2160p | Nodo (% del ancho) |
|---|---|---|---|---|---|
| 32 × 18 *(actual)* | 2048×1152 | 0.94× | 1.25× | 1.875× | 4.7 % |
| 30 × 16.875 | 1920×1080 | **1×** | 1.33× | **2×** | 5.0 % |
| 24 × 13.5 | 1536×864 | 1.25× | 1.67× | 2.5× | 6.3 % |
| **20 × 11.25** *(propuesta)* | **1280×720** | 1.5× | **2×** | **3×** | **7.5 %** |
| 15 × 8.4375 | 960×540 | **2×** | 2.67× | **4×** | 10.0 % |

**El tamaño actual no escala entero a ninguna resolución común.** Es un fallo latente que hoy no duele porque no hay juego corriendo.

A 15 u el nodo es el más grande y es limpio a 1080p, pero un Magnetar N5 (radio 3.6 u) cubriría el 48 % del tablero de diámetro: habría que recortar los radios de [4.4](./NOVA_Nodos.md#44-magnetar).

### Qué cambia si se adopta A con 20 × 11.25 u

Encoger el tablero hace relativamente más grande **todo lo medido en unidades**, no solo los nodos:

| | 32 u | 20 u |
|---|---|---|
| Nodo | 4.7 % del ancho | **7.5 %** |
| Magnetar N5, radio 3.6 u | 22 % del ancho de diámetro | 36 % |
| Alcance de poder 5 u / 7 u | 16 % / 22 % | 25 % / 35 % |
| Protón cruzando el tablero a 2.5 u/s | 12.8 s | 8.0 s |

Ninguno es un fallo: son decisiones de balance, y **no hay un solo nivel diseñado todavía**. La relación huella ↔ radio del Magnetar no se toca, que es justo lo que A.8 #4 protege.

### Por qué la ventana es ahora

| | Existe hoy |
|---|---|
| Líneas de C# | **0** |
| ScriptableObjects con los números de balance | **0** (es `T1-05`) |
| Coordenadas de los 9 niveles | **0** (T.7 #2) ← *el artefacto caro* |
| Sprites de nodo afectados | **0** |
| Fondos a regenerar | 3, una constante en `tools/nova_fondo.py` |

### Al cerrarla, tocar

1. `tools/nova_fondo.py`: `ANCHO, ALTO`. Regenerar con `gen_fondos_v1.py` y comprobar que el presupuesto sigue en verde — las constantes de `sigma`, `comba` y tamaño de grava están en píxeles y habrá que reajustarlas al lienzo nuevo.
2. [A.8 #4](./NOVA_Assets_Diseno.md#a8-decisiones-de-diseño-cerradas): la fila de huella y PPU.
3. [NOVA_Arte_Tecnica.md](./NOVA_Arte_Tecnica.md), *Resolución* y *Fondos*: el tamaño del lienzo de fondo.
4. [A.4.5](./NOVA_Assets_Diseno.md#a45-fondos): resolución de los tres `ART-BG-*`.
5. El maestro, donde diga «32 × 18 u».
6. Revisar, sin cambiarlos todavía, los números de [4.4](./NOVA_Nodos.md#44-magnetar) (radios) y de la sección 16 (alcances de poder), y la regla de 11.3 del Asteroide a menos de 5 u.
