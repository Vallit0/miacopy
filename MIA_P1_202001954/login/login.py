import ctypes
import struct
from mount.Discos import DiscosMontados
from functions.estructuras import MBR, Usuario, Superblock, iNodesTable, FolderBlock
from datetime import datetime as fdatetime
import datetime
from login.currentSession import currentSession
# --------- iNodes Table Functions
def getiNodesTable(start, definedPath):
    packed_data = read_packed_data_from_file(definedPath)
    unpacked_data = unpack_iNodesTable(packed_data, start)
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


def unpack_iNodesTable(packed_data, start):
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
    unpacked_dict['i_block'] = unpacked_iNodesTable[7:22]
    unpacked_dict['i_block'] = unpacked_dict['i_block'][::-1]

    return unpacked_dict
#----- Superblock Functions


# ------- Functions
def unpack_mbr(packed_data):
    unpacked_mbr = {}

    mbr_size = struct.calcsize("iii1s")
    mbr_data = packed_data[:mbr_size]
    unpacked_mbr['mbr_tamano'], unpacked_mbr['mbr_fecha_creacion'], unpacked_mbr['mbr_dsk_signature'], unpacked_mbr[
        'mbr_fit'] = struct.unpack("iii1s", mbr_data)

    unpacked_datetime = datetime.fromtimestamp(unpacked_mbr['mbr_fecha_creacion'])
    print(unpacked_datetime)
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
    packed_data = read_packed_data_from_file_login(definedPath)

    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    return unpacked_data
