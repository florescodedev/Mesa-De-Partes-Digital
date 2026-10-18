import json
import os
import tempfile
from pathlib import Path
from datetime import datetime 

# Ruta del archivo JSON
CARPETA_PROYECTO = Path(__file__).resolve().parent
ARCHIVO_JSON = CARPETA_PROYECTO / "expedientes.json"


# Funcion para cargar los expedientes
def cargar_expedientes():
    if not ARCHIVO_JSON.exists():
        return []

    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as archivo:
            expedientes = json.load(archivo)

        if not isinstance(expedientes, list):
            raise ValueError("El JSON debe contener una lista.")

        campos = {
            "codigo", "nombre", "documento",
            "asunto", "datos_adicionales", "fecha"
        }

        for expediente in expedientes:
            if not isinstance(expediente, dict):
                raise ValueError("Hay un expediente inválido.")

            if not campos.issubset(expediente):
                raise ValueError("Faltan campos en un expediente.")

            if not all(
                isinstance(expediente[campo], str)
                for campo in campos
            ):
                raise ValueError("Hay campos con tipos incorrectos.")

        codigos = [e["codigo"] for e in expedientes]

        if len(codigos) != len(set(codigos)):
            raise ValueError("Existen códigos duplicados.")

        return expedientes

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("ERROR: No se pudieron cargar los expedientes.")
        print("Detalle:", error)
        return None


# RF0001: Ingreso de solicitud
def ingresar_solicitud():
    print("\n===== REGISTRO DE SOLICITUD =====")

    nombre = input("Nombre completo: ").strip()
    documento = input("DNI (8 dígitos): ").strip()
    asunto = input("Asunto del trámite: ").strip()
    datos_adicionales = input("Datos adicionales (opcional): ").strip()

    solicitud = {
        "nombre": nombre,
        "documento": documento,
        "asunto": asunto,
        "datos_adicionales": datos_adicionales
    }

    return solicitud


# RF0002: Validación de datos
def validar_datos(solicitud):
    valido = True

    nombre = solicitud["nombre"]
    documento = solicitud["documento"]
    asunto = solicitud["asunto"]

    if len(nombre) == 0:
        print("Error: ingrese el nombre completo.")
        valido = False

    if len(documento) != 8 or not documento.isdigit():
        print("Error: el DNI debe contener 8 dígitos.")
        valido = False

    if len(asunto) == 0:
        print("Error: ingrese el asunto del trámite.")
        valido = False

    return valido


# RF0003: Generación de código único
def generar_codigo(expedientes):
    mayor_numero = 0

    for expediente in expedientes:
        codigo = expediente["codigo"]

        if codigo.startswith("EXP-"):
            numero_texto = codigo[4:]

            if numero_texto.isdigit():
                numero = int(numero_texto)

                if numero > mayor_numero:
                    mayor_numero = numero

    siguiente = mayor_numero + 1

    codigo_nuevo = f"EXP-{siguiente:04d}"

    return codigo_nuevo


