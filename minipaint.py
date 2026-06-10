import tkinter as tk # Biblioteca usada para criar interface    
import collections # Flood Fill

# Cores em tupla RGB
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'CYAN': (0, 255, 255),
    'MAGENTA': (255, 0, 255)
}

# Converte cor para hexadecimal
def rgb_to_hex(rgb):
    """Converte tupla RGB para formato Hexadecimal aceito pelo Tkinter (#RRGGBB)"""
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

# Constantes Globais, usadas para definir a área de desenho
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Ferramentes dispoíveis
TOOLS = ['Lapis', 'Borracha', 'Linha', 'Ret. Vazado', 'Ret. Preenchido', 'Circ. Vazado', 'Circ. Preenchido', 'Balde']
THICKNESS = {'Fino': 1, 'Medio': 3, 'Grosso': 5}

# Armazena os pixels do desenho (Framebuffer)
class Canvas:
    """Gerencia o framebuffer (matriz 2D) e os pixels da tela de desenho."""
    def __init__(self, tk_photo_image, width, height, bg_color=COLORS['WHITE']):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.image = tk_photo_image
        
        # Estrutura em matriz bidimensional
        self.pixels = [[bg_color for _ in range(width)] for _ in range(height)]
        self.clear()

    # Altera cor da matriz e atualiza o pixel
    def put_pixel(self, x, y, color):
        """REQUISITO: put_pixel - Altera a cor na matriz e no PhotoImage do Tkinter."""
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
            # Tkinter PhotoImage exige cor em Hexadecimal
            self.image.put(rgb_to_hex(color), (x, y))

    # Retorna a cor de um pixel
    def get_pixel(self, x, y):
        """REQUISITO: get_pixel - Retorna a cor atual do pixel na matriz."""
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None

    # Simula um pincel mais grosso
    def put_brush(self, x, y, color, thickness):
        """Aplica espessura simulando um pincel quadrado ao redor do pixel."""
        if thickness == 1:
            self.put_pixel(x, y, color)
            return
        
        offset = thickness // 2
        for i in range(-offset, offset + 1):
            for j in range(-offset, offset + 1):
                self.put_pixel(x + i, y + j, color)

    # Limpa a área de desenho
    def clear(self):
        """Limpa o canvas com a cor de fundo."""
        bg_hex = rgb_to_hex(self.bg_color)
        # Preenche a matriz
        self.pixels = [[self.bg_color for _ in range(self.width)] for _ in range(self.height)]
        # Preenche o Tkinter PhotoImage (criando uma linha horizontal do tamanho da tela e replicando)
        row_data = "{" + " ".join([bg_hex] * self.width) + "}"
        self.image.put(" ".join([row_data] * self.height), (0, 0))

# Classe estática, contém os algoritmos (Bresenham)
class Algorithms:
    """Classe estática com os algoritmos matemáticos de rasterização."""
    
    @staticmethod
    def draw_line(canvas, x1, y1, x2, y2, color, thickness=1):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            canvas.put_brush(x1, y1, color, thickness)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    @staticmethod
    def draw_circle(canvas, cx, cy, radius, color, thickness=1):
        cx, cy, radius = int(cx), int(cy), int(radius)
        x = 0
        y = radius
        d = 3 - 2 * radius
        
        Algorithms._draw_circle_points(canvas, cx, cy, x, y, color, thickness)
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            Algorithms._draw_circle_points(canvas, cx, cy, x, y, color, thickness)

    @staticmethod
    def _draw_circle_points(canvas, cx, cy, x, y, color, thickness):
        pts = [
            (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)
        ]
        for px, py in pts:
            canvas.put_brush(px, py, color, thickness)

    @staticmethod
    def draw_filled_circle(canvas, cx, cy, radius, color):
        cx, cy, radius = int(cx), int(cy), int(radius)
        x = 0
        y = radius
        d = 3 - 2 * radius
        
        while y >= x:
            Algorithms.draw_line(canvas, cx - x, cy + y, cx + x, cy + y, color, 1)
            Algorithms.draw_line(canvas, cx - x, cy - y, cx + x, cy - y, color, 1)
            Algorithms.draw_line(canvas, cx - y, cy + x, cx + y, cy + x, color, 1)
            Algorithms.draw_line(canvas, cx - y, cy - x, cx + y, cy - x, color, 1)
            
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

    @staticmethod
    def draw_empty_rect(canvas, x1, y1, x2, y2, color, thickness=1):
        Algorithms.draw_line(canvas, x1, y1, x2, y1, color, thickness)
        Algorithms.draw_line(canvas, x2, y1, x2, y2, color, thickness)
        Algorithms.draw_line(canvas, x2, y2, x1, y2, color, thickness)
        Algorithms.draw_line(canvas, x1, y2, x1, y1, color, thickness)

    @staticmethod
    def draw_filled_rect(canvas, x1, y1, x2, y2, color):
        min_x, max_x = int(min(x1, x2)), int(max(x1, x2))
        min_y, max_y = int(min(y1, y2)), int(max(y1, y2))
        
        for y in range(min_y, max_y + 1):
            Algorithms.draw_line(canvas, min_x, y, max_x, y, color, 1)

    # Preenche regiao
    @staticmethod
    def flood_fill(canvas, start_x, start_y, target_color, replacement_color):
        if target_color == replacement_color:
            return
        
        if not (0 <= start_x < canvas.width and 0 <= start_y < canvas.height):
            return

        queue = collections.deque([(start_x, start_y)])
        canvas.put_pixel(start_x, start_y, replacement_color)
        
        while queue:
            cx, cy = queue.popleft()
            neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
            for nx, ny in neighbors:
                if canvas.get_pixel(nx, ny) == target_color:
                    canvas.put_pixel(nx, ny, replacement_color)
                    queue.append((nx, ny))

