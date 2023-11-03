import struct
import os
from functions.estructuras import Superblock,  iNodesTable, Journal, FolderBlock, FileBlock, blockPointer
from mount.Discos import DiscosMontados
from datetime import datetime as fdatetime # Para formatear la fecha
import datetime
import time
import ctypes
import math

from ctypes import create_string_buffer
from pathlib import Path
class mkgrp:
    def __init__(self):
        self.currentUser = ""
        self.currentId = ""
        self.currentGrp= ""
        self.path = ""
        ### Valores extraidos
        self.name = ""
        self.size = -1
        self.cont = ""
        self.r = ""

        # MKUSR
        self.user = ""
        self.pwd = ""
        self.grp = ""


    def read_packed_data_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            packed_data = file.read()
        return packed_data
    '''
    input         -> Start and Path
    output        -> iNodes Table 
    functionality -> 
    '''
    def getiNodesTable(self, start, definedPath):
        packed_data = self.read_packed_data_from_file(definedPath)
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

    '''
    input -> 
    output->
    '''
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
        unpacked_dict['i_block'] = unpacked_iNodesTable[7:22]
        unpacked_dict['i_block'] = unpacked_dict['i_block'][::-1]

        return unpacked_dict
    def mkgrp(self, currentSession):
        grpName = self.name
        if currentSession.active:
            if currentSession.id_user == 1 and currentSession.id_grp == 1:  # Usuario root
                if len(grpName) <= 10:
                    grupo = self.buscarGrupo(grpName, currentSession)
                    if grupo == -1:
                        idGrp = self.getID_grp(currentSession)  # Assuming getID_grp is a valid function
                        nuevoGrupo = f"{idGrp},G,{grpName}\n"
                        g_respuesta = self.agregarUsersTXT(nuevoGrupo, currentSession)  # Assuming agregarUsersTXT is a valid function
                        if g_respuesta:
                            return "Grupo creado con exito"
                        else:
                            return "No se pudo crear el grupo"
                    else:
                        print("ERROR ya existe un grupo con ese nombre")
                        return "ERROR ya existe un grupo con ese nombre"
                else:
                    print("ERROR el nombre del grupo no puede exceder los 10 caracteres")
                    return "ERROR el nombre del grupo no puede exceder los 10 caracteres"
            else:
                print("ERROR solo el usuario root puede ejecutar este comando")
                return "ERROR SOLO EL USUARIO ROOT PUEDE HACERLo"

    '''
    
    '''
    def unpack_superblock(self, packed_data, start):
        unpacked_superblock = {}
        superblock_size = struct.calcsize("ciiiiiiiiiiiiiiii")
        superblock_data = packed_data[start:start + superblock_size]
        unpacked_superblock = struct.unpack("ciiiiiiiiiiiiiiii", superblock_data)

        # Create a dictionary with field names as keys
        field_names = [field[0] for field in Superblock._fields_]
        unpacked_superblock = dict(zip(field_names, unpacked_superblock))

        return unpacked_superblock
    '''
    input         -> name: nombre del grupo 
    output        -> none 
    functionality -> encontrar un grupo en el archivo users.txt  
    '''
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
    input -> 
    output -> 
    functionality 
    '''
    def buscarGrupo(self, name, currentSession):
        print("&&&&&&& GRUPO &&&&&&&&&")
        archivo = open(DiscosMontados.returnPath(self.id), "rb+")
        cadena = b"\0" * 400
        super = Superblock()
        super_block = self.getSuperblock(DiscosMontados.returnPath(self.id), DiscosMontados.returnStart(self.id))
        inodo = self.getiNodesTable(super_block['s_inode_start'] + ctypes.sizeof(iNodesTable),
                               DiscosMontados.returnPath(self.id))

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

        archivo.close()  # Convert bytes to a string

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
    input -> CurrentSession
    output -> Current ID on Groups (0,1,2,3,4...) 
    functionality -> Opens the file and searchs throughout
    '''
    def getID_grp(self, currentSession):
        print("&&&&&&& GRUPO &&&&&&&&&")
        archivo = open(DiscosMontados.returnPath(self.id), "rb+")
        cadena = b"\0" * 400
        super = Superblock()
        super_block = self.getSuperblock(DiscosMontados.returnPath(self.id), DiscosMontados.returnStart(self.id))
        inodo = self.getiNodesTable(super_block['s_inode_start'] + ctypes.sizeof(iNodesTable), DiscosMontados.returnPath(self.id))
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

        archivo.close()  # Convert bytes to a string
        aux_id = -1
        new_contenido = folder_data[0][0].decode("utf-8")


        cadena_str = new_contenido.decode('utf-8')

        for token in cadena_str.split("\n"):
            id_, tipo = token.split(",", 1)
            if id_ != "0" and tipo == "G":
                aux_id = int(id_)
        return aux_id + 1

    '''
    input -> string, currentSession
    output-> 
    1. Recupera el ultimo iNodo
    2. Lee el contenido y copia hacia un nuevo iNodo 
    3. Se cambia el contenido 
    4. Reescribe el iNodo en donde debería ir 
    '''
    def agregarUsersTXT(self, datos, currentSession):
        #try:
            #with open(currentSession.direccion, "rb+") as fp:
            super = Superblock()
            inodo = iNodesTable()
            blockIndex = 0

            fp = open(currentSession.direccion, "rb+")
            super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)
            # Leemos el inodo del archivo users.txt
            inodo_users = self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable))

            for i in range(14):
                if inodo_users['i_block'][i] != -1:
                    blockIndex = inodo.i_block[i]  # Último bloque utilizado del archivo

            fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * blockIndex)
            archivo = self.getFolderBlock(currentSession.direccion, super['s_block_start'] + ctypes.sizeof(FolderBlock) * blockIndex)

            for i in range(15):
                if inodo_users['i_block'][i] != -1:  # Recorriendo los apuntadores directos del 1er iNODO (15)
                    print(inodo_users['i_block'][i])
                    print(i)
                    # block_offset -> por donde vamos?
                    block_offset = super['s_block_start'] + (inodo_users['i_block'][i] * ctypes.sizeof(FolderBlock))
                    fp.seek(block_offset)
                    folder_data = []
                    #
                    for j in range(int(inodo_users['i_block'][i]) + 1):  #
                        # print("Content----")

                        # Sustituir por un get
                        contenido = fp.read(ctypes.sizeof(FolderBlock))
                        # print(contenido)
                        folder_entry = struct.unpack(f'{len(contenido)}s', contenido)

                        folder_data.append(folder_entry)
                        print(folder_data)



            # Ahora usamos los datos recuperados
            new_contenido = folder_data[0][0].decode("utf-8")
            enUso = len(new_contenido)
            libre = 63 - enUso

            if len(datos) <= libre:
                # Transferimos los datos a un nuevo objeto
                archivo_insertar = FileBlock()
                new_string = new_contenido + datos
                archivo_insertar.b_content = new_string.encode("utf-8")

                # Actualizamos Bloque de Archivos
                fp.seek(int(super['s_block_start']) + ctypes.sizeof(FolderBlock), 0)
                fp.write(self.pack_file_block(archivo_insertar))


                # Pedimos el iNodo del archivo users.txt

                #fp.seek(super.s_inode_start + ctypes.sizeof(inodo))
                users_inode =  self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion)
                inode_insertar = iNodesTable()

                # Actualizamos el iNodo
                inode_insertar.i_uid = users_inode['i_uid']
                inode_insertar.I_gid = users_inode['i_gid']
                inode_insertar.i_s = users_inode['i_s']
                inode_insertar.i_atime = users_inode['i_atime']
                inode_insertar.i_ctime = users_inode['i_ctime']

                current_datetime = datetime.datetime.now()
                current_timestamp_float = current_datetime.timestamp()
                current_timestamp_integer = int(current_timestamp_float)
                inode_insertar.s_mtime = current_timestamp_integer
                inode_insertar.i_block = users_inode['i_block']
                inode_insertar.i_type = users_inode['i_type']
                inode_insertar.i_perm = users_inode['i_perm']
                inode_insertar.i_s = users_inode['i_s'] + len(datos)

                # Actualizamos el iNodo
                fp.seek(super['s_inode_start'] + ctypes.sizeof(iNodesTable))
                fp.write(self.packiNodesTable(inode_insertar))

                return True

            else:
                print("No es posible realizar la operacion")
                return False


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
    def pack_file_block(self, file_block):
        # Define the format string for the struct packing based on the field's size
        format_string = f"{len(file_block.b_content)}s"

        # Pack the FileBlock instance into a binary representation
        packed_data = struct.pack(format_string, file_block.b_content)

        return packed_data

    def getFolderBlock(self, definedPath, start):
        print("--->")
        print(definedPath)
        print("00000")
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpackFolderBlock(packed_data, start)

        # Imprimir los campos de FolderBlock
        print("-------FolderBlock ---------")
        for item in unpacked_data['b_content']:
            print("b_name->" + item.b_name.decode('utf-8'))
            print("b_inodo->" + str(item.b_inodo))

        return unpacked_data
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






    def packFolderBlock(self, folder_block):
       # puedo resolver el problema de manera similar a como
        packed_data = b''
        for i in range(4):
            packed_data += struct.pack('12s', folder_block.b_content[i].b_name.encode('utf-8'))
            packed_data += struct.pack('i', folder_block.b_content[i].b_inodo)
        return packed_data
    def guardarJournal(self, operacion, tipo, permisos, nombre, content, currentSession):
        try:
            super = Superblock()
            registro = Journal()
            registro.journal_operation_type = operacion.encode('utf-8')
            registro.journal_type = tipo
            registro.journal_name = nombre.encode('utf-8')
            registro.journal_content = content.encode('utf-8')
            registro.journal_date = int(time.time())
            registro.journal_owner = currentSession.id_user
            registro.journal_permissions = permisos

            with open(currentSession.direccion, "rb+") as fp:
                # Buscar el último journal
                registroAux = Journal()
                ultimo = False

                fp.seek(currentSession.inicioSuper)
                super_data = fp.read(ctypes.sizeof(super))
                super.unpack(super_data)

                inicio_journal = currentSession.inicioSuper + ctypes.sizeof(Superblock)
                final_journal = super.s_bm_inode_start

                fp.seek(inicio_journal)
                while fp.tell() < final_journal and not ultimo:
                    registroAux_data = fp.read(ctypes.sizeof(registroAux))
                    registroAux.unpack(registroAux_data)
                    if registroAux.journal_type != 0 and registroAux.journal_type != 1:
                        ultimo = True

                fp.seek(fp.tell() - ctypes.sizeof(Journal))
                fp.write(registro.pack())

        except Exception as e:
            print("Error:", e)

    '''
    BUSCAR BIT
    '''
    def buscarBit(self, fp, tipo, fit, currentSession):
        super = Superblock()
        inicio_bm = 0
        tempBit = '0'
        bit_libre = -1
        tam_bm = 0

        fp.seek(currentSession.inicioSuper)
        super_data = fp.read(ctypes.sizeof(super))
        super.unpack(super_data)

        if tipo == 'I':
            tam_bm = super.s_inodes_count
            inicio_bm = super.s_bm_inode_start
        elif tipo == 'B':
            tam_bm = super.s_blocks_count
            inicio_bm = super.s_bm_block_start

        # Tipo de ajuste a utilizar
        if fit == 'F':  # Primer ajuste
            for i in range(tam_bm):
                fp.seek(inicio_bm + i)
                tempBit = chr(fp.read(1)[0])
                if tempBit == '0':
                    bit_libre = i
                    return bit_libre

            if bit_libre == -1:
                return -1

        elif fit == 'B':  # Mejor ajuste
            libres = 0
            auxLibres = -1

            for i in range(tam_bm):  # Primer recorrido
                fp.seek(inicio_bm + i)
                tempBit = chr(fp.read(1)[0])
                if tempBit == '0':
                    libres += 1
                    if i + 1 == tam_bm:
                        if auxLibres == -1 or auxLibres == 0:
                            auxLibres = libres
                        else:
                            if auxLibres > libres:
                                auxLibres = libres
                        libres = 0
                elif tempBit == '1':
                    if auxLibres == -1 or auxLibres == 0:
                        auxLibres = libres
                    else:
                        if auxLibres > libres:
                            auxLibres = libres
                    libres = 0

            # Implement your logic for best fit here
            # You need to find the best fit block and return its index
            # Implement logic to track the 'auxLibres' variable and find the best fit block

        return bit_libre  # Return

    '''
    PERMISO 
    '''
    def permisos_de_escritura(self, permisos, flag_user, flag_group):
        permisos_str = str(permisos)
        propietario = permisos_str[0]
        grupo = permisos_str[1]
        otros = permisos_str[2]

        if (propietario in ['2', '3', '6', '7'] and flag_user) or (
                grupo in ['2', '3', '6', '7'] and flag_group) or otros in ['2', '3', '6', '7']:
            return True

        return False

    ########### - RM USER
    '''
    Input -> flag_login, currentSession, username 
    Output-> none
    Functionality -> Elimina un usuario del archivo users.txt
    '''
    def rmusr(self, flag_login, currentSession):
        userName = self.name # Assuming name is a valid variable
        if flag_login:
            if currentSession.id_user == 1 and currentSession.id_grp == 1:  # Usuario root
                if self.buscarUsuario(userName, currentSession):
                    print("Usuario Encontrado")
                    eliminado = self.eliminarUsuario(userName, currentSession)
                    if eliminado:
                        return "Usuario eliminado con exito"
                    else:
                        return "No se pudo eliminar el usuario"
                else:
                    print("ERROR el usuario no existe")
                    return "ERROR el usuario no existe"
            else:
                print("ERROR solo el usuario root puede ejecutar este comando")
                return "ERROR solo el usuario Root puede ejecutar esto"
        else:
            print("ERROR necesita iniciar sesión para poder ejecutar este comando")
            return "ERROR necesita iniciar sesión para poder ejecutar este comando"



    '''
    Input -> Sesion Actual y Nombre del Usuario que se quiere eliminar 
    Output-> True si el usuario existe, False si no existe 
    Functionality -> Busca un usuario en el archivo users.txt
    '''
    def buscarUsuario(self, name, currentSession):
        cadena = b""
        super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)

        # Nos posicionamos en el inodo del archivo users.txt
        inodo = self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion)
        archivo = open(currentSession.direccion, "rb+")
        contenido = ""
        for i in range(15):
            if inodo['i_block'][i] != -1:# Recorriendo los apuntadores directos del 1er iNODO (15)
                print(inodo['i_block'][i])
                print(i)
                # block_offset -> por donde vamos?
                block_offset = super['s_block_start'] + (inodo['i_block'][i] * ctypes.sizeof(FolderBlock))
                archivo.seek(block_offset)
                folder_data = []
                #
                for j in range(int(inodo['i_block'][i]) + 1): #
                    #print("Content----")

                    # Sustituir por un get
                    contenido = archivo.read(ctypes.sizeof(FolderBlock))
                    #print(contenido)
                    folder_entry = struct.unpack(f'{len(contenido)}s', contenido)

                    folder_data.append(folder_entry)
                    print(folder_data)


        archivo.close()

        archivo.close()
        # verificamos si la contraseña es correcta
        new_contenido = folder_data[0][0].decode("utf-8")

        for token in new_contenido.split('\n'):
            id, tipo, user = token.split(',')[0], token.split(',')[1], token.split(',')[3]
            print("id", id)
            print("tipo", tipo)
            print("user", user)


            if id != "0" and tipo == "U" and user == name:
                return True

        return False

    def getID_usr(self, currentSession):
        try:
            with open(currentSession.direccion, "rb+") as fp:
                cadena = b""
                res = 0
                super = Superblock()
                inodo = iNodesTable()

                super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)

                # Nos posicionamos en el inodo del archivo users.txt
                inodo = self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion)

                for i in range(15):
                    if inodo['i_block'][i] != -1:
                        archivo = FolderBlock()
                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * inodo['i_block'][i])
                        archivo_data = fp.read(ctypes.sizeof(archivo))
                        archivo.unpack(archivo_data)
                        for j in range(63):
                            actual = archivo.b_content[j:j + 1]
                            if actual == b'\n':
                                id, tipo = cadena.split(b',')[0], cadena.split(b',')[1]
                                if id != b"0" and tipo == b"U":
                                    res += 1
                                cadena = b""
                            else:
                                cadena += actual

        except Exception as e:
            print("Error:", e)

        return res + 1
    '''
    Input 
    Output 
    Functionality 
    '''
    def eliminarUsuario(self, name, currentSession): # 80% sure it will fail
        try:
            with open(currentSession.direccion, "rb+") as fp:
                archivo = FolderBlock()

                col = 1
                palabra = b""
                posicion = 0
                numBloque = 0
                id = -1
                tipo = b'\0'
                grupo = b""
                usuario = b""
                flag = False

                super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper) # Error

                # Nos posicionamos en el inodo del archivo users.txt
                fp.seek(super['s_inode_start'] + ctypes.sizeof(iNodesTable))
                inodo = self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion)

                for i in range(14):
                    if inodo['i_block'][i] != -1:
                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * inodo['i_block'][i])
                        archivo_data = fp.read(ctypes.sizeof(archivo))
                        archivo.unpack(archivo_data)
                        for j in range(63):
                            actual = archivo.b_content[j:j + 1]
                            if actual == b'\n':
                                if tipo == b'U':
                                    if usuario == name.encode('utf-8'):
                                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * numBloque)
                                        archivo_data = fp.read(ctypes.sizeof(archivo))
                                        archivo.b_content = archivo.b_content[:posicion] + b'0' + archivo.b_content[
                                                                                                  posicion + 1:]
                                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * numBloque)
                                        fp.write(archivo.pack())
                                        print("Usuario eliminado con éxito")
                                        flag = True
                                        break
                                    usuario = b""
                                    grupo = b""
                                col = 1
                                palabra = b""
                            elif actual != b',':
                                palabra += actual
                                col += 1
                            elif actual == b',':
                                if col == 2:
                                    id = int(palabra)
                                    posicion = j - 1
                                    numBloque = inodo['i_block'][i]
                                elif col == 4:
                                    tipo = palabra[:1]
                                elif not grupo:
                                    grupo = palabra
                                elif not usuario:
                                    usuario = palabra
                                col += 1
                                palabra = b""
                        if flag:
                            break

        except Exception as e:
            print("Error:", e)
            return "ERROR"
        return flag # True or False

    import os
    import struct

    def buscar_carpeta_archivo(self, stream, path, currentSession):
        super_struct = struct.Struct('I I 8s I I I I I I')
        super_size = super_struct.size

        lista = []
        token = path.split("/")
        cont = 0
        num_inodo = 0

        for t in token:
            lista.append(t)
            cont += 1

        stream.seek(currentSession.inicioSuper, os.SEEK_SET)
        super_data = stream.read(super_size)
        super_values = super_struct.unpack(super_data)
        num_inodo = super_values[7]  # Byte where the inode starts

        for cont2 in range(cont):
            stream.seek(num_inodo, os.SEEK_SET)
            inodo_data = stream.read(128)
            inodo_values = struct.unpack('I I 15I', inodo_data)
            siguiente = 0

            for i in range(15):
                if inodo_values[i] != -1:  # Direct pointers
                    byte_bloque = self.byte_inodo_bloque(stream, inodo_values[i], '2')
                    stream.seek(byte_bloque, os.SEEK_SET)

                    if i < 12:
                        carpeta_data = stream.read(64)
                        carpeta_values = struct.unpack('4s 12s', carpeta_data)

                        for j in range(4):
                            if (cont2 == cont - 1) and (carpeta_values[j][0] == lista[cont2].encode('utf-8')):
                                return carpeta_values[j][1]
                            elif (cont2 != cont - 1) and (carpeta_values[j][0] == lista[cont2].encode('utf-8')):
                                num_inodo = self.byte_inodo_bloque(stream, carpeta_values[j][1], '1')
                                siguiente = 1
                                break
                    elif i == 12:  # Indirect pointer
                        apuntador_data = stream.read(64)
                        apuntador_values = struct.unpack('16I', apuntador_data)

                        for j in range(16):
                            if apuntador_values[j] != -1:
                                byte_bloque = self.byte_inodo_bloque(stream, apuntador_values[j], '2')
                                stream.seek(byte_bloque, os.SEEK_SET)
                                carpeta_data = stream.read(64)
                                carpeta_values = struct.unpack('4s 12s', carpeta_data)

                                for k in range(4):
                                    if (cont2 == cont - 1) and (carpeta_values[k][0] == lista[cont2].encode('utf-8')):
                                        return carpeta_values[k][1]
                                    elif (cont2 != cont - 1) and (carpeta_values[k][0] == lista[cont2].encode('utf-8')):
                                        num_inodo = self.byte_inodo_bloque(stream, carpeta_values[k][1], '1')
                                        siguiente = 1
                                        break

                                if siguiente == 1:
                                    break
            return -1

    def buscarContentLibre(self, stream, numInodo, inodo, carpeta, apuntadores, content, bloque, pointer, currentSession):
        libre = 0
        super = struct.Struct('I I I I I I I I I I I I')
        stream.seek(currentSession.inicioSuper)
        super_data = struct.unpack(super.format, stream.read(super.size))

        stream.seek(super_data[5] + struct.calcsize('I') * numInodo)
        inodo_data = struct.unpack('I H H H H H H 8I', stream.read(struct.calcsize('I H H H H H H 8I')))
        inodo.inodo = inodo_data

        for i in range(15):
            if inodo.inodo[7 + i] != -1:
                if i == 12:
                    stream.seek(super_data[6] + struct.calcsize('I') * inodo.inodo[7 + i])
                    apuntadores_data = struct.unpack('16I', stream.read(struct.calcsize('16I')))
                    apuntadores.apuntadores = apuntadores_data

                    for j in range(16):
                        if apuntadores.apuntadores[j] != -1:
                            stream.seek(super_data[6] + struct.calcsize('I') * apuntadores.apuntadores[j])
                            carpeta_data = struct.unpack('4I 1024s', stream.read(struct.calcsize('4I 1024s')))
                            carpeta.b_content = carpeta_data[0:4]

                            for k in range(4):
                                if carpeta.b_content[k] == -1:
                                    libre = 1
                                    bloque[0] = i
                                    pointer[0] = j
                                    content[0] = k
                                    break
                        if libre == 1:
                            break
                elif i == 13:
                    pass  # Handle Apuntador indirecto doble (not implemented)
                elif i == 14:
                    pass  # Handle Apuntador indirecto triple (not implemented)
                else:
                    stream.seek(super_data[6] + struct.calcsize('1024s') * inodo.inodo[7 + i])
                    carpeta_data = struct.unpack('4I 1024s', stream.read(struct.calcsize('4I 1024s')))
                    carpeta.b_content = carpeta_data[0:4]

                    for j in range(4):
                        if carpeta.b_content[j] == -1:
                            libre = 1
                            bloque[0] = i
                            content[0] = j
                            break
            if libre == 1:
                break

        return libre

    '''
    BYTE INODO
    '''

    def byte_inodo_bloque(self, stream, pos, tipo, currentSession):
        super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)
        if tipo == '1':
            return super['s_inode_start'] + int(ctypes.sizeof(iNodesTable) * pos)
        elif tipo == '2':
            return super['s_block_start'] + int(ctypes.sizeof(FolderBlock) * pos)
        return 0

    '''
    BUSCAR CARPETAS ARCHIVO 
    
    '''
    def buscar_carpeta_archivo(self, stream, path, currentSession):
        lista = []
        token = path.split("/")
        cont = 0
        numInodo = 0

        for t in token:
            lista.append(t)
            cont += 1

        super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)

        numInodo = super['s_inode_start']  # Byte donde inicia el inodo

        for cont2 in range(cont):
            #stream.seek(numInodo, 0)
            #inodo = InodoTable()
            inodo = self.getiNodesTable(numInodo, currentSession.direccion)

            siguiente = 0

            for i in range(15):
                if inodo['i_block'][i] != -1:  # Apuntadores directos
                    byteBloque = self.byte_inodo_bloque(stream, inodo['i_block'][i], '2', currentSession)
                    stream.seek(byteBloque, 0)
                    if i < 12:
                        carpeta = FolderBlock()
                        carpeta.__dict__ = stream.read(ctypes.sizeof(FolderBlock))

                        for j in range(4):
                            if (cont2 == cont - 1) and (carpeta.b_content[j].b_name == lista[cont2].c_str()):
                                return carpeta.b_content[j].b_inodo
                            elif (cont2 != cont - 1) and (carpeta.b_content[j].b_name == lista[cont2].c_str()):
                                numInodo = self.byte_inodo_bloque(stream, carpeta.b_content[j].b_inodo, '1', currentSession)
                                siguiente = 1
                                break
                    elif i == 12:  # Apuntador indirecto
                        apuntador = blockPointer()
                        apuntador.__dict__ = stream.read(ctypes.sizeof(blockPointer))

                        for j in range(16):
                            if apuntador.b_pointer[j] != -1:
                                byteBloque = self.byte_inodo_bloque(stream, apuntador.b_pointer[j], '2', currentSession)
                                stream.seek(byteBloque, 0)

                                carpeta = FolderBlock()
                                carpeta.__dict__ = stream.read(ctypes.sizeof(blockPointer))

                                for k in range(4):
                                    if (cont2 == cont - 1) and (carpeta.b_content[k].b_name == lista[cont2].c_str()):
                                        return carpeta.b_content[k].b_inodo
                                    elif (cont2 != cont - 1) and (carpeta.b_content[k].b_name == lista[cont2].c_str()):
                                        numInodo = self.byte_inodo_bloque(stream, carpeta.b_content[k].b_inodo, '1', currentSession)
                                        siguiente = 1
                                        break

                                if siguiente == 1:
                                    break
                    elif i == 13:
                        pass
                    elif i == 14:
                        pass

                    if siguiente == 1:
                        break

        return -1
    '''
    PERMISOS DE ESCRITURA 
    
    '''

    def permisos_de_escritura(self, permisos, flag_user, flag_group):
        permisos_str = str(permisos)
        propietario = permisos_str[0]
        grupo = permisos_str[1]
        otros = permisos_str[2]

        if (propietario in ['2', '3', '6', '7'] and flag_user) or (
                grupo in ['2', '3', '6', '7'] and flag_group) or otros in ['2', '3', '6', '7']:
            return True

        return False

    '''
    Pack Superblock 
    '''
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
    '''
    CREAR INODO 
    '''

    def crear_inodo(self, size, type, perm, currentSession):
        inodo = iNodesTable()
        inodo.i_uid = currentSession.id_user
        inodo.i_gid = currentSession.id_grp
        inodo.i_size = size
        inodo.i_atime = int(time.time())
        inodo.i_ctime = int(time.time())
        inodo.i_mtime = int(time.time())
        inodo.i_block = [-1] * 15
        inodo.i_type = type
        inodo.i_perm = perm
        return inodo

    '''
    CREAR BLOQUE CARPETA
    '''

    def crearBloqueCarpeta(self):
        carpeta = FolderBlock()

        for i in range(4):
            carpeta.b_content[i].b_name = ""
            carpeta.b_content[i].b_inodo = -1

        return carpeta

    '''
    NUEVA CARPETA 
    '''


    def nuevaCarpeta(self, stream, fit, flagP, path, index, currentSession):
        super = Superblock()
        inodo = iNodesTable()
        inodoNuevo = iNodesTable()
        carpeta = FolderBlock()
        carpetaNueva = FolderBlock()
        carpetaAux = FolderBlock()
        apuntadores = blockPointer()
        lista = []
        copiaPath = path
        directorio = os.path.dirname(copiaPath)
        copiaPath = path
        nombreCarpeta = os.path.basename(copiaPath)

        token = path.split("/")
        cont = 0
        numInodo = index
        response = 0

        for t in token:
            cont += 1
            lista.append(t)

        super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)
        new_super = Superblock()
        new_super.s_first_ino = super['s_first_ino']
        new_super.s_first_blo = super['s_first_blo']
        new_super.s_inode_size = super['s_inode_size']
        new_super.s_block_size = super['s_block_size']
        new_super.s_inodes_count = super['s_inodes_count']
        new_super.s_blocks_count = super['s_blocks_count']
        new_super.s_free_blocks_count = super['s_free_blocks_count']
        new_super.s_free_inodes_count = super['s_free_inodes_count']
        new_super.s_mtime = super['s_mtime']
        new_super.s_umtime = super['s_umtime']
        new_super.s_mnt_count = super['s_mnt_count']
        new_super.s_magic = super['s_magic']
        new_super.s_inode_start = super['s_inode_start']
        new_super.s_block_start = super['s_block_start']
        new_super.s_bm_inode_start = super['s_bm_inode_start']
        new_super.s_bm_block_start = super['s_bm_block_start']

        if cont == 1:  # Solo es una carpeta '/home' | '/archivos'
            content = 0
            bloque = 0
            pointer = 0
            libre = self.buscarContentLibre(stream, numInodo, inodo, carpeta, apuntadores, content, bloque, pointer)

            if libre == 1:
                if bloque == 12:  # Apuntador indirecto simple
                    permissions = self.permisos_de_escritura(inodo.i_perm, (inodo.i_uid == currentSession.id_user),
                                                      (inodo.i_gid == currentSession.id_grp))

                    if permissions or (currentSession.id_user == 1 and currentSession.id_grp == 1):
                        buffer = b'1'
                        bitInodo = self.buscarBit(stream, b'I', fit, currentSession)
                        carpeta.b_content[content].b_inodo = bitInodo
                        carpeta.b_content[content].b_name = nombreCarpeta.encode('utf-8')

                        stream.seek(super['s_block_size'] + struct.calcsize('IhcchI') + (
                                    super['s_block_size'] * apuntadores.b_pointer[pointer]))
                        stream.write(carpeta)

                        inodoNuevo = self.crear_inodo(0, b'0', 664, currentSession)
                        bitBloque = self.buscarBit(stream, b'B', fit, currentSession)
                        inodoNuevo.i_block[0] = bitBloque

                        stream.seek(super['s_inode_size'] + (struct.calcsize('IhcchI') * bitInodo))
                        stream.write(inodoNuevo)

                        stream.seek(super['s_bm_inode_start'] + bitInodo)
                        stream.write(buffer)

                        carpetaNueva = self.crearBloqueCarpeta()
                        carpetaNueva.b_content[0].b_inodo = bitInodo
                        carpetaNueva.b_content[1].b_inodo = numInodo
                        carpetaNueva.b_content[0].b_name = b'.'
                        carpetaNueva.b_content[1].b_name = b'..'

                        stream.seek(super['s_block_size'] + (super['s_block_size'] * bitBloque))
                        stream.write(carpetaNueva)

                        stream.seek(super['s_bm_block_start'] + bitBloque)
                        stream.write(buffer)

                        new_super.s_free_inodes_count = super['s_free_inodes_count'] - 1
                        new_super.s_free_blocks_count = super['s_free_blocks_count'] - 1
                        new_super.s_first_ino = super['s_first_ino'] + 1
                        new_super.s_first_blo = super['s_first_blo'] + 1

                        stream.seek(currentSession.inicioSuper)
                        self.packSuperblock(new_super)

                        return 1
                    else:
                        return 2
                elif bloque == 13:  # Apuntador indirecto doble
                    pass
                elif bloque == 14:  # Apuntador indirecto triple
                    pass
                else:  # Apuntadores directos
                    permisos = self.permisos_de_escritura(inodo.i_perm, (inodo.i_uid == currentSession.id_user),
                                                   (inodo.i_gid == currentSession.id_grp))

                    if permisos or (currentSession.id_user == 1 and currentSession.id_grp == 1):
                        buffer = b'1'
                        bitInodo = self.buscarBit(stream, b'I', fit, currentSession)
                        carpeta.b_content[content].b_inodo = bitInodo
                        carpeta.b_content[content].b_name = nombreCarpeta.encode('utf-8')

                        stream.seek(super['s_block_size'] + struct.calcsize('IhcchI') + (
                                    super['s_block_size'] * inodo.i_block[bloque]))
                        stream.write(carpeta)

                        inodoNuevo = self.crear_inodo(0, b'0', 664)
                        bitBloque = self.buscarBit(stream, b'B', fit)
                        inodoNuevo.i_block[0] = bitBloque

                        stream.seek(super['s_inode_size'] + (struct.calcsize('IhcchI') * bitInodo))
                        stream.write(inodoNuevo)

                        stream.seek(super['s_bm_inode_start'] + bitInodo)
                        stream.write(buffer)

                        stream.seek(super['s_bm_block_start'] + bitBloque)
                        stream.write(buffer)

                        carpetaNueva = self.crearBloqueCarpeta()
                        carpetaNueva.b_content[0].b_inodo = bitInodo
                        carpetaNueva.b_content[1].b_inodo = numInodo
                        carpetaNueva.b_content[0].b_name = b'.'
                        carpetaNueva.b_content[1].b_name = b'..'

                        stream.seek(super['s_block_size'] + (super['s_block_size'] * bitBloque))
                        stream.write(carpetaNueva)

                        new_super.s_free_inodes_count = super['s_free_inodes_count'] - 1
                        new_super.s_free_blocks_count = super['s_free_blocks_count'] - 1
                        new_super.s_first_ino = super['s_first_ino'] + 1
                        new_super.s_first_blo = super['s_first_blo'] + 1

                        stream.seek(currentSession.inicioSuper)
                        stream.write(new_super)

                        return 1
                    else:
                        return 2

            elif libre == 0:

                flag = False
                pointer = -1
                stream.seek(super['s_inode_start'] + int(struct.calcsize("=I") * numInodo))
                inodo_data = stream.read(struct.calcsize("=I"))
                inodo_values = struct.unpack("=I", inodo_data)
                inodo.i_block = list(inodo_values)
                for i in range(15):
                    if i == 12:
                        if inodo.i_block[i] == -1:
                            bloque = 12
                            flag = True
                            break
                        else:
                            stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * inodo.i_block[12]))
                            apuntadores_data = stream.read(struct.calcsize("=16I"))
                            apuntadores_values = struct.unpack("=16I", apuntadores_data)
                            apuntadores.b_pointer = list(apuntadores_values)
                            for j in range(16):
                                if apuntadores.b_pointer[j] == -1:
                                    bloque = 12
                                    pointer = j
                                    break
                        if flag or pointer != -1:
                            break
                    elif i == 13:
                        pass  # Apuntador indirecto doble
                    elif i == 14:
                        pass  # Apuntador indirecto triple
                    else:
                        if inodo.i_block[i] == -1:
                            bloque = i
                            break

                if bloque == 12 and flag:
                    permissions = self.permisos_de_escritura(inodo.i_perm, (inodo.i_uid == currentSession.id_user),
                                                      (inodo.i_gid == currentSession.id_grp))
                    if permissions or (currentSession.id_user == 1 and currentSession.id_grp == 1):
                        buffer = 1
                        buffer3 = 3
                        bitBloque = self.buscarBit(stream, 'B', fit, currentSession)
                        inodo.i_block[bloque] = bitBloque
                        stream.seek(super['s_inode_start'] + int(struct.calcsize("=I") * numInodo))
                        stream.write(inodo)
                        stream.seek(super['s_bm_block_start'] + bitBloque)
                        stream.write(struct.pack("=c", bytes([buffer3])))
                        bitBloqueCarpeta = self.buscarBit(stream, 'B', fit, currentSession)
                        apuntadores.b_pointer[0] = bitBloqueCarpeta
                        for i in range(1, 16):
                            apuntadores.b_pointer[i] = -1
                        stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloque))
                        stream.write(apuntadores)
                        bitInodo = self.buscarBit(stream, 'I', fit, currentSession)
                        carpetaAux = self.crearBloqueCarpeta()
                        carpetaAux.b_content[0].b_inodo = bitInodo
                        carpetaAux.b_content[0].b_name = nombreCarpeta.encode('utf-8')
                        stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloqueCarpeta))
                        stream.write(carpetaAux)
                        stream.seek(super['s_bm_block_start'] + bitBloqueCarpeta)
                        stream.write(struct.pack("=c", bytes([buffer])))
                        inodoNuevo = self.crear_inodo(0, '0', 664, currentSession)
                        bitBloque = self.buscarBit(stream, 'B', fit, currentSession)
                        inodoNuevo.i_block[0] = bitBloque
                        stream.seek(super['s_inode_start'] + int(struct.calcsize("=I") * bitInodo))
                        stream.write(inodoNuevo)
                        stream.seek(super['s_bm_inode_start'] + bitInodo)
                        stream.write(struct.pack("=c", bytes([buffer])))
                        carpetaNueva = self.crearBloqueCarpeta()
                        carpetaNueva.b_content[0].b_inodo = bitInodo
                        carpetaNueva.b_content[1].b_inodo = numInodo
                        carpetaNueva.b_content[0].b_name = ".".encode('utf-8')
                        carpetaNueva.b_content[1].b_name = "..".encode('utf-8')
                        stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloque))
                        stream.write(carpetaNueva)
                        stream.seek(super['s_bm_block_start'] + bitBloque)
                        stream.write(struct.pack("=c", bytes([buffer])))
                        new_super.s_inode_start = super['s_inode_start']
                        new_super.s_block_start = super['s_block_start']
                        new_super.s_bm_inode_start = super['s_bm_inode_start']
                        new_super.s_bm_block_start = super['s_bm_block_start']
                        new_super.s_first_ino = super['s_first_ino']
                        new_super.s_first_blo = super['s_first_blo']
                        new_super.s_inode_size = super['s_inode_size']
                        new_super.s_block_size = super['s_block_size']
                        new_super.s_inodes_count = super['s_inodes_count']
                        new_super.s_blocks_count = super['s_blocks_count']
                        new_super.s_free_blocks_count = super['s_free_blocks_count']
                        new_super.s_free_inodes_count = super['s_free_inodes_count']
                        new_super.s_mtime = super['s_mtime']
                        new_super.s_umtime = super['s_umtime']
                        new_super.s_mnt_count = super['s_mnt_count']
                        new_super.s_magic = super['s_magic']
                        new_super.s_inode_start = super['s_inode_start']
                        new_super.s_block_start = super['s_block_start']
                        new_super.s_bm_inode_start = super['s_bm_inode_start']



                        new_super.s_free_inodes_count -= 1
                        new_super.s_free_blocks_count -= 3
                        new_super.s_first_ino += 1
                        new_super.s_first_blo += 3
                        stream.seek(currentSession.inicioSuper)
                        stream.write(super)
                        return 1
                    else:
                        return 2
                elif bloque == 12 and not flag:
                    buffer = 1
                    bitBloque = self.buscarBit(stream, 'B', fit, currentSession)
                    apuntadores.b_pointer[pointer] = bitBloque
                    stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * inodo.i_block[12]))
                    stream.write(apuntadores)
                    bitInodo = self.buscarBit(stream, 'I', fit, currentSession)
                    carpetaAux = self.crearBloqueCarpeta()
                    carpetaAux.b_content[0].b_inodo = bitInodo
                    carpetaAux.b_content[0].b_name = nombreCarpeta.encode('utf-8')
                    stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloque))
                    stream.write(carpetaAux)
                    stream.seek(super['s_bm_block_start'] + bitBloque)
                    stream.write(struct.pack("=c", bytes([buffer])))
                    inodoNuevo = self.crearInodo(0, '0', 664)
                    inodoNuevo.i_uid = currentSession.id_user
                    inodoNuevo.i_gid = currentSession.id_grp
                    bitBloque = self.buscarBit(stream, 'B', fit)
                    inodoNuevo.i_block[0] = bitBloque
                    stream.seek(super['s_inode_start'] + int(struct.calcsize("=I") * bitInodo))
                    stream.write(inodoNuevo)
                    stream.seek(super['s_bm_inode_start'] + bitInodo)
                    stream.write(struct.pack("=c", bytes([buffer])))
                    carpetaNueva = self.crearBloqueCarpeta()
                    carpetaNueva.b_content[0].b_inodo = bitInodo
                    carpetaNueva.b_content[1].b_inodo = numInodo
                    carpetaNueva.b_content[0].b_name = ".".encode('utf-8')
                    carpetaNueva.b_content[1].b_name = "..".encode('utf-8')
                    stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloque))
                    stream.write(carpetaNueva)
                    stream.seek(super['s_bm_block_start'] + bitBloque)
                    stream.write(struct.pack("=c", bytes([buffer])))
                    new_super.s_free_inodes_count -= 1
                    new_super.s_free_blocks_count -= 2
                    new_super.s_first_ino += 1
                    new_super.s_first_blo += 2
                    stream.seek(currentSession.inicioSuper)
                    self.packSuperblock(new_super)
                    return 1
                elif bloque == 13:
                    pass  # Apuntador indirecto doble
                elif bloque == 14:
                    pass  # Apuntador indirecto triple
                else:
                    permissions = self.permisos_de_escritura(inodo.i_perm, (inodo.i_uid == currentSession.id_user),
                                                      (inodo.i_gid == currentSession.id_grp))
                    if permissions or (currentSession.id_user == 1 and currentSession.id_grp == 1):
                        buffer = 1
                        bitBloque = self.buscarBit(stream, 'B', fit, currentSession)
                        inodo.i_block[bloque] = bitBloque
                        stream.seek(super['s_inode_start'] + int(struct.calcsize("=I") * numInodo))
                        stream.write(inodo)
                        bitInodo = self.buscarBit(stream, 'I', fit, currentSession)
                        carpetaAux = self.crearBloqueCarpeta()
                        carpetaAux.b_content[0].b_inodo = bitInodo
                        carpetaAux.b_content[0].b_name = nombreCarpeta.encode('utf-8')
                        stream.seek(super['s_block_start'] + int(struct.calcsize("=I") * bitBloque))

                        '''
    CREAR CARPETA 
    
    '''

    def crear_carpeta(self, path, p, currentSession):
        with open(currentSession.direccion, "rb+") as fp:
            super  = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)

            aux = path.encode('utf-8')
            auxPath = aux.decode('utf-8')
            existe = self.buscar_carpeta_archivo(fp, auxPath, currentSession)
            auxPath = aux.decode('utf-8')
            response = -1

            if existe != -1:
                response = 0
            else:
                response = self.nueva_carpeta(fp, currentSession.fit, p, auxPath, 0)

        return response

    '''
    NUEVO ARCHIVO 
    '''
    # Metodo para post revision
    def nuevoArchivo(self, stream, fit, flagP, path, size, contenido, index, auxPath, currentSession):
        # Agregamos algunas cosas
        inodo = iNodesTable()
        carpeta = FolderBlock()
        apuntadores = blockPointer()
        contentSize = "1234567890"
        nombreCarpeta = ""
        numInodo = index
        finalSize = size

        directorio = os.path.dirname(path)
        nombreCarpeta = os.path.basename(path)





        cont = 0
        lista = []
        token = path.split("/")
        # Finalmente se obtiene el nombre del archivo o carpeta
        lista = token

        if len(contenido) != 0:
            archivoCont = None
            try:
                archivoCont = open(contenido, "r")
                finalSize = archivoCont.seek(0, 2)
                archivoCont.seek(0, 0)
                content = archivoCont.read()
            except FileNotFoundError:
                return 3
            finally:
                if archivoCont:
                    archivoCont.close()

        # Read Superblock (not shown in the provided code)
        super = self.getSuperblock(stream, currentSession.inicioSuper)
        if cont == 1:
            bloque = 0
            pointer = 0
            b_content = 0
            libre = self.buscarContentLibre(stream, numInodo, inodo, carpeta, apuntadores, b_content, bloque, pointer, currentSession)

            if libre == 1:
                permisos = self.permisos_de_escritura(inodo.i_perm, inodo.i_uid == currentSession.id_user,
                                               inodo.i_gid == currentSession.id_grp)

                if permisos or (currentSession.id_user == 1 and currentSession.id_grp == 1):
                    buffer = '1'
                    buffer2 = '2'
                    buffer3 = '3'

                    # Add the file to the corresponding block

                    bitInodo = self.buscarBit(stream, 'I', fit)
                    carpeta.b_content[b_content].b_inodo = bitInodo
                    carpeta.b_content[b_content].b_name = nombreCarpeta
                    stream.seek(super['s_block_start'] + int(ctypes.sizeof(FolderBlock)) * inodo.i_block[bloque])
                    stream.write(carpeta)
                    inodoNuevo = self.crear_inodo(0, '1', 664, currentSession)
                    stream.seek(super['s_block_start'] + int(ctypes.sizeof(iNodesTable)) * bitInodo)
                    stream.write(inodoNuevo)
                    stream.seek(super['s_bm_inode_start'] + bitInodo)
                    stream.write(buffer)

                    if finalSize != 0:
                        n = float(finalSize) / 63
                        numBloques = int(math.ceil(n))
                        caracteres = finalSize
                        charNum = 0
                        contChar = 0
                        numInodo = self.buscar_carpeta_archivo(stream, auxPath, currentSession)

                        for i in range(numBloques):
                            archivo = blockPointer()
                            archivo.b_content = [0] * len(archivo.b_content)

                            if i == 12:
                                bitBloqueA = self.buscarBit(stream, 'B', fit, currentSession)
                                stream.seek(super['s_inode_start'] + int(ctypes.sizeof(iNodesTable) * numInodo))
                                inodo = stream.read(iNodesTable)
                                inodo.i_block[i] = bitBloqueA
                                stream.seek(super['s_inode_start'] + int(ctypes.sizeof(iNodesTable) * numInodo))
                                stream.write(inodo)
                                stream.seek(super['s_bm_block_start'] + bitBloqueA)
                                stream.write(buffer3)
                                bitBloque = self.buscarBit(stream, 'B', fit, currentSession)
                                apuntadores.b_pointer[0] = bitBloque

                                for i in range(1, 16):
                                    apuntadores.b_pointer[i] = -1

                                stream.seek(super['s_block_start'] + int(ctypes.sizeof(blockPointer) * bitBloqueA))
                                stream.write(apuntadores)

                                for j in range(63):
                                    if len(content) != 0:
                                        archivo.b_content[j] = content[contChar]
                                        contChar += 1
                                    else:
                                        archivo.b_content[j] = contentSize[charNum]
                                        charNum += 1
                                        if charNum == 10:
                                            charNum = 0

                                stream.seek(super['s_block_start'] + int(ctypes.sizeof(FileBlock) * bitBloque))
                                stream.write(archivo)
                                caracteres -= 63
                            else:
                                print("Handle")
                        # Handle other cases for blocks, similar to the above logic

                    # Cambiamos el superbloque y escribimos
                    new_super = Superblock()
                    # pasamos los valores de super a new_super
                    new_super.s_filesystem_type = super['s_filesystem_type']
                    new_super.s_inodes_count = super['s_inodes_count']
                    new_super.s_first_ino = super['s_first_ino']
                    new_super.s_first_blo = super['s_first_blo']
                    new_super.s_free_blocks_count = super['s_free_blocks_count']
                    new_super.s_free_inodes_count = super['s_free_inodes_count']
                    new_super.s_mtime = super['s_mtime']
                    new_super.s_umtime = super['s_umtime']
                    new_super.s_mnt_count = super['s_mnt_count']
                    new_super.s_magic = super['s_magic']
                    new_super.s_inode_size = super['s_inode_size']
                    new_super.s_block_size = super['s_block_size']
                    new_super.s_first_ino = super['s_first_ino']
                    new_super.s_first_blo = super['s_first_blo']
                    new_super.s_bm_inode_start = super['s_bm_inode_start']
                    new_super.s_bm_block_start = super['s_bm_block_start']
                    new_super.s_inode_start = super['s_inode_start']
                    new_super.s_block_start = super['s_block_start']
                    # Ahora aplicamos los cambios a los valores

                    new_super.s_free_blocks_count -= numBloques
                    new_super.s_free_inodes_count -= 1
                    new_super.s_first_ino += 1
                    new_super.s_first_blo += numBloques
                    stream.seek(currentSession.inicioSuper)
                    stream.write(self.packSuperblock(new_super))
                    return 1

                else:
                    return 2
            else:
                # Handle the case where all blocks are full
                # Similar to the logic in C++
                pass
        else:
            # Handle the directory case
            # Similar to the logic in C++
            pass

        return 0

    '''
    CREAR ARCHIVO 
    crea archivo a partir de algunos valores clave 
    '''

    def crearArchivo(self, path, p, size, cont, currentSession):
        # Open the file for reading and writing in binary mode
        fp = open(currentSession.direccion, "rb+")
        # Define the SuperBloque structure
        # Seek to the position of the SuperBloque
        super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)
        # Convert the 'path' to a string
        auxPath = path
        auxPath2 = path
        # Call the 'buscarCarpetaArchivo' function to check if the file or folder exists
        existe = self.buscar_carpeta_archivo(fp, auxPath, currentSession)
        # Reset 'auxPath' to the original 'path'
        auxPath = path
        # Initialize the 'response' variable
        response = -1
        if existe != -1:
            response = 0
        else:
            response = self.nuevoArchivo(fp, currentSession.fit, p, auxPath, size, cont, 0, auxPath2, currentSession)
        # Close the file
        fp.close()

        return response
    def ruta(self, carpetas):
        return "/".join(carpetas[:-1])

    '''
    MKDIR 
    
    '''
    import os
    def recorrer_mkdir(self, flag, flagPath, valPath, flagP, valP, flag_login, currentSession):
        # Banderas para verificar cuando venga un parametro

        if not flag:
            if flagPath:
                name = os.path.basename(valPath)
                if len(name) <= 11:
                    if flag_login:  # You need to define flag_login and currentSession
                        result = self.crear_carpeta(valPath, valP)  # Define crear_carpeta function
                        if result == 0:
                            print("ERROR: La carpeta ya existe")
                        elif result == 1:

                            print("Carpeta creada con exito")
                        elif result == 2:
                            print("ERROR: No se tienen permisos de escritura")
                        elif result == 3:
                            print("ERROR: No existe el directorio y no esta el parametro -p")
                    else:
                        print("ERROR: necesita iniciar sesion para poder ejecutar este comando")
                else:
                    print("ERROR: el nombre de la carpeta es más grande de lo esperado")
            else:
                print("ERROR: parametro -path no definido")


    '''
    MKFILE
    name -> nombre archivo
    flag_login bool -> esta o no iniciada sesion
    valPath -> path del archivo
    flagP -> si se crea la carpeta padre o no
    valSize -> tamaño del archivo
    valCont -> contenido del archivo
    currentSession -> sesion actual
    '''

    def mkfile_files(self, currentSession):
        name = self.name
        flag_login = currentSession.active
        valPath = self.path
        valSize = self.size

        if(self.r == True):
            flagP = True
        else:
            flagP = False

        # Si se esta utilizando cont
        if self.cont != "":
            # Entonces debemos ir a buscar el path de ese archivo
            self.cont = "." + self.cont
            self.cont = self.cont.replace('"', '')
            self.cont = self.cont.replace("'", '')
            self.cont = self.cont.replace(" ", '')
            self.cont = self.cont.replace("\n", '')
            self.cont = self.cont.replace("\t", '')
            self.cont = self.cont.replace("\r", '')
            self.cont = self.cont.replace("\b", '')
            # Entonces, vamos a buscar el path de ese archivo
            # Si el path es correcto, entonces procedemos a crear el archivo
            # Si el path no es correcto, entonces no se crea el archivo
            # Si el path no existe, entonces no se crea el archivo
            with open(self.cont, "r+") as archivito:
                valCont = archivito.read()

        if len(name) <= 11:
            if flag_login:
                result = self.crearArchivo(valPath, flagP, valSize, valCont, currentSession)
                if result == 1:
                    if currentSession.tipo_sistema == 3:
                        aux = valPath
                        operacion = "mkfile"
                        content = valCont
                    print("Archivo creado con éxito")
                elif result == 2:
                    print("ERROR: el usuario actual no tiene permisos de escritura")
                elif result == 3:
                    print("ERROR: el archivo contenido no existe")
                elif result == 4:
                    print("ERROR: no existe la ruta y no se tiene el parámetro -p")
            else:
                print("ERROR: necesita iniciar sesión para poder ejecutar este comando")
        else:
            print("ERROR: el nombre del archivo es más grande de lo esperado")

    # Para usar la función:
    # mkfile_(name, flag_login, valPath, flagP, valSize, valCont, currentSession)

    def rmgrp(self, flag_login, currentSession):
        grpName = self.name # Asumiendo que esta bien
        if flag_login:
            if currentSession.id_user == 1 and currentSession.id_grp == 1:  # Usuario root
                grupo = self.buscarGrupo(grpName, currentSession)
                if grupo != -1:
                    eliminado = self.eliminarGrupo(grpName, currentSession)
                    if eliminado:
                        return "Grupo eliminado con éxito"
                    else:
                        return "Error al eliminar el grupo"

                else:
                    print("ERROR el grupo no existe")
                    return "ERROR el grupo no existe"
            else:
                print("ERROR solo el usuario root puede ejecutar este comando")
                return "ERROR solo el usuario root puede ejecutar este comando"
        else:
            print("ERROR necesita iniciar sesión para poder ejecutar este comando")
            return "ERROR necesita iniciar sesión para poder ejecutar este comando"
    def mkusr(self, currentSession):
        user = self.user
        passw = self.pwd
        group = self.grp
        flag_login = currentSession.active

        if len(user) <= 10:
            if len(passw) <= 10:
                if len(group) <= 10:
                    if currentSession.active:
                        if currentSession.id_user == 1 and currentSession.id_grp == 1:  # Usuario root
                            if self.buscarGrupo(group, currentSession) != -1:
                                if not self.buscarUsuario(user, currentSession): # verificando que no existe

                                    id = self.getID_usr(currentSession)
                                    datos = f"{id},U,{group},{user},{passw}\n"
                                    u_respuesta = self.agregarUsersTXT(datos, currentSession)
                                    #print("Usuario creado con éxito")
                                    if u_respuesta:
                                        return "Usuario Creado con Exito"
                                    else:
                                        return "Error al crear el usuario"
                                    # Guardamos el registro en el journal si es un sistema EXT3

                                else:
                                    print("ERROR el usuario ya existe")
                                    return "ERROR el usuario ya existe"
                            else:
                                print("ERROR no se encuentra el grupo al que pertenecerá el usuario")
                                return "ERROR no se encuentra el grupo al que pertenecerá el usuario"
                        else:
                            print("ERROR solo el usuario root puede ejecutar este comando")
                            return "Error solo el usuario root puede"
                    else:
                        print("ERROR necesita iniciar sesión para poder ejecutar este comando")
                        return "ERROR necesita iniciar sesión para poder ejecutar este comando"
                else:
                    print("ERROR grupo del usuario excede los 10 caracteres permitidos")
                    return "ERROR grupo del usuario excede los 10 caracteres permitidos"
            else:
                print("ERROR contraseña de usuario excede los 10 caracteres permitidos")
                return "ERROR contraseña de usuario excede los 10 caracteres permitidos"
        else:
            print("ERROR nombre de usuario excede los 10 caracteres permitidos")
            return "ERROR nombre de usuario excede los 10 caracteres permitidos"

    def eliminarGrupo(self, name, currentSession):
        try:
            with open(currentSession.direccion, "rb+") as fp:
                archivo = FolderBlock()

                col = 1
                palabra = b""
                flag = False
                actual = b""
                posicion = 0
                numBloque = 0
                id = -1
                tipo = b"\0"
                grupo = b""

                super = self.getSuperblock(currentSession.direccion, currentSession.inicioSuper)

                # Nos posicionamos en el inodo del archivo users.txt
                fp.seek(super['s_inode_start'] + ctypes.sizeof(iNodesTable))
                inodo = self.getiNodesTable(super['s_inode_start'] + ctypes.sizeof(iNodesTable), currentSession.direccion)

                for i in range(12):
                    if inodo['i_block'][i] != -1:
                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * inodo['i_block'][i])

                        # Get el String del Archivo
                        archivo_data = fp.read(ctypes.sizeof(archivo))
                        archivo.unpack(archivo_data)
                        for j in range(63):
                            actual = archivo.b_content[j:j + 1]
                            if actual == b'\n':
                                if tipo == b'G':
                                    grupo = palabra
                                    if grupo == name.encode('utf-8'):
                                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * numBloque)
                                        archivo_data = fp.read(ctypes.sizeof(FolderBlock))
                                        archivo.unpack(archivo_data)
                                        archivo.b_content = archivo.b_content[:posicion] + b'0' + archivo.b_content[
                                                                                                  posicion + 1:]
                                        fp.seek(super['s_block_start'] + ctypes.sizeof(FolderBlock) * numBloque)
                                        fp.write(archivo.pack())
                                        print("Grupo eliminado con éxito")
                                        flag = True
                                        break
                                col = 1
                                palabra = b""
                            elif actual != b',':
                                palabra += actual
                                col += 1
                            elif actual == b',':
                                if col == 2:
                                    id = int(palabra)
                                    posicion = j - 1
                                    numBloque = inodo['i_block'][i]
                                elif col == 4:
                                    tipo = palabra[0:j]
                                col += 1
                                palabra = b""

                        if flag:

                            break

        except Exception as e:
            print("Error:", e)
            return "ERROR"

        return flag




'''
[X] LOGIN Done and tested 
[ ] MKUSR Done not tested yet 
[ ] MKGRP Done not tested yet 
[ ] RMUSR Done, trustability about 50%
[ ] RMGRP Done, trustability about 40% 
Parte Final 
[ ] MKDIR 
[ ] MKFILE 

'''