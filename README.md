# Mini Paint: Implementação de um Editor Gráfico

## Objetivos de aprendizado

- Compreender e manipular uma matriz de pixels (framebuffer);
- Implementar algoritmos de rasterização de primitivas (linhas, círculos, retângulos, polígonos);

- Aplicar transformações geométricas simples (translado, rotação, escala) em objetos desenhados;

- Implementar preenchimento de regiões (flood fill ou boundary fill);
- Gerenciar interação do usuário (mouse/teclado) para desenho em tempo real;
- Entender o conceito  de cores (RGB) e operações de blend.

## Requisitos Funcionais mínimos (versão básica)

O software deve permitir ao usuário:
- Área de desenho (canvas) de tamanho fixo (ex.: 800x600 pixels).
- Ferramentas essenciais:
    - Lápis (pincel de 1 pixel).
    - Borracha (pinta com a cor de fundo).
    - Linha reta (algoritmo de Bresenham ou DDA).
    - Retângulo vazado e preenchido.
    - Círculo vazado e preenchido.
    - Balde de tinta (flood fill 4 ou 8 conectado).
- Paleta de cores com pelo menos 8 cores pré-definidas (preto, branco, vermelho, verde, azul, amarelo, ciano, magenta).
- Seleção de espessura do pincel/ferramentas (3 opções: fino, médio e grosso).
- Botão "Novo" (limpar canvas com cor de fundo).
- Botão "Salvar" (exportar para um formato simples, como BMP, PPM ou PNG via biblioteca).

Requisitos ténicos (núcleo)  Sem uso de bibliotecas gráficas de alto nível
- Para desenho primitivo (ex.: não pode usar drawLine pronta). Você pode usar SDL2, SFML, OpenGL com glDrawPixels, ou até uma biblioteca simples como graphics.h (Turbo C++) apenas para criar a janela e acesso ao framebuffer.

Deve ser implementado:
- put_pixel(x, y, cor)
- get_pixel(x, y)
- Algoritmo de linha (Bresenham).
- Algoritmo de Círculo (Bresenham ou ponto médio).
- Flood fill recursivo ou com pilha/queue (não usar função pronta).
- Tratamento de eventos do mouse (clique, arrastar, soltar).
- Estrutura de dados para o canvas: Matriz 2D de inteiros (cores indexadas) ou struct RGB. 