# Interface do programa
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Paint - Computação Gráfica (Tkinter)")
        self.root.resizable(False, False)

        # Variáveis de Estado
        self.current_color = tk.Variable(value=COLORS['BLACK'])
        self.current_tool = tk.StringVar(value='Lapis')
        self.current_thick = tk.IntVar(value=THICKNESS['Fino'])
        
        self.drawing = False
        self.start_pos = None
        self.last_pos = None

        self._setup_ui()
        self._setup_canvas()

    def _setup_ui(self):
        # Frame Superior para Controles
        toolbar = tk.Frame(self.root, padx=5, pady=5, bg='#e0e0e0')
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # 1. Cores
        color_frame = tk.LabelFrame(toolbar, text="Cores", bg='#e0e0e0')
        color_frame.pack(side=tk.LEFT, padx=5)
        for name, rgb in COLORS.items():
            btn = tk.Button(color_frame, bg=rgb_to_hex(rgb), width=2, 
                            command=lambda c=rgb: self.current_color.set(c))
            btn.pack(side=tk.LEFT, padx=1, pady=2)

        # 2. Ferramentas
        tool_frame = tk.LabelFrame(toolbar, text="Ferramentas", bg='#e0e0e0')
        tool_frame.pack(side=tk.LEFT, padx=5)
        
        # Grid para as ferramentas para ficar mais organizado
        for i, tool in enumerate(TOOLS):
            btn = tk.Radiobutton(tool_frame, text=tool, variable=self.current_tool, 
                                 value=tool, indicatoron=0, width=12, bg='#f0f0f0')
            btn.grid(row=i//4, column=i%4, padx=1, pady=1)

        # 3. Espessuras
        thick_frame = tk.LabelFrame(toolbar, text="Espessura", bg='#e0e0e0')
        thick_frame.pack(side=tk.LEFT, padx=5)
        for name, val in THICKNESS.items():
            btn = tk.Radiobutton(thick_frame, text=name, variable=self.current_thick, 
                                 value=val, indicatoron=0, width=6, bg='#f0f0f0')
            btn.pack(side=tk.LEFT, padx=1, pady=2)

        # 4. Ações
        action_frame = tk.Frame(toolbar, bg='#e0e0e0')
        action_frame.pack(side=tk.RIGHT, padx=5)
        tk.Button(action_frame, text="Novo", command=self.action_new, width=8).pack(side=tk.TOP, pady=1)
        tk.Button(action_frame, text="Salvar", command=self.action_save, width=8).pack(side=tk.TOP, pady=1)

    def _setup_canvas(self):
        # O PhotoImage atua como nosso Framebuffer de pixels brutos
        self.tk_image = tk.PhotoImage(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas_widget = tk.Label(self.root, image=self.tk_image, cursor="cross")
        self.canvas_widget.pack(side=tk.BOTTOM)

        # Nossa classe de abstração do Canvas de CG
        self.canvas = Canvas(self.tk_image, CANVAS_WIDTH, CANVAS_HEIGHT)

        # Eventos do Mouse
        self.canvas_widget.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas_widget.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas_widget.bind("<ButtonRelease-1>", self.on_mouse_up)

    def action_new(self):
        self.canvas.clear()

    def action_save(self):
        """Salva em formato PPM, que é suportado nativamente pelo Tkinter sem libs externas."""
        filename = "desenho.ppm"
        self.tk_image.write(filename, format="ppm")
        print(f"Imagem salva como {filename}!")

    def on_mouse_down(self, event):
        x, y = event.x, event.y
        self.drawing = True
        self.start_pos = (x, y)
        self.last_pos = (x, y)
        tool = self.current_tool.get()
        color = self.current_color.get()

        if tool == 'Balde':
            target = self.canvas.get_pixel(x, y)
            if target:
                Algorithms.flood_fill(self.canvas, x, y, target, color)

    def on_mouse_move(self, event):
        if not self.drawing:
            return
        x, y = event.x, event.y
        tool = self.current_tool.get()
        color = self.current_color.get()
        thick = self.current_thick.get()

        if tool == 'Lapis':
            Algorithms.draw_line(self.canvas, self.last_pos[0], self.last_pos[1], x, y, color, thick)
        elif tool == 'Borracha':
            Algorithms.draw_line(self.canvas, self.last_pos[0], self.last_pos[1], x, y, self.canvas.bg_color, thick)
        
        self.last_pos = (x, y)

    def on_mouse_up(self, event):
        if not self.drawing:
            return
        self.drawing = False
        x, y = event.x, event.y
        sx, sy = self.start_pos
        
        tool = self.current_tool.get()
        color = self.current_color.get()
        thick = self.current_thick.get()

        if tool == 'Linha':
            Algorithms.draw_line(self.canvas, sx, sy, x, y, color, thick)
        elif tool == 'Ret. Vazado':
            Algorithms.draw_empty_rect(self.canvas, sx, sy, x, y, color, thick)
        elif tool == 'Ret. Preenchido':
            Algorithms.draw_filled_rect(self.canvas, sx, sy, x, y, color)
        elif tool in ['Circ. Vazado', 'Circ. Preenchido']:
            radius = int(((x - sx)**2 + (y - sy)**2)**0.5)
            if tool == 'Circ. Vazado':
                Algorithms.draw_circle(self.canvas, sx, sy, radius, color, thick)
            else:
                Algorithms.draw_filled_circle(self.canvas, sx, sy, radius, color)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
