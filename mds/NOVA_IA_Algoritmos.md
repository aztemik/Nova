# NOVA — IA del Enemigo: algoritmos

> Parte de la especificación de **NOVA**. Documento maestro: [NOVA_GameDesign_Spec.md](./NOVA_GameDesign_Spec.md).
> Corresponde a la **sección 12** del maestro; la numeración `12.x` se conserva.
>
> Este documento es **algorítmico**: define el comportamiento computable del Enemigo. No contiene reglas de juego ni arte. Las reglas que la IA debe respetar están en el maestro; los nodos sobre los que opera, en [NOVA_Nodos.md](./NOVA_Nodos.md).
>
> **Scripts que lo implementan** (ver [15.7](./NOVA_GameDesign_Spec.md#157-input-ia-y-ui)): `EnemyBrain.cs`, `AIEvaluator.cs`, `AIThreatResponder.cs`, `EnemyCommandIssuer.cs`, `AIProfile.cs`.

---

## 12. IA del Enemigo — algoritmos

El Enemigo no es un jugador humano. Es un algoritmo que evalúa el estado del tablero y ejecuta las mismas acciones legales que el jugador.

### 12.1 Ciclo de decisión

```
cada IntervaloDeDecision segundos:
    1. Snapshot del tablero (NodeRegistry, ver 15.6)
    2. Si hay una amenaza crítica -> responder (defensa)
    3. Si no, generar lista de acciones candidatas
    4. Puntuar cada candidata
    5. Ejecutar la mejor si su puntuación supera UmbralDeAccion
    6. Si ninguna supera el umbral, no hacer nada (acumular)
```

La IA **nunca actúa más de una vez por ciclo**. Esto la hace legible y evita ráfagas inhumanas.

### 12.2 Acciones candidatas

| Acción | Cuándo se considera |
|---|---|
| Atacar nodo | Existe un nodo no propio dentro del alcance efectivo |
| Encender Asteroide | Posee un Asteroide con ≥ 10 de Energía |
| Mejorar nodo | Un nodo propio tiene Energía ≥ coste de mejora |
| Reforzar nodo | Un nodo propio está bajo amenaza y otro tiene excedente |
| Cargar poder | Posee un Púlsar sin poder cargado |
| Lanzar poder | Posee un Púlsar con poder cargado y objetivo válido |
| Reconvertir | Se queda sin Estrellas y tiene un nodo con Energía suficiente |

### 12.3 Función de puntuación (atacar)

```
Score(origen, destino) =
      ValorTipo(destino)              # Estrella 100, Púlsar 80, Magnetar 70, Asteroide 40
    + BonusPowerUp(destino)           # +60 si el Asteroide está marcado con power-up
    - CosteEfectivo(origen, destino)  # energía necesaria, incluida resistencia x2
    - RiesgoDeRuta(origen, destino)   # 6 por cada Magnetar hostil que cubre la trayectoria
    - PenalizacionVaciado(origen)     # 30 si dejar el origen por debajo del 30% lo expone
    * MultiplicadorAgresividad
```

Se descartan de entrada las acciones cuyo `CosteEfectivo` supere la Energía disponible del origen al 100%.

### 12.4 Detección de amenaza y defensa

Un nodo propio está **amenazado** si la suma de Carga de los protones hostiles dirigidos a él, aplicando su multiplicador, es mayor o igual que su Energía actual.

Respuesta, en este orden de prioridad:
1. Si un nodo propio tiene Energía suficiente y está a distancia, **reforzar** (enviar el 50%).
2. Si tiene un Púlsar con Cero Absoluto cargado y el origen del ataque está en alcance, **congelarlo**.
3. Si el refuerzo no llega a tiempo, **evacuar**: enviar toda la Energía del nodo amenazado a otro nodo propio, cediendo un nodo vacío en lugar de un nodo lleno.

La evacuación es lo que hace que la IA se sienta inteligente. Debe implementarse.

### 12.5 Perfiles por mapa

`AIProfile` es un ScriptableObject (ver [15.4](./NOVA_GameDesign_Spec.md#154-data--scriptableobjects)). Un perfil por mapa.

| Parámetro | Mapa 1 | Mapa 2 | Mapa 3 |
|---|---|---|---|
| Intervalo de decisión | 3.0 s | 2.0 s | 1.2 s |
| Umbral de acción | 40 | 25 | 10 |
| Multiplicador de agresividad | 0.7 | 1.0 | 1.3 |
| Usa evacuación | No | Sí | Sí |
| Usa reconversión | No | No | Sí |
| Prioriza power-ups | No | Sí | Sí |
| Envía al 100% | Nunca | Si el margen es > 1.5× | Si el margen es > 1.2× |
| Ruido de decisión | ±25% | ±15% | ±5% |

El **ruido de decisión** altera aleatoriamente la puntuación final. Es el mecanismo principal para que el mapa 1 se sienta torpe sin necesidad de un algoritmo distinto.

### 12.6 Prohibiciones

La IA no puede: ver protones antes de que se lancen, conocer los poderes que el jugador está cargando antes de que la barra sea visible, generar Energía extra, ni ignorar tiempos de carga o de reconversión.

---


---

## 12.7 Contrato de implementación

| Requisito | Regla |
|---|---|
| Canal único | Toda acción sale por `INodeCommandIssuer` ([15.1](./NOVA_GameDesign_Spec.md#151-principios), principio 5). |
| Pureza | `AIEvaluator` es estático y sin estado: misma entrada → misma salida (salvo el ruido, que recibe una semilla). |
| Determinismo testeable | El ruido de decisión usa un `System.Random` con semilla inyectable, no `UnityEngine.Random`. |
| Una acción por ciclo | `EnemyBrain` ejecuta como máximo un comando por `IntervaloDeDecision`. |
| Sin arte | Ninguna tarea de IA depende de assets. La fase 4 del tracking es desbloqueable siempre. |

### Tests mínimos exigidos

1. `AIEvaluator` prefiere una Estrella nivel 3 a un Asteroide cuando ambos son alcanzables.
2. Descarta un objetivo cuyo `CosteEfectivo` supera la Energía del origen al 100%.
3. `RiesgoDeRuta` penaliza 6 por cada Magnetar hostil cuyo radio cruza el segmento origen→destino.
4. Con perfil de mapa 1, dos ejecuciones con semillas distintas pueden elegir acciones distintas; con la misma semilla, no.
5. `AIThreatResponder` evacúa (no refuerza) cuando el refuerzo no llega antes del impacto.
