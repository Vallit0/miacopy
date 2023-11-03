# Aqui se deberian hacer imports
from functions.functions import get_tipo_parametro, get_valor_parametro, processPath, removeQuotes
from datetime import datetime
import struct
# Administracion de Discos
from mkdisk.mkdisk import MkDisk
from mkfs.mkfs import Mkfs
from fdisk.fdisk import FDisk
from mount.mount import Mount
from rmdisk.rmdisk import rmdisk_func
from mkgrp.mkgrp import  mkgrp
from rep.rep import rep
from login.login import Login
import re
import sys
import io # For capturing stdout
from graphviz import Digraph
import os
import ctypes
import sys
import os
# Agregar el directorio raíz de tu proyecto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


## Funciones que deberian estar en Functions


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
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analizar', methods=['GET', 'POST'])
def informacion_estudiante():

    if request.method == 'POST':
        # Asumiendo que se hace un POST DE LINEA POR LINEA DESDE EL FRONTEND
        data = request.get_json()
        data = data.trim()
        # Tenemos todos nuestros datos aqui
        # Capture the standard output and standard error
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout


        new_exec = exec()
        new_exec.data = data
        new_exec.executeEndpoint()


        # Restore the original stdout and get the captured output
        sys.stdout = old_stdout
        captured_output = new_stdout.getvalue()

        print("**********", captured_output)


        return jsonify({"respuesta": captured_output}), 200
    else:
        print("GENERAR NUEVO FILE")




if __name__ == '__main__':
    app.run(debug=True)



def analizar_mkdisk(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    #print(parametros)
    #print("Parametros ok")

    # Inicializamos nuestro disco

    ## MKDISK - CLASE
    ## SIZE
    ## UNIT
    ## FIT
    ## CREADO



    disco = MkDisk()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam).replace("\n", "")

        if tipo == "#":
            break
        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-size":
            print("check->", valor)
            disco.size = int(valor)
        elif tipo == "-path":
            print("check->", valor)
            disco.path = valor
        elif tipo == "-name":
            print("check->", valor)
            disco.name = valor
        elif tipo == "-unit":
            print("check->", valor)
            disco.unit = valor
        elif tipo == "-fit":
            print("check->", valor)
            disco.fit = valor
        elif tipo == "#":
            print("check->", valor)
            disco.fit = valor
        else:
            print("Parametro no aceptado en 'mkdisk':", valor)

    answer = disco.make_mkdisk()
    printMBRFile(disco.path)
    return answer




def analizar_mkfs(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    # Inicializamos nuestro disco
    mkfs = Mkfs()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)
        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-id":
            print("check->", valor)
            mkfs.id = valor
        elif tipo == "-type":
            print("check->", valor)
            mkfs.type = valor
        elif tipo == "-fs":
            print("check->", valor)
            mkfs.name = valor
        else:
            print("Parametro no aceptado en 'mkfs':", valor)
            return "Parametro no aceptado en 'mkfs':", valor

    return mkfs.mkfs()


def analizar_mkgrp(parametros):
    new_mkgrp = mkgrp()
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-name":
            print("name->", valor)
            new_mkgrp.name = valor

        else:
            print("Parametro no aceptado en 'mkfs':", valor)

    return new_mkgrp.mkgrp(currentSession)
def analizar_mkfile(parametros):
    new_mkgrp = mkgrp()
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-id":
            print("check->", valor)
            mkgrp.name = valor

        else:
            print("Parametro no aceptado en 'mkfs':", valor)

    new_mkgrp.mkgrp(currentSession)


