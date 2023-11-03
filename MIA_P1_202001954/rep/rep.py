from graphviz import Digraph
import struct
from datetime import datetime, time
import os
import ctypes
import subprocess
import time
import subprocess
import os
import struct
import time

from mount.Discos import DiscosMontados


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

class Journal(ctypes.Structure):
    _fields_ = [
        ("journal_operation_type", ctypes.c_char * 10),
        ("journal_type", ctypes.c_int),
        ("journal_name", ctypes.c_char * 100),
        ("journal_content", ctypes.c_char * 100),
        ("journal_date", ctypes.c_long),  # Assuming time_t is a long
        ("journal_owner", ctypes.c_int),
        ("journal_permissions", ctypes.c_int)
    ]
# ESTRUCTURAS
class content(ctypes.Structure):
    _fields_ = [
        ("b_name", ctypes.c_char * 12),
        ("b_inodo", ctypes.c_int),
    ]
class FolderBlock(ctypes.Structure):
    _fields_ = [
        ("b_content", content * 4),
    ]
class iNodesTable(ctypes.Structure):
    _fields_ = [
        ("i_uid", ctypes.c_char),
        ("I_gid", ctypes.c_char),
        ("i_s", ctypes.c_int),
        ("i_atime", ctypes.c_int),
        ("i_ctime", ctypes.c_int),
        ("s_mtime", ctypes.c_int),
        ("i_block", ctypes.c_int),
        ("i_type", ctypes.c_int),
        ("i_perm", ctypes.c_int),
    ]

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


class blockPointer(ctypes.Structure):
    _fields_ = [
        ("b_pointers", ctypes.c_int * 16),
    ]


class FileBlock(ctypes.Structure):
    _fields_ = [
        ("b_content", ctypes.c_char * 64),
    ]
class EBR(ctypes.Structure):
    _fields_ = [
        ("part_status", ctypes.c_char),
        ("part_fit", ctypes.c_char),
        ("part_start", ctypes.c_int),
        ("part_size", ctypes.c_int),
        ("part_next", ctypes.c_int),
        ("part_name", ctypes.c_char * 16),
        # Add other fields from the 'particion' struct here
    ]


