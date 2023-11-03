import os
import ctypes
import datetime
import random
import struct
import hexdump
class Particion(ctypes.Structure):
    _fields_ = [
        ("part_status", ctypes.c_char),
        ("part_type", ctypes.c_char),
        ("part_fit", ctypes.c_char),
        ("part_start", ctypes.c_int),
        ("part_size", ctypes.c_int),
        ("part_name", ctypes.c_char * 16),
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

class MkDisk:
    def __init__(self):
        self.size = 0
        self.path = ""
        self.name = ""
        self.unit = ""
        self.fit = ""
        self.date = ""
        self.packed_particiones = ""

    def create_empty_file(self):
        with open("empty_data.bin", "wb") as file:
            num_zeros = 1024
            for i in range(0, 100):
                file.write(b'\x00' * num_zeros)

    def crear_disco(self, size, path, unit, fit):
        print("Path inicial")
        print(path)

        nombre_archivo = ""
        ruta_carpetas = ""
        ## /home/mis discos/
        carpetas = self.descomponer_ruta(path)
        print(carpetas)
        nombre_archivo = carpetas[-1]
        ## Verificamos que la extension sea valida
        if nombre_archivo.endswith(".dsk"):
            ruta_carpetas = "." + self.ruta(carpetas) + "/"
            print("Carpetas:", ruta_carpetas)
            ## /home/mis discos/
            self.createDir(ruta_carpetas)
            print("Working Directory:", os.getcwd())

            print(ruta_carpetas + "creado")
            ## /home/mis discos/disco1.dsk
            te = os.path.join(ruta_carpetas, nombre_archivo)
            self.generar_disco(size, te, unit, fit)
            print("\033[1;32m===============================\033[0m*")
            print("\033[1;32m** Disco creado correctamente ***\033[0m*")
            print("\033[1;32m===============================\033[0m*")
            print("..", te)
            self.imprimir_disco(".." + te)
            return self.printMBRFile(".." + te)
        else:
            print("Extension de disco invalida")
            return "Extension de disco invalida"

    def createDir(self, path):
        path_parts = path.split(os.path.sep)
        current_path = ""
        for part in path_parts:
            current_path = os.path.join(current_path, part)
            if not os.path.exists(current_path):
                os.makedirs(current_path)
                print(f"Created directory: {current_path}")
            else:
                print(f"Directory already exists: {current_path}")
    def pack_mbr(self, mbr: MBR):
        # Pack the provided values using the desired format
        # Tomamos el tiempo y lo convertimos en struct de tiempo
        print(ctypes.sizeof(Particion))
        print(mbr.mbr_fecha_creacion)
        packedData = struct.pack("iii1s", mbr.mbr_tamano, mbr.mbr_fecha_creacion, mbr.mbr_dsk_signature, mbr.mbr_fit.encode("utf-8"))
        print("Packing Partitions")
        print("LEN NEC-> " + str(len(packedData)))
        for particion in mbr.mbr_particiones:
            particion_name_packed = particion.part_name
            packedData+= struct.pack("cccii16s", particion.part_status, particion.part_type, particion.part_fit,particion.part_start, particion.part_size, particion.part_name)
            #packedData += particion_name_packed


        print("====================")
        print("TAMANO->")
        print(ctypes.sizeof(MBR))
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



    def read_packed_data_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            packed_data = file.read()
        return packed_data

    def printMBRFile(self, definedPath):
        packed_data = self.read_packed_data_from_file(definedPath)

        unpacked_data = self.unpack_mbr(packed_data)
        print(unpacked_data)
        print("--------------")
        return unpacked_data
    def descomponer_ruta(self, path):
        return path.split("/")





    def ruta(self, carpetas):
        return "/".join(carpetas[:-1])

    ## Implementada ->
    def imprimir_disco(self, path):
        pass  # Implement this method according to your needs
    ## Generar Disco
    ## output -> Generacion del Disco $$1.dato
    def generar_disco(self, size, path, unit, fit):
        newPathWithoutQuotationMarks = self.removeQuotes(path)
        print("imprimimos sin quotes >> ")
        print(newPathWithoutQuotationMarks)
        # MBR
        instancia_mbr = MBR()
        archivo = open(newPathWithoutQuotationMarks,"wb")
        if archivo is not None:
            print("Path: Good")
            buffer = bytearray(1024)
            if unit == "-1" or unit == "":
                unit = "k"
            if unit.lower() == "k":
                print("Size: " + str(size))
                instancia_mbr.mbr_tamano = size * 1024
                for i in range(1024):
                    buffer[i] = 0
                for i in range(0, size):
                    archivo.write(b'\x00' * 1024)
                archivo.close()
            elif unit.lower() == "m":
                print("Size: " + str(size))
                instancia_mbr.mbr_tamano = size * 1024 * 1024
                for i in range(1024):
                    buffer[i] = 0
                for i in range(0, size):
                    archivo.write(b'\x00' * 1024 * 1024)
                archivo.close()
            current_datetime = datetime.datetime.now()
            current_timestamp_float = current_datetime.timestamp()
            current_timestamp_integer = int(current_timestamp_float)
            instancia_mbr.mbr_fecha_creacion = current_timestamp_integer

            if fit == "-1" or fit == "" or fit == b'1' or fit == b'0':
                fit = "F"

            instancia_mbr.mbr_fit = fit
            particionNueva = Particion(b'0', b'0', b'0', -1, 0, "null".encode("utf-8"))
            instancia_mbr.mbr_dsk_signature = random.randint(0, 100)
            instancia_mbr.mbr_particiones[0] = particionNueva
            instancia_mbr.mbr_particiones[1] = particionNueva
            instancia_mbr.mbr_particiones[2] = particionNueva
            instancia_mbr.mbr_particiones[3] = particionNueva
            # abrimos el archivo de nuevo
            archivo = open(newPathWithoutQuotationMarks, "wb")
            self.write_mbr(instancia_mbr, archivo, newPathWithoutQuotationMarks)
            archivo.close()

        else:
            print("NO EXISTE EL PATH")

        current_datetime = datetime.datetime.now()
        current_timestamp_float = current_datetime.timestamp()
        current_timestamp_integer = int(current_timestamp_float)
        instancia_mbr.mbr_fecha_creacion = current_timestamp_integer

        if fit == "-1" or fit == "" or fit == b'1' or fit  == b'0':
            fit="F"
        elif fit == "bf":
            fit="B"
        elif (fit == "ff"):
            fit="F"
        elif (fit == "wf"):
            fit="W"
        else:
            fit="F"
        instancia_mbr.mbr_fit = fit
        print("Aqui probablemente -> " + str(fit))
        particionNueva = Particion(b'0', b'0', b'0', -1, 0, "null".encode("utf-8"))
        instancia_mbr.mbr_dsk_signature = random.randint(0,100)
        instancia_mbr.mbr_particiones[0] = particionNueva
        instancia_mbr.mbr_particiones[1] = particionNueva
        instancia_mbr.mbr_particiones[2] = particionNueva
        instancia_mbr.mbr_particiones[3] = particionNueva
        # abrimos el archivo de nuevo
        archivo = open(newPathWithoutQuotationMarks, "wb")
        self.write_mbr(instancia_mbr, archivo, newPathWithoutQuotationMarks)
        archivo.close()

    def readMBR(self, file_path):
        with open(file_path, 'rb') as binary_file:
            while True:
                data = binary_file.read(73)  # Read a block of 77 bytes (2 + 25 + 25 + 25)
                if not data:
                    break  # End of file

                # Unpack the data using the specified format
                unpacked_data = struct.unpack('ii15s25s25s', data)

                string1 = unpacked_data[1]
                string2 = unpacked_data[2].decode('utf-8').replace('\x00', '')
                string3 = unpacked_data[3].decode('utf-8').replace('\x00', '')

                print(f"Id: {unpacked_data[0]}")
                print(f"Tipo: {string1}")
                print(f"Cui: {string2}")
                print(f"Nombre: {string3}")

                print()
    def removeQuotes(self, normalS):
        n = len(normalS)
        new_str = ""
        j = 0

        for i in range(n):
            if normalS[i] == '"':
                continue
            new_str += normalS[i]
            j += 1

        return new_str
    def make_mkdisk(self):
        print("[MKDISK] - Aqui")
        print("name:", self.name)
        print("path:", self.path)
        print("size:", self.size)
        print("unit:", self.unit)
        return self.crear_disco(self.size, self.path, self.unit, self.fit)


