# Trabalho prático 3 de Computação Gráfica
### Aluno: Guilherme Torres
### Matrícula: 2015083744
### Departamento de Ciência da Computação - Universidade Federal de Minas Gerais

O trabalho que segue é uma implementação de um leitor de arquivos .md2 (do Quake 2), com um renderizador do modelo e e suporte às animações usando shape interpolation entre as frames. A implementação foi em Python 3, OpenGL 3.3 e, portanto, com shaders em GLSL 330.

# Como usar

### Dependências - bibliotecas não-padrão usadas

O numpy é usado para transformar os buffers de dados em estruturas de dados tipadas para fazer os buffers de OpenGL. Além disso, a biblioteca Pillow (PIL) é usada para fazer o carregamento das imagens para textura (que ainda não é suportada no programa, por conta de alguns problemas técnicos com os índices de UVs nos modelos MD2), a bilbioteca Pyrr é usada para fazer a construção das matrizes de transformação e o gerenciador de display GLFW é usado para administrar a janela do sistema.

### Execução

- python3 main.py <arquivo md2> --tex <imagem de textura (opcional)> --anim <arquivo com índices de frames para a animação (opcional)>

Um exemplo de execução com o arquivo md2 oferecido junto do trabalho está no script example.sh

### Arquivo com os índices das frames para a animação

Este arquivo deve ser um arquivo de texto no seguinte formato:

<nome da animação 1> <primeira frame> <última frame> <fps>
<nome da animação 2> <primeira frame> <última frame> <fps>
<nome da animação 3> <primeira frame> <última frame> <fps>
.
.
.
<nome da animação n> <primeira frame> <última frame> <fps>

# Decisões de implementação

### Importador

O importador foi baseado [neste tutorial](http://tfc.duke.free.fr/old/models/md2.htm). Porém, algumas decisões típicas de C foram trocadas por métodos mais característicos de Python. O leitor de arquivos, por exemplo, foi declarado como o construtor de uma classe MD2Object. Não foram usados buffers de dados ou casts de dados em formato char para float ou int, no lugar disso, foi usado o método from_bytes() do tipo int em Python e a biblioteca padrão struct para desempacotar os dados do formato de bytes no caso de números de ponto flutuante. Também no construtor, é declarado o VAO e os VBOs que serão responsáveis por manter os dados dos vértices na GPU durante a renderização.

### Renderização e animação

A etapa de renderização ocorre como é padrão no OpenGL moderno: os atributos para a shader (no caso, os inputs para a vertex shader) são mandados através de ponteiros para buffers na GPU e os uniforms (no caso, a matriz MVP, que é um uniform estático no programa) e o coeficiente de interpolação entre as duas posições que estão sendo enviadas para a vertex shader (que gradualmente a cada frame) são passados subsequentemente.

O que ocorre depois na shader para realizar a animação com sucesso é uma interpolação de vetores acelerada pela GPU para se obter uma boa performance. Isso ocorre com a função mix(). Como os modelos md2 não possuem normais neles, na fragment shader ao ser calculada a iluminação do modelo, o flat shading é usado (uma possível melhoria futura seria o uso do Phong shading para renderizar a malha, o que precisa que as normais sejam calculadas manualmente).