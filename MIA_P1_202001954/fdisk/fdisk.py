import struct
from datetime import datetime
from functions.estructuras import MBR, EBR # potential error
from functions.estructuras import Particion
import os
import ctypes # potential error


def printEBRFile(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    unpacked_data = unpack_ebr(packed_data, start)
    send_data = ""
    print("-------EBR 1 ---------")
    send_data += "part_status->" + str(unpacked_data['part_status']) + "\n"
    print("part_status->" + str(unpacked_data['part_status']))
    send_data += "part_fit->" + str(unpacked_data['part_fit']) + "\n"
    print("part_fit->" + str(unpacked_data['part_fit']))
    send_data += "part_start->" + str(unpacked_data['part_start']) + "\n"
    print("part_start->" + str(unpacked_data['part_start']))
    send_data += "part_next->" + str(unpacked_data['part_next']) + "\n"
    print("part_next->" + str(int(unpacked_data['part_next'])))
    send_data += "part_size->" + str(unpacked_data['part_size']) + "\n"
    print("part_size->" + str(unpacked_data['part_size']))
    send_data += "part_name->" + str(unpacked_data['part_name']) + "\n"
    print("part_name->" + str(unpacked_data['part_name']))
    return send_data

def printMBRFile(definedPath):
    packed_data = read_packed_data_from_file(definedPath)

    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    print(unpacked_data)
    print("--------------")

def unpack_ebr1(packed_data, start):
    unpacked_ebr = {}
    ebr_format = "cciii16s"
    ebr_size = struct.calcsize(ebr_format)
    print("ebr_size->", end="")
    print(ebr_size)
    ebr_data = packed_data[start:start + ebr_size]

    # Unpack the data without padding
    unpacked_ebr['part_status'], unpacked_ebr['part_fit'], unpacked_ebr['part_start'], unpacked_ebr['part_size'], \
        unpacked_ebr['part_next'], unpacked_ebr['part_name'] = struct.unpack(ebr_format, ebr_data)

    return unpacked_ebr

class Superblock(ctypes.Structure):
    _fields_ = [
        ("s_filesystem_type", ctypes.c_char), #1
        ("s_inodes_count", ctypes.c_char),    #2
        ("s_blocks_count", ctypes.c_int),     #3
        ("s_free_blocks_count", ctypes.c_int),#4
        ("s_free_inodes_count", ctypes.c_int),#5
        ("s_mtime", ctypes.c_int),            #6
        ("s_umtime", ctypes.c_int),           #7
        ("s_mnt_count", ctypes.c_int),        #8
        ("s_magic", ctypes.c_int),            #9
        ("s_inode_s", ctypes.c_int),          #10
        ("s_block_s", ctypes.c_int),          #11
        ("s_first_ino", ctypes.c_int),        #12
        ("s_first_blo", ctypes.c_int),        #13
        ("s_bm_inode_start", ctypes.c_int),   #14
        ("s_bm_block_start", ctypes.c_int),   #15
        ("s_inode_start", ctypes.c_int),      #16
        ("s_block_start", ctypes.c_int),      #17
    ]
def unpack_ebr(packed_data, start):
    print("UNPACKING")
    print("start->", end="")
    print(start)
    print("packed_data->", end="")
    print(packed_data)
    unpacked_superblock = {}
    superblock_size = struct.calcsize("cciii16s")
    superblock_data = packed_data[start:start + superblock_size]
    unpacked_superblock = struct.unpack("cciii16s", superblock_data)

    # Create a dictionary with field names as keys
    field_names = [field[0] for field in EBR._fields_]
    unpacked_superblock = dict(zip(field_names, unpacked_superblock))
    print(unpacked_superblock)

    return unpacked_superblock



def unpack_ebrList(packed_data, start):
    ebr_list = []
    unpacked_ebr = {}
    ebr_size = struct.calcsize("cciii16s")
    ebr_data = packed_data[start:start + ebr_size]
    unpacked_ebr['part_status'], unpacked_ebr['part_fit'], unpacked_ebr['part_start'], unpacked_ebr[
        'part_size'],unpacked_ebr['part_next'], unpacked_ebr['part_name'] = struct.unpack("cciii16s", ebr_data)

    while(unpacked_ebr['part_next'] != -1):
        ebr_list.append(unpacked_ebr)
        start = unpacked_ebr['part_next']
        ebr_data = packed_data[start:start + ebr_size]
        unpacked_ebr['part_status'], unpacked_ebr['part_fit'], unpacked_ebr['part_start'], unpacked_ebr[
            'part_size'], unpacked_ebr['part_next'], unpacked_ebr['part_name'] = struct.unpack("cciii16s", ebr_data)
    return ebr_list




def unpack_mbr(packed_data):
    unpacked_mbr = {}

    mbr_size = struct.calcsize("iii1s")
    mbr_data = packed_data[:mbr_size] # cambio aqui
    unpacked_mbr['mbr_tamano'], unpacked_mbr['mbr_fecha_creacion'], unpacked_mbr['mbr_dsk_signature'], unpacked_mbr[
        'mbr_fit'] = struct.unpack("iii1s", mbr_data)

    unpacked_datetime = datetime.fromtimestamp(unpacked_mbr['mbr_fecha_creacion'])
    print(unpacked_datetime)
    partition_size = struct.calcsize("cccii16s" )
    unpacked_mbr['mbr_particiones'] = []
    partition_data = packed_data[mbr_size:]
    # aqui puede existir un problema pues -> las particiones son variables
    num_partitions = len(partition_data) // partition_size



    for i in range(num_partitions):
        partition_start = i * partition_size
        partition_end = partition_start + partition_size
        partition = struct.unpack("cccii16s" , partition_data[partition_start:partition_end])
        unpacked_mbr['mbr_particiones'].append(partition)

    return unpacked_mbr



# Recibido From File

def read_packed_data_from_file( file_path):
    # Aqui puede estar el error, porque se le envia ".."
    print(file_path)
    with open(file_path, 'rb') as file:
        file.seek(0)
        packed_data = file.read()

    return packed_data


def getMBR(definedPath):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    return unpacked_data
def getEBR(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    unpacked_data = unpack_ebr(packed_data, start)
    print("-------EBR 1 ---------")
    print("part_status->" + str(unpacked_data['part_status']))
    print("part_fit->" + str(unpacked_data['part_fit']))
    print("part_start->" + str(unpacked_data['part_start']))
    print("part_next->" + str(unpacked_data['part_next']))
    print("part_size->" + str(unpacked_data['part_size']))
    return unpacked_data

def getEBRlist(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    ebr_list = unpack_ebrList(packed_data, start)
    for unpacked_data in ebr_list:
        print("-------EBR 1 ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
    return ebr_list

def printEBRlist(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    ebr_list = unpack_ebrList(packed_data, start)
    for unpacked_data in ebr_list:
        print("-------EBR 1 ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
    #return ebr_list
class FDisk:
    def __init__(self):
        self.size = 0
        self.path = ""
        self.name = ""
        self.unit = "K"
        self.type = "P"
        self.fit = "W"
        self.start = -1
        self.add = 0
        self.addValue = "0"
        self.deleteValue = "null"
        self.delete = 0
    def fdisk(self):
        print("======== Format Disk =========")
        # Existencia Archivo
        if os.path.exists("." + self.path):
            self.checkVariables()
        else:
            print("- Path No Existente")
            return "Path No Existente"

    def checkVariables(self):
        # Lectura de Datos Usuario y Chequeos iniciales
        if self.add == 1:
            print("[+++++++++++ADD++++++++++++++]")
            if self.unit.lower() == "k":
                self.addValue = int(self.addValue) * 1024
            elif self.unit.lower() == "m":
                self.addValue = int(self.addValue) * 1024 * 1024

            print("-> " + str(self.addValue))
            self.addParticion()
        elif self.delete == 1:
            print("[-------------DELETE-----------]")
            if self.unit.lower() == "k":
                self.addValue = int(self.addValue) * 1024
            elif self.unit.lower() == "m":
                self.addValue = int(self.addValue) * 1024 * 1024

            return self.deleteParticion()
        else:
            return self.createParticion()

    def createParticion(self):
        print("Create Particion")
        # Leemos MBR e instanciamos MBR
        print("." + self.path)
        mbr = getMBR("." + self.path)  # diccionario
        mbr_written = MBR()
        # ailsamos los datos del MBR
        print(mbr)
        # Pre-chequeo
        print("TYPE --> ", end="")
        print(self.type.lower())
        if mbr['mbr_fit'] == b'F' and self.validate_names_status_extended(mbr):
            print("FF ")
            if(self.type.lower() == 'l'):

                if(self.existsExtended(mbr)):
                    print("EXISTE EXTENDIDA.")
                    return self.insert_logic(mbr_written, mbr)
                else:
                    print("\x1b[32mError: No hay particion extendida\x1b[0m")
                    return "Error: No hay particion extendida"

            else:
                return self.first_fit(mbr_written, mbr)
        elif mbr['mbr_fit'] == b'B' and self.validate_names_status_extended(mbr):
            print("BF")
            if (self.type.lower() == 'l'):
                if (self.existsExtended(mbr)):
                    return self.insert_logic(mbr_written, mbr)
                else:
                    print("No hay particion extendida")
            else:
                return self.best_fit(mbr_written, mbr)

        elif mbr['mbr_fit'] == b'W' and self.validate_names_status_extended(mbr):
            print("BF")
            if (self.type.lower() == 'l'):
                if (self.existsExtended(mbr)):
                    return self.insert_logic(mbr_written, mbr)
                else:
                    print("No hay particion extendida")
            else:
                return self.worst_fit(mbr_written, mbr)
        else:
            print("\x1b[93mError-> No existen Particiones Vacias\x1b[0m")
            return "Error-> No existen Particiones Vacias"

    ##
    def validate_names_status_extended(self, mbr) -> bool:
        print("validacion errores -> create")
        particiones = mbr['mbr_particiones']
        flagNotName = True
        flagNotPart = True
        flagNotExtendida = True

        for i in range(0, 4):
            # En las particiones buscamos
            # Como son tuplas (no podemos acceder a distintas formas
            # particiones[i].get('name')
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][5].decode().rstrip('\x00').lower() == self.name.lower():
                # Aca se debe borrar la particion
                print("Nombre ya utilizado")
                flagNotName = False

            # particiones[i].get('status')
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            print(particiones[i][0].decode("utf-8"))

            # PARTICION VACIA (SIEMPRE)
            if particiones[i][0] == b'0':
                # verificamos que hayan particiones vacias
                print("particiones" + str(i) + "->vacia")
                flagNotPart = False

            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][1] == b'E' and self.type.lower() == 'e':
                # Si ya hay extendida Y se desea ingresar una extendida
                print("particiones" + str(i) + "->extendida")
                flagNotExtendida = False

            if self.type.lower() == 'l':
                # Si es logica, no nos importa la cantidad de particiones libres
                flagNotPart = False

        print("flagNotName->" + str(flagNotName))
        print("flagNotPart->" + str(not flagNotPart))
        print("flagNotExt->" + str(flagNotExtendida))

        return flagNotName and (not flagNotPart) and flagNotExtendida

    def particionExtendida(self, mbr) -> int:
        print("validacion errores -> create")
        j = 0
        particiones = mbr['mbr_particiones']
        for i in range(0, 4):
            # vemos particiones extendidas
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][1] == b'E':
                # Si ya hay extendida Y se desea ingresar una extendida
                print("particiones" + str(i) + "->extendida")
                j = i

        return j

    def existsExtended(self, mbr) -> bool:
        print("validacion errores -> create")
        flagNotExtendida = False
        particiones = mbr['mbr_particiones']
        for i in range(0, 4):
            # vemos particiones extendidas
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][1] == b'E':
                # Si ya hay extendida Y se desea ingresar una extendida
                print("particiones" + str(i) + "->extendida")
                flagNotExtendida = True

        return flagNotExtendida


    def deleteParticion(self):
        print("init full->")
        print(self.deleteValue.capitalize())
        if self.deleteValue.lower() == "full":
            print("Delete Particion")
            # Leemos MBR e instanciamos MBR
            mbr = getMBR("." + self.path)  # diccionario
            mbr_written = MBR() # objeto MBR
            # ailsamos los datos del MBR
            print(mbr)
            print("delete")
            # recorremos las particiones en busca de errores
            particiones = mbr['mbr_particiones']
            notCreatedFlag = True
            # Valores comparativos
            menor_diferencia_actual = "-1"
            particion_actual = 5  # inicializa con 5 para detectar errores
            for i in range(0, 4):
                # En las particiones buscamos
                # status -0, type -1 , fit -2, start -3, size -4, name -5
                print(particiones[i][5].decode("utf-8").rstrip('\x00'))
                print(self.name)
                if particiones[i][5].decode("utf-8").rstrip('\x00').lower() == self.name.lower() and notCreatedFlag == True:
                    print("<<>>")
                    # Aca se debe borrar la particion
                    # status -0, type -1 , fit -2, start -3, size -4, name -5
                    # le envio el start de la particion actual y el size actual
                    self.full(int(particiones[i][3]), int(particiones[i][4]))
                    # Significa que debemos hacer un 'reset' en esta particion
                    mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
                    mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
                    mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
                    mbr_written.mbr_fit = mbr['mbr_fit']
                    # Deberia de poner donde empieza?
                    self.type = b'-1'
                    self.fit  = b'W'
                    self.start  = -1
                    self.size = 1
                    self.name = "null"
                    nullName = "null"
                    # 3. Vaciamos el espacio de la particion

                    # 2. Cambiar los datos de las particiones
                    particion_insertar = Particion(b'0',
                                                   b'0',
                                                   self.fit,
                                                   int(self.start),
                                                   int(self.size),
                                                   nullName.encode("utf-8"))

                    particion_insertar.start = -1
                    # Escribimos Particion en MBR
                    mbr_written.mbr_particiones[i] = particion_insertar

                    # Packing Data
                    packedMBR = struct.pack("iii1s",
                                            mbr_written.mbr_tamano,
                                            mbr_written.mbr_fecha_creacion,
                                            mbr_written.mbr_dsk_signature,
                                            mbr_written.mbr_fit)
                    j = 0
                    for particion in mbr['mbr_particiones']:
                        if j == i:
                            packedMBR += struct.pack("cccii16s",

                                                     particion_insertar.part_status,
                                                     particion_insertar.part_type,
                                                     particion_insertar.part_fit,
                                                     particion_insertar.part_start,
                                                     particion_insertar.part_size,
                                                     particion_insertar.part_name)
                        else:  # Si no, escribimos lo que ya estaba en el MBR
                            packedMBR += struct.pack("cccii16s",
                                                     # status -0, type -1 , fit -2, start -3, size -4, name -5
                                                     particiones[j][0],
                                                     particiones[j][1],
                                                     particiones[j][2],
                                                     int(particiones[j][3]),
                                                     int(particiones[j][4]),
                                                     particiones[j][5])
                        j = j + 1

                    # Ya se escribio Particion a MBR
                    # Escribimos MBR en Archivo
                    # potencial error (comillas)
                    print(self.path)
                    archivo = open("." + self.path, "wb")
                    archivo.write(packedMBR)
                    archivo.close()
                    notCreatedFlag = False



            print("-No se encontro la particion") if notCreatedFlag else print("done")
            return "No se encontro la particion" if notCreatedFlag else "************ Particion Eliminada ************"
            if notCreatedFlag:
                return "No se encontro la particion"
            else:
                return "************ Particion Eliminada ************"
        else:
            print("-- FULL no fue escrito")
            return "FULL no fue escrito"


    def full(self, start, size):
        print("start->", end="")
        print(start)
        print("size->", end="")
        print(size)
        print("-init full")
        archivo = open("." + self.path, "wb+")
        archivo.seek(int(start))
        archivo.write(b'\x00' * int(size))
        archivo.close()
    def addParticion(self):
        print("ADD Particion")
        # Leemos MBR e instanciamos MBR
        mbr = getMBR("." + self.path)  # diccionario
        mbr_written = MBR()  # objeto MBR
        # ailsamos los datos del MBR
        print(mbr)
        print("ADD")
        # recorremos las particiones en busca de errores
        particiones = mbr['mbr_particiones']
        for i in range(0, 4):
            # particiones[i].get('name')
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            print(particiones[i][5].decode("utf-8").rstrip("\x00").lower())
            if particiones[i][5].decode("utf-8").rstrip("\x00").lower() == self.name.lower():
                print("Particion Encontrada")
                # Aca se puede agregar
                if int(self.addValue) > 0:
                    print("mayor")
                    # Si es mayor, entonces, debemos checar el espacio hacia la derecha
                    comodin = 0
                    if i < 3:
                        comodin = i + 1
                    else:
                        comodin = i
                    # status -0, type -1 , fit -2, start -3, size -4, name -5
                    if (int(particiones[comodin][3]) - (int(particiones[i][3]) + int(particiones[i][4])) > int(self.addValue))  or (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])) > int(self.addValue))):
                        # Entonces, se puede ejecutar la accion
                        print("ejecutar la accion")
                        # La accion es sumarle el valor self.value a self.size y agregarlo
                        # Pasamos los valores a la nueva Particion
                        # Significa que debemos hacer un 'reset' en esta particion
                        mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
                        mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
                        mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
                        mbr_written.mbr_fit = mbr['mbr_fit']
                        # Cambiamos la Particion a Insertar
                        # buscamos la particion actual
                        # particiones[i].get('name')
                        # status -0, type -1 , fit -2, start -3, size -4, name -5
                        particion_agregada = Particion(b'1',
                                                       int(particiones[i][1]), #type
                                                       particiones[i][2], #fit
                                                       particiones[i][3], #start
                                                       int(particiones[i][4]) + int(self.addValue), #size
                                                       particiones[i][5]) #name

                        # Ahora escribimos en el MBR
                        mbr_written.mbr_particiones[i] = particion_agregada

                        # Packing Data
                        packedMBR = struct.pack("iii1s",
                                                mbr_written.mbr_tamano,
                                                mbr_written.mbr.mbr_fecha_creacion,
                                                mbr_written.mbr_dsk_signature,
                                                mbr_written.mbr_fit)

                        j = 0
                        for particion in mbr['mbr_particiones']:
                            if j == i:
                                packedMBR += struct.pack("cccii16s",
                                                         particion_agregada.part_status,
                                                         particion_agregada.part_type,
                                                         particion_agregada.part_fit,
                                                         particion_agregada.part_start,
                                                         particion_agregada.part_size,
                                                         particion_agregada.part_name)
                            else:  # Si no, escribimos lo que ya estaba en el MBR
                                # particiones[i].get('name')
                                # status -0, type -1 , fit -2, start -3, size -4, name -5
                                packedMBR += struct.pack("cccii16s",
                                                         particiones[j][0], # status
                                                         particiones[j][1], # type
                                                         particiones[j][2], # fit
                                                         int(particiones[j][3]), # start
                                                         int(particiones[j][4]), # size
                                                         particiones[j][5]) # name
                            j = j + 1

                        # Ahora escribimos al archivo
                        print(self.path)
                        archivo = open("." + self.path, "wb")
                        archivo.write(packedMBR)
                        archivo.close()

                    else:
                        print("No se puede Ejecutar la accion porque no hay espacio")
                        print("Se quieren insertar-> "+ str(self.addValue) )



                elif int(self.addValue) < 0:
                    print("Menor")
                    # particiones[i].get('name')
                    # status -0, type -1 , fit -2, start -3, size -4, name -5
                    # particiones[i].get('name')
                    # int(particiones[i]['size']) > abs(int(self.size)) and int(particiones[i]['size']
                    print("DATOS --> ")
                    print(int(particiones[i][4]))
                    print(abs(int(self.addValue)))
                    if (int(particiones[i][4]) > abs(int(self.addValue)) and int(particiones[i][4]) != -1):
                        # entonces puedo hacer la accion
                        print("")
                        # Entonces, se puede ejecutar la accion
                        print("ejecutar la accion")
                        # La accion es sumarle el valor self.value a self.size y agregarlo
                        # Pasamos los valores a la nueva Particion
                        # Significa que debemos hacer un 'reset' en esta particion
                        mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
                        mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
                        mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
                        mbr_written.mbr_fit = mbr['mbr_fit']
                        # Cambiamos la Particion a Insertar
                        # buscamos la particion actual
                        particion_agregada = Particion(b'1',
                                                       # particiones[i].get('name')
                                                       # status -0, type -1 , fit -2, start -3, size -4, name -5
                                                       particiones[i][1],# type
                                                       particiones[i][2],#fit
                                                       particiones[i][3],#start
                                                       int(particiones[i][4]) + int(self.addValue), # size
                                                       particiones[i][5]) # name

                        # Ahora escribimos en el MBR
                        mbr_written.mbr_particiones[i] = particion_agregada

                        # Packing Data
                        packedMBR = struct.pack("iii1s",
                                                mbr_written.mbr_tamano,
                                                mbr_written.mbr_fecha_creacion,
                                                mbr_written.mbr_dsk_signature,
                                                mbr_written.mbr_fit)

                        j = 0
                        for particion in mbr['mbr_particiones']:
                            if j == i:
                                packedMBR += struct.pack("cccii16s",
                                                         particion_agregada.part_status,
                                                         particion_agregada.part_type,
                                                         particion_agregada.part_fit,
                                                         particion_agregada.part_start,
                                                         particion_agregada.part_size,
                                                         particion_agregada.part_name)
                            else:  # Si no, escribimos lo que ya estaba en el MBR
                                packedMBR += struct.pack("cccii16s",
                                                         # particiones[i].get('name')
                                                         # status -0, type -1 , fit -2, start -3, size -4, name -5
                                                         particiones[j][0],
                                                         particiones[j][1],
                                                         particiones[j][2],
                                                         int(particiones[j][3]),
                                                         int(particiones[j][4]),
                                                         particiones[j][5])
                            j = j + 1

                        # Ahora escribimos al archivo
                        print(self.path)
                        archivo = open("." + self.path, "wb")
                        archivo.write(packedMBR)
                        archivo.close()
                        print("ejecutar la accion")
                    else:
                        print("NO es posible la accion por el tamano de 'add' ")

                else:
                    # Si es igual, no hacemos nada
                    print("no se ha agregado nada")




    def best_fit(self, mbr_written: MBR, mbr):
        print("best fit")
        # recorremos las particiones en busca de errores
        particiones = mbr['mbr_particiones']
        notCreatedFlag = True
        # Valores comparativos
        menor_diferencia_actual = "-1"
        particion_actual = 5 # inicializa con 5 para detectar errores
        for i in range(0, 4):
            # En las particiones buscamos
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][0] == b'0' and notCreatedFlag:
               # print("- PARTICION" + str(i) + "VACIA")
                # Reviso cuanto espacio tengo a la derecha
                # status -0, type -1 , fit -2, start -3, size -4, name -5
                comodinParticion = 0
                if(i == 3):
                    comodinParticion = i
                else:
                    comodinParticion = i + 1

                if self.unit.lower() == "k":
                    self.size = self.size * 1024
                elif self.unit.lower() == "m":
                    self.size = self.size * 1024 * 1024
                # Debemos establacer el caso del la particion numero 3
                #print("comparativa de valores")
                #print("particion[i+1][3] - particiones[i][3]" + str(int(particiones[comodinParticion][3]) - int(particiones[i][3])))
                #print(str(self.size))
                if (((int(particiones[comodinParticion][3]) - int(particiones[i][3]) > self.size) and i < 3) or
                        ((int(particiones[i][3]) == -1) and (int(particiones[comodinParticion][3]) == -1)) or
                        (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])) > self.size))):
                    # sabemos que aqui hay un espacio en donde "podria entrar" asi que
                    #print(str(i) + "-> Espacio Suficiente")
                    if menor_diferencia_actual == "-1" or (menor_diferencia_actual > int(particiones[comodinParticion][3]) - int(particiones[i][3])) or (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])) < menor_diferencia_actual)):
                        # si es mayor, la actualizamos
                        if(i < 3):
                            menor_diferencia_actual = int(particiones[i + 1][3]) - int(particiones[i][3])
                            particion_actual = i
                            notCreatedFlag = False
                            #print("MENOR_DIFERENCIA ->" + str(particion_actual))
                        elif(i == 3):
                            menor_diferencia_actual = int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])
                            particion_actual = i
                            notCreatedFlag = False
                            #print("->" + str(particion_actual))



        # Si si hay espacio, entonces puedo proceder a crear la particion
        # Con "Crear" la particion, me refiero a apartar el espacio en MBR
        # Cambiamos mbr_written (Que es el mbr que el que escribiremos)
        # Primero -> Buscamos la particion i
        # Idea: 1. Bajar los datos del MBR leido
        mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
        mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
        mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
        mbr_written.mbr_fit = mbr['mbr_fit']
        if particion_actual == 0:
            #print("potencial error -- linea 396 fdisk")
            self.start = 128 + 1  # Verificar Luego
        else:
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            # print("Se escribe a particion actual -> " + str(particion_actual))
            self.start = particiones[particion_actual - 1][3] + 1
        # 2. Cambiar los datos de las particiones
        particion_insertar = Particion(b'1',
                                       self.type.encode("utf-8"),
                                       self.fit.encode("utf-8"),
                                       int(self.start),
                                       int(self.size),
                                       self.name.encode("utf-8"))

        # Escribimos Particion en MBR
        mbr_written.mbr_particiones[particion_actual] = particion_insertar

        # Packing Data
        packedMBR = struct.pack("iii1s",
                                mbr_written.mbr_tamano,
                                mbr_written.mbr_fecha_creacion,
                                mbr_written.mbr_dsk_signature,
                                mbr_written.mbr_fit)
        j = 0
        for particion in mbr['mbr_particiones']:
            if j == particion_actual:
                #print("packed in mbr ")
                packedMBR += struct.pack("cccii16s",
                                         particion_insertar.part_status,
                                         particion_insertar.part_type,
                                         particion_insertar.part_fit,
                                         particion_insertar.part_start,
                                         particion_insertar.part_size,
                                         particion_insertar.part_name)
            else:  # Si no, escribimos lo que ya estaba en el MBR
                packedMBR += struct.pack("cccii16s",
                                         # status -0, type -1 , fit -2, start -3, size -4, name -5
                                         particiones[j][0],
                                         particiones[j][1],
                                         particiones[j][2],
                                         int(particiones[j][3]),
                                         int(particiones[j][4]),
                                         particiones[j][5])
            j = j + 1

        # Ya se escribio Particion a MBR
        # Escribimos MBR en Archivo
        # potencial error (comillas)
        #print(self.path)
        #print("se escribe en archivo -- ")
        archivo = open("." + self.path, "wb+")
        archivo.write(packedMBR)
        archivo.close()
        #print("_____ REPORTE MBR ____ " + "." + self.path)
        #printMBRFile("." + self.path)
        # Aca debemos hacer el reporte
        # Si era particion extendida, ahora debemos escribir el EBR
        if (self.type.lower() == 'e'):
            # Creamos un objeto EBR
            #print("AQUI -0 EBR")
            ebr = EBR()
            ebr.ebr_status = b'1'
            ebr.ebr_fit = self.fit.encode()
            ebr.ebr_next = -1
            ebr.ebr_start = self.start + ctypes.sizeof(EBR) # Start de la particion logica
            ebr.ebr_size = -1
            ebr.ebr_name = self.name.encode()

            # empacamos en binario EBR
            # Ahora escribimos el EBR
            packedEBR = struct.pack("cciii16s",
                                    ebr.ebr_status,
                                    ebr.ebr_fit,
                                    ebr.ebr_start,
                                    ebr.ebr_size,
                                    ebr.ebr_next,
                                    ebr.ebr_name)



            print("*********************************************")
            print("*************ESCRITURA EBR 0 *******************")
            print("path->" + "." + self.path)
            print("start->" + str(self.start))
            print("size->" + str(self.size))
            print("name->" + str(self.name))
            print("*********************************************")
            #printMBRFile("." + self.path)
            with open("." + self.path, "rb+") as newFile:
                print("SEEK-> " + str(self.start))
                newFile.seek(int(self.start), 0)
                newFile.write(packedEBR)
                newFile.close()

            print("EBR CREADO")
            print("reporte mbr ->" + "." + self.path)
            printMBRFile("." + self.path)
            print("EBR CREADO")
            print("=============EBR CREADO========")
            print("getEBR Call -> " + str(self.start))
            print("getEBR Call -> " + str(self.path))
            print("start->" + str(self.start))
            print("path->" + str(self.path))
            printEBRFile("." + self.path, int(self.start))


        #print("-No hay suficiente espacio") if notCreatedFlag else print("done")

    def insert_logic(self, mbr_written: MBR, mbr):
        print("\033[1;35m*****PARTICION LOGICA*****\033[0m")

        # recorremos las particiones en busca de errores
        particiones = mbr['mbr_particiones']
        particion_actual = self.particionExtendida(mbr)

        printEBRFile("." + self.path, int(particiones[particion_actual][3]))
        ebr_inicial = getEBR("." + self.path, int(particiones[particion_actual][3])) # diccionario
        ebr_written = EBR() # objeto EBR

        # VALORES COMPARATIVOS
        print()
        print("############################")
        print("size->" + str(ebr_inicial['part_size']))
        print("start real -> " + str(int(particiones[particion_actual][3])))
        print("start virtual -> " + str(ebr_inicial['part_start']))
        print("next -> " + str(ebr_inicial['part_next']))
        print("############################")
        print()

        recorridoEBR = 0
        espacioUtilizado = ctypes.sizeof(EBR)
        print("L" + str(recorridoEBR) + " -> ", end="")
        while(int(ebr_inicial['part_next']) != -1):
            recorridoEBR +=1
            print("L" + str(recorridoEBR) + " -> ", end="")
            ebr_inicial = getEBR("." + self.path, int(ebr_inicial['part_next']))
            espacioUtilizado += int(ebr_inicial['part_size'])

        # status -0, type -1 , fit -2, start -3, size -4, name -5
        # para este caso tenemos 2 situaciones
        # 1- si se inserta de primero (para lo cual hay 1 solo EBR)
        # 2- si se inserta de ultimo (para lo cual hay n EBR)

        # COMPARCION
        # P[___________] -
        print("^^^^^^^^^^^^^^^^^^")
        print("espacioUtilizado->" + str(espacioUtilizado))
        print((int(particiones[particion_actual][4])))

        if((((int(particiones[particion_actual][4]) - espacioUtilizado > int(self.size) + ctypes.sizeof(EBR)) and recorridoEBR > 0)
            or  # insercion para 1 caso
             (((int(particiones[particion_actual][4]) - espacioUtilizado) > int(self.size)) and recorridoEBR == 0))): # insercion para n casos

            # si es la primera, se cambia el EBR inicial y se agrega uno despues
            # si es la n, se cambia el EBR final y se agrega uno despues
            if recorridoEBR == 0:
                print("[++++++++++++++++++++++++++++++++++++++++++++++++++]")
                print("[ ESCRITURA DE EBR LUEGO DE 1 PASO                ]")
                print("[++++++++++++++++++++++++++++++++++++++++++++++++++]")

                # --------------------------------------
                # Actualmente el archivo se encuentra asi
                # Input -> [[MBR] P [[EBR nulo]____________]]
                # Esta operacion busca llevarlo a esta forma
                # Output -> P [[EBR util ]_____]
                ebr = EBR()
                ebr.ebr_status = b'1'
                ebr.ebr_fit = self.fit.encode()
                print("value->" + str(int(ebr_inicial['part_start']) + self.size))
                ebr.ebr_next = int(ebr_inicial['part_start']) + self.size
                ebr.ebr_start = int(ebr_inicial['part_start'])
                ebr.ebr_size = self.size
                ebr.ebr_name = self.name.encode()
                packedEBR = struct.pack("cciii16s",
                                        ebr.ebr_status,
                                        ebr.ebr_fit,
                                        ebr.ebr_start,
                                        ebr.ebr_size,
                                        int(ebr.ebr_next),
                                        ebr.ebr_name)

                print("*** Escribiendo EBR1 -> util ****")
                print("start virtual->" + str(ebr.ebr_start))
                print("start real->" + str(ebr.ebr_start - ctypes.sizeof(EBR)))
                print("next->" + str(ebr.ebr_next))
                print("size->" + str(ebr.ebr_size))
                print("path-> " + "." + self.path)
                print("************************************")
                archivo = open("." + self.path, "rb+")
                archivo.seek(0)
                archivo.seek(int(ebr_inicial['part_start']) - ctypes.sizeof(EBR), 0)
                archivo.write(packedEBR)
                archivo.close()




                # Input -> [[MBR] P [ [EBR valor ]____________]]
                # EBR null ->
                # Esta operacion busca llevarlo a esta forma
                # Output -> P [ [EBR valor ]_____[EBR null con next valido] ]
                ebr = EBR()
                ebr.ebr_status = b'0'
                ebr.ebr_fit = b'W'
                ebr.ebr_next = -1
                ebr.ebr_start = int(ebr_inicial['part_start']) + self.size
                ebr.ebr_size = 0
                ebr.ebr_name = "empty"
                # Ahora escribimos el EBR
                packedEBR = struct.pack("cciii16s",
                                        ebr.ebr_status,
                                        ebr.ebr_fit,
                                        ebr.ebr_start,
                                        ebr.ebr_size,
                                        ebr.ebr_next,
                                        ebr.ebr_name.encode())
                print("*** Escribiendo EBR null nuevo ****")
                print("start->" + str(ebr.ebr_start))
                print("next->" + str(ebr.ebr_next))
                print("size->" + str(ebr.ebr_size))
                print("path-> " + "." + self.path)
                print("************************************")
                archivo = open("." + self.path, "rb+")
                archivo.seek(0)
                archivo.seek(ebr.ebr_start)
                archivo.write(packedEBR)
                archivo.close()
                # Operacion terminada

                # @ Unit Test EBR 1
                print("........... UNIT TESTS ..........")
                print("<< EBR INICIAL >> ")
                print("---- // comp values // --  ")
                print("start->" + str(ebr_inicial['part_start'] - ctypes.sizeof(EBR)))
                print("size->" + str(self.size))
                print("path-> " + "." + self.path)
                print("---- // // // // //  // --  ")
                printEBRFile("." + self.path, int(ebr_inicial['part_start']) - ctypes.sizeof((EBR)))

                # @ Unit Test EBR 2
                print("<< EBR NULO >> ")
                print("---- // comp values // --  ")
                print("start->" + str(ebr_inicial['part_start']) + str(self.size))
                print("size->" + str(int(-1)))
                print("path-> " + "." + self.path)
                print("---- // // // // // //  // --  ")
                return printEBRFile("." + self.path, int(ebr_inicial['part_start']) + self.size)


            else:
                print("[////////////////////////////////////////////////]")
                print("[ ESCRITURA DE EBR LUEGO DE n PASOS")
                print("[////////////////////////////////////////////////]")
                print("[//// VALORES ULTIMO EBR ////////////////////////]")
                print("start->" + str(ebr_inicial['part_start']))
                print("size->" + str(ebr_inicial['part_size']))
                print("next->" + str(ebr_inicial['part_next']))
                print("[////////////////////////////////////////////////]")
                # ERROR AQUI  escritura de n particiones logicas
                # --------------------------------------
                # Actualmente el archivo se encuentra asi
                # Input -> [[MBR] P [[EBR util]____[EBR inicial null n ]  ]]
                # Esta operacion busca llevarlo a esta forma
                # Output -> P [[EBR util ]_____[EBR util n ]]
                ebr = EBR()
                ebr.ebr_status = b'1'
                ebr.ebr_fit = self.fit.encode()
                ebr.ebr_next = int(ebr_inicial['part_start']) + int(self.size)
                ebr.ebr_start = int(ebr_inicial['part_start'])
                ebr.ebr_size = self.size
                ebr.ebr_name = self.name.encode()
                packedEBR = struct.pack("cciii16s",
                                        ebr.ebr_status,
                                        ebr.ebr_fit,
                                        ebr.ebr_start,
                                        ebr.ebr_size,
                                        ebr.ebr_next,
                                        ebr.ebr_name)

                print("*** Escribiendo EBR util nuevo ****")
                print("start->" + str(ebr.ebr_start))
                print("size->" + str(ebr.ebr_size))
                print("path-> " + "." + self.path)
                print("************************************")
                archivo = open("." + self.path, "rb+")
                archivo.seek(0)
                archivo.seek(int(ebr_inicial['part_start']), 0)
                archivo.write(packedEBR)
                archivo.close()

                # Actualmente el archivo se encuentra asi
                # Input -> [[MBR] P [[EBR util]____[EBR inicial util n ]]]
                # Esta operacion busca llevarlo a esta forma
                # Output -> P [[EBR util ]_____[EBR util n ]_____ [EBR null n+1]]
                ebr = EBR()
                ebr.ebr_status = b'0'
                ebr.ebr_fit = b'W'
                ebr.ebr_next = -1
                ebr.ebr_start = int(ebr_inicial['part_start']) + int(self.size)
                ebr.ebr_size = 0
                ebr.ebr_name = "empty"
                packedEBR = struct.pack("cciii16s",
                                        ebr.ebr_status,
                                        ebr.ebr_fit,
                                        ebr.ebr_start,
                                        ebr.ebr_size,
                                        ebr.ebr_next,
                                        ebr.ebr_name.encode())
                archivo = open("." + self.path, "rb+")
                archivo.seek(0)
                archivo.seek(int(ebr_inicial['part_start']) + int(self.size), 0)
                archivo.write(packedEBR)
                archivo.close()

                # @ unit test ebr 1
                print("........... UNIT TESTS ..........")
                print("<< EBR INICIAL >> ")
                print("---- // comp values // --  ")
                print("start->" + str(ebr_inicial['part_start']))
                print("size->" + str(self.size))
                print("path-> " + "." + self.path)
                print("---- // // // // //  // --  ")
                printEBRFile("." + self.path, int(ebr_inicial['part_start']))

                # @ unit test ebr 2
                print("........... UNIT TESTS ..........")
                print("<< EBR INICIAL >> ")
                print("---- // comp values // --  ")
                print("start->" + str(ebr_inicial['part_start']))
                print("size->" + str(self.size))
                print("path-> " + "." + self.path)
                print("---- // // // // //  // --  ")
                printEBRFile("." + self.path, int(ebr_inicial['part_start']) + self.size)


                # @ unit test ebr list
                print("........... UNIT TESTS ..........")
                print("<< EBR INICIAL >> ")
                print("---- // comp values // --  ")
                print("start->" + str(ebr_inicial['part_start']))
                print("size->" + str(self.size))
                print("path-> " + "." + self.path)
                print("---- // // // // //  // --  ")
                printEBRFile("." + self.path, int(ebr_inicial['part_start']) + self.size)
                return "*********** LOGICA INSERTADA *******************"
        else:
            print("\x1b[93mno hay espacio\x1b[0m" + " hay -> " + str(int(ebr_inicial['part_start']) + int(ebr_inicial['part_size']) ))
            print("y se quieren insertar " +  str(self.size))
            return "\x1b[93mno hay espacio\x1b[0m" + " hay -> " + str(int(ebr_inicial['part_start']) + int(ebr_inicial['part_size']) ) + " y se quieren insertar " +  str(self.size)






        #print("-No hay suficiente espacio") if notCreatedFlag else print("done")


    def addEBR(self, start):
        # en este metodo se agrega el EBR
        print("addEBR")
        # Leemos MBR e instanciamos MBR
        mbr = getMBR("." + self.path)  # diccionario
        mbr_written = MBR()  # objeto MBR
        # ailsamos los datos del MBR
        print(mbr)
        print("ADD")
        # recorremos las particiones en busca de errores



    def worst_fit(self, mbr_written: MBR, mbr):
        print("best fit")
        # recorremos las particiones en busca de errores
        particiones = mbr['mbr_particiones']
        notCreatedFlag = True
        # Valores comparativos
        mayor_diferencia_actual = "-1"
        particion_actual = 5 # inicializa con 5 para detectar errores
        for i in range(0, 4):
            # En las particiones buscamos
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if particiones[i][0] == b'0' and notCreatedFlag:
                print("- PARTICION" + str(i) + "VACIA")
                # Reviso cuanto espacio tengo a la derecha
                # status -0, type -1 , fit -2, start -3, size -4, name -5
                comodinParticion = 0
                if(i == 3):
                    comodinParticion = i
                else:
                    comodinParticion = i + 1

                if self.unit.lower() == "k":
                    self.size = self.size * 1024
                elif self.unit.lower() == "m":
                    self.size = self.size * 1024 * 1024
                # Debemos establacer el caso del la particion numero 3
                print("comparativa de valores")
                print("particion[i+1][3] - particiones[i][3]" + str(int(particiones[comodinParticion][3]) - int(particiones[i][3])))
                print(str(self.size))
                if (((int(particiones[comodinParticion][3]) - int(particiones[i][3]) > self.size) and i < 3) or
                        ((int(particiones[i][3]) == -1) and (int(particiones[comodinParticion][3]) == -1)) or
                        (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])) > self.size))):
                    # sabemos que aqui hay un espacio en donde "podria entrar" asi que
                    print(str(i) + "-> Espacio Suficiente")
                    if mayor_diferencia_actual == "-1" or (mayor_diferencia_actual < int(particiones[comodinParticion][3]) - int(particiones[i][3])) or (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])) > mayor_diferencia_actual)):
                        # si es mayor, la actualizamos
                        if(i < 3):
                            mayor_diferencia_actual = int(particiones[i + 1][3]) - int(particiones[i][3])
                            particion_actual = i
                            notCreatedFlag = False
                            print("MENOR_DIFERENCIA ->" + str(particion_actual))
                        elif(i == 3):
                            mayor_diferencia_actual = int(mbr['mbr_tamano']) - int(particiones[i-1][3]) - int(particiones[i-1][4])
                            particion_actual = i
                            notCreatedFlag = False
                            print("->" + str(particion_actual))



        # Si si hay espacio, entonces puedo proceder a crear la particion
        # Con "Crear" la particion, me refiero a apartar el espacio en MBR
        # Cambiamos mbr_written (Que es el mbr que el que escribiremos)
        # Primero -> Buscamos la particion i
        # Idea: 1. Bajar los datos del MBR leido
        mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
        mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
        mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
        mbr_written.mbr_fit = mbr['mbr_fit']
        if particion_actual == 0:
            print("potencial error -- linea 396 fdisk")
            self.start = 128 + 1  # Verificar Luego
        else:
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            print("Se escribe a particion actual -> " + str(particion_actual))
            self.start = particiones[particion_actual - 1][3] + 1
        # 2. Cambiar los datos de las particiones
        particion_insertar = Particion(b'1',
                                       self.type.encode(),
                                       self.fit.encode(),
                                       int(self.start),
                                       int(self.size),
                                       self.name.encode())

        # Escribimos Particion en MBR
        mbr_written.mbr_particiones[particion_actual] = particion_insertar

        # Packing Data
        packedMBR = struct.pack("iii1s",
                                mbr_written.mbr_tamano,
                                mbr_written.mbr_fecha_creacion,
                                mbr_written.mbr_dsk_signature,
                                mbr_written.mbr_fit)
        j = 0
        for particion in mbr['mbr_particiones']:
            if j == particion_actual:
                print("packed in mbr ")
                packedMBR += struct.pack("cccii16s",
                                         particion_insertar.part_status,
                                         particion_insertar.part_type,
                                         particion_insertar.part_fit,
                                         particion_insertar.part_start,
                                         particion_insertar.part_size,
                                         particion_insertar.part_name)
            else:  # Si no, escribimos lo que ya estaba en el MBR
                packedMBR += struct.pack("cccii16s",
                                         # status -0, type -1 , fit -2, start -3, size -4, name -5
                                         particiones[j][0],
                                         particiones[j][1],
                                         particiones[j][2],
                                         int(particiones[j][3]),
                                         int(particiones[j][4]),
                                         particiones[j][5])
            j = j + 1

        # Ya se escribio Particion a MBR
        # Escribimos MBR en Archivo
        # potencial error (comillas)
        print(self.path)
        print("se escribe en archivo -- ")
        archivo = open("." + self.path, "wb")
        archivo.write(packedMBR)
        archivo.close()
        # Aca debemos hacer el reporte
        #print("-No hay suficiente espacio") if notCreatedFlag else print("done")
        return "******* TERMINADO ********************"

        # si es particion extendida, entonces escribirmos aca el EBR
        if (self.type.lower() == 'e'):
            # Creamos un objeto EBR
            # print("AQUI -0 EBR")
            ebr = EBR()
            ebr.ebr_status = b'1'
            ebr.ebr_fit = self.fit.encode()
            ebr.ebr_next = -1
            ebr.ebr_start = self.start + ctypes.sizeof(EBR)  # Start de la particion logica
            ebr.ebr_size = -1
            ebr.ebr_name = self.name.encode()

            # empacamos en binario EBR
            # Ahora escribimos el EBR
            packedEBR = struct.pack("cciii16s",
                                    ebr.ebr_status,
                                    ebr.ebr_fit,
                                    ebr.ebr_start,
                                    ebr.ebr_size,
                                    ebr.ebr_next,
                                    ebr.ebr_name)

            print("*********************************************")
            print("*************ESCRITURA EBR 0 *******************")
            print("path->" + "." + self.path)
            print("start->" + str(self.start))
            print("size->" + str(self.size))
            print("name->" + str(self.name))
            print("*********************************************")
            # printMBRFile("." + self.path)
            with open("." + self.path, "rb+") as newFile:
                print("SEEK-> " + str(self.start))
                newFile.seek(int(self.start), 0)
                newFile.write(packedEBR)
                newFile.close()

            print("EBR CREADO")
            print("reporte mbr ->" + "." + self.path)
            printMBRFile("." + self.path)
            print("EBR CREADO")
            print("=============EBR CREADO========")
            print("getEBR Call -> " + str(self.start))
            print("getEBR Call -> " + str(self.path))
            print("start->" + str(self.start))
            print("path->" + str(self.path))
            printEBRFile("." + self.path, int(self.start))
            return printEBRFile("." + self.path, int(self.start))

    def first_fit(self, mbr_written: MBR, mbr):
        print("first fit")
        # recorremos las particiones en busca de errores
        particiones = mbr['mbr_particiones']
        print("-----")
        print(particiones)
        particion_first_fit = 0
        notCreatedFlag = True
        for i in range(0, 4):
            # En las particiones buscamos
            # status -0, type -1 , fit -2, start -3, size -4, name -5
            print(particiones[i][0])
            # status
            if particiones[i][0] == b'0' and notCreatedFlag:
                print("Particion Vacia Encontrada")
                # Reviso cuanto espacio tengo a la derecha
                # status -0, type -1 , fit -2, start -3, size -4, name -5
                print("particiones i+1-> ")
                #print(particiones[i+1][3])
                print("particiones i-> ")
                print(particiones[i][3])
                frontStep = None
                if (i < 3):
                    frontStep = int(particiones[i+1][3])
                else:
                    frontStep = int(particiones[i][3])

                if(((frontStep - int(particiones[i][3]) > self.size) and notCreatedFlag) or
                  ((int(particiones[i][3]) == -1) and (frontStep == -1))               or
                        (i == 3 and ((int(mbr['mbr_tamano']) - int(particiones[i-1][3]) + self.size) > 0))):
                    print("si hay espacio")
                    notCreatedFlag = False
                    # Si si hay espacio, entonces puedo proceder a crear la particion
                    # Con "Crear" la particion, me refiero a apartar el espacio en MBR
                    # Cambiamos mbr_written (Que es el mbr que el que escribiremos)
                    # Primero -> Buscamos la particion i
                    # Idea: 1. Bajar los datos del MBR leido
                    mbr_written.mbr_tamano = int(mbr['mbr_tamano'])
                    mbr_written.mbr_dsk_signature = int(mbr['mbr_dsk_signature'])
                    mbr_written.mbr_fecha_creacion = int(mbr['mbr_fecha_creacion'])
                    mbr_written.mbr_fit = mbr['mbr_fit']

                    # 2. Cambiar los datos de las particiones
                    print(self.name)
                    print(self.type)
                    print(self.fit)
                    if self.unit.lower() == "k":
                        self.size = self.size*1024
                    elif self.unit.lower() == "m":
                        self.size = self.size*1024*1024

                    print(self.size)
                    print(self.start)
                    if i == 0:
                        print("potencial error traslape mbr -- linea 476 fdisk")
                        self.start = ctypes.sizeof(MBR) + 1# Verificar Luego
                    else:
                        # status -0, type -1 , fit -2, start -3, size -4, name -5
                        self.start = int(particiones[i-1][3]) + int(particiones[i-1][4]) + 1
                    # Escribimos Particion en MBR
                    particion_insertar = Particion(b'1', self.type.encode(), self.fit.encode(), int(self.start), int(self.size), self.name.encode())

                    mbr_written.mbr_particiones[i] = particion_insertar

                    # Packing Data
                    packedMBR = struct.pack("iii1s",
                                            mbr_written.mbr_tamano,
                                            mbr_written.mbr_fecha_creacion,
                                            mbr_written.mbr_dsk_signature,
                                            mbr_written.mbr_fit)
                    j = 0
                    for particion in mbr['mbr_particiones']:
                        if j == i:
                            packedMBR += struct.pack("cccii16s",
                                                     particion_insertar.part_status,
                                                     particion_insertar.part_type,
                                                     particion_insertar.part_fit,
                                                     particion_insertar.part_start,
                                                     particion_insertar.part_size,
                                                     particion_insertar.part_name)
                        else: # Si no, escribimos lo que ya estaba en el MBR
                            packedMBR += struct.pack("cccii16s",
                                                     # status -0, type -1 , fit -2, start -3, size -4, name -5
                                                     particiones[j][0],
                                                     particiones[j][1],
                                                     particiones[j][2],
                                                     int(particiones[j][3]),
                                                     int(particiones[j][4]),
                                                     particiones[j][5])
                        j = j + 1


                    # Ya se escribio Particion a MBR
                    # Escribimos MBR en Archivo
                    # potencial error (comillas)
                    print(self.path)
                    archivo = open("." + self.path,"wb")
                    archivo.write(packedMBR)
                    archivo.close()
                    notCreatedFlag = False

                    # Ahora que cambiamos el MBR, escribimos el EBR con los datos proporcionados
                    if (self.type.lower() == 'e'):
                        # Creamos un objeto EBR
                        # print("AQUI -0 EBR")
                        ebr = EBR()
                        ebr.ebr_status = b'1'
                        ebr.ebr_fit = self.fit.encode()
                        ebr.ebr_next = -1
                        ebr.ebr_start = self.start + ctypes.sizeof(EBR)  # Start de la particion logica
                        ebr.ebr_size = -1
                        ebr.ebr_name = self.name.encode()

                        # empacamos en binario EBR
                        # Ahora escribimos el EBR
                        packedEBR = struct.pack("cciii16s",
                                                ebr.ebr_status,
                                                ebr.ebr_fit,
                                                ebr.ebr_start,
                                                ebr.ebr_size,
                                                ebr.ebr_next,
                                                ebr.ebr_name)

                        print("*********************************************")
                        print("*************ESCRITURA EBR 0 *******************")
                        print("path->" + "." + self.path)
                        print("start->" + str(self.start))
                        print("size->" + str(self.size))
                        print("name->" + str(self.name))
                        print("*********************************************")
                        # printMBRFile("." + self.path)
                        with open("." + self.path, "rb+") as newFile:
                            print("SEEK-> " + str(self.start))
                            newFile.seek(int(self.start), 0)
                            newFile.write(packedEBR)
                            newFile.close()

                        print("EBR CREADO")
                        print("reporte mbr ->" + "." + self.path)
                        printMBRFile("." + self.path)
                        print("EBR CREADO")
                        print("=============EBR CREADO========")
                        print("getEBR Call -> " + str(self.start))
                        print("getEBR Call -> " + str(self.path))
                        print("start->" + str(self.start))
                        print("path->" + str(self.path))
                        printEBRFile("." + self.path, int(self.start))








        print("-No hay suficiente espacio") if notCreatedFlag else print("done")
        return "done" if notCreatedFlag else "-No hay suficiente espacio"