# CLASE REP
class rep:
    def __init__(self):
        self.name ="" # mbr | disk | inode | Journaling | block | bm_inode | bm_block | tree | sb | file | ls
        self.path =""
        self.id = ""
        self.ruta = ""

    def reportar(self):
        if self.name.lower() == 'mbr':
            self.reporteMBR() ## Done
        elif self.name.lower() == 'disk':
            self.reporteDisk() ## Done
        elif self.name.lower() == 'inode':
            self.reporteInode()
        elif self.name.lower() == 'journaling':
            self.reporteJournaling()
        elif self.name.lower() == 'block':
            self.reporteBlock() ##
        elif self.name.lower() == 'bm_inode':
            self.reporteBm_iNode()
        elif self.name.lower() == 'bm_block':
            #reporte.name = "bm_block"
            self.reporteBm_block()
        elif self.name.lower() == 'tree':
            #reporte.name = "tree"
            self.reporteTree()
        elif self.name.lower() == 'sb':
            #reporte.name = "sb"
            self.reporteSB() ## DONE
        elif self.name.lower() == 'file':
            #reporte.name = "file"
            self.reporteFile()
        elif self.name.lower() == 'ls':
            #reporte.name = "ls"
            self.reporteLS()
        else:
            print("No se reconoce el reporte")

    def unpack_mbr(self, packed_data):
        unpacked_mbr = {}

        mbr_size = struct.calcsize("iii1s")
        mbr_data = packed_data[:mbr_size]  # probablemente
        unpacked_mbr['mbr_tamano'], unpacked_mbr['mbr_fecha_creacion'], unpacked_mbr['mbr_dsk_signature'], unpacked_mbr[
            'mbr_fit'] = struct.unpack("iii1s", mbr_data)

        unpacked_datetime = datetime.fromtimestamp(unpacked_mbr['mbr_fecha_creacion'])
        print(unpacked_datetime)
        partition_size = struct.calcsize("cccii16s")
        unpacked_mbr['mbr_particiones'] = []
        partition_data = packed_data[mbr_size:]
        num_partitions = len(partition_data) // partition_size

        for i in range(num_partitions):
            partition_start = i * partition_size
            partition_end = partition_start + partition_size
            partition = struct.unpack("cccii16s", partition_data[partition_start:partition_end])
            unpacked_mbr['mbr_particiones'].append(partition)

        return unpacked_mbr
    def read_packed_data_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            packed_data = file.read()
        return packed_data


    def unpack_ebr(self, packed_data, start):
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
    def getEBR(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpack_ebr(packed_data, start)
        print("-------EBR 1 ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
        return unpacked_data

    def get_filename_without_extension(self, path):
        # Use os.path.basename() to extract the filename and os.path.splitext() to split the filename and extension
        filename = os.path.basename(path)
        filename_without_extension, _ = os.path.splitext(filename)
        return filename_without_extension
    def graficarMBR(self):
        print("[--------- MBR ----------]")
        print("00000000")
        print(self.id)
        print("00000000")
        direccion = DiscosMontados.returnPath(self.id)
        if(direccion != False):
            auxDir = direccion
            print(auxDir)
            destino = os.path.dirname("." + self.path)
            filename = self.get_filename_without_extension(self.path)
            self.createDir(destino)
            extension = "png"
            graphDot = None

            with open(auxDir, "rb") as fp:
                print("Abriendo archivo...")
                with open(filename + ".dot", "w") as graphDot:
                    print("Creando archivo dot...")

                    # Encabezado
                    graphDot.write("digraph G {\n")
                    graphDot.write("subgraph cluster{\n label=\"MBR\"")
                    graphDot.write("\ntbl[shape=box,label=<\n")
                    graphDot.write("<table border='0' cellborder='1' cellspacing='0' width='300' height='200'>\n")
                    graphDot.write("<tr>  <td width='150'> <b>Nombre</b> </td> <td width='150'> <b>Valor</b> </td>  </tr>\n")

                    # Unpacking MBR
                    print("getting the MBR")
                    mbr_new = self.getMBR(auxDir)

                    tamano = str(mbr_new['mbr_tamano'])
                    graphDot.write("<tr>  <td><b>mbr_tamaño</b></td><td>%s</td>  </tr>\n" % tamano)

                    fecha = str(datetime.fromtimestamp(mbr_new['mbr_fecha_creacion']))
                    graphDot.write("<tr>  <td><b>mbr_fecha_creacion</b></td> <td>%s</td>  </tr>\n" % fecha)

                    graphDot.write("<tr>  <td><b>mbr_disk_signature</b></td> <td>%s</td>  </tr>\n" % str(mbr_new['mbr_dsk_signature']))
                    graphDot.write("<tr>  <td><b>Disk_fit</b></td> <td>%s</td>  </tr>\n" % str(mbr_new['mbr_fit']))

                    index_Extendida = -1
                    for i in range(4):
                        if (
                                # status -0, type -1 , fit -2, start -3, size -4, name -5
                                mbr_new['mbr_particiones'][i][3] != -1
                        ):
                            if mbr_new['mbr_particiones'][i][1].lower() == 'e':
                                index_Extendida = i
                            # status -0, type -1 , fit -2, start -3, size -4, name -5
                            status = "0" if mbr_new['mbr_particiones'][i][0] == '0' else "2"
                            graphDot.write(
                                "<tr>  <td><b>part_status_%d</b></td> <td>%s</td>  </tr>\n" % (i + 1, status))
                            graphDot.write("<tr>  <td><b>part_type_%d</b></td> <td>%s</td>  </tr>\n" % (
                            i + 1, mbr_new['mbr_particiones'][i][1]))
                            graphDot.write("<tr>  <td><b>part_fit_%d</b></td> <td>%s</td>  </tr>\n" % (
                            i + 1, mbr_new['mbr_particiones'][i][2]))
                            graphDot.write("<tr>  <td><b>part_start_%d</b></td> <td>%s</td>  </tr>\n" % (
                            i + 1, mbr_new['mbr_particiones'][i][3]))
                            graphDot.write("<tr>  <td><b>part_size_%d</b></td> <td>%s</td>  </tr>\n" % (
                            i + 1, mbr_new['mbr_particiones'][i][4]))
                            graphDot.write("<tr>  <td><b>part_name_%d</b></td> <td>%s</td>  </tr>\n" % (
                            i + 1, mbr_new['mbr_particiones'][i][5]))

                    graphDot.write("</table>\n")
                    graphDot.write(">];\n}\n")

                    if index_Extendida != -1:
                        # Ahora buscamos el EBR inicial de la particion
                        index_ebr = 1
                        # El start debe ser el inicio de la parrrticion
                        logicPartitionCounter = 0
                        ebr_establecido = self.getEBR("." + self.path, mbr_new['mbr_particiones'][index_Extendida][3])['part_start']
                        punteroActual = 0
                        while True:

                            # Sistema para ir hacia adelante en el MBR
                            if logicPartitionCounter == 0 and ebr_establecido != -1:
                                ebr_inicial = self.getEBR("." + self.path, mbr_new['mbr_particiones'][index_Extendida][3])
                                logicPartitionCounter += 1
                            elif logicPartitionCounter == 1 and ebr_establecido != -1:
                                # Si no, leemos la siguiente direccion y leemos
                                punteroActual = ebr_inicial['part_next']
                                ebr_inicial = self.getEBR("." + self.path, punteroActual)
                                logicPartitionCounter += 1
                            elif logicPartitionCounter > 1 and ebr_establecido != -1:
                                # Si no, leemos la siguiente direccion y leemos
                                punteroActual = ebr_inicial['part_next']
                                ebr_inicial = self.getEBR("." + self.path, punteroActual)
                                logicPartitionCounter += 1
                            else:
                                break


                            if ebr_inicial['part_status'] != '0':
                                graphDot.write("subgraph cluster_%d{\n label=\"EBR_%d\"\n" % (index_ebr, index_ebr))
                                graphDot.write("\ntbl_%d[shape=box, label=<\n " % index_ebr)
                                graphDot.write(
                                    "<table border='0' cellborder='1' cellspacing='0'  width='300' height='160' >\n ")
                                graphDot.write(
                                    "<tr>  <td width='150'><b>Nombre</b></td> <td width='150'><b>Valor</b></td>  </tr>\n")

                                status = "0" if ebr_inicial['part_status'].decode() == '0' else "2"
                                graphDot.write("<tr>  <td><b>part_status_1</b></td> <td>%s</td>  </tr>\n" % ebr_inicial['part_status'].decode())
                                graphDot.write(
                                    "<tr>  <td><b>part_fit_1</b></td> <td>%c</td>  </tr>\n" % ebr_inicial['part_fit'])
                                graphDot.write(
                                    "<tr>  <td><b>part_start_1</b></td> <td>%d</td>  </tr>\n" % ebr_inicial['part_start'])
                                graphDot.write(
                                    "<tr>  <td><b>part_size_1</b></td> <td>%d</td>  </tr>\n" % ebr_inicial['part_size'])
                                graphDot.write(
                                    "<tr>  <td><b>part_next_1</b></td> <td>%d</td>  </tr>\n" % ebr_inicial['part_next'])
                                graphDot.write(
                                    "<tr>  <td><b>part_name_1</b></td> <td>%s</td>  </tr>\n" % ebr_inicial['part_name'].decode())
                                graphDot.write("</table>\n")
                                graphDot.write(">];\n}\n")
                                index_ebr += 1



                    graphDot.write("}\n")

            print("Ingresando comando a consola...")
            comando = "dot -T" + extension + " grafica.dot -o " + destino
            os.system(comando)
            print("Reporte generado con exito")
        else:
            print("No se encontro el disco")


        #except Exception as e:
        #   print("Error:", str(e))


    def unpack_iNodesTable(packed_data, start):
        iNodesTable_size = struct.calcsize("cciiiiiii")
        iNodesTable_data = packed_data[start:start + iNodesTable_size]
        unpacked_iNodesTable = struct.unpack("cciiiiiii", iNodesTable_data)

        # Create a dictionary with field names as keys
        field_names = [field[0] for field in iNodesTable._fields_]
        unpacked_dict = dict(zip(field_names, unpacked_iNodesTable))

        return unpacked_dict
    def getiNodesTable(self, start, definedPath):
        packed_data = self.read_packed_data_from_file(definedPath)
        unpacked_data = self.unpack_iNodesTable(packed_data, start)


        print("-------iNodesTable---------")
        print("i_uid->" + str(unpacked_data['i_uid']))
        print("I_gid->" + str(unpacked_data['i_gid']))
        print("i_s->" + str(unpacked_data['i_s']))
        print("i_atime->" + str(unpacked_data['i_atime']))
        print("i_ctime->" + str(unpacked_data['i_ctime']))
        print("s_mtime->" + str(unpacked_data['s_mtime']))
        print("i_block->" + str(unpacked_data['i_block']))
        print("i_perm->" + str(unpacked_data['i_perm']))
        return unpacked_data

    def getFolderBlock(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpack_folderblock(packed_data, start)
        print("-------Superbloque ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
        return unpacked_data

    def getFileBlock(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpack_fileblock(packed_data, start)
        print("-------Superbloque ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
        return unpacked_data

    def unpack_block_pointer(self, packed_data, start):
        # Assuming packed_data is a bytes object
        block_pointer = blockPointer()
        ctypes.memmove(ctypes.byref(block_pointer), packed_data[start:], ctypes.sizeof(block_pointer))
        return block_pointer

    def getApuntadores(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro # ->>
        unpacked_data = self.unpack_block_pointer(packed_data, start)
        print("-------Apuntadores ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
        return unpacked_data
# Graficar Tree

    def unpack_fileblock(self, packed_data, start):
        unpacked_folderblock = []

        for i in range(4):  # Assuming there are 4 content items in a FolderBlock
            content_size = ctypes.sizeof(FileBlock.b_content)
            content_data = packed_data[start:start + content_size]
            unpacked_content = struct.unpack("64s", content_data)[0].decode("utf-8").strip('\x00')

            # Append each content item to the unpacked_folderblock list
            unpacked_folderblock.append({"data": unpacked_content})
            start += content_size


        return unpacked_folderblock




    def unpack_folderblock(self, packed_data, start):
        unpacked_folderblock = []

        for i in range(4):  # Assuming there are 4 content items in a FolderBlock
            content_size = ctypes.sizeof(FileBlock.b_content)
            content_data = packed_data[start:start + content_size]
            unpacked_content = struct.unpack("64s", content_data)[0].decode("utf-8").strip('\x00')

            # Append each content item to the unpacked_folderblock list
            unpacked_folderblock.append({"data": unpacked_content})

            start += content_size

        return unpacked_folderblock
    def graficar_tree(self,  start_super):
        try:
            direccion = self.path # direccion del archivo
            destino = "." # destino de la imagen
            extension = "png" # extension de la imagen

            with open(direccion, "rb+") as fp:
                # Arreglar metodos
                super_data = self.getSuperblock(direccion, start_super)
                inodo = self.getiNodesTable(super_data['s_inode_start'], direccion)
                carpeta = self.getFolderBlock(direccion, super_data['s_block_start'])     #
                archivo = self.getFileBlock(super_data['s_block_start'], inodo['i_block'])       #
                apuntadores = self.getApuntadores(super_data['s_block_start'], inodo['i_block']) #

            with open("grafica.dot", "w") as graph:
                graph.write("digraph G{\n\n")
                graph.write("    rankdir=\"LR\" \n")

                aux = super_data['s_bm_inode_start']
                i = 0

                while aux < super_data['s_bm_block_start']:
                    fp.seek(super_data['s_bm_inode_start'] + i)
                    buffer = chr(fp.read(1)[0])
                    aux += 1
                    port = 0

                    if buffer == '1':
                        fp.seek(super_data['s_inode_start'] + ctypes.sizeof(iNodesTable) * i)
                        fp.readinto(inodo)

                        graph.write(f"    inodo_{i} [shape=plaintext fontname=\"Century Gothic\" label=<\n")
                        graph.write("   <table bgcolor=\"royalblue\" border='0' >\n")
                        graph.write(f"    <tr> <td colspan='2'><b>Inode {i}</b></td></tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_uid </td> <td bgcolor=\"white\"> {inodo.i_uid} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_gid </td> <td bgcolor=\"white\"> {inodo.i_gid} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_size </td><td bgcolor=\"white\"> {inodo.i_size} </td> </tr>\n")

                        tm = time.localtime(inodo['i_atime'])
                        fecha = time.strftime('%d/%m/%y %H:%S', tm)
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_atime </td> <td bgcolor=\"white\"> {fecha} </td> </tr>\n")

                        tm = time.localtime(inodo['i_ctime'])
                        fecha = time.strftime('%d/%m/%y %H:%S', tm)
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_ctime </td> <td bgcolor=\"white\"> {fecha} </td> </tr>\n")

                        tm = time.localtime(inodo['i_mtime'])
                        fecha = time.strftime('%d/%m/%y %H:%S', tm)
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_mtime </td> <td bgcolor=\"white\"> {fecha} </td> </tr>\n")

                        for b in range(15):
                            graph.write(
                                f"    <tr> <td bgcolor=\"lightsteelblue\"> i_block_{port} </td> <td bgcolor=\"white\" port=\"f{port}\"> {inodo['i_block'][b]} </td></tr>\n")
                            port += 1

                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_type </td> <td bgcolor=\"white\"> {inodo['i_type']} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_perm </td> <td bgcolor=\"white\"> {inodo['i_perm']} </td>  </tr>\n")
                        graph.write("   </table>>]\n\n")

                        for j in range(15):
                            port = 0

                            if inodo['i_block'][j] != -1:
                                fp.seek(super_data['s_bm_block_start'] + inodo['i_block'][j])
                                buffer = chr(fp.read(1)[0])

                                if buffer == '1':
                                    fp.seek(super_data['s_block_start'] + ctypes.sizeof(FolderBlock) * inodo.i_block[j])
                                    fp.readinto(carpeta)

                                    graph.write(
                                        f"    bloque_{inodo['i_block'][j]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                    graph.write("   <table bgcolor=\"seagreen\" border='0'>\n")
                                    graph.write(
                                        f"    <tr> <td colspan='2'><b>Folder block {inodo['i_block'][j]}</b></td></tr>\n")
                                    graph.write(
                                        f"    <tr> <td bgcolor=\"mediumseagreen\"> b_name </td> <td bgcolor=\"mediumseagreen\"> b_inode </td></tr>\n")

                                    for c in range(4):
                                        graph.write(
                                            f"    <tr> <td bgcolor=\"white\" > {carpeta['b_content'][c]['b_name']} </td> <td bgcolor=\"white\"  port=\"f{port}\"> {carpeta.b_content[c].b_inodo} </td></tr>\n")
                                        port += 1

                                    graph.write("   </table>>]\n\n")

                                    for c in range(4):
                                        if carpeta['b_content'][c].b_inodo != -1:
                                            if carpeta['b_content'][c].b_name != "." and carpeta['b_content'][
                                                c].b_name != "..":
                                                graph.write(
                                                    f"    bloque_{inodo['i_block'][j]}:f{c} -> inodo_{carpeta['b_content'][c].b_inodo};\n")
                                elif buffer == '2':
                                    fp.seek(super_data['s_block_start'] + ctypes.sizeof(FolderBlock) * inodo['i_block'][j])
                                    fp.readinto(archivo)

                                    graph.write(
                                        f"    bloque_{inodo['i_block'][j]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                    graph.write("   <table border='0' bgcolor=\"sandybrown\">\n")
                                    graph.write(f"    <tr> <td> <b>File block {inodo['i_block'][j]}</b></td></tr>\n")
                                    graph.write(f"    <tr> <td bgcolor=\"white\"> {archivo['b_content']} </td></tr>\n")
                                    graph.write("   </table>>]\n\n")
                                elif buffer == '3':
                                    pass

                                graph.write(f"    inodo_{i}:f{j} -> bloque_{inodo['i_block'][j]}; \n")
                    i += 1

                graph.write("\n\n}")

            comando = f"dot -T{extension} grafica.dot -o {destino}"
            subprocess.run(comando, shell=True)
            print("Reporte Tree generado con éxito")
        except Exception as e:
            print(f"Error: {e}")

    # You would need to define the SuperBloque, InodoTable, BloqueCarpeta, BloqueArchivo, and BloqueApuntadores classes in Python with the same structure as in C++.
    # Also, ensure you've imported the necessary libraries and defined the required data structures.

    def read_journal_from_file(self, file_path, start):
        with open(file_path, "rb") as file:
            file.seek(start)  # Move to the start position
            packed_data = file.read(ctypes.sizeof(Journal))  # Read the binary data
            journal = Journal()
            ctypes.memmove(ctypes.byref(journal), packed_data, ctypes.sizeof(Journal))
        return journal



    ## Graficar_journaling
    def graficar_journaling(self, inicio_super):
        direccion = self.path
        destino = "."
        extension = "png"

        try:
            with open(direccion, "rb") as fp:
                super_data = self.getSuperblock(direccion, inicio_super)


            with open("grafica.dot", "w") as graph:
                graph.write("digraph G{\n")
                graph.write("    nodo [shape=none, fontname=\"Century Gothic\" label=<\n")
                graph.write("   <table border='0' cellborder='1' cellspacing='0'>\n")
                graph.write("    <tr> <td COLSPAN='7' bgcolor=\"cornflowerblue\"> <b>JOURNALING</b> </td></tr>\n")
                graph.write(
                    "    <tr> <td bgcolor=\"lightsteelblue\"><b>Operacion</b></td> <td bgcolor=\"lightsteelblue\"><b>Tipo</b></td><td bgcolor=\"lightsteelblue\"><b>Nombre</b></td><td bgcolor=\"lightsteelblue\"><b>Contenido</b></td>\n")
                graph.write(
                    "    <td bgcolor=\"lightsteelblue\"><b>Propietario</b></td><td bgcolor=\"lightsteelblue\"><b>Permisos</b></td><td bgcolor=\"lightsteelblue\"><b>Fecha</b></td></tr>\n")

                fp.seek(inicio_super + ctypes.sizeof(Superblock))

                while fp.tell() < super_data['s_bm_inode_start']:
                    j = Journal()
                    j = self.read_journal_from_file(direccion, fp.tell())

                    if j.journal_type == 0 or j.journal_type == 1:
                        tm = time.localtime(j.journal_date)
                        fecha = time.strftime('%d/%m/%y %H:%S', tm)
                        graph.write(
                            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(
                                j.journal_operation_type, j.journal_type, j.journal_name, j.journal_content,
                                j.journal_owner, j.journal_permissions, fecha))

                graph.write("   </table>>]\n")
                graph.write("}")

            comando = "dot -T{} grafica.dot -o {}".format(extension, destino)
            subprocess.run(comando, shell=True)
            print("Reporte Journaling generado con éxito")
        except Exception as e:
            print(f"Error: {e}")

    # You would need to define the SuperBloque and Journal classes in Python with the same structure as in C++.
    # Also, ensure you've imported the necessary libraries and defined the required data structures.

    def graficar_permisos(self, start_super, n, user, name):
        direccion = self.path
        destino = "."
        extension = "png"

        try:
            with open(direccion, "rb+") as fp:
                super_data = self.getSuperblock(direccion, start_super)
                inodo = self.getiNodesTable(super_data['s_inode_start'], direccion)
                fp.seek(start_super)
                fp.readinto(super_data)
                fp.seek(super_data['s_inode_start'] + n * ctypes.sizeof(iNodesTable))
                fp.readinto(inodo)

            with open("grafica.dot", "w") as graph:
                graph.write("digraph G{\n\n")
                graph.write("    nodo [ shape=none, fontname=\"Century Gothic\" \n")
                graph.write(
                    "    label=< <table border='0' cellborder='1' cellspacing='0' bgcolor=\"lightsteelblue\">\n")
                graph.write(
                    "     <tr> <td><b>Permisos</b></td><td><b>Owner</b></td><td><b>Grupo</b></td><td><b>Size</b></td><td><b>Fecha</b></td><td><b>Hora</b></td><td><b>Tipo</b></td><td><b>Name</b></td> </tr>\n")

                auxPermisos = str(inodo['i_perm'])
                propietario = auxPermisos[0]
                grupo = auxPermisos[1]
                otros = auxPermisos[2]
                permisos = []

                def obtener_permiso(num):
                    if num == '0':
                        return "---"
                    elif num == '1':
                        return "--x"
                    elif num == '2':
                        return "-w-"
                    elif num == '3':
                        return "-wx"
                    elif num == '4':
                        return "r--"
                    elif num == '5':
                        return "r-x"
                    elif num == '6':
                        return "rw-"
                    elif num == '7':
                        return "rwx"

                propietario_permisos = obtener_permiso(propietario)
                grupo_permisos = obtener_permiso(grupo)
                otros_permisos = obtener_permiso(otros)

                permisos.append(propietario_permisos)
                permisos.append(grupo_permisos)
                permisos.append(otros_permisos)

                graph.write(f"<tr> <td bgcolor=\"white\">{' '.join(permisos)}</td>")
                graph.write(f"<td bgcolor=\"white\">{user.username}</td>")
                graph.write(f"<td bgcolor=\"white\">{user.group}</td>")
                graph.write(f"<td bgcolor=\"white\">{inodo['i_size']}</td>")

                fecha = time.strftime('%d/%m/%y', time.localtime(inodo['i_atime']))
                hora = time.strftime('%H:%M', time.localtime(inodo['i_atime']))

                graph.write(f"<td bgcolor=\"white\">{fecha}</td>")
                graph.write(f"<td bgcolor=\"white\">{hora}</td>")

                tipo = "Carpeta" if inodo['i_type'] == '0' else "Archivo"
                graph.write(f"<td bgcolor=\"white\">{tipo}</td>")
                graph.write(f"<td bgcolor=\"white\">{name}</td> </tr>\n")

                graph.write("    </table>>]\n")
                graph.write("\n}")

            comando = f"dot -T{extension} grafica.dot -o {destino}"
            subprocess.run(comando, shell=True)
            print("Reporte ls generado con éxito")
        except Exception as e:
            print(f"Error: {e}")

    # You would need to define the SuperBloque and InodoTable classes in Python with the same structure as in C++.
    # Also, ensure you've imported the necessary libraries and defined the required data structures.

    import subprocess
    import time

    def graficar_super(self, start_super, dir):
        direccion = dir
        destino = "." + self.path
        extension = "png"
        destino = os.path.dirname("." + self.path)
        self.createDir(destino)
        destino = "." + self.path
        filename = self.get_filename_without_extension(self.path)
        super_data = self.getSuperblock(direccion, start_super)

        with open(filename + ".dot", "w") as graph:
            graph.write("digraph G{\n")
            graph.write("    nodo [shape=none, fontname=\"Century Gothic\" label=<")
            graph.write("   <table border='0' cellborder='1' cellspacing='0' bgcolor=\"cornflowerblue\">")
            graph.write("    <tr> <td COLSPAN='2'> <b>SUPERBLOQUE</b> </td></tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_inodes_count </td> <td bgcolor=\"white\"> {super_data['s_inodes_count']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_blocks_count </td> <td bgcolor=\"white\"> {super_data['s_blocks_count']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_free_block_count </td> <td bgcolor=\"white\"> {super_data['s_free_blocks_count']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_free_inodes_count </td> <td bgcolor=\"white\"> {super_data['s_free_inodes_count']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_mtime </td> <td bgcolor=\"white\"> {time.strftime('%d/%m/%y %H:%M', time.localtime(super_data['s_mtime']))} </td></tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_umtime </td> <td bgcolor=\"white\"> {time.strftime('%d/%m/%y %H:%M', time.localtime(super_data['s_umtime']))} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_mnt_count </td> <td bgcolor=\"white\"> {super_data['s_mnt_count']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_magic </td> <td bgcolor=\"white\"> {super_data['s_magic']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_inode_s </td> <td bgcolor=\"white\"> {super_data['s_inode_s']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_block_size </td> <td bgcolor=\"white\"> {super_data['s_block_s']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_first_ino </td> <td bgcolor=\"white\"> {super_data['s_first_ino']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_first_blo </td> <td bgcolor=\"white\"> {super_data['s_first_blo']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_bm_inode_start </td> <td bgcolor=\"white\"> {super_data['s_bm_inode_start']} </td></tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_bm_block_start </td> <td bgcolor=\"white\"> {super_data['s_bm_block_start']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_inode_start </td> <td bgcolor=\"white\"> {super_data['s_inode_start']} </td> </tr>\n")
            graph.write(
                f"    <tr> <td bgcolor=\"lightsteelblue\"> s_block_start </td> <td bgcolor=\"white\"> {super_data['s_block_start']} </td> </tr>\n")
            graph.write("   </table>>]\n")
            graph.write("\n}")

        comando = f"dot -T{extension} grafica.dot -o {destino}"
        subprocess.run(comando, shell=True)
        print("Reporte SuperBloque generado con éxito")


    # You would need to define the SuperBloque class in Python with the same structure as in C++.
    # Also, ensure you've imported the necessary libraries and defined the required data structures.

    def reporte_bm(self, direccion, destino, start_bm, n):
        try:
            with open(direccion, "rb+") as fp:
                with open(destino, "w+") as report:
                    report.seek(0)
                    cont = 0

                    for i in range(n):
                        fp.seek(start_bm + i)
                        byte = fp.read(1)
                        if byte == b'0':
                            report.write("0 ")
                        else:
                            report.write("1 ")
                        if cont == 19:
                            cont = 0
                            report.write("\n")
                        else:
                            cont += 1

            print("Reporte generado con éxito")
        except Exception as e:
            print(f"Error: {e}")


    def graficar_bloques(self, direccion, destino, extension, bm_block_start, block_start, inode_start):
        try:
            fp = open(direccion, "rb")
            carpeta = None
            archivo = None
            apuntador = None
            aux = bm_block_start
            i = 0

            with open("grafica.dot", "w") as graph:
                graph.write("digraph G{\n\n")

                while aux < inode_start:
                    fp.seek(bm_block_start + i)
                    buffer = fp.read(1)
                    aux += 1

                    if buffer == b'1':
                        fp.seek(block_start + i * ctypes.sizeof(FolderBlock))
                        # potencial error
                        carpeta = self.getFolderBlock(direccion, block_start + i * ctypes.sizeof(FolderBlock))
                        fp.readinto(carpeta)
                        graph.write(f"    nodo_{i} [ shape=none, fontname=\"Century Gothic\" label=< \n")
                        graph.write("   <table border='0' cellborder='1' cellspacing='0' bgcolor=\"seagreen\">")
                        graph.write(f"    <tr> <td colspan='2'> <b>Bloque Carpeta {i}</b> </td></tr>\n")
                        graph.write(
                            "    <tr> <td bgcolor=\"mediumseagreen\"> b_name </td> <td bgcolor=\"mediumseagreen\"> b_inode </td></tr>\n")
                        for c in range(4):
                            graph.write(
                                f"    <tr> <td bgcolor=\"white\"> {carpeta.b_content[c].b_name.decode()} </td> <td bgcolor=\"white\"> {carpeta.b_content[c].b_inodo} </td></tr>\n")
                        graph.write("   </table>>]\n\n")
                    elif buffer == b'2':
                        fp.seek(block_start + i * ctypes.sizeof(FolderBlock))
                        archivo = FolderBlock()
                        fp.readinto(archivo)
                        graph.write(f"    nodo_{i} [ shape=none, label=< \n")
                        graph.write("   <table border='0' cellborder='1' cellspacing='0' bgcolor=\"sandybrown\">")
                        graph.write(f"    <tr> <td colspan='2'> <b>Bloque Archivo {i} </b></td></tr>\n")
                        graph.write(
                            f"    <tr> <td colspan='2' bgcolor=\"white\"> {archivo['b_content'].decode()} </td></tr>\n")
                        graph.write("   </table>>]\n\n")
                    elif buffer == b'3':
                        fp.seek(block_start + i * ctypes.sizeof(blockPointer))
                        apuntador = blockPointer()
                        fp.readinto(apuntador)
                        fp.seek(block_start + i * ctypes.sizeof(FolderBlock))
                        fp.readinto(apuntador)
                        graph.write(f"    bloque_{i} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                        graph.write("   <table border='0' bgcolor=\"khaki\">\n")
                        graph.write(f"    <tr> <td> <b>Pointer block {i}</b></td></tr>\n")
                        for j in range(16):
                            graph.write(f"    <tr> <td bgcolor=\"white\">{apuntador['b_pointer'][j]}</td> </tr>\n")
                        graph.write("   </table>>]\n\n")
                    i += 1

                graph.write("\n}")

            fp.close()

            comando = f"dot -T{extension} grafica.dot -o {destino}"
            subprocess.run(comando, shell=True)
            print("Reporte generado con éxito")
        except Exception as e:
            print(f"Error: {e}")

    # You would need to define the BloqueCarpeta, BloqueArchivo, and BloqueApuntadores classes as Python classes.
    # Also, ensure you've imported the necessary libraries and defined the required data structures.

    # --> Graficar el disco (para esto usamos el MBR
    def graficar_disco(self):
        # primero que nada, debemos buscar el disco entre las particiones montadas
        # para esto, usamos el metodo de buscar disco
        # potencial error
        print("00000000")
        print(self.id)
        print("00000000")
        direccion = DiscosMontados.returnPath(self.id)

        destino = os.path.dirname("." + self.path)
        self.createDir(destino)
        destino = "." + self.path
        extension = "png"
        # Open the input file for reading
        with open(direccion, 'rb') as fp:
            with open('disk.dot', 'w') as graph_dot:
                graph_dot.write("digraph G{\n\n")
                graph_dot.write("  tbl [\n    shape=box\n    label=<\n")
                graph_dot.write(
                    "     <table border='0' cellborder='2' width='600' height=\"200\" color='LIGHTSTEELBLUE'>\n")
                graph_dot.write("     <tr>\n")
                graph_dot.write("     <td height='200' width='100'> MBR </td>\n")


                masterboot = self.getMBR(direccion)
                fp.seek(0, os.SEEK_SET)
                #masterboot_data = fp.read(ctypes.sizeof(MBR))  # Assuming sizeof is defined elsewhere
                #masterboot.__dict__.update(masterboot_data)

                total = int(masterboot['mbr_tamano'])
                espacio_usado = 0

                for i in range(4):
                    parcial = masterboot['mbr_particiones'][i][4]
                    if masterboot['mbr_particiones'][i][3] != -1:  # Partition not empty
                        porcentaje_real = (parcial * 100) / total
                        porcentaje_aux = (porcentaje_real * 500) / 100
                        espacio_usado += porcentaje_real

                        # status -0, type -1 , fit -2, start -3, size -4, name -5
                        if masterboot['mbr_particiones'][i][0] != b'0':
                            print(masterboot['mbr_particiones'][i][1].decode().lower())
                            if masterboot['mbr_particiones'][i][1].decode().lower() == 'p':
                                graph_dot.write(
                                    "     <td height='200' width='%.1f'>PRIMARIA <br/> Ocupado: %.1f%c</td>\n" %
                                    (porcentaje_aux, porcentaje_real, '%'))
                                if i != 3:
                                    # status -0, type -1 , fit -2, start -3, size -4, name -5
                                    p1 = masterboot['mbr_particiones'][i][3] + masterboot['mbr_particiones'][i][4]
                                    p2 = masterboot['mbr_particiones'][i + 1][3]
                                    if masterboot['mbr_particiones'][i + 1][3] != -1:
                                        if (p2 - p1) != 0:
                                            fragmentacion = p2 - p1
                                            porcentaje_real = (fragmentacion * 100) / total
                                            porcentaje_aux = (porcentaje_real * 500) / 100
                                            graph_dot.write(
                                                "     <td height='200' width='%.1f'>LIBRE<br/> Ocupado: %.1f%c</td>\n" %
                                                (porcentaje_aux, porcentaje_real, '%'))
                                    else:
                                        p1 = masterboot['mbr_particiones'][i][3] + masterboot['mbr_particiones'][
                                            i][4]
                                        # status -0, type -1 , fit -2, start -3, size -4, name -5

                                        mbr_size = total + ctypes.sizeof(MBR)
                                        if (mbr_size - p1) != 0:
                                            libre = (mbr_size - p1) + ctypes.sizeof(MBR)
                                            porcentaje_real = (libre * 100) / total
                                            porcentaje_aux = (porcentaje_real * 500) / 100
                                            graph_dot.write(
                                                "     <td height='200' width='%.1f'>LIBRE<br/> Ocupado: %.1f%c</td>\n" %
                                                (porcentaje_aux, porcentaje_real, '%'))
                            else:  # Extendida
                                # Assuming EBR is a C++ struct, define it as a Python class
                                graph_dot.write(
                                    "     <td  height='200' width='%.1f'>\n     <table border='0'  height='200' WIDTH='%.1f' cellborder='1'>\n" %
                                    (porcentaje_real, porcentaje_real))
                                graph_dot.write(
                                    "     <tr>  <td height='60' colspan='15'>EXTENDIDA</td>  </tr>\n     <tr>\n")
                                #fp.seek(0)
                                print("*******************")
                                print("GET EBR ***********")
                                print("direccion -> " + direccion)
                                print("start-> " + str(masterboot['mbr_particiones'][i][3]))
                                ebr_data = self.getEBR(direccion, masterboot['mbr_particiones'][i][3])
                                print("**************************************************************")
                                if ebr_data['part_size'] != 0:  # If there are logical partitions
                                    puntero = masterboot['mbr_particiones'][i][3]
                                    while True:

                                        ebr_data = self.getEBR(direccion, puntero)
                                        if ebr_data['part_size'] == 0:
                                            break
                                        #ebr.__dict__.update(ebr_data)
                                        parcial = ebr_data['part_size']
                                        print("TOTAL-> " + str(ebr_data['part_size']))
                                        porcentaje_real = (parcial * 100) / total

                                        if porcentaje_real != 0:
                                            if ebr_data['part_status'] != '1':
                                                graph_dot.write("     <td height='140'>EBR</td>\n")
                                                graph_dot.write(
                                                    "     <td height='140'>LOGICA<br/>Ocupado: %.1f%c</td>\n" %
                                                    (porcentaje_real, '%'))
                                            else:
                                                graph_dot.write(
                                                    "      <td height='150'>LIBRE 1 <br/> Ocupado: %.1f%c</td>\n" %
                                                    (porcentaje_real, '%'))

                                            if ebr_data['part_next'] == -1:
                                                parcial = (masterboot['mbr_particiones'][i][3] +
                                                           masterboot['mbr_particiones'][i][4]) - (
                                                                      ebr_data['part_start'] + ebr_data['part_size'])
                                                porcentaje_real = (parcial * 100) / total
                                                if porcentaje_real != 0:
                                                    graph_dot.write(
                                                        "     <td height='150'>LIBRE 2<br/> Ocupado: %.1f%c </td>\n" %
                                                        (porcentaje_real, '%'))
                                                break
                                            else:
                                                puntero = ebr_data['part_next']
                                                #fp.seek(ebr_data['part_next'], os.SEEK_SET)
                                    else:
                                        graph_dot.write(
                                            "     <td height='140'> Ocupado %.1f%c</td>" % (porcentaje_real, '%'))
                                graph_dot.write("     </tr>\n     </table>\n     </td>\n")

                                if i != 3:
                                    # status -0, type -1 , fit -2, start -3, size -4, name -5

                                    p1 = masterboot['mbr_particiones'][i][3] + masterboot['mbr_particiones'][i][4]
                                    p2 = masterboot['mbr_particiones'][i + 1][3]
                                    if masterboot['mbr_particiones'][i + 1][3] != -1:
                                        if (p2 - p1) != 0:
                                            fragmentacion = p2 - p1
                                            porcentaje_real = (fragmentacion * 100) / total
                                            porcentaje_aux = (porcentaje_real * 500) / 100
                                            graph_dot.write(
                                                "     <td height='200' width='%.1f'>LIBRE<br/> Ocupado: %.1f%c</td>\n" %
                                                (porcentaje_aux, porcentaje_real, '%'))
                                else:
                                    p1 = masterboot['mbr_particiones'][i][3] + masterboot['mbr_particiones'][i][4]
                                    mbr_size = total + sizeof(MBR)
                                    if (mbr_size - p1) != 0:
                                        libre = (mbr_size - p1) + sizeof(MBR)
                                        porcentaje_real = (libre * 100) / total
                                        porcentaje_aux = (porcentaje_real * 500) / 100
                                        graph_dot.write(
                                            "     <td height='200' width='%.1f'>LIBRE<br/> Ocupado: %.1f%c</td>\n" %
                                            (porcentaje_aux, porcentaje_real, '%'))

                graph_dot.write("     </tr> \n     </table>        \n>];\n\n}")

        # Execute the command to generate the graph
        comando = f"dot -T{extension} disk.dot -o {destino}"
        os.system(comando)
        print("Reporte generado con éxito")

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

    def unpack_superblock(self, packed_data, start):
        unpacked_superblock = {}
        superblock_size = struct.calcsize("cccciiiiiiiiiiiiiiii")
        superblock_data = packed_data[start:start + superblock_size]
        unpacked_superblock = struct.unpack("cccciiiiiiiiiiiiiiii", superblock_data)

        # Create a dictionary with field names as keys
        field_names = [field[0] for field in Superblock._fields_]
        unpacked_superblock = dict(zip(field_names, unpacked_superblock))

        return unpacked_superblock

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
        print("s_mtime->" + str(unpacked_data['s_mtime']))
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

    def getPointerblock(self, definedPath, start):
        packed_data = self.read_packed_data_from_file(definedPath)
        ## unpack_mbr puede tener un error dentro
        unpacked_data = self.unpack_superblock(packed_data, start)
        print("-------Superbloque ---------")
        print("part_status->" + str(unpacked_data['part_status']))
        print("part_fit->" + str(unpacked_data['part_fit']))
        print("part_start->" + str(unpacked_data['part_start']))
        print("part_next->" + str(unpacked_data['part_next']))
        print("part_size->" + str(unpacked_data['part_size']))
        return unpacked_data




    # EDITAR AQUI PORQUE AUN ES NECESARIO
    def graficar_inodosMBR(self, bm_inode_start, inode_start, bm_block_start):
        # Open the input file for reading
        direccion = self.path
        destino = "."
        extension = "png"

        # Leemos el MBR
        mbr = self.getMBR(direccion)
        # Leemos el SuperBloque
        super_bloque = self.getSuperBloque(direccion, mbr['mbr_particiones'][0][3])

        with open(direccion, 'rb') as fp:
            aux = bm_inode_start
            i = 0

            with open('grafica.dot', 'w') as graph:
                graph.write("digraph G{\n\n")

                while aux < bm_block_start:
                    fp.seek(bm_inode_start + i)
                    buffer = struct.unpack('c', fp.read(1))[0]
                    aux += 1

                    if buffer == b'1':
                        fp.seek(inode_start + struct.calcsize('InodoTable') * i)
                        inodo_data = fp.read(struct.calcsize('InodoTable'))
                        inodo = struct.unpack('IIIIIII15si', inodo_data)

                        graph.write(f"    nodo_{i} [ shape=none fontname=\"Century Gothic\" label=<\n")
                        graph.write(f"   <table border='0' cellborder='1' cellspacing='0' bgcolor=\"royalblue\">")
                        graph.write(f"    <tr> <td colspan='2'> <b>Inodo {i}</b> </td></tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_uid </td> <td bgcolor=\"white\"> {inodo[0]} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_gid </td> <td bgcolor=\"white\"> {inodo[1]} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_size </td> <td bgcolor=\"white\"> {inodo[2]} </td> </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_atime </td> <td bgcolor=\"white\"> {time.strftime('%d/%m/%y %H:%M', time.localtime(inodo[3]))} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_ctime </td> <td bgcolor=\"white\"> {time.strftime('%d/%m/%y %H:%M', time.localtime(inodo[4]))} </td>  </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_mtime </td> <td bgcolor=\"white\"> {time.strftime('%d/%m/%y %H:%M', time.localtime(inodo[5]))} </td></tr>\n")
                        for b in range(15):
                            graph.write(
                                f"    <tr> <td bgcolor=\"lightsteelblue\"> i_block_{b} </td> <td bgcolor=\"white\"> {inodo[6 + b]} </td> </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_type </td> <td bgcolor=\"white\"> {struct.unpack('c', struct.pack('i', inodo[21]))[0].decode()} </td> </tr>\n")
                        graph.write(
                            f"    <tr> <td bgcolor=\"lightsteelblue\"> i_perm </td> <td bgcolor=\"white\"> {inodo[22]} </td> </tr>\n")
                        graph.write(f"   </table>>]\n")
                    i += 1

                graph.write("\n}")

        # Execute the command to generate the graph
        comando = f"dot -T{extension} grafica.dot -o {destino}"
        os.system(comando)
        print("Reporte de inodos generado con éxito")

    def graficarTree(self, direccion, destino, extension, start_super):
        with open(direccion, "rb") as fp:
            super_struct = struct.Struct("...")  # Define the structure of SuperBloque here
            inodo_struct = struct.Struct("...")  # Define the structure of InodoTable here
            carpeta_struct = struct.Struct("...")  # Define the structure of BloqueCarpeta here
            archivo_struct = struct.Struct("...")  # Define the structure of BloqueArchivo here
            apuntador_struct = struct.Struct("...")  # Define the structure of BloqueApuntadores here

            fp.seek(start_super)
            super_data = super_struct.unpack(fp.read(super_struct.size))

            aux = super_data[...]  # Replace ... with the appropriate field index
            i = 0

            graph = open("grafica.dot", "w")
            graph.write("digraph G{\n\n")
            graph.write("    rankdir=\"LR\" \n")

            # Create the inodos
            while aux < super_data[...]:  # Replace ... with the appropriate field index
                fp.seek(super_data[...] + i)
                buffer = struct.unpack("c", fp.read(1))[0]
                aux += 1
                port = 0
                if buffer == b'1':
                    fp.seek(super_data[...] + struct.calcsize(inodo_struct.format) * i)
                    inodo_data = inodo_struct.unpack(fp.read(inodo_struct.size))
                    graph.write(f"    inodo_{i} [ shape=plaintext fontname=\"Century Gothic\" label=<\n")
                    graph.write(f"   <table bgcolor=\"royalblue\" border='0' >")
                    graph.write(f"    <tr> <td colspan='2'><b>Inode {i}</b></td></tr>\n")
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_uid </td> <td bgcolor='white'> {inodo_data[...]} </td>  </tr>\n")
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_gid </td> <td bgcolor='white'> {inodo_data[...]} </td>  </tr>\n")
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_size </td><td bgcolor='white'> {inodo_data[...]} </td> </tr>\n")
                    tm = time.localtime(inodo_data[...])
                    fecha = time.strftime("%d/%m/%y %H:%S", tm)
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_atime </td> <td bgcolor='white'> {fecha} </td> </tr>\n")
                    tm = time.localtime(inodo_data[...])
                    fecha = time.strftime("%d/%m/%y %H:%S", tm)
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_ctime </td> <td bgcolor='white'> {fecha} </td> </tr>\n")
                    tm = time.localtime(inodo_data[...])
                    fecha = time.strftime("%d/%m/%y %H:%S", tm)
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_mtime </td> <td bgcolor='white'> {fecha} </td> </tr>\n")
                    for b in range(15):
                        graph.write(
                            f"    <tr> <td bgcolor='lightsteelblue'> i_block_{b} </td> <td bgcolor='white' port='f{b}'> {inodo_data[...][b]} </td></tr>\n")
                        port += 1
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_type </td> <td bgcolor='white'> {inodo_data[...]} </td>  </tr>\n")
                    graph.write(
                        f"    <tr> <td bgcolor='lightsteelblue'> i_perm </td> <td bgcolor='white'> {inodo_data[...]} </td>  </tr>\n")
                    graph.write("   </table>>]\n\n")
                    # Create the blocks related to the inodo
                    for j in range(15):
                        port = 0
                        if inodo_data[...][j] != -1:
                            fp.seek(super_data[...] + inodo_data[...][j])
                            buffer = struct.unpack("c", fp.read(1))[0]
                            if buffer == b'1':  # Block is a folder
                                fp.seek(super_data[...] + struct.calcsize(carpeta_struct.format) * inodo_data[...][j])
                                carpeta_data = carpeta_struct.unpack(fp.read(carpeta_struct.size))
                                graph.write(
                                    f"    bloque_{inodo_data[...][j]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                graph.write(f"   <table bgcolor=\"seagreen\" border='0'>\n")
                                graph.write(
                                    f"    <tr> <td colspan='2'><b>Folder block {inodo_data[...][j]}</b></td></tr>\n")
                                graph.write(
                                    f"    <tr> <td bgcolor='mediumseagreen'> b_name </td> <td bgcolor='mediumseagreen'> b_inode </td></tr>\n")
                                for c in range(4):
                                    graph.write(
                                        f"    <tr> <td bgcolor='white' > {carpeta_data[...][c].b_name} </td> <td bgcolor='white'  port='f{c}'> {carpeta_data[...][c].b_inodo} </td></tr>\n")
                                    port += 1
                                graph.write("   </table>>]\n\n")
                                # Relationship of blocks to inodos
                                for c in range(4):
                                    if carpeta_data[...][c].b_inodo != -1:
                                        if carpeta_data[...][c].b_name != b'.' and carpeta_data[...][c].b_name != b'..':
                                            graph.write(
                                                f"    bloque_{inodo_data[...][j]}:f{c} -> inodo_{carpeta_data[...][c].b_inodo};\n")
                            elif buffer == b'2':  # Block is a file
                                fp.seek(super_data[...] + struct.calcsize(archivo_struct.format) * inodo_data[...][j])
                                archivo_data = archivo_struct.unpack(fp.read(archivo_struct.size))
                                graph.write(
                                    f"    bloque_{inodo_data[...][j]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                graph.write(f"   <table border='0' bgcolor=\"sandybrown\">\n")
                                graph.write(f"    <tr> <td> <b>File block {inodo_data[...][j]}</b></td></tr>\n")
                                graph.write(f"    <tr> <td bgcolor='white'> {archivo_data[...].b_content} </td></tr>\n")
                                graph.write("   </table>>]\n\n")
                            elif buffer == b'3':  # Block is a pointer block
                                fp.seek(super_data[...] + struct.calcsize(apuntador_struct.format) * inodo_data[...][j])
                                apuntador_data = apuntador_struct.unpack(fp.read(apuntador_struct.size))
                                graph.write(
                                    f"    bloque_{inodo_data[...][j]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                graph.write(f"   <table border='0' bgcolor=\"khaki\">\n")
                                graph.write(f"    <tr> <td> <b>Pointer block {inodo_data[...][j]}</b></td></tr>\n")
                                for a in range(16):
                                    graph.write(
                                        f"    <tr> <td bgcolor='white' port='f{a}'>{apuntador_data[...][a]} </td> </tr>\n")
                                    port += 1
                                graph.write("   </table>>]\n\n")
                                # Blocks within the pointer block
                                for x in range(16):
                                    port = 0
                                    if apuntador_data[...][x] != -1:
                                        fp.seek(super_data[...] + apuntador_data[...][x])
                                        buffer = struct.unpack("c", fp.read(1))[0]
                                        if buffer == b'1':
                                            fp.seek(super_data[...] + struct.calcsize(carpeta_struct.format) *
                                                    apuntador_data[...][x])
                                            carpeta_data = carpeta_struct.unpack(fp.read(carpeta_struct.size))
                                            graph.write(
                                                f"    bloque_{apuntador_data[...][x]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                            graph.write(f"   <table border='0' bgcolor=\"seagreen\" >\n")
                                            graph.write(
                                                f"    <tr> <td colspan='2'> <b>Folder block {apuntador_data[...][x]}</b> </td></tr>\n")
                                            graph.write(
                                                f"    <tr> <td bgcolor='mediumseagreen'> b_name </td> <td bgcolor='mediumseagreen'> b_inode </td></tr>\n")
                                            for c in range(4):
                                                graph.write(
                                                    f"    <tr> <td bgcolor='white'> {carpeta_data[...][c].b_name} </td> <td bgcolor='white' port='f{c}'> {carpeta_data[...][c].b_inodo} </td></tr>\n")
                                                port += 1
                                            graph.write("   </table>>]\n\n")
                                            # Relationship of blocks to inodos
                                            for c in range(4):
                                                if carpeta_data[...][c].b_inodo != -1:
                                                    if carpeta_data[...][c].b_name != b'.' and carpeta_data[...][
                                                        c].b_name != b'..':
                                                        graph.write(
                                                            f"    bloque_{apuntador_data[...][x]}:f{c} -> inodo_{carpeta_data[...][c].b_inodo};\n")
                                        elif buffer == b'2':
                                            fp.seek(super_data[...] + struct.calcsize(archivo_struct.format) *
                                                    apuntador_data[...][x])
                                            archivo_data = archivo_struct.unpack(fp.read(archivo_struct.size))
                                            graph.write(
                                                f"    bloque_{apuntador_data[...][x]} [shape=plaintext fontname=\"Century Gothic\" label=< \n")
                                            graph.write(f"   <table border='0' bgcolor=\"sandybrown\">\n")
                                            graph.write(
                                                f"    <tr> <td> <b>File block {apuntador_data[...][x]}</b></td></tr>\n")
                                            graph.write(
                                                f"    <tr> <td bgcolor='white'> {archivo_data[...].b_content} </td></tr>\n")
                                            graph.write("   </table>>]\n\n")
                                        elif buffer == b'3':
                                            pass  # Handle as needed
                            # Relationship of inodos to blocks
                            graph.write(f"    inodo_{i}:f{j} -> bloque_{inodo_data[...][j]}; \n")
                i += 1

            graph.write("\n\n}")
            graph.close()

        comando = f"dot -T{extension} grafica.dot -o {destino}"
        os.system(comando)
        print("Reporte Tree generado con exito")

    # Example usage:
    #graficar_inodos("disk.bin", "reporte.png", "png", bm_inode_start, inode_start, bm_block_start)

    # Example usage:
    #graficar_disco("disk.bin", "reporte.png", "png")

    def printMBRFile(self, definedPath):
        # Primero hacemos el cuadro en el que iran las particiones


        packed_data = self.read_packed_data_from_file(definedPath)



        unpacked_data = self.unpack_mbr(packed_data)

        print("-------MBR---------")
        print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
        print("mbr_fit->" + str(unpacked_data['mbr_fit']))
        print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
        print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
        print(unpacked_data)
        print("--------------")

    def getMBR(self, definedPath):
        # Primero hacemos el cuadro en el que iran las particiones
        packed_data = self.read_packed_data_from_file(definedPath)
        unpacked_data = self.unpack_mbr(packed_data)

        print("-------MBR---------")
        print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
        print("mbr_fit->" + str(unpacked_data['mbr_fit']))
        print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
        print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
        print(unpacked_data)
        print("--------------")
        return unpacked_data # Dictionary

    def graficar_file(self, direccion, destino, extension, name, start_super, n):
        direccion = "."
        with open(direccion, "rb") as fp:
            super_struct = struct.Struct("...")  # Define the structure format for SuperBloque
            inodo_struct = struct.Struct("...")  # Define the structure format for InodoTable
            archivo_struct = struct.Struct("...")  # Define the structure format for BloqueArchivo

            fp.seek(start_super)
            super_data = super_struct.unpack(fp.read(super_struct.size))

            fp.seek(super_data.s_inode_start + (inodo_struct.size * n))
            inodo_data = inodo_struct.unpack(fp.read(inodo_struct.size))

        with open("grafica.dot", "w") as graph:
            graph.write("digraph G{\n")
            graph.write("    nodo [shape=none, fontname=\"Century Gothic\" label=<\n")
            graph.write("   <table border='0' cellborder='1' cellspacing='0' bgcolor=\"lightsteelblue\">\n")
            graph.write("    <tr><td align=\"left\"> <b>%s</b> </td></tr>\n" % name)
            graph.write("    <tr><td bgcolor=\"white\">")

            for i in range(15):
                if inodo_data.i_block[i] != -1:
                    if i == 12:  # Apuntador indirecto simple
                        apuntador_struct = struct.Struct("...")  # Define the structure format for BloqueApuntadores
                        apuntador = apuntador_struct.unpack(fp.read(apuntador_struct.size))

                        for j in range(16):
                            if apuntador.b_pointer[j] != -1:
                                fp.seek(super_data.s_block_start + (ctypes.sizeof(FolderBlock) * apuntador.b_pointer[j]))
                                archivo_data = archivo_struct.unpack(fp.read(archivo_struct.size))
                                graph.write("%s <br/>" % archivo_data.b_content)
                    elif i == 13:
                        pass
                    elif i == 14:
                        pass
                    else:  # Apuntadores directos
                        fp.seek(super_data.s_block_start + (sizeof(BloqueCarpeta) * inodo_data.i_block[i]))
                        archivo_data = archivo_struct.unpack(fp.read(archivo_struct.size))
                        graph.write("%s <br/>" % archivo_data.b_content)

            graph.write("    </td></tr>\n")
            graph.write("   </table>>]\n")
            graph.write("\n}")

        comando = "dot -T%s grafica.dot -o %s" % (extension, destino)
        subprocess.call(comando, shell=True)
        print("Reporte file generado con éxito")

    def graficar_bm(self, direccion, start_bm, n):
        destino = "."
        fp = open(direccion, "rb+")
        byte = None
        report = open(destino, "w+")
        report.seek(0)
        cont = 0

        for i in range(n):
            fp.seek(start_bm + i, 0)
            byte = fp.read(1)
            if byte == b'0':
                report.write("0 ")
            else:
                report.write("1 ")
            if cont == 19:
                cont = 0
                report.write("\n")
            else:
                cont += 1

        report.close()
        fp.close()
        print("Reporte generado con éxito")

    def reporteMBR(self):
        # recorrer MBR e imprimir
        self.path = "." + self.path
        self.graficarMBR()
        print("reporte MBR")

    def reporteEBR(self):
        # recorrer EBR e imprimir
        self.path = "." + self.path

        print("reporte EBR")

    def reporteDisk(self):
        # recorrer Disk e imprimir
        self.path = self.path
        self.graficar_disco()
        print("reporte Disk")

    def reporteInode(self):
        # recorrer Inode e imprimir
        # self.graficar
        print("reporte Inode")

    def reporteJournaling(self):
        # recorrer Journaling e imprimir
        print("reporte Journaling")

    def reporteBlock(self):
        # recorrer Block e imprimir
        print("reporte Block")


    def reporteBm_block(self):
        # recorrer Bm_block e imprimir
        print("********reporte Bm_block********")
        directory = DiscosMontados.returnPath(self.id)
        mbr = self.getMBR(directory)
        print("***** INICIA GRAFICA BM_BLOCK *****")
        print("start->" + str(mbr['mbr_particiones'][0][3]))
        print("direccion-> " + directory)
        print("**************************************")
        # Debemos tambien rescatar el Superbloque para poder hacer el reporte
        super_bloque = self.getSuperblock(directory, mbr['mbr_particiones'][0][3])
        self.graficar_bm(directory, super_bloque['s_bm_block_start'], super_bloque['s_blocks_count'])

    def reporteBm_iNode(self):
        # recorrer Bm_block e imprimir
        print("********reporte Bm_iNode********")
        # antes de graficar el bm_block tenemos que buscar el inicio de la particion
        # para esto, usamos el metodo de buscar disco'
        directory = DiscosMontados.returnPath(self.id)
        mbr = self.getMBR(directory)
        print("***** INICIA GRAFICA BM_INODE*****")
        print("start->" + str(mbr['mbr_particiones'][0][3]))
        print("direccion-> " + directory)
        print("**************************************")
        # Debemos tambien rescatar el Superbloque para poder hacer el reporte
        super_bloque = self.getSuperblock(directory, mbr['mbr_particiones'][0][3])
        self.graficar_bm(directory, super_bloque['s_bm_inode_start'], super_bloque['s_inodes_count'])




    def reporteTree(self):
        # recorrer Tree e imprimir
        print("reporte Tree")
        self.graficarTree() # Fix

    def reporteSB(self):
        # recorrer SB e imprimir
        print("reporte SB")
        # antes de graficar el superbloque tenemos que buscar el inicio de la particion
        # para esto, usamos el metodo de buscar disco
        dir = DiscosMontados.returnPath(self.id)
        mbr = self.getMBR(dir)
        print("***** INICIA GRAFICA SUPERBLOQUE *****")
        print("start->" + str(mbr['mbr_particiones'][0][3]))
        print("direccion-> " + dir)
        print("**************************************")
        self.graficar_super(mbr['mbr_particiones'][0][3], dir)

    def reporteFile(self):
        # recorrer File e imprimir
        print("reporte File")
        self.graficarFile()


    def reporteLS(self):
        # recorrer LS e imprimir
        print("reporte LS")



def create_and_visualize_graph():
    # Create a new directed graph
    graph = Digraph(format='png')

    # Add nodes and edges
    graph.node('A')
    graph.node('B')
    graph.node('C')
    graph.edge('A', 'B')
    graph.edge('B', 'C')
    graph.edge('C', 'A')

    # Save the graph visualization to a file
    graph.render('my_graph')
from graphviz import Digraph

def sample():
    # Create a new Digraph object
    d = Digraph(format='png')

    # Set global attributes for nodes and edges
    d.attr(node_shape='box', style='filled', fillcolor='lightgray', fontname='Arial')
    d.attr(edge_color='blue')
    variable = int(10)
    variable2 = "variable1"
    variable3= 'variable3'
    d.node('sub1', label=f'{variable3}', width=f'{variable}', height='0.5', shape='rectangle', fixedsize='true')
    d.node('sub5', label=variable3, width='2', height='0.5', shape='rectangle', fixedsize='true')
    d.node('sub4', label=f'{variable2}', width='2', height='0.5', shape='rectangle', fixedsize='true')
    d.node('sub2', label='', width='0', height='0.5', shape='rectangle', fixedsize='true')
    d.node('sub3', label='MBR', width='0', height='0.5', shape='rectangle', fixedsize='true')

    with d.subgraph(name='cluster_subrectangles') as c:
        c.node('sub1')
        c.node('sub2')
        c.node('sub3')
        c.node('sub4')
        c.node('sub5')
        c.attr(label='Disco1.dsk')

    # Set the layout
    d.attr(rankdir='TB')

    # Save the visualization to a file
    d.render('rectangle_example', cleanup=True, format='png', directory='./')

    print(f"Visualization saved as /rectangle_example.png")

# Call the function and specify the output directory
sample()
from graphviz import Digraph

def create_division_graph(total_value, values):
    # Create a directed graph
    dot = Digraph()

    # Calculate the percentage for each division
    total_percentage = sum(values) / total_value * 100 if total_value != 0 else 0
    division_percentages = [value / total_value * total_percentage for value in values]

    # Add divisions as nodes
    for i, percentage in enumerate(division_percentages):
        dot.node(f"Division {i + 1}\n({percentage:.2f}%)")

    # Add edges between divisions
    for i in range(len(division_percentages) - 1):
        dot.edge(f"Division {i + 1}\n({division_percentages[i]:.2f}%)",
                 f"Division {i + 2}\n({division_percentages[i + 1]:.2f}%)")

    return dot


def createGraph():
    # Example values
    total_value = 30
    values = [5, 10, 8, 4, 3]

    # Create the graph
    graph = create_division_graph(total_value, values)
    graph.render('division_graph', format='png')
from graphviz import Digraph

def create_one_dimensional_table(header, rows, output_filename='table_graph'):
    # Create a directed graph
    dot = Digraph()

    # Create a node for the table header
    dot.node('header', '|'.join(header), shape='plaintext')

    # Create nodes for each row
    for i, row in enumerate(rows):
        dot.node(f'row_{i}', '|'.join(row), shape='plaintext')

    # Add edges to connect the header and rows
    dot.edge('header', f'row_0', style='invis')
    for i in range(len(rows) - 1):
        dot.edge(f'row_{i}', f'row_{i + 1}', style='invis')

    # Save the graph to a file (output will be in PNG format by default)
    dot.render(output_filename, format='png')


header = ['Header 1', 'Header 2', 'Header 3']
rows = [['Cell 1', 'Cell 2', 'Cell 3'],
        ['Cell 4', 'Cell 5', 'Cell 6'],
        ['Cell 7', 'Cell 8', 'Cell 9']]
if __name__ == "__main__":
    sample()
