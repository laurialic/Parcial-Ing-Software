# Sistema de Gestión Financiera Interactivo

from abc import ABC, abstractmethod

# Singleton para conexión bancaria
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

    def notificar_deposito(self, usuario, monto):
        print(f"\n[Banco] Notificación de depósito: ${monto} para {usuario.nombre}")
        usuario.cuenta.procesar_deposito(monto)

# Clase Usuario
class Usuario:
    def __init__(self, nombre, cuenta):
        self.nombre = nombre
        self.cuenta = cuenta

# Clase Cuenta
class Cuenta:
    def __init__(self, saldo_inicial=0):
        self.saldo = saldo_inicial
        self.gestor = GestorFinanzas(self)

    def procesar_deposito(self, monto):
        self.saldo += monto
        print(f"[Cuenta] Nuevo saldo: ${self.saldo}")
        self.gestor.sugerir_distribucion(monto)

# Facade para simplificar el acceso al sistema financiero
class GestorFinanzas:
    def __init__(self, cuenta):
        self.cuenta = cuenta
        self.plantillas = [Plantilla50_25_25(), Plantilla70_20_10()]

    def sugerir_distribucion(self, monto):
        print("\n[Gestor] Sugerencias de distribución:")
        for idx, plantilla in enumerate(self.plantillas, 1):
            print(f"{idx}. {plantilla.descripcion()}")
        eleccion = int(input("\nSeleccione la plantilla deseada (número): "))
        if 1 <= eleccion <= len(self.plantillas):
            self.plantillas[eleccion - 1].aplicar(monto)
        else:
            print("[Error] Selección inválida.")

# Strategy para diferentes plantillas de ahorro
class PlantillaAhorro(ABC):
    @abstractmethod
    def aplicar(self, monto):
        pass

    @abstractmethod
    def descripcion(self):
        pass

class Plantilla50_25_25(PlantillaAhorro):
    def aplicar(self, monto):
        print(f"\n- 50% Ahorros: ${monto * 0.5:.2f}\n- 25% Emergencias: ${monto * 0.25:.2f}\n- 25% Gastos: ${monto * 0.25:.2f}")

    def descripcion(self):
        return "50% Ahorros, 25% Emergencias, 25% Gastos"

class Plantilla70_20_10(PlantillaAhorro):
    def aplicar(self, monto):
        print(f"\n- 70% Ahorros: ${monto * 0.7:.2f}\n- 20% Educación: ${monto * 0.2:.2f}\n- 10% Ocio: ${monto * 0.1:.2f}")

    def descripcion(self):
        return "70% Ahorros, 20% Educación, 10% Ocio"

# Sistema de Login básico
class SistemaLogin:
    usuarios = {}

    @classmethod
    def registrar_usuario(cls):
        nombre = input("Ingrese su nombre: ")
        saldo_inicial = float(input("Ingrese su saldo inicial: "))
        cuenta = Cuenta(saldo_inicial)
        cls.usuarios[nombre] = Usuario(nombre, cuenta)
        print(f"\n[Login] Usuario {nombre} registrado exitosamente.")

    @classmethod
    def autenticar(cls):
        nombre = input("\nIngrese su nombre para iniciar sesión: ")
        usuario = cls.usuarios.get(nombre, None)
        if usuario:
            print(f"[Login] Bienvenido/a {nombre}!\n")
        else:
            print("[Error] Usuario no encontrado.")
        return usuario

# Simulación interactiva del sistema
if __name__ == "__main__":
    print("Bienvenido al Sistema de Gestión Financiera\n")
    while True:
        print("1. Registrar usuario")
        print("2. Iniciar sesión y realizar depósito")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            SistemaLogin.registrar_usuario()
        elif opcion == "2":
            usuario = SistemaLogin.autenticar()
            if usuario:
                banco = BancoNotificador.get_instance()
                monto = float(input("Ingrese el monto del depósito: "))
                banco.notificar_deposito(usuario, monto)
        elif opcion == "3":
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("[Error] Opción inválida. Intente nuevamente.\n")
