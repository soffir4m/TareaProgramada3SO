from collections import defaultdict
import random


class ResourceAllocationGraph:
    """
    Grafo de asignación de recursos:
      - Nodos: procesos (p1, p2...) y recursos (r1, r2...)
      - Aristas:
          P -> R : proceso espera por recurso
          R -> P : recurso asignado a proceso
    """

    def __init__(self):
        self.adj = defaultdict(set)       # lista de adyacencia
        self.held_by = {}                 # recurso -> proceso que lo tiene (o None)
        self.processes = set()
        self.resources = set()

    # -------- utilidades internas --------
    def _ensure_node(self, node: str):
        _ = self.adj[node]  # fuerza a crear la entrada

    def add_resource(self, resource: str):
        self.resources.add(resource)
        self._ensure_node(resource)
        if resource not in self.held_by:
            self.held_by[resource] = None

    def add_process(self, process: str):
        self.processes.add(process)
        self._ensure_node(process)

    def _add_edge(self, u: str, v: str):
        self._ensure_node(u)
        self._ensure_node(v)
        self.adj[u].add(v)

    def _remove_edge(self, u: str, v: str):
        if v in self.adj.get(u, set()):
            self.adj[u].remove(v)

    # -------- lógica de asignación / solicitud --------
    def request_resource(self, process: str, resource: str):
        """
        Maneja un 'process,resource' en el archivo:
        - Si el recurso está libre -> se asigna R -> P
        - Si está ocupado -> el proceso queda en espera P -> R
        """
        self.add_process(process)
        self.add_resource(resource)

        holder = self.held_by.get(resource)
        if holder is None:
            # asignar directamente
            self._add_edge(resource, process)
            self.held_by[resource] = process
            print(f"  [GRAFO] {resource} -> {process} (asignado)")
        else:
            # el recurso está ocupado: proceso queda esperando
            self._add_edge(process, resource)
            print(f"  [GRAFO] {process} -> {resource} (esperando; lo tiene {holder})")

    def _grant_resource_if_possible(self, resource: str):
        """
        Si el recurso está libre y hay procesos esperando por él (P -> R),
        se le asigna a uno de ellos (política simple: el primero que aparezca).
        """
        if self.held_by.get(resource) is not None:
            return

        # buscar procesos que tengan arista P -> R
        for node, neighbors in self.adj.items():
            if node in self.processes and resource in neighbors:
                # este proceso estaba esperando; se le asigna
                print(f"  [GRAFO] {resource} se reasigna a {node} (liberado y otorgado)")
                self._remove_edge(node, resource)  # quitar P -> R
                self._add_edge(resource, node)     # poner R -> P
                self.held_by[resource] = node
                break

    def terminate_process(self, process: str):
        """
        Termina un proceso:
          - Libera todos los recursos que tiene (R -> P)
          - Quita todas sus solicitudes (P -> R)
          - Quita referencias al proceso en el grafo
        """
        if process not in self.processes:
            return

        print(f"  [GRAFO] Terminando {process}: liberando recursos y eliminando aristas")

        # liberar recursos asignados a este proceso
        for r, holder in list(self.held_by.items()):
            if holder == process:
                self._remove_edge(r, process)
                self.held_by[r] = None
                self._grant_resource_if_possible(r)

        # eliminar todas las aristas P -> R del proceso
        if process in self.adj:
            self.adj.pop(process, None)

        # eliminar aristas entrantes al proceso (R -> P o P' -> P si existiera)
        for node in list(self.adj.keys()):
            if process in self.adj[node]:
                self.adj[node].remove(process)

        self.processes.discard(process)

    # -------- detección de ciclos (deadlock) --------
def has_cycle(self) -> bool:
    visited = set()
    stack = set()

    def dfs(u: str) -> bool:
        visited.add(u)
        stack.add(u)
        for v in sorted(self.adj[u]):   # ordenar vecinos
            if v not in visited:
                if dfs(v):
                    return True
            elif v in stack:
                return True
        stack.remove(u)
        return False

    for node in sorted(self.adj.keys()):  # ordenar nodos
        if node not in visited:
            if dfs(node):
                return True
    return False


