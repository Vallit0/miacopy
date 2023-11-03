from math import floor
import datetime
from datetime import datetime as fdatetime
import struct
from mount.Discos import DiscosMontados
from functions.estructuras import Superblock, iNodesTable, content, FolderBlock, FileBlock, blockPointer, Journal
import ctypes

# ------- Functions
def unpack_mbr(packed_data):
    unpacked_mbr = {}

    mbr_size = struct.calcsize("iii1s")
    mbr_data = packed_data[:mbr_size]
    unpacked_mbr['mbr_tamano'], unpacked_mbr['mbr_fecha_creacion'], unpacked_mbr['mbr_dsk_signature'], unpacked_mbr[
        'mbr_fit'] = struct.unpack("iii1s", mbr_data)

    #unpacked_datetime = fdatetime.fromtimestamp(unpacked_mbr['mbr_fecha_creacion'])
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
    with open("." + file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data
def read_packed_data_from_file_no_add( file_path):
    with open(file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data

class Mkfs:
    def __init__(self):
        self.id = ""
        self.type = ""
        self.fs = ""
        self.path = ""
        self.partName = ""

    def remove_first_dot(self, input_string):
        if input_string.startswith('./'):
            return input_string[1:]
        else:
            return input_string
    """
        Input-> None || implicito -> DiscosMontados, self.id
        Output-> None 
        Funcion-> Ejecuta MKFS dependiendo del input
        """
    def mkfs(self):
        # Ir a buscar el ID a los discos montados
        if DiscosMontados.exists(self.id):
            print("ID encontrado!")
            dir = DiscosMontados.returnPath(self.id)
            realDir = self.remove_first_dot(dir)
            mbr = getMBR(realDir)  # diccionario
            # necesitamos buscar el Disco donde se montara la particion
            if self.type.lower() == "2fs":
                print("EXT2")
                return self.ext2(mbr)
            elif self.type.lower() == "3fs":
                print("EXT3")
                #self.ext3(mbr)
            else:
                print("EXT2")
                return self.ext2(mbr)
        else:
            print("ID no encontrado")
            return "ID no encontrado"
    def unpack_superblock(self, packed_data, start):
        unpacked_superblock = {}
        superblock_size = struct.calcsize("ciiiiiiiiiiiiiiii")
        superblock_data = packed_data[start:start + superblock_size]
        unpacked_superblock = struct.unpack("ciiiiiiiiiiiiiiii", superblock_data)

        # Create a dictionary with field names as keys
        field_names = [field[0] for field in Superblock._fields_]
        unpacked_superblock = dict(zip(field_names, unpacked_superblock))

        return unpacked_superblock

    def read_packed_data_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            packed_data = file.read()
        return packed_data

    def getSuperblock(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpack_superblock(packed_data, start)
        print("-------Superbloque ---------")
        print("s_filesystem_type->" + unpacked_data['s_filesystem_type'].decode('utf-8'))
        print("s_inodes_count->" + str(unpacked_data['s_inodes_count']))
        print("s_blocks_count->" + str(unpacked_data['s_blocks_count']))
        print("s_free_blocks_count->" + str(unpacked_data['s_free_blocks_count']))
        print("s_free_inodes_count->" + str(unpacked_data['s_free_inodes_count']))
        print("s_mtime->" + str(fdatetime.fromtimestamp(unpacked_data['s_mtime'])))
        print("s_umtime->" + str(unpacked_data['s_umtime']))
        print("s_mnt_count->" + str(unpacked_data['s_mnt_count']))
        print("s_magic->" + str(unpacked_data['s_magic']))
        print("s_inode_s->" + str(unpacked_data['s_inode_s']))
        print("s_block_s->" + str(unpacked_data['s_block_s']))
        print("s_first_ino->" + str(unpacked_data['s_first_ino']))
        print("s_first_blo->" + str(unpacked_data['s_first_blo']))
        print("s_bm_inode_start->" + str(unpacked_data['s_bm_inode_start']))
        print("s_bm_block_start->" + str(unpacked_data['s_bm_block_start']))
        print("s_inode_start->" + str(unpacked_data['s_inode_start']))
        print("s_block_start->" + str(unpacked_data['s_block_start']))
        return unpacked_data
    """
    Input-> mbr_dictionary
    Output-> None
    Funcion-> Formatea el disco con EXT2 ||
    cambia el disco montado en DiscosMontados(id) 
    """
    def ext2(self, mbr_dictionary) -> None:
        # recorremos las particiones del disco para encontrar la particion a formatear
        # utilizamos el ID de la particion para encontrarla
        start = DiscosMontados.returnStart(self.id)
        size = DiscosMontados.returnSize(self.id)


        print("&&&&& Discos Montados")
        print("start->" + str(start))
        print("size->" + str(size))
        print("&&&&& &&&&&&&&&&&&&&")
        # Calculos iniciales
        n = (size - ctypes.sizeof(Superblock)) / (4 + int(ctypes.sizeof(iNodesTable)) + 3 * int(ctypes.sizeof(FileBlock)))
        num_estructuras = int(floor(n)) # numero
        num_bloques = int(3 * num_estructuras)
        input(">>")

        # ---------- SUPERBLOQUE INICIAL -------
        superbloque = Superblock()
        superbloque.s_filesystem_type = b'2'
        superbloque.s_inodes_count = int(num_estructuras)
        superbloque.s_blocks_count = int(num_bloques)
        superbloque.s_free_blocks_count = num_bloques - 2
        superbloque.s_free_inodes_count = num_estructuras - 2
        # time
        current_datetime = datetime.datetime.now()
        current_timestamp_float = current_datetime.timestamp()
        current_timestamp_integer = int(current_timestamp_float)

        superbloque.s_mtime = current_timestamp_integer
        superbloque.s_umtime = 0
        superbloque.s_mnt_count = 0
        superbloque.s_magic = 0xEF53
        superbloque.s_inode_s = ctypes.sizeof(iNodesTable)
        superbloque.s_block_s = ctypes.sizeof(FileBlock)
        superbloque.s_first_ino = 2
        superbloque.s_first_blo = 2
        superbloque.s_bm_inode_start = start + ctypes.sizeof(Superblock) # porque estan despuesito del superbloque
        superbloque.s_bm_block_start = start + ctypes.sizeof(Superblock) + num_estructuras
        superbloque.s_inode_start = start + ctypes.sizeof (Superblock) + num_estructuras + num_bloques
        superbloque.s_block_start = start + ctypes.sizeof(Superblock) + num_estructuras + num_bloques + ((ctypes.sizeof(iNodesTable))*num_estructuras);
        print("******** ESCRITURA SB*************")
        print("s_filesystem_type->" + superbloque.s_filesystem_type.decode('utf-8'))
        print("s_inodes_count->" + str(superbloque.s_inodes_count))
        print("s_blocks_count->" + str(superbloque.s_blocks_count))
        print("s_free_blocks_count->" + str(superbloque.s_free_blocks_count))
        print("s_free_inodes_count->" + str(superbloque.s_free_inodes_count))
        print("s_mtime->" + str(superbloque.s_mtime))
        print("s_umtime->" + str(superbloque.s_umtime))
        print("s_mnt_count->" + str(superbloque.s_mnt_count))
        print("s_magic->" + str(superbloque.s_magic))
        print("s_inode_s->" + str(superbloque.s_inode_s))
        print("s_block_s->" + str(superbloque.s_block_s))
        print("s_first_ino->" + str(superbloque.s_first_ino))
        print("s_first_blo->" + str(superbloque.s_first_blo))
        print("s_bm_inode_start->" + str(superbloque.s_bm_inode_start))
        print("s_bm_block_start->" + str(superbloque.s_bm_block_start))
        print("s_inode_start->" + str(superbloque.s_inode_start))
        print("s_block_start->" + str(superbloque.s_block_start))
        print("******** ESCRITURA SB*************")
        input(">>")

        # Escritura SUPERBLOQUE
        archivo = open(DiscosMontados.returnPath(self.id), "rb+")
        archivo.seek(0)
        print("start->" + str(start))
        archivo.seek(int(start))
        archivo.write(self.packSuperblock(superbloque))



        # Lectura SB
        print("^^^^^^^^^^^^^^ Lectura Super Bloque")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("start->"+ str(start))
        superbloque = self.getSuperblock(DiscosMontados.returnPath(self.id), start)
        input(">>")

        print("********* BITMAP iNodos *************")
        buffer = '0' # para escribir solo 0s en el bitmap
        for i in range(0, num_estructuras):
            archivo.seek(int(superbloque['s_bm_inode_start']) + i, 0)
            archivo.write(buffer.encode("utf-8"))
            print(0, end="") if i > 10  else print(" ")
        input(">>")

        print("********* BITMAP Bloques *************")
        # bit para /(root) y para users.txt
        uno = 1
        archivo.seek(int(superbloque['s_bm_inode_start']), 0)
        #archivo.write(struct.pack("i", 1))
        archivo.write(b'1')
        archivo.seek(int(superbloque['s_bm_inode_start']) + 1, 0)
        #archivo.write(struct.pack("i", 1))
        archivo.write(b'1')
        input(">>")

        # BITMAP Bloques
        for i in range(0, num_bloques):
            archivo.seek(int(superbloque['s_bm_block_start']) + i)
            archivo.write(buffer.encode("utf-8"))

        # bit para / y /users.txt
        archivo.seek(int(superbloque['s_bm_inode_start']), 0)
        #archivo.write(struct.pack("i", 1))
        archivo.write(b'1')
        archivo.seek(int(superbloque['s_bm_inode_start']) + 1, 0)
        #archivo.write(struct.pack("i", 1))
        archivo.write(b'1')


        # inicia escritura de carpetas
        '''
        ------- iNode Carpeta Raiz --------
        '''
        carpeta_raiz_iNode = iNodesTable()
        current_datetime = datetime.datetime.now()
        current_timestamp_float = current_datetime.timestamp()
        current_timestamp_integer = int(current_timestamp_float)
        # Necesitamos crear la carpeta raiz (.)
        # Creamos un iNode CARPETA RAIZ (.)
        carpeta_raiz_iNode.i_uid = 1
        carpeta_raiz_iNode.I_gid = 1
        carpeta_raiz_iNode.i_s = 0
        carpeta_raiz_iNode.i_atime = current_timestamp_integer
        carpeta_raiz_iNode.i_ctime = current_timestamp_integer
        carpeta_raiz_iNode.s_mtime = current_timestamp_integer
        carpeta_raiz_iNode.i_block[0] = 0 # Apunta a la carpeta 0
        # formateamos todos los demas nodos
        for i in range(1, 15):
            carpeta_raiz_iNode.i_block[i] = -1
        carpeta_raiz_iNode.i_type = 0 #porque es carpeta
        carpeta_raiz_iNode.i_perm = 664 # permisos
        # Escribimos el iNode (TABLA DE INODOS)
        archivo.seek(int(superbloque['s_inode_start']), 0)
        archivo.write(self.packiNodesTable(carpeta_raiz_iNode))
        # [X] iNodo de '.' -- Ahora escribir bloque de '.' (carpeta raiz)
        # Creamos el bloque de carpeta
        folderBlock = FolderBlock()
        # Creamos el contenido de la carpeta

        # antes de hacer esto
        folderBlock.b_content[0].b_name = ".".encode("utf-8") # se apunta a si mismo
        folderBlock.b_content[0].b_inodo = 0

        folderBlock.b_content[1].b_name = "..".encode("utf-8")
        folderBlock.b_content[1].b_inodo = 0

        # ahora creamos el hijo
        folderBlock.b_content[2].b_name = "users.txt".encode("utf-8")
        folderBlock.b_content[2].b_inodo = 1
        # creamos el padre
        folderBlock.b_content[3].b_name = ".".encode("utf-8")
        folderBlock.b_content[3].b_inodo = -1

        # SE ESCRIBEN AMBOS BLOQUES EN EL ARCHIVO
        # Escribimos el bloque de carpeta
        archivo.seek(int(superbloque['s_block_start']), 0)
        archivo.write(self.packFolderBlock(folderBlock))
        # Escribimos el bitmap de bloques -->
        # inodo para users.txt
        users_iNodo = iNodesTable()
        users_iNodo.i_uid = 1 # cambiar esto
        users_iNodo.I_gid = 1
        users_iNodo.i_s = 27
        users_iNodo.i_atime = current_timestamp_integer
        users_iNodo.i_ctime = current_timestamp_integer
        users_iNodo.s_mtime = current_timestamp_integer
        users_iNodo.i_block[0] = 1
        # formateamos todos los demas nodos
        for i in range(1, 15):
            users_iNodo.i_block[i] = -1

        users_iNodo.i_type = 1 #porque es archivo
        users_iNodo.i_perm = 755 # permisos
        # Escribimos el iNode (TABLA DE INODOS)
        archivo.seek(int(superbloque['s_inode_start'] + ctypes.sizeof(iNodesTable)), 0)
        archivo.write(self.packiNodesTable(users_iNodo))

        #Bloque para users.txt
        fileBlock = FileBlock()
        # Aqui hay un error
        fileBlock.b_content = "1,G,Root\n1,U,root,root,123\n0,G,usuarios\n"
        # Escribimos el bloque de carpeta
        archivo.seek(int(superbloque['s_block_start']) + ctypes.sizeof(FolderBlock), 0)
        archivo.write(self.pack_file_block(fileBlock))
        print("EXT2")
        print("...")
        print("Disco Formateando con exito")

        archivo.close()
        input(">> Unit Tests")

        # @ Unit Test
        self.getMetaData()
        return "Disco Formateado con exito EXT2"

    """
        @ Unit Test 
        Input    -> direccion  
        Output   -> None 
        Function -> Verify Written Data
    """
    def getMetaData(self):
        print("######### METADATA ########")
        print("id->" + self.id)

        direccion = DiscosMontados.returnPath(self.id)
        print("direccion->" + direccion)

        print("############# Superblock ############")
        print(DiscosMontados.returnStart(self.id))
        print(self.id)
        sb = self.getSuperblock(direccion, DiscosMontados.returnStart(self.id))

        print("############# Bitmap iNodes #############")
        #self.getBitmap(direccion, sb['s_bm_inode_start'], sb['s_inodes_count'])

        print("############# Bitmap Bloques #############")
        self.getBitmap(direccion, sb['s_bm_block_start'], sb['s_blocks_count'])

        print("############# Tablas de iNodos #############")
        self.getiNodesTable(sb['s_inode_start'], direccion)

    def unpack_iNodesTable(self, packed_data, start):
        iNodesTable_format = "iiiiiiiii14i"
        iNodesTable_size = struct.calcsize(iNodesTable_format)

        # Extract the packed data for iNodesTable from the packed_data
        iNodesTable_data = packed_data[start:start + iNodesTable_size]

        # Unpack the data according to the format string
        unpacked_iNodesTable = struct.unpack(iNodesTable_format, iNodesTable_data)

        # Now, create a dictionary with field names as keys
        field_names = [
            "i_uid",
            "i_gid",
            "i_s",
            "i_atime",
            "i_ctime",
            "s_mtime",
            "i_block_0",
            "i_block_1",
            "i_block_2",
            "i_block_3",
            "i_block_4",
            "i_block_5",
            "i_block_6",
            "i_block_7",
            "i_block_8",
            "i_block_9",
            "i_block_10",
            "i_block_11",
            "i_block_12",
            "i_block_13",
            "i_block_14",
            "i_type",
            "i_perm"
        ]

        # Create a dictionary with field names as keys
        unpacked_dict = dict(zip(field_names, unpacked_iNodesTable))
        unpacked_dict['i_block'] = unpacked_iNodesTable[7:22][::-1]

        return unpacked_dict

    def getiNodesTable(self, start, definedPath):
        packed_data = read_packed_data_from_file_no_add(definedPath)
        unpacked_data = self.unpack_iNodesTable(packed_data, start)
        print(unpacked_data)
        print("-------Tabla de iNodos---------")
        print("i_uid->" + str(unpacked_data['i_uid']))
        print("i_gid->" + str(unpacked_data['i_gid']))
        print("i_s->" + str(unpacked_data['i_s']))
        print("i_atime->" + str(unpacked_data['i_atime']))
        print("i_ctime->" + str(unpacked_data['i_ctime']))
        print("s_mtime->" + str(unpacked_data['s_mtime']))
        print("i_block 0->" + str(unpacked_data['i_block'][0]))
        print("i_block 1->" + str(unpacked_data['i_block'][1]))
        print("i_block 2->" + str(unpacked_data['i_block'][2]))
        print("i_block 3->" + str(unpacked_data['i_block'][3]))

        print("i_type->" + str(unpacked_data['i_type']))
        print("i_perm->" + str(unpacked_data['i_perm']))
        print("--------------------------------")
        return unpacked_data

    def getBitmap(self, direccion, start, count):
        archivo = open(direccion, "rb+")
        archivo.seek(start)
        buffer = archivo.read(count)
        print(buffer)
        archivo.close()


    """
        Input-> mbr_dictionary
        Output-> None
        Funcion-> Formatea el disco con EXT3 ||
        cambia el disco montado en DiscosMontados(id) 
    """
    def ext3(self):
        print("hola")

    """
        Input-> superblock (estructura)
        Output-> packedData (bytes) 
        Funcion-> empaca en un struct los datos del superblock 
    """
    def packSuperblock(self, superblock: Superblock):
        packedData = struct.pack("ciiiiiiiiiiiiiiii",
                                 superblock.s_filesystem_type,#17
                                    superblock.s_inodes_count,#16
                                    superblock.s_blocks_count,#15
                                    superblock.s_free_blocks_count,#14
                                    superblock.s_free_inodes_count, #13
                                    superblock.s_mtime,#12
                                    superblock.s_umtime,#11
                                    superblock.s_mnt_count,#10
                                    superblock.s_magic,#9
                                    superblock.s_inode_s,#8
                                    superblock.s_block_s,#7
                                    superblock.s_first_ino,#6
                                    superblock.s_first_blo, #5
                                    superblock.s_bm_inode_start, #4
                                    superblock.s_bm_block_start, #3
                                    superblock.s_inode_start, #2
                                    superblock.s_block_start) #1
        return packedData

    """
    Input-> iNodesTable (estructura)
    Output-> packedData (bytes) 
    Funcion-> empaca en un struct los datos de 1 iNodo 
    """
    def packiNodesTable(self, iNTable: iNodesTable):
        packedData = struct.pack("iiiiiiiii14i",
                                    iNTable.i_uid,
                                    iNTable.I_gid,
                                    iNTable.i_s,
                                    iNTable.i_atime,
                                    iNTable.i_ctime,
                                    iNTable.s_mtime,
                                 iNTable.i_block[0],  # First element of i_block
                                 iNTable.i_block[1],
                                 iNTable.i_block[2],
                                 iNTable.i_block[3],
                                 iNTable.i_block[4],
                                 iNTable.i_block[5],
                                 iNTable.i_block[6],
                                 iNTable.i_block[7],
                                 iNTable.i_block[8],
                                 iNTable.i_block[9],
                                 iNTable.i_block[10],
                                 iNTable.i_block[11],
                                 iNTable.i_block[12],
                                 iNTable.i_block[13],
                                 iNTable.i_block[14],
                                    iNTable.i_type,
                                    iNTable.i_perm)

        return packedData

    """
        Input-> folderBlock (estructura) [Bloque de Archivos] 
        Output-> packedData (bytes) 
        Funcion-> empaca en un struct los datos 
    """
    def packFolderBlock(self, folder_block):
       # puedo resolver el problema de manera similar a como
        packed_data = b''
        for i in range(4):
            packed_data += struct.pack('12s', folder_block.b_content[i].b_name.encode('utf-8'))
            packed_data += struct.pack('i', folder_block.b_content[i].b_inodo)
        return packed_data

    def pack_file_block(self, file_block):
        # Define the format string for the struct packing based on the field's size
        format_string = f"{len(file_block.b_content)}s"

        # Pack the FileBlock instance into a binary representation
        packed_data = struct.pack(format_string, file_block.b_content)

        return packed_data


"""
        Pre-Debugging list: 
        - [X] 1. Packing Structures 
        - [X] 1.1.  Packing iNodesTable
        - [X] 1.2.  Packing FolderBlock
        ISSUE FLAG - 
        Probable Fix: 
            Empaquetar primero los elementos de b_content y luego empaquetar el folderBlock 
            Similar Issue: Al empaquetar Particiones 
        ISSUE SOLVED 
        - [X] 1.3.  Packing FileBlock       
        - [X] 1.4.  Packing Superblock
        - [X] 2. Conversion a Bytes
        - [X] 2.1.  conversion iNodesTable
        - [X] 2.2.  conversion FolderBlock
        - [X] 2.3.  conversion FileBlock       
        - [X] 2.4.  conversion Superblock
        - [X] 3. Verificar que el tipo de formateo sea correcto 
        - [X] 4. Verificar que el path sea correcto
        
        Checking List 
        - [X] Superblock Passed Local  
        - [X] Bitmap iNodes Passed
        - [X] Bitmap Bloques Passed 
        - [ ] iNodesTable Passed 
        - [ ] Bloque Carpeta Raiz Passed 
        - [ ] Bloque users.txt Passed 
        - [ ] Busqueda de Archivos
        Mi pregunta es
        Obtengo el iNodo = Obtengo el Bloque 
        Obtengo el iNodo = Obtengo el Bloque 
        ¿ Como hago un transverse de todos los iNodes? 
"""