# RF0004: Almacenamiento seguro en JSON
def guardar_expediente(expedientes, expediente_nuevo):

    codigo_nuevo = expediente_nuevo["codigo"]

    # Verificar que el código no esté repetido
    for expediente in expedientes:
        if expediente["codigo"] == codigo_nuevo:
            print("Error: el código ya existe.")
            return False

    # Crear una copia de la lista
    lista_actualizada = expedientes.copy()

    # Agregar el nuevo expediente a la copia
    lista_actualizada.append(expediente_nuevo)

    archivo_temporal = None

    try:
        # Crear un archivo temporal en la misma carpeta
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".tmp",
            dir=CARPETA_PROYECTO,
            delete=False
        ) as archivo:

            archivo_temporal = archivo.name

            json.dump(
                lista_actualizada,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        # Reemplazar el JSON solo después de escribir
        os.replace(archivo_temporal, ARCHIVO_JSON)

        # Actualizar la lista original después del éxito
        expedientes.append(expediente_nuevo)

        print("Expediente guardado correctamente.")
        return True

    except (OSError, TypeError, ValueError) as error:
        print("Error: no se pudo guardar el expediente.")
        print("Detalle:", error)
        return False

    finally:
        # Eliminar el temporal si quedó sin utilizar
        if archivo_temporal and os.path.exists(archivo_temporal):
            try:
                os.remove(archivo_temporal)
            except OSError:
                pass


# RF0005: Emisión de comprobante y confirmación
def emitir_comprobante(expediente, guardado_correcto):

    # Verificar si el expediente se guardó en JSON
    if not guardado_correcto:
        print("No se puede emitir el comprobante.")
        print("El expediente no fue guardado.")
        return False

    # Preparar el contenido del comprobante
    comprobante = (
        "====================================\n"
        "       COMPROBANTE DE RECEPCIÓN\n"
        "====================================\n"
        f"Código: {expediente['codigo']}\n"
        f"Ciudadano: {expediente['nombre']}\n"
        f"Asunto: {expediente['asunto']}\n"
        f"Fecha: {expediente['fecha']}\n"
        "====================================\n"
    )

    print("\nExpediente registrado correctamente.")
    print(comprobante)

    try:
        # Crear la carpeta de comprobantes
        carpeta = CARPETA_PROYECTO / "comprobantes"
        carpeta.mkdir(exist_ok=True)

        # Preparar el nombre del archivo TXT
        nombre_archivo = (f"comprobante_{expediente['codigo']}.txt")

        ruta_comprobante = carpeta / nombre_archivo

        # Guardar el comprobante
        with open(ruta_comprobante,"w",encoding="utf-8") as archivo:
            archivo.write(comprobante)

        print("Comprobante guardado correctamente.")
        print("Archivo:", ruta_comprobante.name)

        return True

    except OSError as error:
        print("Error: no se pudo guardar el comprobante.")
        print("Detalle:", error)
        print("El expediente sigue registrado en JSON.")
        return False


# RF0006: Búsqueda y consulta de expedientes
def buscar_expediente(expedientes):

    print("\n===== BÚSQUEDA DE EXPEDIENTES =====")

    codigo_buscado = input(
        "Ingrese el código del expediente: "
    ).strip().upper()

    # Validar que se haya ingresado un código
    if codigo_buscado == "":
        print("Error: debe ingresar un código.")
        return None

    # Recorrer los expedientes existentes
    for expediente in expedientes:

        if expediente["codigo"] == codigo_buscado:

            print("\n===== EXPEDIENTE ENCONTRADO =====")
            print("Código:", expediente["codigo"])
            print("Ciudadano:", expediente["nombre"])
            print("Documento:", expediente["documento"])
            print("Asunto:", expediente["asunto"])
            print(
                "Datos adicionales:",
                expediente["datos_adicionales"]
            )
            print("Fecha:", expediente["fecha"])

            return expediente

    # Si termina el bucle sin encontrar coincidencias
    print("\nNo se encontró el expediente.")
    return None


# RF0007: Ordenamiento de expedientes
def ordenar_expedientes(expedientes, criterio):

    # Crear una copia para no alterar la lista original
    lista_ordenada = expedientes.copy()

    cantidad = len(lista_ordenada)

    # Algoritmo de ordenamiento burbuja
    for i in range(cantidad - 1):

        for j in range(cantidad - 1 - i):

            valor_actual = lista_ordenada[j][criterio]
            valor_siguiente = lista_ordenada[j + 1][criterio]

            if valor_actual > valor_siguiente:

                # Intercambiar las posiciones
                lista_ordenada[j], lista_ordenada[j + 1] = (
                    lista_ordenada[j + 1],
                    lista_ordenada[j]
                )
    return lista_ordenada


# RF0007: Listado de expedientes
def listar_expedientes(expedientes):

    print("\n===== LISTADO DE EXPEDIENTES =====")

    if len(expedientes) == 0:
        print("No existen expedientes registrados.")
        return

    print("1. Ordenar por código")
    print("2. Ordenar por fecha")

    opcion_orden = input("Seleccione un criterio: ").strip()

    if opcion_orden == "1":
        criterio = "codigo"

    elif opcion_orden == "2":
        criterio = "fecha"

    else:
        print("Error: criterio de ordenamiento inválido.")
        return

    lista_ordenada = ordenar_expedientes(expedientes,criterio)

    print("\n===== EXPEDIENTES ORDENADOS =====")

    for expediente in lista_ordenada:
        print("------------------------------------")
        print("Código:", expediente["codigo"])
        print("Ciudadano:", expediente["nombre"])
        print("Documento:", expediente["documento"])
        print("Asunto:", expediente["asunto"])
        print("Fecha:", expediente["fecha"])

    print("------------------------------------")
    print("Total de expedientes:", len(lista_ordenada))


# Función del menú principal
def menu_principal():
    expedientes = cargar_expedientes()

    if expedientes is None:
        print("El programa se cerrará para proteger los datos.")
        return

    while True:
        print("\n========== MESA DE PARTES DIGITAL ==========")
        print("1. Registrar nueva solicitud")
        print("2. Buscar expediente")
        print("3. Listar y ordenar expedientes")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()
      
        
        if opcion == "1":
            solicitud = ingresar_solicitud()

            if validar_datos(solicitud):

                codigo = generar_codigo(expedientes)
                fecha = datetime.now().strftime("%Y-%m-%d")

                expediente_nuevo = {
                "codigo": codigo,
                "nombre": solicitud["nombre"],
                "documento": solicitud["documento"],
                "asunto": solicitud["asunto"],
                "datos_adicionales": solicitud["datos_adicionales"],
                "fecha": fecha
                }

                guardado_correcto = guardar_expediente(
                expedientes,
                expediente_nuevo)

                if guardado_correcto:
                    comprobante_guardado = emitir_comprobante(
                    expediente_nuevo,
                    guardado_correcto
                    )

                    if not comprobante_guardado:
                        print("El registro existe, pero falta el TXT.")

                else:
                    print("No se completó el registro.")

            else:
                print("\nLa solicitud contiene errores.")
                print("Intente registrar nuevamente.")



        
        elif opcion == "2":
            buscar_expediente(expedientes)

        
        elif opcion == "3":
            listar_expedientes(expedientes)

        elif opcion == "4":
            print("\nGracias por utilizar el sistema.")
            break

        else:
            print("\nError: seleccione una opción válida.")


# Punto de inicio del programa
if __name__ == "__main__":
    menu_principal()