def read_packed_data_from_file( file_path):
    with open(file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data

def read_packed_data_from_file_login( file_path):
    with open(file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data


class Login:
    def __init__(self):
        self.user = ""
        self.id = ""
        self.pwd = ""
        self.out = ""
        self.path = ""
        self.partName = ""
    def read_packed_data_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            packed_data = file.read()
        return packed_data

    def unpack_superblock(self, packed_data, start):
        unpacked_superblock = {}
        superblock_size = struct.calcsize("ciiiiiiiiiiiiiiii")
        superblock_data = packed_data[start:start + superblock_size]
        unpacked_superblock = struct.unpack("ciiiiiiiiiiiiiiii", superblock_data)

        # Create a dictionary with field names as keys
        field_names = [field[0] for field in Superblock._fields_]
        unpacked_superblock = dict(zip(field_names, unpacked_superblock))

        return unpacked_superblock

    import struct

    def unpackFolderBlock(self, packed_data):
        folder_block = {'b_content': []}
        offset = 0

        for i in range(4):
            name_bytes = struct.unpack('12s', packed_data[offset:offset + 12])[0]
            name = name_bytes.decode('utf-8').strip('\x00')  # Remove any null characters
            offset += 12
            inodo = struct.unpack('i', packed_data[offset:offset + 4])[0]
            offset += 4

            folder_block['b_content'].append({'b_name': name, 'b_inodo': inodo})

        return folder_block

    def getSuperblock(self, definedPath, start):
        print("--->")
        print(definedPath)
        print("00000")
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

    '''
    El login consiste en 
        1) Buscar la particion en los discos montados
        2) Verificar si el usuario existe 
    -- Buscar el archivo users.txt 
    1-Buscar el usuario 
    2-Verificar la contraseña
    3-Verificar el grupo
    '''
    def loginNow(self) -> int:
        # primero debemos buscar la particion en los discos montados (solo Primarias)
        if DiscosMontados.exists(self.id):
            print("ID encontrado!")
            startParticion = DiscosMontados.returnStart(self.id)
            superblock = self.getSuperblock(DiscosMontados.returnPath(self.id), DiscosMontados.returnStart(self.id))

            currentSession.inicio_super =   startParticion
            currentSession.tipo_sistema =   superblock['s_filesystem_type']
            currentSession.direccion =      DiscosMontados.returnPath(self.id)
            currentSession.inicio_Journal = superblock['s_bm_inode_start']


            return self.verificarDatos()

    def verificarDatos(self) -> int: # EDD NIVEL DE ABSTRACCION - PROYECTOS - TIEMPO CONSUMIDO
        archivo = open(currentSession.direccion, "rb+")
        print("############# Lectura Super block valores Sesion ############")
        print("start_superblocok -> " + str(currentSession.inicio_super))
        super = self.getSuperblock(currentSession.direccion, currentSession.inicio_super)
        # verificamos si el usuario existe
        # solo esta recuperando el SEGUNDO iNodo, porque queremos recuperar la 2da Tabla
        nodesTable = getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion) # Error
        contenido = ""
        print(nodesTable)
        # recorremos los iNodos (15) y movemos el puntero
        for i in range(15):
            if nodesTable['i_block'][i] != -1:# Recorriendo los apuntadores directos del 1er iNODO (15)
                print(nodesTable['i_block'][i])
                print(i)
                # block_offset -> por donde vamos?
                block_offset = super['s_block_start'] + (nodesTable['i_block'][i] * ctypes.sizeof(FolderBlock))
                archivo.seek(block_offset)
                folder_data = []
                #
                for j in range(int(nodesTable['i_block'][i]) + 1): #
                    #print("Content----")

                    # Sustituir por un get
                    contenido = archivo.read(ctypes.sizeof(FolderBlock))
                    #print(contenido)
                    folder_entry = struct.unpack(f'{len(contenido)}s', contenido)

                    folder_data.append(folder_entry)
                    print(folder_data)


        archivo.close()
        # verificamos si la contraseña es correcta
        contenido = contenido.decode("utf-8")
        new_contenido = folder_data[0][0].decode("utf-8")
        #print(folder_data)
        print(new_contenido)
        lines = new_contenido.split("\n")
        for line in lines:
            print("line->")
            print(line)
            token, line = line.split(",", 1)
            id = token
            print(token)
            if id != "0":  # Verify it's not a deleted U/G
                tipo, line = line.split(",", 1)
                print("tipo ", end="")
                print(tipo)
                print("line ", end="")
                print(line)
                if tipo == "U":
                    group, line = line.split(",", 1)
                    user_, line = line.split(",", 1)
                    password_ = line.split(",", 1)[0]

                    print("user ", end="")
                    print(user_)
                    print("password ", end="")
                    print(password_)
                    if user_ == self.user and password_ == self.pwd:
                        print("Aqui estamos")
                        currentSession.direccion = self.path
                        currentSession.id_user = int(id)
                        currentSession.id_grp = self.buscarGrupo(group)
                        currentSession.active = True
                        print("+++++++ LOGGED +++++++++")

                        return 1
                    else:
                        return 2
        # recorremos el contenido, verificando user y password
    '''
    input -> self 
    output -> None 
    functionality -> cerrar sesion 
    '''
    def log_out(self):
        global flag_login, currentSession

        if currentSession.active:
            currentSession.active = False
            currentSession.id_user = -1
            currentSession.id_grp = -1
            currentSession.direccion = ""
            currentSession.inicioSuper = -1
            print("...\nSesion finalizada ")
        else:
            print("ERROR no hay ninguna sesion activa")

    '''
    input         -> name: nombre del grupo 
    output        -> none 
    functionality -> encontrar un grupo en el archivo users.txt  
    '''
    def buscarGrupo(self, name):
        print("&&&&&&& GRUPO &&&&&&&&&")
        archivo = open(DiscosMontados.returnPath(self.id), "rb+")
        cadena = b"\0" * 400
        super = Superblock()
        super_block = self.getSuperblock(DiscosMontados.returnPath(self.id), DiscosMontados.returnStart(self.id))
        inodo = getiNodesTable(super_block['s_inode_start'] + ctypes.sizeof(iNodesTable), DiscosMontados.returnPath(self.id))

        # Notas GetContent (Puede servir)
        for i in range(15):
            if inodo['i_block'][i] != -1:  # Recorriendo los apuntadores directos del 1er iNODO (15)
                print(inodo['i_block'][i])
                print(i)
                # block_offset -> por donde vamos?
                block_offset = super['s_block_start'] + (inodo['i_block'][i] * ctypes.sizeof(FolderBlock))
                archivo.seek(block_offset)
                folder_data = []
                for j in range(int(inodo['i_block'][i]) + 1):  #
                    # print("Content----")
                    # Sustituir por un get
                    contenido = archivo.read(ctypes.sizeof(FolderBlock))
                    # print(contenido)
                    folder_entry = struct.unpack(f'{len(contenido)}s', contenido)
                    folder_data.append(folder_entry)
                    print(folder_data)

        archivo.close() # Convert bytes to a string

        new_contenido = folder_data[0][0].decode("utf-8")

        token = new_contenido.split('\n')
        for line in token:
            tokens = line.split(',')
            id = tokens[0]
            if id != "0":
                tipo = tokens[1]
                if tipo == "G":
                    group = tokens[2]
                    if group == name.toStdString():
                        return int(id)

        return -1

    '''
    input   -> iNodesTable Object 
    output  -> Object packed into Bytes 
    functionality -> Pack the iNodesTable Object into Bytes  
    '''
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
    Pre-Debuggin List: 
    ** Issues 
    - [ ] Login Not Done Properly
    - [ ] Readability of the iNode
    Probable Fix: 
    Understand the Structure and the way its being read 
    - [x] Superblock Read Good
    - [ ] Write iNodesTable 
    *  
    ** Knowledge
    -- Questions
"""