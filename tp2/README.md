### Trabalho prático 2 de Computação Gráfica - Ray Tracing - DCC UFMG

- Aluno: Guilherme Torres
- Matrícula: 2015083744
- Professor: Erickson Nascimento

    O trabalho que segue é um ray tracer em CPU distribuído implementado em Python puro, usando apenas as bibliotecas padrão, onde foram implementadas as diversas features que foram propostas e discutidas em sala de aula, que também são mostradas nas imagens no repositório. Foi usado como inspiração o livro "Ray Tracing in One Weekend", de Peter Shirley, mas as decisões de design e alguns algoritmos não foram seguidos à risca. Abaixo segue uma lista do que foi implementado:
    
    ### Execução
    
    O programa é executado simplesmente com o comando python3 raytracer.py <arquivo de output>
    
    ### Funcionalidades básicas
    
    Como mostra o livro nos seus capítulos de fundamentos, o ray tracer apresenta esferas como suas formas principais e estas esferas podem ter 3 tipos de materiais: lambertiano, dielétrico (refrator, ex. vidro), ou reflectivo (ex. metais). O material lambertiano possui um albedo e um coeficiente de difusão, o dielétrico, além do albedo, possui um coeficiente de refração (o do vidro é entre 1.3 e 1.7) e um coeficiente de atenuação, que define o quanto da cor original do material será preservada após a refração. Já o material reflectivo tem um coeficiente de reflexão, que define a porcentagem dos raios que será refletida e um fator "fuzz", que randomiza os raios refletivos, re-distribuíndo eles e formando reflexões imperfeitas.
    
    Anti-aliasing foi implementado usando uma técnica simples de distribuír mais de um raio por pixel.
    
    O programa também foi paralelizado com a biblioteca multiprocessing. O número de processos ativos por vez é igual ao número de CPUs do computador onde o código está sendo executado vezes dois (para ter a vantagem de usar hyperthreading quando estiver disponível). 
    
    Abaixo seguem os extras implementados:
    
    ### Interseção com triângulos
    
    A interseção com triângulos é tratada da maneira que foi descrita no [Scratchapixel](https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution). Basicamente se calcula a interseção do raio com o plano do triângulo para depois se calcular a localização desse ponto perante a cada uma das arestas do triângulo. Como também é necessário obter as meshes para renderizar formas mais interessantes, segue também no programa, no construtor da classe Mesh, um pequeno loader para arquivos Wavefront (.obj).
    
    ### Depth of field
    
    A câmera da cena desfoca em objetos que estejam longe do seu foco como ocorre em uma câmera real. Isso ocorre a partir da randomização dos raios em função da sua distância da abertura. A abertura é definida por um valor (que geralmente se encontra entre 0.5 e 3) e o processo é feito como é descrito no livro de Peter Shirley. 
    
    ### Reflexões imperfeitas
    
    Como foi citado anteriormente, as reflexões têm um fator "fuzz", como também é mostrado no livro, e este fator define o quanto um raio sofre jitter ao ser refletivo por uma superfície com tal material. 
    
    ### Sombras suaves
    
    O cálculo da oclusão é feito a partir do lançamento de outros raios, de um ponto até a luz. O papel do programa ao fazer as sombras suaves é randomizar também a direção desses raios, e feito isso, percebe-se que os cantos das sombras são borrados e têm um blend mais natural com os materiais sombreados.
    
    ### Motion blur
    
    Por fim, foi implementado um motion blur. Isso foi feito também com randomização mas não com a direção dos raios, e sim com a posição das formas. As formas na cena são iniciadas com um vetor velocidade que, por padrão, é zero, e cada raio ao ser lançado leva em conta um componente tempo que varia aleatoriamente de -1 a 1. Dependendo desse valor e do vetor velocidade, é definida a "nova posição" da forma na cena, e por meio da distribuição de raios e da média entre eles, o efeito é semelhante ao das sombras suaves, reflexões imperfeitas ou depth of field: um borrado, que no caso, sugere movimento na cena.