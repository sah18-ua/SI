class Variable:
    # Initialize a cell with its position, value
    def __init__(self, fila, columna):
        self.pos = (fila, columna)
        self.valor = None
        self.dominio = set(range(1, 10))

    # Assign a value to the cell 
    def asignar_valor(self, valor):
        if valor not in self.dominio:
            raise ValueError(f"El valor {valor} no está en el dominio actual: {self.dominio}")
        self.valor = valor

    # Remove a value from the domain
    def eliminar(self, valor):
        if valor in self.dominio:
            self.dominio.remove(valor)

    # Remove the assigned value, making the cell empty again        
    def desasignar_valor(self):
        self.valor = None

    # Update the domain with a new set of possible values
    def actualizar_dominio(self, nuevo_dominio):
        self.dominio = set(nuevo_dominio)

    # Restore the domain to its initial state
    def restaurar_dominio(self):
        self.dominio = set(range(1, 10))
    
    # Reset the cell to its initial state
    def resetear_casilla(self):
        self.restaurar_dominio()
        self.desasignar_valor()

    # Get the next possible value from the domain
    def siguiente_posible(self):
        if not self.dominio:
            return None
        return min(self.dominio)
    
    # Representation of a cell as a string
    def __repr__(self):
        return f"{self.valor}" if self.valor is not None else '0'

def calcular_box_index(i, j):
    return (i // 3) * 3 + (j // 3)

#esta clase esta puesto como para ac3 ya que se hace un precomputo
class Domains:
    def __init__(self, tablero, ac3 = False):
        self.row_domains = [set(range(1, 10)) for _ in range(9)]
        self.col_domains = [set(range(1, 10)) for _ in range(9)]
        self.box_domains = [set(range(1, 10)) for _ in range(9)]

        # Inicializar dominios globales con los valores ya presentes
        if ac3:
            for i in range(9):
                for j in range(9):
                    val = int(tablero.getCelda(i, j))
                    if val != 0:
                        self.eliminar(i, j, val)
    

    def eliminar(self, i, j, val):
        self.row_domains[i].discard(val)
        self.col_domains[j].discard(val)
        self.box_domains[calcular_box_index(i, j)].discard(val)

    def restaurar(self, i, j, val):
        self.row_domains[i].add(val)
        self.col_domains[j].add(val)
        self.box_domains[calcular_box_index(i, j)].add(val)

    def get_domain(self, i, j):
        return self.row_domains[i] & self.col_domains[j] & self.box_domains[calcular_box_index(i, j)]

    def asignar_valor(self, i, j, val, vacias):
        self.eliminar(i, j, val)
        posiciones_afectadas = set()

        # Recolectar posiciones afectadas (fila y columna)
        for col in range(9):
            if col != j:
                posiciones_afectadas.add((i, col))
        for row in range(9):
            if row != i:
                posiciones_afectadas.add((row, j))

        # Recolectar posiciones afectadas (caja)
        box_start_i = (i // 3) * 3
        box_start_j = (j // 3) * 3
        for x in range(box_start_i, box_start_i + 3):
            for y in range(box_start_j, box_start_j + 3):
                if (x, y) != (i, j):
                    posiciones_afectadas.add((x, y))

        # Guardar dominios previos para posible restauración
        actualizados = []

        for var in vacias:
            if var.pos in posiciones_afectadas and var.valor is None:
                fila, col = var.pos
                nuevo_dom = self.get_domain(fila, col)
                actualizados.append(var)

                if not nuevo_dom:
                    self.restaurar(i, j, val)
                    for v in actualizados:
                        dom = self.get_domain(v.pos[0], v.pos[1])
                        v.actualizar_dominio(dom)
                    return False

                var.actualizar_dominio(nuevo_dom)

        return True

        
    
       
