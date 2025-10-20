#########################################################################
# CURSO 25-25
# PRACTICA 1 DE SISTEMAS INTELIGENTES: RESOLUCION DE SUDOKUS
#########################################################################   

import pygame
import copy
from variable import *
from tablero import *
from pygame.locals import *
import sys

GREY=(220,220,220)
NEGRO=(10,10,10)
GRIS_ACTIVO=(245,245,245)
GRIS_NORMAL=(169,169,169)
BLANCO=(255, 255, 255)

MARGEN=5 #ancho del borde entre celdas
MARGEN_DERECHO=125 #ancho del margen derecho entre la cuadrícula y la ventana
TAM=60  #tamaño de la celda
N=9 # número de filas del sudoku
VACIA='0'

#########################################################################
# Detecta si se pulsa un botón
#########################################################################   
def pulsaBoton(pos, boton):
    if boton.collidepoint(pos[0], pos[1]):    
        return True
    else:
        return False

#########################################################################
# Pintar un boton
#########################################################################   
def pintarBoton(screen, fuenteBot, boton, mensaje):
    if boton.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, GRIS_ACTIVO, boton, 0)        
    else:
        pygame.draw.rect(screen, GRIS_NORMAL, boton, 0)
        
    texto=fuenteBot.render(mensaje, True, NEGRO)
    screen.blit(texto, (boton.x+(boton.width-texto.get_width())/2, boton.y+(boton.height-texto.get_height())/2))         

#########################################################################
# Pintar el sudoku
#########################################################################         
def pintarTablero(screen, fuenteSud, tablero, copTab):
    pygame.draw.rect(screen, GREY, [0, 0, N*(TAM+MARGEN)+MARGEN, N*(TAM+MARGEN)+MARGEN],0)
    for fil in range(9):
        for col in range(9):
            if tablero is None or tablero.getCelda(fil, col)==VACIA :
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)            
            else:
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
                if tablero.getCelda(fil, col)==copTab.getCelda(fil, col):
                    color=NEGRO
                else:
                    color=GRIS_NORMAL                 
                texto= fuenteSud.render(tablero.getCelda(fil, col), True, color)            
                screen.blit(texto, [(TAM+MARGEN)*col+MARGEN+15, (TAM+MARGEN)*fil+MARGEN+5])
    
    #dibujar línea de cuadrícula     
    pygame.draw.line(screen, GRIS_NORMAL, (MARGEN, 3*(TAM+MARGEN)+2), (9*(TAM+MARGEN),3*(TAM+MARGEN)+2), 5)
    pygame.draw.line(screen, GRIS_NORMAL, (MARGEN, 6*(TAM+MARGEN)+2), (9*(TAM+MARGEN),6*(TAM+MARGEN)+2), 5)    
    pygame.draw.line(screen, GRIS_NORMAL, (3*(TAM+MARGEN)+2,MARGEN), (3*(TAM+MARGEN)+2,9*(TAM+MARGEN)), 5)
    pygame.draw.line(screen, GRIS_NORMAL, (6*(TAM+MARGEN)+2, MARGEN), (6*(TAM+MARGEN)+2,9*(TAM+MARGEN)), 5)
    pygame.draw.rect(screen, GRIS_NORMAL, [MARGEN, MARGEN, N*(TAM+MARGEN), N*(TAM+MARGEN)],5)