class DeadlockSimulator:
    """
    Simulador de asignación de recursos sin control.
    Lee eventos ordenados por tiempo y actualiza:
      - Grafo de asignación
      - Tiempos de espera (bloqueo)
      - Throughput (procesos completados)
    """

    def __init__(self):
        self.rag = ResourceAllocationGraph()

        # Métricas por proceso
        self.arrival_time = {}          # proceso -> tiempo de llegada
        self.finish_time = {}           # proceso -> tiempo de finalización
        self.total_blocked = defaultdict(int)   # proceso -> tiempo total bloqueado
        self.blocked_since = {}         # proceso -> tiempo desde que quedó bloqueado

        self.deadlock_detected = False
        self.deadlock_time = None

    # -------- gestión de bloqueo --------
    def _is_blocked(self, process: str) -> bool:
        """
        Consideramos que un proceso está bloqueado si tiene alguna arista P -> R
        (es decir, está esperando al menos un recurso).
        """
        neighbors = self.rag.adj.get(process, set())
        for v in neighbors:
            if v in self.rag.resources:   # P -> R
                return True
        return False

    def _update_block_states(self, current_time: int):
        for p in self.rag.processes | set(self.arrival_time.keys()):
            blocked = self._is_blocked(p)

        # Si acaba de entrar en bloqueo
            if blocked and p not in self.blocked_since:
                self.blocked_since[p] = current_time

        # Si estaba bloqueado y ahora ya NO lo está
            elif (not blocked) and (p in self.blocked_since):
                self.total_blocked[p] += current_time - self.blocked_since[p]
                del self.blocked_since[p]

    # -------- simulación principal --------
    def simulate_events(self, events):
        """
        events: lista de diccionarios:
          - {"time": t, "type": "request", "process": "p1", "resource": "r1"}
          - {"time": t, "type": "finish",  "process": "p1"}
        Deben venir ordenados por 'time'.
        """
        if not events:
            print("No hay eventos para simular.")
            return

        events = sorted(events, key=lambda e: e["time"])
        first_time = events[0]["time"]
        last_time = events[-1]["time"]

        print("\n=== INICIO DE LA SIMULACIÓN ===\n")
        for ev in events:
            t = ev["time"]
            etype = ev["type"]

            if etype == "request":
                p = ev["process"]
                r = ev["resource"]
                print(f"[t={t}] {p} solicita {r}")

                if p not in self.arrival_time:
                    self.arrival_time[p] = t

                # solicitud al grafo
                self.rag.request_resource(p, r)

                # actualizar bloqueo después del cambio
                self._update_block_states(t)

                # detección de deadlock
                if self.rag.has_cycle():
                    print("DEADLOCK DETECTADO")
                    self.deadlock_detected = True
                    self.deadlock_time = t
                    break

            elif etype == "finish":
                p = ev["process"]
                print(f"[t={t}] {p} finaliza")

                # cerrar intervalos de bloqueo del proceso (si estaba bloqueado)
                if p in self.blocked_since:
                    self.total_blocked[p] += t - self.blocked_since[p]
                    del self.blocked_since[p]

                self.rag.terminate_process(p)
                self.finish_time[p] = t

                # actualizar bloqueo global (otros procesos pudieron cambiar)
                self._update_block_states(t)

        # cerrar bloqueos de procesos que quedaron bloqueados al final
        final_time = self.deadlock_time if self.deadlock_detected else last_time
        for p in list(self.blocked_since.keys()):
            self.total_blocked[p] += final_time - self.blocked_since[p]
        self.blocked_since.clear()

        print("\n=== FIN DE LA SIMULACIÓN ===")
        self._print_metrics(first_time, final_time)

    # -------- métricas --------
    def _print_metrics(self, first_time: int, final_time: int):
        completed = len(self.finish_time)
        sim_duration = max(1, final_time - first_time)

    # Número total de procesos que existieron
        total_procesos = len(self.arrival_time)

    # CALCULAR PROMEDIO DE ESPERA CORRECTO
        if total_procesos > 0:
         avg_wait = sum(self.total_blocked.values()) / total_procesos
        else:
            avg_wait = 0.0

        throughput = completed / sim_duration

        print(f"\n--- MÉTRICAS ---")
        print(f"Procesos completados       : {completed}")
        print(f"Duración de la simulación : {sim_duration} unidades de tiempo")
        print(f"Throughput                : {throughput:.3f} procesos/unidad tiempo")
        print(f"Tiempo promedio de espera : {avg_wait:.2f} unidades de tiempo")

        print("\nDetalle por proceso:")
        for p in sorted(set(self.arrival_time.keys()) | set(self.finish_time.keys())):
            arr = self.arrival_time.get(p, None)
            fin = self.finish_time.get(p, None)
            wait = self.total_blocked.get(p, 0)
            print(f"  {p}: llegada={arr}, fin={fin}, espera_total={wait}")
    #el docuemento no especific en si pero la formula 
    # usada fue el promedio = sum(esperas) / (todos los procesos)


