import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque

class MapaCarreterasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa de Carreteras")

        # Grafo con 10 ciudades
        self.graph = {
            'A': {'B': 5, 'C': 10},
            'B': {'A': 5, 'C': 3, 'D': 20, 'E': 7},
            'C': {'A': 10, 'B': 3, 'D': 2, 'F': 8},
            'D': {'B': 20, 'C': 2, 'G': 12},
            'E': {'B': 7, 'F': 9, 'H': 6},
            'F': {'C': 8, 'E': 9, 'I': 15},
            'G': {'D': 12, 'J': 4},
            'H': {'E': 6, 'I': 3},
            'I': {'F': 15, 'H': 3, 'J': 14},
            'J': {'G': 4, 'I': 14}
        }
        
        # Cola de automóviles con máximo 5 autos
        self.autos = deque()
        self.viajes_realizados = []
        self.viajes_pendientes = []
        
        # Panel izquierdo para los controles
        self.control_frame = ttk.Frame(root)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Interfaz para escoger el número de autos
        self.autos_label = ttk.Label(self.control_frame, text="Número de autos (máx 5):")
        self.autos_label.grid(row=0, column=0, padx=10, pady=5)

        self.num_autos = tk.IntVar(value=1)
        self.autos_entry = ttk.Spinbox(self.control_frame, from_=1, to=5, textvariable=self.num_autos)
        self.autos_entry.grid(row=0, column=1, padx=10, pady=5)

        # Selección de ciudad de origen
        self.origen_label = ttk.Label(self.control_frame, text="Ciudad de origen:")
        self.origen_label.grid(row=1, column=0, padx=10, pady=5)

        self.origen_combo = ttk.Combobox(self.control_frame, values=list(self.graph.keys()))
        self.origen_combo.grid(row=1, column=1, padx=10, pady=5)

        # Selección de ciudad de destino
        self.destino_label = ttk.Label(self.control_frame, text="Ciudad de destino:")
        self.destino_label.grid(row=2, column=0, padx=10, pady=5)

        self.destino_combo = ttk.Combobox(self.control_frame, values=list(self.graph.keys()))
        self.destino_combo.grid(row=2, column=1, padx=10, pady=5)
        
        # Botón para agregar viajes individualmente
        self.agregar_viaje_button = ttk.Button(self.control_frame, text="Agregar Viaje", command=self.agregar_viaje)
        self.agregar_viaje_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Botón para comenzar la simulación
        self.start_button = ttk.Button(self.control_frame, text="Iniciar Simulación", command=self.iniciar_simulacion)
        self.start_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        
        # Panel derecho para el mapa
        self.map_frame = ttk.Frame(root)
        self.map_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.dibujar_mapa()

        # Area de texto para mostrar los resultados en la parte inferior
        self.resultados_frame = ttk.Frame(root)
        self.resultados_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.resultados = tk.Text(self.resultados_frame, height=10, width=70)
        self.resultados.grid(row=0, column=0, padx=10, pady=10)

    def dibujar_mapa(self):
        # Crear un grafo con networkx y dibujarlo con matplotlib
        G = nx.Graph()
        for city, neighbors in self.graph.items():
            for neighbor, distance in neighbors.items():
                G.add_edge(city, neighbor, weight=distance)
        
        pos = nx.spring_layout(G)
        plt.figure(figsize=(5, 5))
        nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue')
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        plt.savefig("grafo.png")
        
        # Mostrar la imagen en Tkinter
        img = tk.PhotoImage(file="grafo.png")
        panel = tk.Label(self.map_frame, image=img)
        panel.image = img
        panel.grid(row=0, column=0)

    def agregar_viaje(self):
        # Validar si el usuario ha seleccionado origen y destino
        origen = self.origen_combo.get()
        destino = self.destino_combo.get()

        if not origen or not destino:
            self.resultados.insert(tk.END, "Por favor seleccione una ciudad de origen y destino.\n")
            return

        # Agregar el viaje a la lista de pendientes
        auto_id = len(self.viajes_pendientes) + 1
        if auto_id > self.num_autos.get():
            self.resultados.insert(tk.END, "Ya se han asignado todos los autos.\n")
            return

        self.viajes_pendientes.append({
            'auto': f'Auto {auto_id}',
            'origen': origen,
            'destino': destino
        })

        # Mostrar el viaje agregado
        self.resultados.insert(tk.END, f"{f'Auto {auto_id}'} tiene asignado el viaje de {origen} a {destino}.\n")
    
    def dijkstra(self, start, end):
        import heapq
        queue = [(0, start)]
        distances = {vertex: float('infinity') for vertex in self.graph}
        distances[start] = 0
        previous = {vertex: None for vertex in self.graph}
        
        while queue:
            current_distance, current_vertex = heapq.heappop(queue)
            
            if current_distance > distances[current_vertex]:
                continue
            
            for neighbor, weight in self.graph[current_vertex].items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(queue, (distance, neighbor))
        
        path = []
        while end:
            path.append(end)
            end = previous[end]
        
        return path[::-1], distances[path[0]]
    
    def iniciar_simulacion(self):
        self.viajes_realizados.clear()
        
        # Verificar que todos los autos tengan un viaje asignado
        if len(self.viajes_pendientes) < self.num_autos.get():
            self.resultados.insert(tk.END, "No se han asignado viajes a todos los autos.\n")
            return

        # Ejecutar viajes según lo asignado por el usuario
        for viaje in self.viajes_pendientes:
            self.simular_viaje(viaje['auto'], viaje['origen'], viaje['destino'])
        
        # Ordenar viajes por distancia
        self.viajes_realizados.sort(key=lambda x: x['distancia'])
        
        # Mostrar resultados
        self.resultados.insert(tk.END, "\nResultados de los viajes:\n")
        for viaje in self.viajes_realizados:
            self.resultados.insert(tk.END, f"{viaje['auto']} viajó de {viaje['origen']} a {viaje['destino']}. "
                                           f"Distancia: {viaje['distancia']} km\n")
    
    def simular_viaje(self, auto, origen, destino):
        camino, distancia = self.dijkstra(origen, destino)
        self.viajes_realizados.append({
            'auto': auto,
            'origen': origen,
            'destino': destino,
            'distancia': distancia
        })

# Inicializar la aplicación
root = tk.Tk()
app = MapaCarreterasApp(root)
root.mainloop()
