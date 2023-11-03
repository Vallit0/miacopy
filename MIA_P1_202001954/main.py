from typing import List
from analizador import analizador
from analizador.analizador import analizar
import readline # para el autocompletado

# Definición de clases y estructuras (si es necesario)
class disco:
    pass

class datosUSR:
    pass

# Declaración de variables globales
registro: List[disco] = []  # mantiene los datos en memoria RAM
usuario: str = ""  # guarda el usuario en línea
infoUSR = datosUSR()  # guarda información del usuario
estado: int = 0  # indica si el usuario está en línea o no

# Función principal
def main():
    print("\033[1;35m Proyecto1 Manejo e Implementacion \033[0m")
    print("\033[1;35m============================================\033[0m")
    print("|     ", "\033[1;36mEstuardo Sebastian Valle Bances\033[0m", "       |")
    print("|         SISTEMA DE ARCHIVOS               |")
    print("|          PROYECTO 1, MIA                  |")
    print("|              20202001954                  |")
    print("\033[1;35m============================================ \033[0m\n")

    repetir = True
    while repetir:
        # Pedimos el comando
        comando = input("> ")

        # Ahora analizamos
        #print("comando")
        print("\033[1;36m", comando, "\033[0m")
        analizar(comando)

if __name__ == "__main__":
    main()
