# NOVA — Especificación técnica de diseño y arquitectura

> Juego de conquista de nodos en tiempo real, 2D, Unity. Un jugador contra IA.
> **Documento maestro.** Versión 1.1 (dividida en varios archivos).
> Referencia de género: *JellyGo!* (AvoxGames). Tema: astrofísica.

---

## Mapa de documentos

| Archivo | Contiene | Numeración |
|---|---|---|
| **NOVA_GameDesign_Spec.md** (este) | Reglas del juego, economía, poderes, niveles, UI, arquitectura, balance y casos borde. | Secciones 1–19 |
| [NOVA_Nodos.md](./NOVA_Nodos.md) | Los 4 tipos de nodo: stats, niveles, costes y comportamiento. | Sección 4 |
| [NOVA_IA_Algoritmos.md](./NOVA_IA_Algoritmos.md) | Algoritmos del Enemigo: ciclo de decisión, puntuación, amenaza, perfiles. | Sección 12 |
| [NOVA_Estados_Animaciones.md](./NOVA_Estados_Animaciones.md) | Estados y animaciones: qué las dispara, sobre quién, cuánto duran, cómo salen. | Sección 14 |
| [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md) | Inventario de arte: cada sprite/VFX/UI con su ID, archivo esperado y estado. | Sección A |
| [NOVA_Tracking.md](./NOVA_Tracking.md) | Seguimiento de desarrollo y prompt de continuación para la IA. | Sección T |

Las secciones extraídas **conservan su número original**. Una referencia a «ver 4.4» o «ver 12.5» sigue siendo válida; solo cambia el archivo.

---

## Índice

