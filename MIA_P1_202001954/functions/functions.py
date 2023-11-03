import ctypes
import struct
class Particion(ctypes.Structure):
    _fields_ = [
        ("part_status", ctypes.c_char),
        ("part_type", ctypes.c_char),
        ("part_fit", ctypes.c_char),
        ("part_start", ctypes.c_int),
        ("part_size", ctypes.c_int),
        # Add other fields from the 'particion' struct here
    ]
class MBR(ctypes.Structure):
    _fields_ = [
        ("mbr_tamano", ctypes.c_int),
        ("mbr_fecha_creacion", ctypes.c_int),
        ("mbr_disk_signature", ctypes.c_int),
        ("dsk_fit", ctypes.c_char),
        ("mbr_particiones", Particion * 4),
    ]
def processPath(path):
    n = len(path)
    new_path = ""
    j = 0
    inside_quotes = False

    for i in range(n):
        if path[i] == '"':
            inside_quotes = not inside_quotes

        if path[i] == ' ' and not inside_quotes:
            new_path += "`"
        elif path[i] == ' ' and inside_quotes:
            new_path += "-"
        elif path[i] == '"' and (i == 0 or i == n - 1):
            continue
        else:
            new_path += path[i]

    return new_path
def removeQuotes(str):
    n = len(str)
    new_str = ""
    j = 0

    for i in range(n):
        if str[i] == '"':
            continue
        new_str += str[i]
        j += 1

    return new_str

def get_tipo_parametro(parametro: str) -> str:
    # Iteramos hasta obtener el tipo del parametro
    tipo = ""
    for i in range(len(parametro)):
        if parametro[i] == '=':
            break
        caracter = parametro[i].lower()
        tipo = tipo + caracter
    # Devolvemos el string
    return tipo
def get_valor_parametro(parametro: str) -> str:
    # Iteramos hasta obtener el valor del parametro
    valor = ""
    concatenar = False
    for i in range(len(parametro)):
        if concatenar:
            caracter = parametro[i]
            valor = valor + caracter
        if parametro[i] == '=':
            concatenar = True
    # Devolvemos el string
    return valor

def pack_mbr(self, mbr: MBR):
    # Pack the provided values using the desired format
    # Tomamos el tiempo y lo convertimos en struct de tiempo
    print(ctypes.sizeof(Particion))
    print(mbr.mbr_fecha_creacion)
    packedData = struct.pack("iii1s", mbr.mbr_tamano, mbr.mbr_fecha_creacion, mbr.mbr_dsk_signature, mbr.mbr_fit.encode("utf-8"))
    print("Packing Partitions")
    print("LEN NEC-> " + str(len(packedData)))
    for particion in mbr.mbr_particiones:
        packedData+= struct.pack("cccii", particion.part_status, particion.part_type, particion.part_fit,particion.part_start, particion.part_size)
    return packedData

def write_mbr(self, mbr: MBR, archivo, path) -> None:
    print("Prev")
    print(path)
    with open(path, 'rb') as f:
        data = f.read()
        print("ARCHIVO->")
        hexdump.hexdump(data)
    archivo.write(self.pack_mbr(mbr))
    print("Post")
    print(path)
    with open(path, 'rb') as f:
        data = f.read()
        hexdump.hexdump(data)