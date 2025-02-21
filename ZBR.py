import sqlite3
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import defaultdict

# Conexión a la base de datos
def conectar_db():
    return sqlite3.connect('sistema_financiero.db')

# Crear la base de datos y las tablas si no existen
def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        correo TEXT NOT NULL UNIQUE,
                        contrasena TEXT NOT NULL,
                        saldo REAL DEFAULT 0
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER,
                        tipo TEXT,
                        monto REAL,
                        fecha TEXT,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                      )''')
    conn.commit()
    conn.close()

# Función para validar correo electrónico
def validar_correo(correo):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b'
    return re.match(regex, correo) is not None

# Función para validar contraseñas seguras
def validar_contrasena(contrasena):
    # Al menos 8 caracteres, con una mayúscula, una minúscula, y un número
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
    return re.match(regex, contrasena) is not None

# Sistema de Login y Registro
class SistemaLogin:
    @classmethod
    def registrar_usuario(cls):
        nombre = input("Ingrese su nombre: ")
        correo = input("Ingrese su correo: ")
        while not validar_correo(correo):
            print("[Error] Correo inválido. Intente nuevamente.")
            correo = input("Ingrese su correo: ")
        
        contrasena = input("Ingrese su contraseña: ")
        while not validar_contrasena(contrasena):
            print("[Error] Contraseña no segura. Asegúrese de que tenga al menos 8 caracteres, con una mayúscula, minúscula y un número.")
            contrasena = input("Ingrese su contraseña: ")

        saldo_inicial = float(input("Ingrese su saldo inicial: "))
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena, saldo) VALUES (?, ?, ?, ?)",
                       (nombre, correo, contrasena, saldo_inicial))
        conn.commit()
        conn.close()
        print(f"\n[Login] Usuario {nombre} registrado exitosamente.")

    @classmethod
    def autenticar(cls):
        correo = input("\nIngrese su correo para iniciar sesión: ")
        contrasena = input("Ingrese su contraseña: ")
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?", (correo, contrasena))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            print(f"[Login] Bienvenido/a {usuario[1]}!\n")
            return usuario
        else:
            print("[Error] Credenciales inválidas.")
            return None

# BancoNotificador y las clases relacionadas para manejar los depósitos
class BancoNotificador:
    __instance = None

    @staticmethod
    def get_instance():
        if BancoNotificador.__instance is None:
            BancoNotificador()
        return BancoNotificador.__instance

    def __init__(self):
        if BancoNotificador.__instance is not None:
            raise Exception("Esta clase es un Singleton!")
        else:
            BancoNotificador.__instance = self

    def notificar_deposito(self, usuario_id, monto):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (monto, usuario_id))
        conn.commit()
        cursor.execute("INSERT INTO transacciones (usuario_id, tipo, monto, fecha) VALUES (?, ?, ?, ?)",
                       (usuario_id, 'Deposito', monto, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        print(f"[Banco] Notificación de depósito: ${monto}.")

# Estadísticas y gráficos
class Estadisticas:
    @staticmethod
    def generar_grafico(usuario_id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT monto, fecha FROM transacciones WHERE usuario_id = ?", (usuario_id,))
        transacciones = cursor.fetchall()
        conn.close()

        fechas = [datetime.strptime(t[1], "%Y-%m-%d %H:%M:%S") for t in transacciones]
        montos = [t[0] for t in transacciones]

        plt.figure(figsize=(10, 5))
        plt.plot(fechas, montos, label="Ahorros", color="blue", marker='o')
        plt.title("Tendencias de Ahorro")
        plt.xlabel("Fecha")
        plt.ylabel("Monto ($)")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def generar_estadisticas(usuario_id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(monto), strftime('%Y-%m', fecha) FROM transacciones WHERE usuario_id = ? GROUP BY strftime('%Y-%m', fecha)", (usuario_id,))
        transacciones = cursor.fetchall()
        conn.close()

        if transacciones:
            for mes, total in transacciones:
                print(f"{mes}: ${total:.2f}")

# Interfaz para agregar dinero
class InterfazDeposito:
    def realizar_deposito(self, usuario_id):
        monto = float(input("Ingrese el monto del depósito: "))
        banco = BancoNotificador.get_instance()
        banco.notificar_deposito(usuario_id, monto)

# Función principal
if __name__ == "__main__":
    crear_tablas()
    print("Bienvenido al Sistema de Gestión Financiera\n")
    while True:
        print("1. Registrar usuario")
        print("2. Iniciar sesión y realizar depósito")
        print("3. Ver estadísticas")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            SistemaLogin.registrar_usuario()
        elif opcion == "2":
            usuario = SistemaLogin.autenticar()
            if usuario:
                interfaz = InterfazDeposito()
                interfaz.realizar_deposito(usuario[0])  # Usuario ID
        elif opcion == "3":
            usuario = SistemaLogin.autenticar()
            if usuario:
                print("Generando estadísticas...")
                Estadisticas.generar_estadisticas(usuario[0])  # Usuario ID
                Estadisticas.generar_grafico(usuario[0])  # Usuario ID
        elif opcion == "4":
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("[Error] Opción inválida. Intente nuevamente.\n")
