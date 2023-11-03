import ctypes

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

class Superblock(ctypes.Structure):
    _fields_ = [
        ("s_filesystem_type", ctypes.c_char), #1
        ("s_inodes_count", ctypes.c_int),    #2
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
## ¿ Que es iNodesTable?
## Tabla de iNodo
class iNodesTable(ctypes.Structure):
    _fields_ = [
        ("i_uid", ctypes.c_int),
        ("I_gid", ctypes.c_int),
        ("i_s", ctypes.c_int),
        ("i_atime", ctypes.c_int),
        ("i_ctime", ctypes.c_int),
        ("s_mtime", ctypes.c_int),
        ("i_block", ctypes.c_int * 15),
        ("i_type", ctypes.c_int),
        ("i_perm", ctypes.c_int),
    ]

class content(ctypes.Structure):
    _fields_ = [
        ("b_name", ctypes.c_char * 12),
        ("b_inodo", ctypes.c_int),
    ]
class FolderBlock(ctypes.Structure):
    _fields_ = [
        ("b_content", content * 4),
    ]
class FileBlock(ctypes.Structure):
    _fields_ = [
        ("b_content", ctypes.c_char * 64),
    ]
class blockPointer(ctypes.Structure):
    _fields_ = [
        ("b_pointers", ctypes.c_int * 16),
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

class Sesion(ctypes.Structure):
    _fields_ = [
        ("id_user", ctypes.c_int),
        ("id_grp", ctypes.c_int),
        ("inicioSuper", ctypes.c_int),
        ("inicioJournal", ctypes.c_int),
        ("tipo_sistema", ctypes.c_int),
        ("direccion", ctypes.c_wchar_p),  # Assuming QString is equivalent to wchar_t*
        ("fit", ctypes.c_char)
    ]

# Define the Usuario structure in Python using ctypes
class Usuario(ctypes.Structure):
    _fields_ = [
        ("id_usr", ctypes.c_int),
        ("id_grp", ctypes.c_int),
        ("username", ctypes.c_char * 12),
        ("password", ctypes.c_char * 12),
        ("group", ctypes.c_char * 12)
    ]
class DiscoMontado:
    def __init__(self):
        self.path = ""
        self.id = ""
        self.counter = 0 # Contador de discos montados
        self.size = ""
        self.start = 0


class SesionIniciada():
    def __init__(self):
        self.id_user = ""
        self.id_grp = ""
        self.inicio_super = ""
        self.tipo_sistema = ""
        self.direccion = ""
        self.fit = ""
        self.inicio_Journal = ""
        self.counter = 0 # Contador de discos montados
        self.active = False # Indicador de Sesiones





class DiscosMontados:
    def __init__(self):
        self.discos = [] # Arreglo de DiscosMontados
        self.counter = 0 # Contador de discos montados
        self.numeroParticion = -1
    def mountDisco(self, name, path, numeroParticion, size, start):
        disco = DiscoMontado()
        disco.path = path
        disco.counter = numeroParticion
        disco.size = size
        disco.start = start
        # el numero de la particion puede ser 0, 1, 2 o 3
        disco.id = "54" + str(disco.counter) + name
        self.discos.append(disco)
        disco.counter += 1
        self.printDiscos()

    def printDiscos(self):
        for disco in self.discos:
            print("ID: " + disco.id + " Path: " + disco.path + "->" , end="")
        print(self.discos)
    def unmountDisco(self, id)-> bool:
        for disco in self.discos:
            if disco.id == id:
                self.discos.remove(disco)
                return True
        return False
    def exists(self, id) -> bool:
        print("Seaching...")
        # Recuperamos el MBR
        for disco in self.discos:
            if disco.id == id:
                print("Particion encontrada!")
                return True
        return False

    def returnPath(self, id):
        print("Seaching...")
        print(self.discos)
        # Recuperamos el MBR
        for disco in self.discos:
            print("--> " + disco.id)
            if disco.id == id:
                print("Particion encontrada!")
                return disco.path
        return False

    def returnStart(self, id):
        print("Seaching...")
        print(self.discos)
        # Recuperamos el MBR
        for disco in self.discos:
            print("--> " + disco.id)
            if disco.id == id:
                print("Particion encontrada!")
                return disco.start
        return False

    def returnSize(self, id):
        print("Seaching...")
        print(self.discos)
        # Recuperamos el MBR
        for disco in self.discos:
            print("--> " + disco.id)
            if disco.id == id:
                print("Particion encontrada!")
                return disco.size
        return False


