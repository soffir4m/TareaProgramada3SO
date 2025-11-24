# README – Simulador de Deadlocks (SIN CONTROL)

## Descripción General
Este proyecto implementa un simulador de asignación de recursos sin mecanismos de control, siguiendo las especificaciones de la Tarea Programada 3 – Sistemas Operativos (Universidad LEAD, 2025).

El objetivo es modelar procesos y recursos mediante un grafo de asignación, simular solicitudes y liberaciones paso a paso y detectar deadlocks mediante la identificación de ciclos en el grafo.

---

## Características Principales

### Modelo de Grafo de Asignación
- Procesos: p1, p2, …
- Recursos: r1, r2, …
- Aristas P → R: proceso esperando recurso
- Aristas R → P: recurso asignado a proceso

### Simulación paso a paso
El archivo de configuración define eventos de llegada, solicitudes de recursos y finalización.

### Detección de Deadlock
Cada vez que se crea una arista, se ejecuta un DFS para verificar si apareció un ciclo en el grafo.

### Métricas incluidas
- Tiempo total de bloqueo por proceso
- Tiempo promedio de espera
- Throughput (procesos completados por unidad de tiempo)
- Tiempo de llegada y finalización de cada proceso

### Escenario Aleatorio
Incluye un generador con p1..p5 compitiendo por r1 y r2, como exige el enunciado.

---

## Formato del Archivo de Configuración

La primera línea define los recursos:
```
r1,r2,r3
```

Las siguientes líneas pueden ser:

### Solicitud de recurso
```
tiempo,proceso,recurso
```
Ejemplo:
```
0,p1,r1
3,p1,r2
```

### Finalización de proceso
```
tiempo,proceso
```
Ejemplo:
```
10,p1
```

---

## Modo de Uso

Asegúrese de tener el archivo:

```
simuladordeadlock.py
```

Luego ejecute:

```
python simuladordeadlock.py
```

Se mostrará el siguiente menú:

```
1) Cargar archivo de configuración y simular
2) Escenario aleatorio P1..P5 con R1,R2
3) Salir
```

---

## Salida del Programa

Durante la simulación se muestra:

- Solicitudes de recursos
- Liberación de recursos
- Asignaciones y reasignaciones
- Evolución del grafo
- Deadlocks detectados

Al finalizar, imprime algo como:

```
--- MÉTRICAS ---
Procesos completados       : 3
Duración de la simulación : 12 unidades de tiempo
Throughput                : 0.25 procesos/unidad tiempo
Tiempo promedio de espera : 3.33 unidades de tiempo
```

Y el detalle por proceso.

---

## Estructura del Código

### ResourceAllocationGraph
- Maneja los nodos y aristas
- Modela solicitudes y asignaciones
- Libera recursos
- Identifica ciclos en el grafo

### DeadlockSimulator
- Procesa eventos del archivo
- Calcula tiempos de espera y métricas
- Controla bloqueo y desbloqueo
- Detecta deadlock

### load_events_from_config
Interpreta archivos de configuración siguiendo el formato especificado.

### build_random_scenario
Genera el escenario aleatorio requerido por la tarea.

---

## Ejemplo de Deadlock

Archivo de ejemplo:

```
r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
```

Se forma el ciclo:

```
p1 → r2 → p2 → r3 → p3 → r1 → p1
```

El simulador mostrará:

```
DEADLOCK DETECTADO
```

---

## Requisitos de la Tarea – Completados

| Requisito                               | Estado |
|----------------------------------------|--------|
| Grafo de asignación                    | Completado |
| Simulación de solicitudes y liberación | Completado |
| Detección de ciclos (deadlock)         | Completado |
| Tiempo de espera promedio              | Completado |
| Throughput                             | Completado |
| Archivo de configuración personalizado | Completado |
| Escenario aleatorio P1..P5             | Completado |

---

Melany Ramirez
Universidad LEAD – Sistemas Operativos  
2025
