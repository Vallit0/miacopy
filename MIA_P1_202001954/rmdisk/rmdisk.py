import os


def rmdisk_func(file_path):
    file_path = "." + file_path
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print("\x1b[32m****************************\x1b[0m")
            print(f"\x1b[32mDisco '{file_path}' borrado\x1b[0m")
            print("\x1b[32m****************************\x1b[0m")
            return f"Disco '{file_path}' borrado"
        except Exception as e:
            print(f"Error al borrar: {e}")
            return "Error al borrar"
    else:
        print(f"\x1b[93mDisco '{file_path}' no existe. \x1b[0m")
        return f"Disco '{file_path}' no existe."

