import pygame
import sys

# Configurações Globais
WIDTH, HEIGHT = 800, 600
UI_HEIGHT = 80
TOTAL_HEIGHT = HEIGHT + UI_HEIGHT

# Paleta de 8 cores pré-definidas
COLORS = {
    'Preto': (0, 0, 0), 'Branco': (255, 255, 255),
    'Vermelho': (255, 0, 0), 'Verde': (0, 255, 0),
    'Azul': (0, 0, 255), 'Amarelo': (255, 255, 0),
    'Ciano': (0, 255, 255), 'Magenta': (255, 0, 255)
}
BG_COLOR = (255, 255, 255)

class MiniPaint:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, TOTAL_HEIGHT))
        pygame.display.set_caption("Mini Paint - Rasterização Raiz")
        self.font = pygame.font.SysFont(None, 24)
        
        # Estados do App
        self.current_color = COLORS['Preto']
        self.current_size = 1
        self.current_tool = 'Lápis'
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        
        # Buffer de imagem para preview (arrastar formas)
        self.canvas_copy = None
        
        # Estrutura da Interface (UI)
        self.tools = ['Lápis', 'Borracha', 'Linha', 'Ret.Vaz', 'Ret.Pre', 'Circ.Vaz', 'Circ.Pre', 'Balde']
        self.sizes = [1, 3, 5]
        
        self.clear_canvas()

    def clear_canvas(self):
        """Limpa o canvas preenchendo com a cor de fundo (usando manipulação direta)"""
        # Para a limpeza inicial, preenchemos o espaço do canvas
        self.screen.fill(BG_COLOR, (0, UI_HEIGHT, WIDTH, HEIGHT))

    # ==========================================
    # NÚCLEO DO MOTOR GRÁFICO (REQUISITOS)
    # ==========================================

    def put_pixel(self, x, y, color, thickness=1):
        """Atualiza a matriz de pixels. Evita desenhar fora do canvas (UI)."""
        if thickness == 1:
            if 0 <= x < WIDTH and UI_HEIGHT <= y < TOTAL_HEIGHT:
                self.screen.set_at((x, y), color)
        else:
            # Simula espessura pintando um bloco ao redor do centro
            offset = thickness // 2
            for i in range(-offset, offset + 1):
                for j in range(-offset, offset + 1):
                    nx, ny = x + i, y + j
                    if 0 <= nx < WIDTH and UI_HEIGHT <= ny < TOTAL_HEIGHT:
                        self.screen.set_at((nx, ny), color)

    def get_pixel(self, x, y):
        """Lê a cor de um pixel no framebuffer."""
        if 0 <= x < WIDTH and UI_HEIGHT <= y < TOTAL_HEIGHT:
            return self.screen.get_at((x, y))[:3] # Retorna apenas RGB, ignorando Alpha
        return None

    def draw_line(self, x0, y0, x1, y1, color, thickness):
        """Algoritmo de Bresenham para Linhas."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.put_pixel(x0, y0, color, thickness)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_rect(self, x0, y0, x1, y1, color, thickness, filled=False):
        """Desenha retângulo combinando linhas de Bresenham."""
        min_x, max_x = min(x0, x1), max(x0, x1)
        min_y, max_y = min(y0, y1), max(y0, y1)

        if filled:
            for y in range(min_y, max_y + 1):
                self.draw_line(min_x, y, max_x, y, color, thickness=1)
        else:
            self.draw_line(min_x, min_y, max_x, min_y, color, thickness)
            self.draw_line(max_x, min_y, max_x, max_y, color, thickness)
            self.draw_line(max_x, max_y, min_x, max_y, color, thickness)
            self.draw_line(min_x, max_y, min_x, min_y, color, thickness)

    def draw_circle(self, xc, yc, r, color, thickness, filled=False):
        """Algoritmo de Ponto Médio (Bresenham) para Círculos."""
        x = 0
        y = r
        d = 1 - r
        self._plot_circle_points(xc, yc, x, y, color, thickness, filled)
        
        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            self._plot_circle_points(xc, yc, x, y, color, thickness, filled)

    def _plot_circle_points(self, xc, yc, x, y, color, thickness, filled):
        """Espelha os pontos calculados para os 8 octantes."""
        if filled:
            # Preenchimento conectando os lados opostos com retas horizontais
            self.draw_line(xc - x, yc + y, xc + x, yc + y, color, 1)
            self.draw_line(xc - x, yc - y, xc + x, yc - y, color, 1)
            self.draw_line(xc - y, yc + x, xc + y, yc + x, color, 1)
            self.draw_line(xc - y, yc - x, xc + y, yc - x, color, 1)
        else:
            self.put_pixel(xc + x, yc + y, color, thickness)
            self.put_pixel(xc - x, yc + y, color, thickness)
            self.put_pixel(xc + x, yc - y, color, thickness)
            self.put_pixel(xc - x, yc - y, color, thickness)
            self.put_pixel(xc + y, yc + x, color, thickness)
            self.put_pixel(xc - y, yc + x, color, thickness)
            self.put_pixel(xc + y, yc - x, color, thickness)
            self.put_pixel(xc - y, yc - x, color, thickness)

    def flood_fill(self, x, y, target_color, replacement_color):
        """Preenchimento usando estrutura de dados Pilha (Stack 4-conectado)."""
        if target_color == replacement_color:
            return

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if 0 <= cx < WIDTH and UI_HEIGHT <= cy < TOTAL_HEIGHT:
                current_pixel = self.get_pixel(cx, cy)
                if current_pixel == target_color:
                    self.put_pixel(cx, cy, replacement_color, thickness=1)
                    stack.append((cx + 1, cy))
                    stack.append((cx - 1, cy))
                    stack.append((cx, cy + 1))
                    stack.append((cx, cy - 1))

    def save_ppm(self):
        """Exporta o canvas manualmente varrendo a matriz para o formato PPM."""
        print("Salvando imagem... aguarde.")
        with open("desenho.ppm", "w") as f:
            f.write(f"P3\n{WIDTH} {HEIGHT}\n255\n")
            for y in range(UI_HEIGHT, TOTAL_HEIGHT):
                for x in range(WIDTH):
                    r, g, b = self.get_pixel(x, y)
                    f.write(f"{r} {g} {b} ")
                f.write("\n")
        print("Salvo como 'desenho.ppm'!")

    # ==========================================
    # INTERFACE E EVENTOS (USANDO PYGAME BÁSICO)
    # ==========================================
    
    def draw_ui(self):
        self.screen.fill((200, 200, 200), (0, 0, WIDTH, UI_HEIGHT))
        
        # Desenha paleta de cores
        x_offset = 10
        for name, color in COLORS.items():
            rect = pygame.Rect(x_offset, 10, 20, 20)
            pygame.draw.rect(self.screen, color, rect)
            if color == self.current_color:
                pygame.draw.rect(self.screen, (255, 0, 0), rect, 2) # Destaque
            x_offset += 30
            
        # Desenha Ferramentas
        x_offset = 260
        for tool in self.tools:
            color = (150, 150, 150) if tool == self.current_tool else (220, 220, 220)
            rect = pygame.Rect(x_offset, 10, 80, 25)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            text = self.font.render(tool, True, (0, 0, 0))
            self.screen.blit(text, (x_offset + 5, 15))
            x_offset += 85
            
        # Desenha Espessuras
        x_offset = 10
        for size in self.sizes:
            color = (150, 150, 150) if size == self.current_size else (220, 220, 220)
            rect = pygame.Rect(x_offset, 45, 30, 25)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            text = self.font.render(str(size), True, (0, 0, 0))
            self.screen.blit(text, (x_offset + 10, 50))
            x_offset += 40
            
        # Botões Novo e Salvar
        pygame.draw.rect(self.screen, (255, 100, 100), (150, 45, 60, 25))
        self.screen.blit(self.font.render("Novo", True, (0,0,0)), (155, 50))
        
        pygame.draw.rect(self.screen, (100, 255, 100), (220, 45, 60, 25))
        self.screen.blit(self.font.render("Salvar", True, (0,0,0)), (225, 50))

    def handle_ui_click(self, pos):
        x, y = pos
        
        # Checa cores
        x_offset = 10
        for color in COLORS.values():
            if pygame.Rect(x_offset, 10, 20, 20).collidepoint(x, y):
                self.current_color = color
            x_offset += 30
            
        # Checa ferramentas
        x_offset = 260
        for tool in self.tools:
            if pygame.Rect(x_offset, 10, 80, 25).collidepoint(x, y):
                self.current_tool = tool
            x_offset += 85
            
        # Checa espessuras
        x_offset = 10
        for size in self.sizes:
            if pygame.Rect(x_offset, 45, 30, 25).collidepoint(x, y):
                self.current_size = size
            x_offset += 40
            
        # Checa botões
        if pygame.Rect(150, 45, 60, 25).collidepoint(x, y):
            self.clear_canvas()
        if pygame.Rect(220, 45, 60, 25).collidepoint(x, y):
            self.save_ppm()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.draw_ui()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[1] < UI_HEIGHT:
                        self.handle_ui_click(event.pos)
                    else:
                        self.drawing = True
                        self.start_pos = event.pos
                        self.last_pos = event.pos
                        
                        # Salva o canvas atual para lidar com a "pré-visualização" ao arrastar formas
                        self.canvas_copy = self.screen.subsurface((0, UI_HEIGHT, WIDTH, HEIGHT)).copy()
                        
                        if self.current_tool == 'Balde':
                            target = self.get_pixel(*event.pos)
                            if target:
                                self.flood_fill(event.pos[0], event.pos[1], target, self.current_color)
                        elif self.current_tool in ['Lápis', 'Borracha']:
                            col = BG_COLOR if self.current_tool == 'Borracha' else self.current_color
                            self.put_pixel(event.pos[0], event.pos[1], col, self.current_size)

                elif event.type == pygame.MOUSEMOTION:
                    if self.drawing:
                        if self.current_tool in ['Lápis', 'Borracha']:
                            col = BG_COLOR if self.current_tool == 'Borracha' else self.current_color
                            # Traça reta entre o último ponto e o atual para não criar buracos se o mouse for rápido
                            self.draw_line(self.last_pos[0], self.last_pos[1], event.pos[0], event.pos[1], col, self.current_size)
                            self.last_pos = event.pos
                        elif self.current_tool not in ['Balde']:
                            # Restaura o canvas limpo para desenhar a prévia dinâmica
                            self.screen.blit(self.canvas_copy, (0, UI_HEIGHT))
                            col = self.current_color
                            sz = self.current_size
                            x0, y0 = self.start_pos
                            x1, y1 = event.pos
                            
                            if self.current_tool == 'Linha':
                                self.draw_line(x0, y0, x1, y1, col, sz)
                            elif self.current_tool == 'Ret.Vaz':
                                self.draw_rect(x0, y0, x1, y1, col, sz, filled=False)
                            elif self.current_tool == 'Ret.Pre':
                                self.draw_rect(x0, y0, x1, y1, col, sz, filled=True)
                            elif self.current_tool in ['Circ.Vaz', 'Circ.Pre']:
                                r = int(((x1 - x0)**2 + (y1 - y0)**2)**0.5)
                                filled = (self.current_tool == 'Circ.Pre')
                                self.draw_circle(x0, y0, r, col, sz, filled)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drawing = False

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = MiniPaint()
    app.run()