#Comprueba restricciones del tablero de sudoku
def es_valido(tablero, fila, col, valor):
    # Verifica fila
    for c in range(9):
        if tablero.getCelda(fila, c) == valor:
            return False

    # Verifica columna
    for f in range(9):
        if tablero.getCelda(f, col) == valor:
            return False

    # Verifica bloque 3x3
    inicio_fila = (fila // 3) * 3
    inicio_col = (col // 3) * 3
    for r in range(inicio_fila, inicio_fila + 3):
        for c in range(inicio_col, inicio_col + 3):
            if tablero.getCelda(r, c) == valor:
                return False

    return True


#busca la lista de posiciones vacias
def buscar_vacias(tablero):
    vacias = []
    for fila in range(9):
        for col in range(9):
            if tablero.getCelda(fila, col) == "0":
                vacias.append(Variable(fila, col))
    return vacias

#resuelve por backtracking el sudoku
def backtracking(tablero):
    pila = []  # pila de variables asignadas
    vacias = buscar_vacias(tablero)  # lista de Variables
    i = 0
    
    while True:
        if i == len(vacias):
            return True  # Sudoku resuelto
        
        variable = vacias[i]
        valor = variable.siguiente_posible()
        
        if valor is not None:
            fila, col = variable.pos
            if es_valido(tablero, fila, col, str(valor)):
                variable.asignar_valor(valor)
                variable.eliminar(valor)  # Eliminar valor del dominio

                tablero.setCelda(fila, col, str(valor))
                pila.append(variable)
                i += 1
            else:
                # Valor inválido, eliminar para no volver a probar
                variable.eliminar(valor)
        else:
            # No quedan valores, hacer backtrack
            if not pila:
                return False  # No hay solución
            
            variable_back = pila.pop()
            fila, col = variable_back.pos

            tablero.setCelda(fila, col, "0")
            variable_back.desasignar_valor()
            variable.restaurar_dominio()  # Restaurar dominio para probar otros valores
            i -= 1

def forward_checking(tablero):
    dominios = Domains(tablero)
    vacias = buscar_vacias(tablero)

    stack = []  # pila de (índice_variable, valor_asignado)
    i = 0

    while i < len(vacias):
        variable = vacias[i]
        fila, col = variable.pos

        valor = variable.siguiente_posible()
        print(f"\nIntentando variable {i} en posición ({fila},{col}) con dominio {variable.dominio}")
        print(f"Valor siguiente posible: {valor}")

        if valor is not None:
            if es_valido(tablero, fila, col, valor):
                print(f"Asignando valor {valor} a variable {i} ya que es valido")
                variable.asignar_valor(valor)
                tablero.setCelda(fila, col, str(valor))

                if dominios.asignar_valor(fila, col, valor, vacias):
                    print(f"Dominio actualizado correctamente tras asignar {valor} en ({fila},{col})")
                    stack.append((i, valor))
                    i += 1
                else:
                    print(f"Dominio vacío tras asignar {valor} en ({fila},{col}), deshaciendo asignación")
                    variable.eliminar(valor)
                    variable.desasignar_valor()
                    tablero.setCelda(fila, col, "0")

        else:
            print(f"No quedan valores posibles para variable {i} en posición ({fila},{col}), backtracking")
            if not stack:
                print("Pila vacía, no hay solución")
                return False

            i, valor_asignado = stack.pop()
            var = vacias[i]
            fila, col = var.pos

            print(f"Retrocediendo a variable {i} en ({fila},{col}), desasignando valor {valor_asignado}")
            var.desasignar_valor()
            tablero.setCelda(fila, col, "0")
            dominios.restaurar(fila, col, valor_asignado)
            variable.restaurar_dominio()

            var.eliminar(valor_asignado)

    print("Solución encontrada!")
    return True

def AC3(tablero):
    dominios = Domains(tablero,True)
    vacias = buscar_vacias(tablero)

    stack = []  # pila de (índice_variable, valor_asignado)
    i = 0

    while i < len(vacias):
        variable = vacias[i]
        fila, col = variable.pos

        valor = variable.siguiente_posible()
        print(f"\nIntentando variable {i} en posición ({fila},{col}) con dominio {variable.dominio}")
        print(f"Valor siguiente posible: {valor}")

        if valor is not None:
            print(f"Asignando valor {valor} a variable {i}")
            variable.asignar_valor(valor)
            tablero.setCelda(fila, col, str(valor))

            if dominios.asignar_valor(fila, col, valor, vacias):
                print(f"Dominio actualizado correctamente tras asignar {valor} en ({fila},{col})")
                stack.append((i, valor))
                i += 1
            else:
                print(f"Dominio vacío tras asignar {valor} en ({fila},{col}), deshaciendo asignación")
                variable.eliminar(valor)
                variable.desasignar_valor()
                tablero.setCelda(fila, col, "0")

        else:
            print(f"No quedan valores posibles para variable {i} en posición ({fila},{col}), backtracking")
            if not stack:
                print("Pila vacía, no hay solución")
                return False

            i, valor_asignado = stack.pop()
            var = vacias[i]
            fila, col = var.pos

            print(f"Retrocediendo a variable {i} en ({fila},{col}), desasignando valor {valor_asignado}")
            var.desasignar_valor()
            tablero.setCelda(fila, col, "0")
            dominios.restaurar(fila, col, valor_asignado)
            variable.restaurar_dominio()

            var.eliminar(valor_asignado)

    print("Solución encontrada!")
    return True
#########################################################################  
# Principal
#########################################################################
def main():    
    
    pygame.init()
    reloj=pygame.time.Clock()
    
    if len(sys.argv)==1: #si no se indica un mapa coge mapa.txt por defecto
        file='m1.txt'
    else:
        file=sys.argv[-1]
    
    anchoVentana=N*(TAM+MARGEN)+MARGEN_DERECHO
    altoVentana= N*(TAM+MARGEN)+2*MARGEN    
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygame.display.set_caption("Practica 1: Sudoku") 
    
    fuenteBot=pygame.font.Font(None, 30)
    fuenteSud= pygame.font.Font(None, 70)
    
    botLoad=pygame.Rect(anchoVentana-95, 75, 70, 50)    
    botBK=pygame.Rect(anchoVentana-95, 203, 70, 50)
    botFC=pygame.Rect(anchoVentana-95, 333, 70, 50)
    botAC3=pygame.Rect(anchoVentana-95, 463, 70, 50)
    
    game_over=False
    tablero=None
    copTab=None
    
    
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición                               
                pos=pygame.mouse.get_pos()
                if pulsaBoton(pos, botLoad):                                      
                    tablero=Tablero(file)
                    copTab=copy.deepcopy(tablero)                                    
                if pulsaBoton(pos, botBK):                    
                    if tablero is None:
                        print('Hay que cargar un sudoku')
                    else:
                        print("BK")
                        backtracking(tablero)
                elif pulsaBoton(pos, botFC):                    
                    if tablero is None:
                        print('Hay que cargar un sudoku')
                    else:
                        print("FC")
                        forward_checking(tablero)
                elif pulsaBoton(pos, botAC3):
                    if tablero is None:
                        print('Hay que cargar un sudoku')
                    else:                        
                        print("AC3")                        
                        #aquí llamar al AC3    
               
        #limpiar pantalla
        screen.fill(GREY)
        #pintar cuadrícula del sudoku  
        pintarTablero(screen, fuenteSud, tablero, copTab)                   
        #pintar botones        
        pintarBoton(screen, fuenteBot, botLoad, "Load")
        pintarBoton(screen, fuenteBot, botBK, "BK")
        pintarBoton(screen, fuenteBot, botFC, "FC")
        pintarBoton(screen, fuenteBot, botAC3, "AC3")        
        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()
 