1. [Concepto y alcance](#1-concepto-y-alcance)
2. [Glosario normativo](#2-glosario-normativo)
3. [Facciones](#3-facciones)
4. Personajes (nodos) → **[NOVA_Nodos.md](./NOVA_Nodos.md)**
5. [Economía: la Energía](#5-economía-la-energía)
6. [Protones y resolución de impacto](#6-protones-y-resolución-de-impacto)
7. [Poderes del Púlsar](#7-poderes-del-púlsar)
8. [Reconversión](#8-reconversión)
9. [Power-ups del cielo](#9-power-ups-del-cielo)
10. [Condiciones de victoria y derrota](#10-condiciones-de-victoria-y-derrota)
11. [Progresión: 3 mapas × 3 niveles](#11-progresión-3-mapas--3-niveles)
12. IA del Enemigo (algoritmos) → **[NOVA_IA_Algoritmos.md](./NOVA_IA_Algoritmos.md)**
13. [Controles y UI](#13-controles-y-ui)
14. Feedback visual y estados → **[NOVA_Estados_Animaciones.md](./NOVA_Estados_Animaciones.md)**
15. [Arquitectura en Unity](#15-arquitectura-en-unity)
16. [Tablas de balance consolidadas](#16-tablas-de-balance-consolidadas)
17. [Casos borde y reglas de resolución](#17-casos-borde-y-reglas-de-resolución)
18. [Decisiones tomadas por defecto](#18-decisiones-tomadas-por-defecto)
19. [Checklist de implementación por fases](#19-checklist-de-implementación-por-fases)

---

## 1. Concepto y alcance

### 1.1 Pitch

El jugador controla un conjunto de cuerpos celestes en un sistema estelar. Cada cuerpo almacena **Energía**. Enviar Energía de un cuerpo a otro lanza un **Protón** que viaja por el espacio. Si el Protón llega a un cuerpo aliado, lo recarga. Si llega a un cuerpo rival o neutral, le resta Energía; cuando la Energía del objetivo llega a cero, el cuerpo cambia de bando.

El objetivo de cada nivel es que no quede ningún cuerpo del Enemigo ni ningún Asteroide neutral.

### 1.2 Alcance cerrado

| Aspecto | Decisión |
|---|---|
| Jugadores | 1 humano contra 1 IA. Sin multijugador, sin red. |
| Dimensión | 2D, vista cenital ortográfica. |
| Motor | Unity 2D, URP 2D o Built-in. Sin física de Rigidbody para el gameplay. |
| Niveles | 9 (3 mapas × 3 niveles). |
| Tipos de nodo | 4 (Asteroide, Estrella, Púlsar, Magnetar). |
| Progresión entre niveles | Ninguna. Cada nivel arranca desde cero, igual que en JellyGo. |
| Persistencia | Solo el nivel máximo desbloqueado. |
| Duración objetivo por nivel | 90 s (mapa 1) a 240 s (mapa 3). |

### 1.3 Fuera de alcance en v1.0

Multijugador, economía entre partidas, árbol de habilidades global, más de 4 tipos de nodo, niveles con scroll de cámara (todos los niveles caben en una pantalla fija).

---

## 2. Glosario normativo

Estos términos son los que deben usarse en el código, sin sinónimos. Cualquier ambigüedad aquí se traduce en bugs.

| Término | Significado exacto | Identificador en código |
|---|---|---|
| **Nodo** | Cualquier cuerpo celeste del mapa, de cualquier tipo y bando. | `Node` |
| **Tipo de nodo** | Asteroide, Estrella, Púlsar o Magnetar. | `NodeType` |
| **Bando / Facción** | Neutral, Jugador o Enemigo. | `Faction` |
| **Energía** | Recurso único. Se almacena en nodos y viaja en protones. Entero. | `Energy` |
| **Materia Inerte** | La Energía de un Asteroide neutral. No es utilizable ni contable en la barra de poder. Siempre vale 10. | `InertMatter` |
| **Tope** | Energía máxima que un nodo puede almacenar. Depende del tipo, no del nivel. | `EnergyCap` |
| **Protón** | Proyectil único generado por un envío. Lleva una **Carga**. | `Proton` |
| **Carga** | Energía que transporta un Protón. Se muestra como número sobre el proyectil. | `Charge` |
| **Nivel de nodo** | 0 (Asteroide) a 5. Determina las estadísticas del nodo. | `NodeLevel` |
| **Encendido** | Convertir un Asteroide propio de nivel 0 en un nodo de nivel 1 de otro tipo. | `Ignition` |
| **Reconversión** | Cambiar un nodo ya encendido a otro tipo. Lo devuelve a nivel 1. | `Conversion` |
| **Mejora** | Subir un nivel dentro del mismo tipo. | `Upgrade` |
| **Poder** | Habilidad del Púlsar. Cero Absoluto, Decaimiento o Agujero de Gusano. | `Power` |
| **Cadencia** | Disparos por segundo del Magnetar. | `FireRate` |
| **Velocidad de ataque** | Término visible en la UI. Se traduce distinto según tipo (ver 13.4). | `AttackSpeed` |
| **Barra de poder** | Barra inferior, comparativa e informativa. | `PowerBar` |

**Unidad de distancia:** unidad de mundo de Unity (u). El área jugable mide **32 × 18 u** y coincide con una cámara ortográfica de `size = 9` en 16:9.

---

## 3. Facciones

```
Faction { Neutral = 0, Player = 1, Enemy = 2 }
```

| Facción | Color primario | Control | Notas |
|---|---|---|---|
| **Jugador** | Cian `#3FD7F5` | Ratón del usuario | Siempre es la facción 1. |
| **Enemigo** | Magenta `#F2456B` | `EnemyBrain` (IA) | Ejecuta exactamente las mismas acciones legales que el jugador. Sin ventajas ocultas de reglas; solo varían sus parámetros de decisión. |
| **Neutral** | Gris `#8A93A6` | Nadie | Solo existe como Asteroide nivel 0. No actúa, no genera, no dispara, salvo el caso del Magnetar neutral descrito en [4.4](./NOVA_Nodos.md#44-magnetar). |

### 3.1 Regla de paridad

El Enemigo y el Jugador comparten el mismo conjunto de acciones legales y la misma tabla de costes. Todo comando de ambos pasa por la misma interfaz (`INodeCommandIssuer`). Está prohibido que la IA modifique energía, niveles o estados por vías que el jugador no tenga.

### 3.2 Nota sobre el Magnetar neutral

Un Magnetar puede existir en estado Neutral únicamente si empieza el nivel así por diseño de mapa (`LevelDefinition`). Un Magnetar capturado nunca vuelve a Neutral. Un Magnetar neutral **sí dispara**, y dispara a protones de ambas facciones. Es el único nodo neutral con comportamiento activo, y es una herramienta central de diseño de niveles: bloquea corredores para los dos bandos hasta que alguien lo tome.

---

## 4. Personajes (nodos)

> **Movido a [NOVA_Nodos.md](./NOVA_Nodos.md).** La numeración se conserva: toda referencia a «4.x» de este documento apunta a ese archivo.

## 5. Economía: la Energía

### 5.1 Regla fundamental

**Solo la Estrella genera Energía. Sin excepciones.** Púlsar, Magnetar y Asteroide almacenan Energía recibida y la gastan, pero nunca la producen.

Consecuencias de diseño que deben respetarse:
- La Energía total de un bando solo puede crecer si tiene al menos una Estrella.
- Las capturas no crean Energía: el defensor pierde y el atacante gasta.
- Los protones derribados destruyen Energía permanentemente.

### 5.2 Envío

Cualquier nodo con Energía > 0, excepto el Asteroide, puede enviar.

| Acción | Resultado |
|---|---|
| Clic izquierdo sobre origen, clic izquierdo sobre destino | Envía el **50%** de la Energía del origen (redondeo hacia abajo). |
| Clic izquierdo sobre origen, **doble** clic sobre destino | Envía el **100%** de la Energía del origen. |

- El envío es **instantáneo** en el origen: la Energía sale del nodo y entra en el protón en el mismo frame.
- Con varios orígenes seleccionados, cada uno lanza su propio protón con su propio cálculo.
- Un envío del 50% de 1 de Energía redondea a 0 y **no se ejecuta**. Se requiere Energía ≥ 2 para el envío al 50%, y ≥ 1 para el envío al 100%.
- Un nodo puede quedar en 0 de Energía sin morir, sin cambiar de bando y sin perder nivel.

### 5.3 Recepción

| Caso | Efecto |
|---|---|
| Destino de la misma facción | Suma la Carga a su Energía. El excedente sobre el tope **se descarta**. |
| Destino de la misma facción, tipo Magnetar | Suma **1:1**. La resistencia ×2 solo aplica a impactos hostiles. |
| Destino de otra facción o neutral | Resta (ver sección 6). |

### 5.4 Topes

| Tipo | Tope |
|---|---|
| Asteroide neutral | 10 (Materia Inerte, no utilizable) |
| Asteroide propio | 10 |
| Estrella | 50 |
| Púlsar | 100 |
| Magnetar | 100 |

El tope no cambia con el nivel. Es una propiedad del tipo.

---

## 6. Protones y resolución de impacto

### 6.1 El protón

- Cada envío genera **un único protón**, no un enjambre. Su Carga es la Energía enviada.
- Muestra su Carga como número pequeño sobre el sprite. El número se actualiza en tiempo real si un Magnetar lo va desgastando.
- **Velocidad:** 2.5 u/s, constante, en línea recta desde el centro del origen al centro del destino.
- El tamaño del sprite cambia con la Carga en **tres escalones discretos** (ver 14.3), pero eso es solo presentación.
- Un protón en vuelo **conserva la facción de su emisor en el momento del lanzamiento**, aunque el nodo origen cambie de bando durante el viaje.
- Un protón no puede ser redirigido tras lanzarse.
- Los protones no colisionan entre sí.

### 6.2 Resolución de impacto

Pseudocódigo normativo. Es la única fuente de verdad para `ImpactResolver`.

```
ResolveImpact(proton, target):

    if proton.faction == target.faction:
        target.energy = min(target.energy + proton.charge, target.cap)
        return ABSORBED

    # Impacto hostil
    multiplier = (target.type == Magnetar) ? 0.5 : 1.0
    effective  = floor(proton.charge * multiplier)

    if effective < target.energy:
        target.energy -= effective
        return DAMAGED

    # Captura
    remainder = effective - target.energy
    target.energy = min(remainder, target.cap)
    ChangeFaction(target, proton.faction)
    return CAPTURED
```

Notas obligatorias:
- El redondeo del multiplicador es **hacia abajo**, y se aplica una sola vez sobre la Carga total, no disparo a disparo.
- En una captura, el remanente también está afectado por el multiplicador. Un protón de 120 contra un Magnetar con 50 lo captura y le deja `120*0.5 - 50 = 10`.
- Al capturar, el nodo **conserva su tipo y su nivel**. Solo cambia de facción.
- Un nodo capturado a 0 de Energía sigue siendo un nodo válido del nuevo bando.

### 6.3 Efecto del Magnetar sobre protones

```
OnMagnetarShot(proton):
    proton.charge -= 2
    if proton.charge <= 0:
        DestroyProton(proton)   # La Energía se pierde. No vuelve al emisor.
```

Varios Magnetares que cubran el mismo tramo de trayectoria disparan de forma independiente y acumulativa.

### 6.4 Casos de captura por tipo

| Objetivo | Energía | Carga necesaria |
|---|---|---|
| Asteroide neutral | 10 | 10 |
| Estrella nivel 5 llena | 50 | 50 |
| Púlsar lleno | 100 | 100 |
| Magnetar lleno | 100 | **200** |
| Cualquier nodo a 0 | 0 | 1 |

---

## 7. Poderes del Púlsar

### 7.1 Regla de carga

- El Púlsar carga **un solo poder a la vez**.
- Al iniciar la carga, la Energía del Púlsar **baja progresivamente** mientras la barra de carga del poder sube. Las dos curvas están acopladas: la barra refleja `energíaInvertida / costeTotal`.
- Si la Energía del Púlsar se agota antes de completar la carga, la carga **se pausa** en el porcentaje alcanzado y se reanuda automáticamente cuando el Púlsar reciba Energía. Lo ya invertido no se pierde.
- Una vez cargado al 100%, el poder **se mantiene indefinidamente** hasta que se lance. Durante ese tiempo no se puede cargar otro poder.
- La carga puede **cancelarse manualmente**. Se recupera el **50%** de lo invertido, redondeado hacia abajo, respetando el tope.

### 7.2 Tabla de poderes

| Poder | Nivel req. | Coste | Tiempo de carga | Drenaje | Alcance | Objetivos válidos |
|---|---|---|---|---|---|---|
| **Cero Absoluto** | 1 | 20 | 8 s | 2.5 E/s | 7 u | Enemigo, Neutral |
| **Decaimiento** | 2 | 35 | 12 s | 2.9 E/s | 7 u | Enemigo, Neutral |
| **Agujero de Gusano** | 3 | 60 | 16 s | 3.75 E/s | 5 u | Cualquier nodo no propio |

El alcance se mide de centro a centro. Los objetivos fuera de alcance se muestran atenuados y no son clicables al apuntar.

El proyectil del poder viaja a **6 u/s** y no puede ser derribado por un Magnetar. Solo los protones son derribables.

### 7.3 Cero Absoluto

Congela el nodo objetivo. Representa un enfriamiento al cero absoluto: el cuerpo queda inerte.

**Mientras está congelado, el nodo:**
- No genera Energía (Estrella).
- No dispara (Magnetar).
- No carga ni lanza poderes (Púlsar). Una carga en curso queda **pausada**, no se pierde.
- No puede enviar Energía.
- No puede mejorarse ni reconvertirse.
- **Sí puede recibir impactos.**

**Deshielo.** Es la regla especial que invierte el sentido de recibir Energía:

> Un nodo congelado pierde Energía cuando **cualquier** facción, incluida la suya, le envía Energía. Cuando su Energía llega a 0, el nodo se descongela y pasa al bando del **último emisor que impactó**.

```
ResolveImpact_Frozen(proton, target):
    multiplier = (target.type == Magnetar) ? 0.5 : 1.0
    effective  = floor(proton.charge * multiplier)

    if effective < target.energy:
        target.energy -= effective
        target.lastToucher = proton.faction
        return THAW_PROGRESS

    target.energy = 0
    Unfreeze(target)
    ChangeFaction(target, proton.faction)
    return THAWED_AND_CAPTURED
```

- Un nodo congelado que ya está a **0 de Energía** se descongela y cambia de bando con el siguiente protón que lo alcance, de Carga 1 o superior.
- El remanente de Carga se pierde: un nodo descongelado siempre queda a 0.
- **Auto-deshielo de seguridad:** si un nodo congelado permanece 30 s sin recibir ningún impacto, se descongela solo, conservando su facción y su Energía. Evita nodos muertos permanentes que bloqueen la condición de victoria.

### 7.4 Decaimiento

Infecta el nodo objetivo con decaimiento radiactivo. Su Energía cae sola.

- **Tasa:** −2 de Energía por segundo, hasta 0.
- Al llegar a 0, el nodo **permanece infectado** a 0 de Energía y sigue perteneciendo a su dueño.
- Un nodo infectado sigue funcionando con normalidad: la Estrella genera (y pierde más de lo que genera), el Magnetar dispara, el Púlsar carga.
- **Cura:** cualquier facción que le envíe Energía elimina la infección. Se resuelve como un impacto normal (sección 6.2), es decir:
  - Si lo cura su propio dueño, recupera Energía y pierde la infección.
  - Si lo cura otra facción y la Carga basta para vaciarlo, cambia de bando sin infección.
  - Si lo cura otra facción y la Carga no basta, pierde la infección pero sigue siendo del dueño original.
- No es acumulable: un segundo Decaimiento sobre un nodo ya infectado **reinicia** el efecto, no duplica la tasa.
- Visual: aura verde pulsante `#7CF23F` y partículas descendentes. Un contador visible de la Energía cayendo.

### 7.5 Agujero de Gusano

Cambia de bando el nodo objetivo **conservando su Energía, su tipo y su nivel**. Es el poder definitivo y por eso es el más caro.

- Funciona sobre cualquier nodo que no sea ya propio, incluidos Asteroides neutrales, Magnetares llenos y Púlsares.
- **Ignora la resistencia ×2 del Magnetar.** Un Magnetar con 100 de Energía cambia de bando íntegro.
- Elimina los estados Congelado y Decaimiento del objetivo al capturarlo.

**Robo de carga (regla táctica clave).** Si el objetivo es un Púlsar enemigo que está cargando o tiene cargado un poder:

| Momento del impacto | Resultado |
|---|---|
| Carga en curso (1–99%) | El Púlsar cambia de bando y la carga **se resetea a 0%**. La Energía invertida se pierde. |
| Carga al 100%, poder aún no lanzado | El Púlsar cambia de bando **con el poder cargado intacto**, utilizable de inmediato por el nuevo dueño. |
| Poder ya lanzado (proyectil en vuelo) | El proyectil ya lanzado **completa su efecto** a favor de quien lo lanzó. El Púlsar cambia de bando vacío. |

Esta ventana es intencional y debe ser legible en pantalla: la barra de carga del Púlsar enemigo es visible para el jugador en todo momento.

---

## 8. Reconversión

Permite cambiar un nodo ya encendido a otro tipo. No existe en JellyGo; es propia de este juego.

### 8.1 Reglas

- Se paga con la **Energía del propio nodo**, que debe tenerla disponible en ese momento.
- El nodo vuelve a **nivel 1** del nuevo tipo.
- Conserva la Energía sobrante, recortada al tope del nuevo tipo.
- Dura **3 segundos** con una animación de colapso y reencendido.
- Durante esos 3 s el nodo **no genera, no dispara, no envía y no puede mejorarse**, pero **sí puede ser impactado y capturado**. Si es capturado durante la animación, la reconversión se cancela y el nodo queda como estaba antes de iniciarla, con el nuevo dueño.
- **No se puede iniciar** si el nodo está Congelado, Infectado, cargando un poder o ya reconvirtiéndose.
- Un nodo **no puede volver a Asteroide**. La reconversión es solo entre Estrella, Púlsar y Magnetar.

### 8.2 Costes

| Desde | Hacia | Coste |
|---|---|---|
| Estrella | Púlsar o Magnetar | 20 |
| Púlsar | Estrella o Magnetar | 20 |
| Magnetar | Estrella o Púlsar | 30 |

El Magnetar cuesta más de desmontar porque su resistencia ×2 lo hace más caro de perder por la vía normal.

### 8.3 Ejemplo

Un Magnetar nivel 4 con 45 de Energía se reconvierte a Estrella: paga 30, queda como **Estrella nivel 1 con 15 de Energía** (15 < tope 50, no hay recorte). Ha perdido 3 niveles de inversión. La reconversión es una maniobra de emergencia, no una rutina.

---

## 9. Power-ups del cielo

### 9.1 Funcionamiento

Un power-up cae sobre un **Asteroide neutral elegido al azar** y lo marca con un halo luminoso y un icono flotante. **El primer bando que encienda ese Asteroide recibe el efecto.**

- Solo puede haber **un Asteroide marcado a la vez**.
- Si nadie lo enciende en **30 s**, el power-up se apaga y arranca el temporizador del siguiente.
- Si no queda ningún Asteroide neutral cuando toca un drop, el drop se **salta** y el temporizador se reinicia.
- El efecto se aplica a **toda la facción**, no solo al nodo encendido.
- **Duración:** 20 s.
- **Magnitud:** +50%.
- Dos power-ups del mismo tipo no se acumulan: el segundo **reinicia el temporizador** a 20 s.
- Los dos tipos sí pueden estar activos a la vez.

### 9.2 Tipos

| Power-up | Icono | Efecto | Afecta a |
|---|---|---|---|
| **Rayo Cósmico** | Rayo | +50% velocidad de ataque | Cadencia del Magnetar y velocidad de carga del Púlsar |
| **Nube de Hidrógeno** | Nube con cruz | +50% generación de Energía | Intervalo de la Estrella (se multiplica por 0.667) |

Probabilidad: 50% / 50%.

### 9.3 Calendario de drops

| Mapa | Primer drop | Intervalo | Máximo por nivel |
|---|---|---|---|
| 1 (niveles 1–3) | 25 s | 40–55 s aleatorio | 3 |
| 2 (niveles 4–6) | 30 s | 50–70 s aleatorio | 4 |
| 3 (niveles 7–9) | 35 s | 60–85 s aleatorio | 5 |

El intervalo se cuenta desde que el power-up anterior es recogido o expira, no desde que aparece.

---

## 10. Condiciones de victoria y derrota

### 10.1 Victoria del Jugador

Se cumple cuando **el Enemigo no posee ningún nodo**.

**Cascada de conquista:** al cumplirse, todos los Asteroides neutrales restantes pasan automáticamente al Jugador en una animación de 3 s, de más cercano a más lejano. Esto satisface la regla de que ningún nodo puede quedar Neutral al final de la partida, sin obligar al jugador a limpiar manualmente el mapa cuando el resultado ya está decidido.

Los protones del Enemigo en vuelo cuando pierde su último nodo **se desvanecen** sin impactar.

### 10.2 Derrota del Jugador

Cualquiera de estas dos:

1. **Aniquilación:** el Jugador no posee ningún nodo.
2. **Estancamiento:** el Jugador no posee ninguna Estrella **y** la suma de Energía de todos sus nodos es **menor que 10**, es decir, no puede encender ni reconvertir nada. Se comprueba solo si tampoco tiene protones en vuelo ni poderes cargados.

El estancamiento evita partidas zombi en las que el jugador está vivo pero es matemáticamente incapaz de volver a crecer.

### 10.3 Fin de nivel

| Resultado | Acción |
|---|---|
| Victoria | Pantalla de victoria. Se desbloquea el siguiente nivel. Botón "Siguiente" y "Repetir". |
| Derrota | Pantalla de derrota. Botón "Reintentar" que **reinicia el nivel desde cero**, y "Volver al mapa". |

El jugador puede reiniciar el nivel en cualquier momento desde el menú de pausa. No hay guardado a mitad de nivel.

---

## 11. Progresión: 3 mapas × 3 niveles

### 11.1 Estructura

| Mapa | Nombre | Niveles | Mecánicas introducidas |
|---|---|---|---|
| 1 | Sistema Interior | 1–3 | Envío, captura, Estrella, Magnetar, mejoras |
| 2 | El Cinturón | 4–6 | Púlsar, Cero Absoluto, Decaimiento, Magnetar neutral |
| 3 | Espacio Profundo | 7–9 | Agujero de Gusano, reconversión, IA agresiva |

### 11.2 Diseño de niveles

`N` = nodos totales. `Ast` = asteroides neutrales al inicio. Los nodos iniciales de cada bando se indican como tipo(nivel).

| Nivel | N | Jugador inicia con | Enemigo inicia con | Ast | Neutrales especiales | Duración objetivo |
|---|---|---|---|---|---|---|
| 1 | 5 | Estrella(1) | Estrella(1) | 3 | — | 90 s |
| 2 | 7 | Estrella(1) | Estrella(2) | 5 | — | 110 s |
| 3 | 8 | Estrella(1), Asteroide | Estrella(2), Magnetar(1) | 4 | — | 130 s |
| 4 | 9 | Estrella(1) | Estrella(2), Púlsar(1) | 6 | — | 150 s |
| 5 | 10 | Estrella(1), Magnetar(1) | Estrella(2), Púlsar(1) | 6 | 1 Magnetar(2) neutral | 170 s |
| 6 | 11 | Estrella(2) | Estrella(3), Púlsar(2), Magnetar(2) | 6 | 1 Magnetar(3) neutral | 190 s |
| 7 | 12 | Estrella(1), Estrella(1) | Estrella(3), Púlsar(3), Magnetar(3) | 7 | 1 Magnetar(3) neutral | 210 s |
| 8 | 13 | Estrella(2) | Estrella(3)×2, Púlsar(3), Magnetar(3) | 7 | 2 Magnetar(3) neutrales | 230 s |
| 9 | 14 | Estrella(2), Magnetar(1) | Estrella(4)×2, Púlsar(3)×2, Magnetar(4) | 7 | 2 Magnetar(4) neutrales | 240 s |

### 11.3 Curva de dificultad

La dificultad sube por tres vías simultáneas, todas parametrizadas en `LevelDefinition`:

1. **Ventaja inicial del Enemigo:** más nodos y de mayor nivel.
2. **Calidad de la IA:** intervalo de decisión más corto y mejor evaluación (ver [sección 12](./NOVA_IA_Algoritmos.md)).
3. **Geometría del mapa:** más Magnetares neutrales bloqueando rutas y mayores distancias entre los nodos del jugador.

Ningún nivel debe ser imposible: en todos, el jugador debe tener al menos un Asteroide neutral a menos de 5 u de su posición inicial, alcanzable antes de que el Enemigo llegue a él.

---

## 12. IA del Enemigo — algoritmos

> **Movido a [NOVA_IA_Algoritmos.md](./NOVA_IA_Algoritmos.md).** La numeración se conserva: toda referencia a «12.x» de este documento apunta a ese archivo.

## 13. Controles y UI

### 13.1 Ratón

| Entrada | Acción |
|---|---|
| **Clic izquierdo** sobre nodo propio | Seleccionar / deseleccionar |
| **Clic izquierdo** sobre nodo destino (con selección activa) | Enviar el **50%** |
| **Doble clic izquierdo** sobre nodo destino | Enviar el **100%** |
| **Arrastre** desde nodo propio hasta destino | Equivalente al envío al 50% |
| **Arrastre en vacío** (lazo) | Selección múltiple de nodos propios |
| **Clic derecho** sobre cualquier nodo | Abrir panel de información y mejoras |
| **Clic derecho** en vacío | Cancelar selección / cerrar panel |
| **Esc** | Menú de pausa |

### 13.2 Resolución del doble clic

Clic simple y doble clic comparten el primer evento, así que el envío **no se ejecuta en el primer clic**. Se usa un buffer:

```
OnClickDestino():
    if bufferActivo:
        CancelarBuffer()
        Enviar(100%)
    else:
        bufferActivo = true
        EsperarSegundos(0.25)   # cancelable
        Enviar(50%)
        bufferActivo = false
```

0.25 s de latencia es imperceptible y evita el bug de enviar 50% + 50% = 75% acumulado.

### 13.3 Panel de clic derecho

Contiene, en este orden:

1. Tipo y **nivel** actual (`Estrella · Nivel 3`).
2. Energía actual / tope.
3. **Velocidad de ataque** (ver 13.4).
4. Botón de **mejora** con su coste, si el nodo no está al nivel máximo y si es propio. Si está al máximo, se muestra `NIVEL MÁXIMO` y el botón desaparece.
5. Botón de **reconversión** con los tres destinos posibles y su coste.
6. Si es un Púlsar propio: rueda de poderes (ver 13.5).

El botón de mejora se muestra **deshabilitado y con el coste en rojo** cuando no hay Energía suficiente, nunca oculto. El jugador necesita saber cuánto le falta.

### 13.4 Traducción de "velocidad de ataque"

Es un único campo en la UI que significa cosas distintas según el tipo:

| Tipo | Se muestra como |
|---|---|
| Estrella | Generación: `X.XX E/s` |
| Magnetar | Cadencia: `X.X disparos/s` |
| Púlsar | Carga: `X.XX E/s` |
| Asteroide | El panel solo muestra `DORMIDO` y el coste de encendido |

### 13.5 Rueda de poderes del Púlsar

Clic izquierdo sobre un Púlsar propio abre tres ranuras en orden fijo: **1 Cero Absoluto · 2 Decaimiento · 3 Agujero de Gusano**. Las no desbloqueadas aparecen con candado y el nivel requerido.

- Clic en una ranura: inicia la carga. Aparece una barra bajo el nodo.
- Con un poder cargado, la ranura brilla y el cursor pasa a modo apuntado.
- Clic en un objetivo válido: lanza. Clic derecho: cancela el apuntado sin perder la carga.

### 13.6 HUD permanente

| Elemento | Posición | Contenido |
|---|---|---|
| Barra de poder | Inferior, ancho completo | Dos colores. Jugador crece desde la izquierda, Enemigo desde la derecha. **Solo informativa, sin ningún efecto de juego.** |
| Cronómetro | Superior derecha | Tiempo transcurrido |
| Nivel | Superior izquierda | `Mapa 2 · Nivel 5` |
| Pausa | Superior derecha | Botón |

La barra de poder suma la Energía de todos los nodos de cada bando. **No cuenta** la Materia Inerte de los Asteroides neutrales ni la Carga de los protones en vuelo.

---

## 14. Feedback visual y estados

> **Movido a [NOVA_Estados_Animaciones.md](./NOVA_Estados_Animaciones.md).** La numeración se conserva: toda referencia a «14.x» de este documento apunta a ese archivo.
> Los assets que estas animaciones consumen están inventariados en [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md).

## 15. Arquitectura en Unity

### 15.1 Principios

1. **Los datos no son MonoBehaviour.** Todo el balance vive en ScriptableObjects. Cambiar un número no requiere tocar código.
2. **Un script, una responsabilidad.** Si un script necesita la palabra "y" para describirse, hay que partirlo.
3. **La presentación solo lee.** Ningún script de `Presentation` o `UI` modifica estado de juego. Se suscriben a eventos.
4. **La lógica de reglas es estática y pura.** `ImpactResolver`, `EnergyMath` y `ConversionRules` no tienen estado ni referencias a escena, y son testeables sin abrir Unity.
5. **Jugador e IA usan el mismo canal.** Ambos emiten comandos a través de `INodeCommandIssuer`. Es imposible que la IA haga algo ilegal porque no existe la vía.
6. **Sin `Find`, sin `SendMessage`, sin singletons salvo los tres registros del apartado 15.6.**

### 15.2 Estructura de carpetas

```
Assets/
├── Scripts/
│   ├── Core/                 # C# puro, sin UnityEngine salvo tipos básicos
│   │   ├── Enums/
│   │   ├── Rules/
│   │   └── Events/
│   ├── Data/                 # ScriptableObjects
│   ├── Gameplay/
│   │   ├── Nodes/
│   │   ├── Combat/
│   │   ├── Powers/
│   │   └── Economy/
│   ├── AI/
│   ├── Input/
│   ├── Systems/
│   ├── UI/
│   ├── Presentation/
│   └── Utils/
├── Data/                     # Instancias .asset de los SO
│   ├── Nodes/
│   ├── Powers/
│   ├── Levels/
│   └── AIProfiles/
├── Prefabs/
├── Art/
├── Audio/
└── Scenes/
    ├── Boot.unity
    ├── MainMenu.unity
    ├── LevelSelect.unity
    └── Game.unity            # Escena única reutilizada por los 9 niveles
```

### 15.3 Core — reglas puras (sin MonoBehaviour)

| Script | Responsabilidad única |
|---|---|
| `Faction.cs` | Enum de facciones |
| `NodeType.cs` | Enum de tipos |
| `NodeState.cs` | Enum de estados |
| `PowerType.cs` | Enum de poderes |
| `ImpactResult.cs` | Enum: Absorbed, Damaged, Captured, ThawProgress, ThawedAndCaptured, Destroyed |
| `EnergyMath.cs` | Multiplicadores, redondeos, cálculo de coste efectivo de captura |
| `ImpactResolver.cs` | Resolución de impacto de protón, incluido el caso congelado. Entrada: snapshot. Salida: `ImpactResult` + deltas. **Sin efectos secundarios.** |
| `ConversionRules.cs` | Validez y coste de encendido, mejora y reconversión |
| `ThreatCalculator.cs` | Dado un nodo y los protones en vuelo, dice si está amenazado y en cuánto tiempo. Usado por la IA **y** por el estado `Asustado`. |
| `GameEventChannels.cs` | Definición de los canales de evento |

### 15.4 Data — ScriptableObjects

| Script | Contenido |
|---|---|
| `NodeDefinition.cs` | Tipo, tope, nº de niveles, array de `NodeLevelData`, prefab, sprites por facción |
| `NodeLevelData.cs` | `[Serializable] struct`: coste de mejora, intervalo de generación, radio, cadencia |
| `PowerDefinition.cs` | Tipo, coste, tiempo de carga, alcance, velocidad del proyectil, nivel requerido, VFX |
| `BalanceConfig.cs` | Velocidad del protón, daño por disparo del Magnetar, multiplicador del Magnetar, buffer de doble clic, duración de reconversión, auto-deshielo, tasa de decaimiento |
| `LevelDefinition.cs` | Lista de `NodeSpawnData`, referencia a `AIProfile`, config de drops, duración objetivo |
| `NodeSpawnData.cs` | `[Serializable] struct`: posición, tipo, nivel, facción, energía inicial |
| `PowerUpDefinition.cs` | Tipo, magnitud, duración, icono, estadística afectada |
| `AIProfile.cs` | Los 8 parámetros de la tabla [12.5](./NOVA_IA_Algoritmos.md#125-perfiles-por-mapa) |

### 15.5 Gameplay — componentes de nodo

Todos viven en el mismo GameObject. `NodeController` es el único que los conoce entre sí.

| Script | Responsabilidad única |
|---|---|
| `NodeController.cs` | Orquestador. **No contiene reglas.** Expone la API pública del nodo y delega. |
| `NodeIdentity.cs` | Tipo actual y `NodeDefinition` asociada |
| `NodeOwnership.cs` | Facción actual. Emite `OnFactionChanged`. Única puerta para cambiar de bando. |
| `NodeEnergy.cs` | Valor, tope, `Add`, `Subtract`, `Clamp`. Emite `OnEnergyChanged`. |
| `NodeLevelComponent.cs` | Nivel actual, aplicación de `NodeLevelData`, validación de mejora |
| `NodeStateMachine.cs` | Estados de [14.1](./NOVA_Estados_Animaciones.md#141-estados-del-nodo), sus timers y sus bloqueos mutuos |
| `StarGenerator.cs` | Solo en Estrella. Temporizador de generación. Se desactiva si el estado lo bloquea. |
| `MagnetarTurret.cs` | Solo en Magnetar. Detección por radio, selección de objetivo, cadencia. |
| `PulsarCaster.cs` | Solo en Púlsar. Carga, pausa, cancelación, lanzamiento, robo de carga. |
| `NodeIgnition.cs` | Encendido de Asteroide, incluida la recogida del power-up |
| `NodeConverter.cs` | Reconversión y su ventana de vulnerabilidad de 3 s |
| `NodeCollider2D` | Trigger circular, solo para input y detección. Sin Rigidbody. |

### 15.6 Systems — escena

| Script | Responsabilidad única |
|---|---|
| `GameManager.cs` | Flujo del nivel: carga, inicio, pausa, fin. Único singleton de flujo. |
| `NodeRegistry.cs` | Registro vivo de todos los nodos indexado por facción. Consultado por IA, victoria y barra de poder. **Singleton.** |
| `ProtonRegistry.cs` | Registro de protones en vuelo indexado por destino. Lo usan `ThreatCalculator` y el Magnetar. **Singleton.** |
| `LevelLoader.cs` | Instancia el mapa desde `LevelDefinition` |
| `ProtonLauncher.cs` | Servicio de lanzamiento: valida, descuenta y pide un protón al pool |
| `ProtonPool.cs` | Object pooling de protones |
| `Proton.cs` | Movimiento, Carga, notificación de impacto. **No resuelve el impacto**, llama a `ImpactResolver`. |
| `PowerProjectile.cs` | Movimiento del proyectil de poder y aplicación del efecto |
| `PowerUpSpawner.cs` | Temporizadores, elección de Asteroide, expiración |
| `FactionBuffs.cs` | Buffs activos por facción y su consulta por los componentes |
| `WinConditionChecker.cs` | Victoria, derrota, estancamiento, cascada de conquista |
| `ProgressSaver.cs` | Nivel máximo desbloqueado en `PlayerPrefs` |

### 15.7 Input, IA y UI

| Script | Responsabilidad única |
|---|---|
| `InputRouter.cs` | Traduce ratón a intenciones. Buffer de doble clic. **No conoce reglas.** |
| `SelectionManager.cs` | Conjunto de nodos seleccionados, lazo, feedback de selección |
| `PlayerCommandIssuer.cs` | Implementa `INodeCommandIssuer` para el Jugador |
| `EnemyBrain.cs` | Ciclo de decisión de [12.1](./NOVA_IA_Algoritmos.md#121-ciclo-de-decisión) |
| `AIEvaluator.cs` | Función de puntuación de [12.3](./NOVA_IA_Algoritmos.md#123-función-de-puntuación-atacar). Pura, testeable. |
| `AIThreatResponder.cs` | Refuerzo, congelación y evacuación de [12.4](./NOVA_IA_Algoritmos.md#124-detección-de-amenaza-y-defensa) |
| `EnemyCommandIssuer.cs` | Implementa `INodeCommandIssuer` para el Enemigo |
| `NodeHUD.cs` | Número de Energía sobre el nodo |
| `NodeInfoPanel.cs` | Panel de clic derecho |
| `PulsarPowerWheel.cs` | Rueda de poderes |
| `IgnitionMenu.cs` | Menú radial de encendido |
| `PowerBarUI.cs` | Barra inferior. Lee de `NodeRegistry`, no acumula estado. |
| `EndLevelScreen.cs` | Victoria y derrota |

### 15.8 Presentation

| Script | Responsabilidad única |
|---|---|
| `NodeVisual.cs` | Sprite correcto según tipo, nivel y facción |
| `NodeAnimator.cs` | Animaciones de estado de [14.1](./NOVA_Estados_Animaciones.md#141-estados-del-nodo) |
| `ProtonVisual.cs` | Número de Carga y escala |
| `VFXPool.cs` | Pool de efectos |
| `AudioDirector.cs` | Reacción sonora a eventos |
| `CameraShake.cs` | Sacudida en capturas grandes |

### 15.9 Comunicación entre capas

```
InputRouter ──► PlayerCommandIssuer ──┐
                                      ├──► NodeController ──► Core.Rules
EnemyBrain  ──► EnemyCommandIssuer ───┘           │
                                                  ▼
                                          GameEventChannels
                                                  │
                        ┌─────────────────────────┼─────────────────────┐
                        ▼                         ▼                     ▼
                  Presentation                   UI            WinConditionChecker
```

**Regla de oro:** las flechas nunca apuntan hacia arriba. `Presentation` y `UI` jamás llaman a `NodeController`.

### 15.10 Orden de ejecución

Configurar en `Script Execution Order`:

```
-100  NodeRegistry, ProtonRegistry
 -50  InputRouter
 -40  EnemyBrain
   0  NodeController y componentes de nodo
  10  Proton, PowerProjectile
  20  WinConditionChecker
  50  UI
 100  Presentation
```

Los impactos se resuelven en el orden en que los protones llegan dentro del mismo frame. Con empate exacto, el de mayor Carga primero.

---

## 16. Tablas de balance consolidadas

Estos valores deben vivir en `BalanceConfig.asset` y en las `NodeDefinition`. No deben aparecer escritos a mano en ningún script.

### 16.1 Globales

| Parámetro | Valor |
|---|---|
| Velocidad del protón | 2.5 u/s |
| Velocidad del proyectil de poder | 6.0 u/s |
| Daño del Magnetar por disparo | 2 de Carga |
| Multiplicador de resistencia del Magnetar | 0.5 |
| Buffer de doble clic | 0.25 s |
| Duración de la reconversión | 3.0 s |
| Auto-deshielo | 30 s |
| Tasa de Decaimiento | 2 E/s |
| Duración de los power-ups | 20 s |
| Magnitud de los power-ups | +50% |
| Ventana de expiración del power-up | 30 s |
| Umbral de susto | 1.5 s |
| Área jugable | 32 × 18 u |
| Coste de encendido | 10 |
| Materia Inerte del Asteroide | 10 |
| Devolución al cancelar carga | 50% |

### 16.2 Costes de nivel

| Nivel | Estrella | Púlsar | Magnetar |
|---|---|---|---|
| 1 (encendido) | 10 | 10 | 10 |
| 2 | 20 | 25 | 20 |
| 3 | 30 | 40 | 30 |
| 4 | 40 | — | 40 |
| 5 | 50 | — | 50 |
| **Total a nivel máx.** | **150** | **75** | **150** |

### 16.3 Poderes

| Poder | Coste | Carga | Drenaje | Alcance |
|---|---|---|---|---|
| Cero Absoluto | 20 | 8 s | 2.50 E/s | 7 u |
| Decaimiento | 35 | 12 s | 2.92 E/s | 7 u |
| Agujero de Gusano | 60 | 16 s | 3.75 E/s | 5 u |

### 16.4 Reconversión

| Desde | Coste |
|---|---|
| Estrella | 20 |
| Púlsar | 20 |
| Magnetar | 30 |

---

## 17. Casos borde y reglas de resolución

Cada fila es un test de aceptación.

| # | Caso | Resolución |
|---|---|---|
| 1 | Dos protones de facciones distintas impactan el mismo nodo en el mismo frame | Se resuelven secuencialmente por orden de llegada; con empate exacto, primero el de mayor Carga. El segundo opera sobre el resultado del primero. |
| 2 | Un protón llega a un nodo que ya cambió a su propia facción | Se resuelve como absorción, no como ataque. La facción se comprueba **en el impacto**, no en el lanzamiento. |
| 3 | El nodo origen cambia de bando con protones en vuelo | Los protones conservan la facción del emisor en el momento del lanzamiento y completan su viaje. |
| 4 | El nodo destino deja de existir | Imposible: los nodos nunca se destruyen, solo cambian de facción. |
| 5 | Un protón excede el tope del destino aliado | El excedente se descarta. No rebota ni se redistribuye. |
| 6 | Un Magnetar reduce un protón exactamente a 0 | El protón se destruye. No impacta. La Energía se pierde. |
| 7 | Un protón de Carga 1 impacta un Magnetar con 0 de Energía | `floor(1 * 0.5) = 0`. **No lo captura.** Se requiere Carga ≥ 2 para capturar un Magnetar a 0. Es intencional y debe documentarse en la UI. |
| 8 | Se congela un nodo que está reconvirtiéndose | No permitido. La reconversión es inmune a Cero Absoluto durante sus 3 s. |
| 9 | Se congela un Púlsar a mitad de carga | La carga se pausa. Al descongelarse, se reanuda desde donde estaba. |
| 10 | Un Púlsar es capturado con un poder cargado | Ver 7.5: si la carga está al 100%, el nuevo dueño lo hereda. Si no, se resetea. |
| 11 | Un nodo infectado llega a 0 y sigue infectado | Correcto. Permanece en 0 y del mismo dueño hasta que alguien lo cure o lo capture. |
| 12 | Un nodo infectado es curado por su propio dueño | Pierde la infección y suma la Energía recibida. |
| 13 | Se lanza Decaimiento sobre un nodo ya infectado | Reinicia el efecto. No acumula la tasa. |
| 14 | Se lanza Agujero de Gusano sobre un nodo congelado | Lo captura y elimina el congelamiento. |
| 15 | Un power-up cae y nadie enciende el Asteroide | Expira a los 30 s. Arranca el siguiente temporizador. |
| 16 | Un power-up debe caer pero no hay Asteroides neutrales | El drop se salta. El temporizador se reinicia. No cuenta contra el máximo por nivel. |
| 17 | Dos Nubes de Hidrógeno consecutivas en el mismo bando | La segunda reinicia la duración a 20 s. No acumula magnitud. |
| 18 | El jugador se queda sin Estrellas pero con 80 de Energía en un Magnetar | Puede reconvertirlo por 30. No hay derrota por estancamiento. |
| 19 | El jugador se queda sin Estrellas y con 6 de Energía total | Derrota por estancamiento, siempre que no tenga protones en vuelo ni poderes cargados. |
| 20 | Un Magnetar neutral dispara al último protón antes de la victoria | Se resuelve normalmente. La victoria se comprueba después. |
| 21 | El Enemigo pierde su último nodo con protones en vuelo | Los protones se desvanecen. Comienza la cascada de conquista. |
| 22 | Selección múltiple con nodos a 1 de Energía | Los que no llegan al mínimo de envío se ignoran silenciosamente. Los demás envían. |
| 23 | Clic derecho sobre un nodo enemigo | Muestra tipo, nivel, Energía y velocidad de ataque. **No** muestra botones de mejora ni reconversión. |
| 24 | Un nodo alcanza el nivel máximo | El botón de mejora se sustituye por `NIVEL MÁXIMO`. |
| 25 | Envío al 100% desde un nodo que está siendo atacado | Legal. Es la maniobra de evacuación, disponible también para el jugador. |
| 26 | Un Asteroide propio recibe un power-up marcado | Imposible: los power-ups solo caen sobre Asteroides **neutrales**. |

---

## 18. Decisiones tomadas por defecto

Reglas que no estaban en el diseño original y que se añadieron para cerrar huecos. Todas son revisables sin afectar a la arquitectura.

| # | Regla añadida | Motivo |
|---|---|---|
| 1 | Auto-deshielo a los 30 s | Evita nodos congelados permanentemente que bloqueen la victoria |
| 2 | Cascada de conquista al ganar | Cumple "ningún nodo queda Neutral" sin obligar a limpiar el mapa manualmente |
| 3 | Buffer de 0.25 s en el doble clic | Sin él, el doble clic enviaría 75% en lugar de 100% |
| 4 | Los power-ups afectan a toda la facción | Aplicado solo al nodo encendido, el power-up sería inútil la mayoría de las veces |
| 5 | Daño del Magnetar = 2 por disparo | Ajusta la curva para que el nivel 1 sea testimonial y el nivel 5 decisivo |
| 6 | Un Magnetar aliado recibe Energía 1:1 | La resistencia ×2 penalizaría reforzar tu propia defensa |
| 7 | Derrota por estancamiento | Evita partidas matemáticamente perdidas que no terminan |
| 8 | Devolución del 50% al cancelar una carga | Permite rectificar sin castigo total |
| 9 | Un Magnetar a 0 requiere Carga ≥ 2 | Consecuencia matemática del multiplicador 0.5 con redondeo hacia abajo |
| 10 | Ruido de decisión en la IA | Hace torpe a la IA del mapa 1 sin escribir un algoritmo distinto |
| 11 | Evacuación de la IA | Sin ella la IA regala nodos llenos y se siente tonta |
| 12 | Un nodo no puede volver a Asteroide | No aporta nada y complica el menú de reconversión |

---

## 19. Checklist de implementación por fases

### Fase 1 — Núcleo jugable (sin arte)

- [ ] Enums de `Core`
- [ ] `EnergyMath`, `ImpactResolver`, `ConversionRules` con tests unitarios
- [ ] `NodeDefinition`, `NodeLevelData`, `BalanceConfig`
- [ ] `NodeController` y sus componentes, con sprites provisionales
- [ ] `StarGenerator`
- [ ] `ProtonLauncher`, `Proton`, `ProtonPool`
- [ ] `NodeRegistry`, `ProtonRegistry`
- [ ] `InputRouter` con clic simple y buffer de doble clic
- [ ] Captura y cambio de facción funcionando
- **Criterio de salida:** se puede capturar un Asteroide, encenderlo como Estrella y tomar un nodo enemigo.

### Fase 2 — Tipos y defensa

- [ ] `NodeIgnition` y `IgnitionMenu`
- [ ] `NodeLevelComponent` y mejoras
- [ ] `MagnetarTurret` con radio, cadencia y desgaste del protón
- [ ] Regla de resistencia ×2
- [ ] Magnetar neutral disparando a ambos bandos
- [ ] `NodeConverter` y reconversión
- **Criterio de salida:** los cuatro tipos son funcionales y el nivel 3 es jugable.

### Fase 3 — Poderes

- [ ] `PulsarCaster` con carga acoplada a la Energía
- [ ] Cero Absoluto y la regla de deshielo invertida
- [ ] Decaimiento
- [ ] Agujero de Gusano y el robo de carga
- [ ] `PulsarPowerWheel`
- **Criterio de salida:** los tres poderes funcionan y pasan los casos 8 a 14 de la sección 17.

### Fase 4 — IA

- [ ] `AIEvaluator` con tests
- [ ] `EnemyBrain` y el ciclo de decisión
- [ ] `AIThreatResponder` con refuerzo, congelación y evacuación
- [ ] Los tres `AIProfile` (ver [12.5](./NOVA_IA_Algoritmos.md#125-perfiles-por-mapa))
- **Criterio de salida:** la IA del mapa 3 vence a un jugador descuidado.

### Fase 5 — Flujo y contenido

- [ ] `LevelDefinition` de los 9 niveles
- [ ] `LevelLoader`
- [ ] `WinConditionChecker` con cascada y estancamiento
- [ ] `PowerUpSpawner` y `FactionBuffs`
- [ ] `ProgressSaver`, selección de nivel, pantallas de fin
- **Criterio de salida:** los 9 niveles son completables de principio a fin.

### Fase 6 — Presentación

- [ ] Sprites definitivos por tipo, nivel y facción (inventario en [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md))
- [ ] Todas las animaciones de estado de [14.1](./NOVA_Estados_Animaciones.md#141-estados-del-nodo)
- [ ] Número de Carga sobre el protón
- [ ] `PowerBarUI`
- [ ] VFX, audio, pulido
- **Criterio de salida:** ver el **documento 2** (paleta, pixel art y pipeline en Python).

---

## Apéndice — Pendientes para el documento 2

> El inventario de qué arte falta, con IDs y nombres de archivo, vive ahora en [NOVA_Assets_Diseno.md](./NOVA_Assets_Diseno.md). El documento 2 solo debe aportar el *cómo* (pipeline y estilo), no el *qué*.

| Pendiente | Estado |
|---|---|
| Paleta completa y rampas de color | ✅ `tools/nova_paleta.py`, reglas en el contrato |
| Tamaño de sprite por tipo y nivel | ✅ Huella 0.6–1.2 u, celda 96 px = 1.5 u, PPU 64 ([A.8](./NOVA_Assets_Diseno.md#a8-decisiones-de-diseño-cerradas) #4) |
| Número de frames por animación | ✅ 12 fps fijo, `frames = ceil(duración × 12)` |
| Pipeline de generación en Python | ✅ [NOVA_Arte_Tecnica.md](./NOVA_Arte_Tecnica.md) + `tools/` |
| Convención de nombres de assets | ✅ [A.1](./NOVA_Assets_Diseno.md#a1-convención-de-nombres) |
| Tipografía | ✅ Una pixel font libre en TextMeshPro |
| Atlas y pivotes | ⬜ Pivote decidido (Bottom / Center); el empaquetado en atlas, no |
| Estilo de la UI | ⬜ Solo está la paleta; falta el lenguaje de paneles y botones |
| Diseño de los 9 niveles con coordenadas exactas | ⬜ Sin empezar |
