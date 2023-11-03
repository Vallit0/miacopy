import os
import struct , datetime
from mount.Discos import DiscosMontados

# ------- Functions
def unpack_mbr(packed_data):
    unpacked_mbr = {}

    mbr_size = struct.calcsize("iii1s")
    mbr_data = packed_data[:mbr_size]
    unpacked_mbr['mbr_tamano'], unpacked_mbr['mbr_fecha_creacion'], unpacked_mbr['mbr_dsk_signature'], unpacked_mbr[
        'mbr_fit'] = struct.unpack("iii1s", mbr_data)

    #unpacked_datetime = datetime.fromtimestamp(unpacked_mbr['mbr_fecha_creacion'])
    #print(unpacked_datetime)
    partition_size = struct.calcsize("cccii16s" )
    unpacked_mbr['mbr_particiones'] = []
    partition_data = packed_data[mbr_size:]
    num_partitions = len(partition_data) // partition_size



    for i in range(num_partitions):
        partition_start = i * partition_size
        partition_end = partition_start + partition_size
        partition = struct.unpack("cccii16s" , partition_data[partition_start:partition_end])
        unpacked_mbr['mbr_particiones'].append(partition)

    return unpacked_mbr
def getMBR(definedPath):
    packed_data = read_packed_data_from_file(definedPath)

    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    #print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    return unpacked_data
def read_packed_data_from_file( file_path):
    with open(file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data


class Mount:
    def __init__(self):
        self.path = ""
        self.name = ""
        self.id = ""


    def mount(self):
        print("Mounting...")
        #print(self.name)
        # Recuperamos el MBR
        mbr = getMBR(self.path)  # diccionario
        # Buscamos la particion a montar
        numeroParticion = 0
        montado = False
        for i in range(0,4):
            print("[PARTICION ACTUAL]")
            print(mbr['mbr_particiones'][i])
            print(mbr['mbr_particiones'][i][5])
            print("[]")

            # status -0, type -1 , fit -2, start -3, size -4, name -5
            if mbr['mbr_particiones'][i][5].decode().rstrip('\x00') == self.name:
                print("Particion encontrada!")
                # Montamos la particion en estructura global
                # ID -> Ultimos 2 digitos carnet + No. Particion + Nombre Disco
                tmpPath = self.path
                tmpName = os.path.basename(self.path).replace(".dsk", "")
                tmpSize = mbr['mbr_particiones'][i][4]
                tmpStart = mbr['mbr_particiones'][i][3]
                DiscosMontados.mountDisco(tmpName, tmpPath, numeroParticion,tmpSize, tmpStart )
                print()
                print("++++++++++++++++++++++++++++++++++++")
                print("***********Montado!*****************")
                print("++++++++++++++++++++++++++++++++++++")
                montado = True

            numeroParticion += 1
        if montado:
            return "********* MONTADO ***********"
        else:
            return "++++++++ NO MONTADO +++++++++"
    def printMount(self):
        DiscosMontados.printDiscos(DiscosMontados)

    def unmount(self):
        print("Unmounting...")
        if (DiscosMontados.unmountDisco(self.id)):
            print("[++++++++++++++++++++++]")
            print("+++++++Desmontado!+++++")
            print("[++++++++++++++++++++++]")
            return "+++++++++++ Desmontado ++++++++"

        else:
            print("unmount -id=54XXXX")
            return "+++++++++++ No Desmontado ++++++++"







        # Creamos ID segun lo que esta en el enunciado
        # Guardamos en Arreglo la estructura montada para guardar informacion