def analizar_mkusr(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    # Inicializamos nuestro disco
    new_mkgrp = mkgrp()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-name":
            print("name->", valor)
            new_mkgrp.name = valor
        elif tipo == "-grp":
            print("grp->", valor)
            new_mkgrp.grp = valor
        elif tipo == "-pass":
            print("pas->", valor)
            new_mkgrp.pwd = valor


        else:
            print("Parametro no aceptado en 'mkgrp':", valor)
            return "Parametro no aceptado en 'mkgrp':", valor


    return new_mkgrp.mkusr(currentSession)

def analizar_rmusr(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    # Inicializamos nuestro disco
    new_mkgrp = mkgrp()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-user":
            print("user->", valor)
            new_mkgrp.name = valor

        else:
            print("Parametro no aceptado en 'rmusr':", valor)
            return "Parametro no aceptado en 'rmusr':", valor

    return new_mkgrp.rmusr(currentSession.active, currentSession)

'''
Borrado de Grupo
'''
def analizar_rmgrp(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    # Inicializamos nuestro disco
    new_mkgrp = mkgrp()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-name":
            print("name->", valor)
            new_mkgrp.name = valor

        else:
            print("Parametro no aceptado en 'rmgrp':", valor)
            return "Parametro no aceptado en 'rmgrp':", valor

    return new_mkgrp.rmgrp(currentSession.active, currentSession)

def analizar_login(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    # Inicializamos nuestro disco
    login = Login()

    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-user":
            print("user->", valor)
            login.user = valor
        elif tipo == "-pass":
            print("pass->", valor)
            login.pwd = valor
        elif tipo == "-id":
            print("id->", valor)
            login.id = valor
        else:
            print("Parametro no aceptado en 'login':", valor)
            return "Parametro no aceptado en 'login':", valor


    # Check later if it works
    if(login.loginNow() == 1):
        print("Login exitoso")
        return "Login exitoso"
    else:
        print("Login fallido")
        return "Login fallido"


def analizar_logout(parametros):
    login = Login()
    login.log_out()

def graphvizMBR(definedPath):
    packed_data = read_packed_data_from_file(definedPath)
    directory, filename = os.path.split(definedPath)

    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------") # Tambien vamos haciendo el graphviz con Tablas
    partition_table = Digraph(format='png')
    partition_table.attr(node_shape='box', style='filled', fillcolor='lightgray', fontname='Arial')
    partition_table.attr(edge_color='blue')
    # Ahora tomamos el tamano del disco y crearemos una regla de 3 donde 100 -> unpacked_data['mbr_tamano']
    # por lo tanto, si 100/mbr_tamano = x/tamano_particion => x = tamano_particion / mbr_tamano
    # asignaremos width ese valor / 100 por lo que tamano_particion / mbr_tamano


    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print(unpacked_data)
    print("-- Particiones --") # Vamos creando los objetos por particion
    print("0 -> " + str(unpacked_data['mbr_particiones'][0]))
    # status -0, type -1 , fit, start, size, name
    # name
    value = int(unpacked_data['mbr_tamano']) / 100
    partition_table.node('sub0', label='MBR', width='0.5', height='0.5', shape='rectangle', fixedsize='true')
    label = unpacked_data['mbr_particiones'][0][5].decode("utf-8").rstrip('\x00')
    #size = int(unpacked_data['mbr_particiones'][0][4]) / int(unpacked_data['mbr_tamano']) * 10000
    size = 1
    print(size)
    print(str(label))

    partition_table.node('sub1', label=f'{str(label)}', width=f'{size}', height='0.5', shape='rectangle', fixedsize='true')
    print("1 -> " + str(unpacked_data['mbr_particiones'][1]))
    label = unpacked_data['mbr_particiones'][1][5].decode("utf-8").rstrip('\x00')
    #size = int(unpacked_data['mbr_particiones'][1][4]) / int(unpacked_data['mbr_tamano']) * 10000
    size = 1
    print(size)
    print(str(label).rstrip('\x00'))
    partition_table.node('sub2', label=f'{label}', width=f'{size}', height='0.5', shape='rectangle', fixedsize='true')

    print("2 -> " + str(unpacked_data['mbr_particiones'][2]))
    label = unpacked_data['mbr_particiones'][2][5].decode("utf-8").rstrip('\x00')
    #size = int(unpacked_data['mbr_particiones'][2][4]) / int(unpacked_data['mbr_tamano']) * 10000
    size = 1
    print(size)
    print(str(label))
    partition_table.node('sub3', label=f'{label}', width=f'{size}', height='0.5', shape='rectangle', fixedsize='true')

    label = unpacked_data['mbr_particiones'][3][5].decode("utf-8").rstrip('\x00')
    #size = int(unpacked_data['mbr_particiones'][3][4]) / int(unpacked_data['mbr_tamano']) * 10000
    print("3 -> " + str(unpacked_data['mbr_particiones'][3]))
    size = 1
    print(size)
    print(str(label))
    partition_table.node('sub4', label=f'{label}', width=f'{size}', height='0.5', shape='rectangle', fixedsize='true')

    print("--------------")

    with partition_table.subgraph(name='cluster_subrectangles') as c:
        c.node('sub4') if int(unpacked_data['mbr_particiones'][3][0]) == 1 else None
        c.node('sub3') if int(unpacked_data['mbr_particiones'][2][0]) == 1 else None
        c.node('sub2') if int(unpacked_data['mbr_particiones'][1][0]) == 1 else None
        c.node('sub1') if int(unpacked_data['mbr_particiones'][0][0]) == 1 else None
        c.node('sub0')
        c.attr(label=f'{filename}')

    # Set the layout
    partition_table.attr(rankdir='TB')
    partition_table.render('rectangle_example', cleanup=True, format='png', directory='./')
def analizar_fdisk(parametros):
    print(parametros)
    fdisk = FDisk()
    tempPath = ""
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam).replace("\n", "").replace(" ", "")


        if tipo == "#":
            break
        pattern = r'^#'
        if re.match(pattern, tipo):
            break

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-size":
            print("size ->", valor)
            fdisk.size = int(valor)
        elif tipo == "-path":
            print("path ->", valor)
            # clean path

            fdisk.path = valor
            tempPath = valor
        elif tipo == "-name":
            print("name ->", valor)
            fdisk.name = valor
        elif tipo == "-unit":
            print("unit ->", valor)
            fdisk.unit = valor
        elif tipo == "-fit":
            print("check->", valor)
            if(valor.lower() == "bf"):
                fdisk.fit = "B"
            elif(valor.lower() == "ff"):
                fdisk.fit = "F"
            elif(valor.lower() == "wf"):
                fdisk.fit = "W"
            else:
                fdisk.fit = ""
        elif tipo == "-type":
            print("type ->", valor)
            fdisk.type = valor
        elif tipo == "-add":
            print("add-> 1")
            fdisk.addValue = int(valor)
            fdisk.add = 1
            fdisk.delete = 0
        elif tipo == "-delete":
            print("delete-> 1")
            fdisk.deleteValue = valor
            fdisk.delete = 1
            fdisk.add = 0
        else:
            print("Parametro no aceptado en 'fdisk':", valor)

    answer = fdisk.fdisk()
    #print("." + fdisk.path)
    #print("---------------------------------------------")
    #print("------- MBR ---------------------------------")

    # @Unit Test: Print MBR
    print("")
    printMBRFile(fdisk.path)
    return answer


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
def printEBRFile(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    unpacked_data = unpack_ebr(packed_data, start)
    print("-------EBR 1 ---------")
    print("part_status->" + str(unpacked_data['part_status']))
    print("part_fit->" + str(unpacked_data['part_fit']))
    print("part_start->" + str(unpacked_data['part_start']))
    print("part_next->" + str(unpacked_data['part_next']))
    print("part_size->" + str(unpacked_data['part_size']))
def analizar_mount(parametros):
    print(parametros)
    mount = Mount()
    tempPath = ""
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam).replace("\n", "").replace(" ", "")

        if tipo == "#":
            break
        pattern = r'^#'
        if re.match(pattern, tipo):
            break
        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-path":
            print("path ->", valor)
            mount.path = "." + valor
        elif tipo == "-name":
            print("name ->", valor)
            mount.name = valor

        else:
            print("Parametro no aceptado en 'mount':", valor)

    return mount.mount()
    #graphvizMBR(tempPath)
def analizar_unmount(parametros):
    print(parametros)
    mount = Mount()
    tempPath = ""
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam).replace("\n", "").replace(" ", "")

        # Verificamos cuál parámetro es para inicializar el objeto (los parámetros ya vienen en lowercase)
        if tipo == "-id":
            print("id ->", valor)
            mount.id = valor
        else:
            print("Parametro no aceptado en 'unmount':", valor)
            return ("Parametro no aceptado en 'unmount':" + str(valor))

    return mount.unmount()
    # graphvizMBR(tempPath)
def analizar_rep(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    print(parametros)
    print("Parametros ok")
    path = ""
    reporte = rep()
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)

        if tipo == "-name":
            print("path->", valor)
            path = valor
            if valor == 'mbr':
                reporte.name = "mbr"
            elif valor == 'disk':
                reporte.name = "disk"
            elif valor == 'inode':
                reporte.name = "inode"
            elif valor == 'journaling':
                reporte.name = "journaling"
            elif valor == 'block':
                reporte.name = "block"
            elif valor == 'bm_inode':
                reporte.name = "bm_inode"
            elif valor == 'bm_block':
                reporte.name = "bm_block"
            elif valor == 'tree':
                reporte.name = "tree"
            elif valor == 'sb':
                reporte.name = "sb"
            elif valor == 'file':
                reporte.name = "file"
            elif valor == 'ls':
                reporte.name = "ls"
            else:
                print("No se reconoce el reporte")

        elif tipo == "-path":
            print("path->", valor)
            reporte.path = valor
        elif tipo == "-id":
            print("path->", valor)
            reporte.id = valor
        elif tipo == "-ruta":
            print("path->", valor)
            reporte.ruta = valor
        else:
            print("Parametro no aceptado en 'rep':", valor)

    reporte.reportar()
def analizar_exec(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    execute = exec()
    #print(parametros)
    #print("Parametros ok")
    #path = ""
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam)
        if tipo == "-path":
            print("check->", valor)
            execute.path = "." + valor

        else:
            print("Parametro no aceptado en 'execute':", valor)

    execute.execute()


def analizar_rmdisk(parametros):
    # Pasamos a la siguiente posición
    # parametros = parametros.split("`")[1:]
    print(parametros)
    print("Parametros ok")
    path = ""
    while parametros:
        # Obtenemos el tipo y el valor del parametro actual
        tmpParam = parametros.pop(0)
        tipo = get_tipo_parametro(tmpParam)
        valor = get_valor_parametro(tmpParam).replace("\n", "").replace(" ", "")

        if tipo == "-path":
            print("check->", valor)
            path = valor
        else:
            print("Parametro no aceptado en 'rmdisk':", valor)


    return rmdisk_func(path)
def unpack_mbr(packed_data):
    unpacked_mbr = {}

    mbr_size = struct.calcsize("iii1s")
    mbr_data = packed_data[:mbr_size] # probablemente
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

def read_packed_data_from_file( file_path):
    with open("." + file_path, 'rb') as file:
        packed_data = file.read()
    return packed_data

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


def getMBR(definedPath):
    packed_data = read_packed_data_from_file(definedPath)

    unpacked_data = unpack_mbr(packed_data)
    print("-------MBR---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    return unpacked_data

def unpack_superblock(packed_data, start):
    unpacked_superblock = {}
    superblock_size = struct.calcsize("cccciiiiiiiiiiiiiiii")
    superblock_data = packed_data[start:start + superblock_size]
    unpacked_superblock = struct.unpack("cccciiiiiiiiiiiiiiii", superblock_data)

    # Create a dictionary with field names as keys
    field_names = [field[0] for field in Superblock._fields_]
    unpacked_superblock = dict(zip(field_names, unpacked_superblock))

    return unpacked_superblock

def unpack_iNodesTable(packed_data, start):
    iNodesTable_size = struct.calcsize("cciiiiiii")
    iNodesTable_data = packed_data[start:start + iNodesTable_size]
    unpacked_iNodesTable = struct.unpack("cciiiiiii", iNodesTable_data)

    # Create a dictionary with field names as keys
    field_names = [field[0] for field in iNodesTable._fields_]
    unpacked_dict = dict(zip(field_names, unpacked_iNodesTable))

    return unpacked_dict

def log_out(self):
    global flag_login, currentSession

    if flag_login:
        flag_login = False
        currentSession.id_user = -1
        # currentUser.id_grp = -1
        currentSession.direccion = ""
        currentSession.inicioSuper = -1
        print("...\nSesion finalizada ")
    else:
        print("ERROR no hay ninguna sesion activa")
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


def getSuperblock(definedPath, start):
    packed_data = read_packed_data_from_file(definedPath)
    ## unpack_mbr puede tener un error dentro
    unpacked_data = unpack_superblock(packed_data, start)
    print("-------Superbloque ---------")
    print("part_status->" + str(unpacked_data['part_status']))
    print("part_fit->" + str(unpacked_data['part_fit']))
    print("part_start->" + str(unpacked_data['part_start']))
    print("part_next->" + str(unpacked_data['part_next']))
    print("part_size->" + str(unpacked_data['part_size']))
    return unpacked_data
def getiNodesTable(start, definedPath):
    packed_data = read_packed_data_from_file(definedPath)

    unpacked_data = unpack_iNodesTable(packed_data, start)
    print("-------Superbloque---------")
    print("mbr_tamano->" + str(unpacked_data['mbr_tamano']))
    print("mbr_fit->" + str(unpacked_data['mbr_fit']))
    print("mbr_disk_signature->" + str(unpacked_data['mbr_dsk_signature']))
    print("mbr_fecha->" + str(datetime.fromtimestamp(unpacked_data['mbr_fecha_creacion'])))
    return unpacked_data

class exec:
    def __init__(self):
        self.path = ""
        self.data = ""

    def execute(self):
        i = 0
        self.remove_quotes()
        print("Ejecutando: " + self.path)
        try:
            archivo = open(self.path, "r")
            for linea in archivo.readlines():
                print(linea)
                print("------------------------------")
                print(i, end="")
                i = i + 1
                try:
                    analizar(linea)
                except:
                    print("\x1b[93mError al ejecutar el comando " + linea + "\x1b[0m")
                    continue

            print("Ejecucion finalizada")
        except:
            print("Error al abrir el archivo")

    def executeEndpoint(self):
        i = 0
        self.remove_quotes()
        print("Ejecutando: " + self.path)
        try:
            archivo = self.data.split('\n')
            for linea in archivo:
                print(linea)
                print("------------------------------")
                print(i, end="")
                i = i + 1
                try:
                    analizar(linea)
                except:
                    print("\x1b[93mError al ejecutar el comando " + linea + "\x1b[0m")
                    continue

            print("Ejecucion finalizada")
        except:
            print("Error al abrir el archivo")



    def remove_quotes(self):
        if isinstance(self.path, str):
            self.path = self.path.replace('"', '').replace("'", '')
        else:
            self.path = self.path  # Return unchanged if not a string



# Ahora analizar retorna un string
def analizar(comando):
    # Antes de empezar a analizar el comando, debemos hacer una función que reciba
    # como parámetro el comando y busque si hay "" en "path"
    #print("===========")
    #print(comando)
    newComando = processPath(comando)
    #print("------- Parsing ------")
    #print(newComando)
    #print("===== Eliminacion Comillas ======")
    ComandoFinal = removeQuotes(newComando)
    #print(ComandoFinal)
    # Use a list to split the command into tokens
    tokens = ComandoFinal.split("`")
    if tokens[0].lower() == "mkdisk":
        print("\033[1;35m[MKDISK]\033[0m")
        # analizar_mkdisk
        respuesta  = analizar_mkdisk(tokens)
        return respuesta
    elif tokens[0].lower() == "rmdisk":
        print("\033[1;35m[RMDISK]\033[0m")
        # analizar_rmdisk
        respuesta  = analizar_rmdisk(tokens)
        return respuesta
    elif tokens[0].lower() == "fdisk":
        print("\033[1;35m[FDISK]\033[0m")
        # analizar_fdisk
        respuesta  = analizar_fdisk(tokens)
        return respuesta
    elif tokens[0].lower() == "mount":
        print("\033[1;35m[MOUNT]\033[0m")
        #analizar_mount
        respuesta  = analizar_mount(tokens)
        return respuesta
    elif tokens[0].lower() == "unmount":
        print("\033[1;35m[UNMOUNT]\033[0m")
        # analizar_unmount
        respuesta  = analizar_unmount(tokens)
        return respuesta
    elif tokens[0].lower() == "mkfs":
        print("\033[1;35m[MKFS]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_mkfs(tokens)
        return respuesta

    elif tokens[0].lower() == "login":
        print("\033[1;35m[LOGIN]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_login(tokens)
        return respuesta

    elif tokens[0].lower() == "logout":
        print("\033[1;35m[LOGOUT]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_logout(tokens)
        return respuesta

    elif tokens[0].lower() == "mkgrp":
        print("\033[1;35m[MKGRP]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_mkgrp(tokens)
        return respuesta
    elif tokens[0].lower() == "mkusr":
        print("\033[1;35m[MKUSR]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_mkusr(tokens)
        return respuesta
    elif tokens[0].lower() == "rmgrp":
        print("\033[1;35m[RMGRP]\033[0m")
        # analizar_mkfs
        respuesta  = analizar_rmgrp(tokens)
        return respuesta
    elif tokens[0].lower() == "rmusr":
        print("\033[1;35m[RMGRP]\033[0m")
        # analizar_mkfs
        respuesta = analizar_rmusr(tokens)
        return respuesta
    elif tokens[0].lower() == "mkfile":
        print("\033[1;35m[MKFILE]\033[0m")
        # analizar_mkfs
        analizar_mkfile(tokens)
    elif tokens[0].lower() == "rep":
        print("\033[1;35m[REP]\033[0m")
        # analizar_rep
        respuesta  = analizar_rep(tokens)
        # Caso a tomar en cuenta luego
        return respuesta
    elif tokens[0].lower() == "execute":
        print("\033[1;35m[EXECUTE]\033[0m")
        # analizar_rep
        analizar_exec(tokens)
    elif tokens[0].lower() == "pause":
        print("\033[1;35m[Pause]\033[0m")
        # analizar_rep
        input("Presione enter para continuar...")
        return "pause"
    elif tokens[0].lower() == "#":
        print("----------")
        # analizar_rep
        #analizar_exec(tokens)