# LECTURA DEL ARCHIVO DE CONFIGURACIÓN (formato tarea)
def load_events_from_config(path: str):
    """
    Lee el archivo de configuración con formato:
      r1,r2,r3
      0,p1,r1
      1,p2,r2
      2,p3,r3
      3,p1,r2
      4,p2,r3
      5,p3,r1
      10,p1
    Devuelve: (resources, events)
    """
    resources = []
    events = []

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # primera línea: recursos
    resources = [x.strip() for x in lines[0].split(",")]

    # resto: eventos
    for line in lines[1:]:
        parts = [x.strip() for x in line.split(",")]

        if len(parts) == 3:
            # tiempo, proceso, recurso
            t_str, p, r = parts
            t = int(t_str)
            events.append({
                "time": t,
                "type": "request",
                "process": p,
                "resource": r,
            })
        elif len(parts) == 2:
            # tiempo, proceso (termina)
            t_str, p = parts
            t = int(t_str)
            events.append({
                "time": t,
                "type": "finish",
                "process": p,
            })
        else:
            raise ValueError(f"Línea inválida en config: {line}")

    return resources, events


# ESCENARIO ALEATORIO P1..P5 COMPITIENDO POR R1,R2
def build_random_scenario():
    """
    Genera un escenario donde P1..P5 compiten por R1 y R2
    de forma aleatoria, como pide el enunciado.
    """
    processes = [f"p{i}" for i in range(1, 6)]
    resources = ["r1", "r2"]
    events = []

    t = 0

    # todos los procesos hacen al menos una solicitud
    for p in processes:
        r = random.choice(resources)
        events.append({"time": t, "type": "request", "process": p, "resource": r})
        t += 1

    # solicitudes extra aleatorias
    for _ in range(10):
        p = random.choice(processes)
        r = random.choice(resources)
        events.append({"time": t, "type": "request", "process": p, "resource": r})
        t += 1

    # algunas terminaciones
    random.shuffle(processes)
    for p in processes:
        events.append({"time": t, "type": "finish", "process": p})
        t += 1

    return resources, events


#MAIN / MENÚ
def main():
    while True:
        print("===== SIMULADOR DE DEADLOCK (SIN CONTROL) =====")
        print("1) Cargar archivo de configuración y simular")
        print("2) Escenario aleatorio P1..P5 con R1,R2")
        print("3) Salir")

        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            path = input("Ruta del archivo de configuración (ej: config.txt): ").strip()
            try:
                resources, events = load_events_from_config(path)
            except Exception as e:
                print(f"Error leyendo archivo: {e}")
                input("\nPresione Enter para volver al menú...")
                continue

            sim = DeadlockSimulator()
            # registrar recursos en el grafo
            for r in resources:
                sim.rag.add_resource(r)

            sim.simulate_events(events)
            input("\nPresione Enter para volver al menú...")

        elif opcion == "2":
            resources, events = build_random_scenario()
            print("\nRecursos del escenario aleatorio:", ", ".join(resources))
            sim = DeadlockSimulator()
            for r in resources:
                sim.rag.add_resource(r)
            sim.simulate_events(events)
            input("\nPresione Enter para volver al menú...")

        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")
            input("\nPresione Enter para volver al menú...")


if __name__ == "__main__":
    main()