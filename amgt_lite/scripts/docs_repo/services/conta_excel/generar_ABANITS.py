import os
from lxml import etree
import pandas as pd

import unicodedata

def normalizar_texto(texto: str) -> str:
    if texto is None:
        return ""
    # Quitar acentos/tildes
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("utf-8")
    # Pasar a minúsculas y quitar espacios extra
    return texto.strip().lower()

# Namespaces UBL 2.1
ns = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
}

def extraer_proveedores(carpeta: str) -> pd.DataFrame:
    registros = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xml"):
            ruta = os.path.join(carpeta, archivo)
            try:
                tree = etree.parse(ruta)

                # Proveedor
                nit_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=ns)
                nombre_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", namespaces=ns)
                razon_social = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces=ns)
                direccion_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line", namespaces=ns)
                email_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=ns)
                telefono_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone", namespaces=ns)
                ciudad_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName", namespaces=ns)
                departamento_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity", namespaces=ns)

                registros.append({
                    "nit": nit_prov,
                    "nombre": nombre_prov,
                    "Razon_Social": razon_social,
                    "Direccion": direccion_prov,
                    "departamento": departamento_prov,
                    "Ciudad": ciudad_prov,
                    "Telefono": telefono_prov,
                    "Email": email_prov
                })

            except Exception as e:
                print(f"Error procesando {archivo}: {e}")

    # Crear DataFrame
    columnas = [
        "nit", "nombre", "Razon_Social", "Direccion", "departamento", "Ciudad", "Telefono", "Email"
    ]
    return pd.DataFrame(registros, columns=columnas)



def extraer_clientes(carpeta: str) -> pd.DataFrame:
    registros = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xml"):
            ruta = os.path.join(carpeta, archivo)
            try:
                tree = etree.parse(ruta)

                # Cliente
                nit_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=ns)
                nombre_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name", namespaces=ns)
                razon_social_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", namespaces=ns)
                direccion_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:RegistrationAddress/cac:AddressLine/cbc:Line", namespaces=ns)
                email_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=ns)
                telefono_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone", namespaces=ns)
                ciudad_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName", namespaces=ns)
                departamento_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity", namespaces=ns)
                registros.append({
                    "nit": nit_cli,
                    "nombre": nombre_cli,
                    "Razon_Social": razon_social_cli,
                    "Direccion": direccion_cli,
                    "departamento": departamento_cli,
                    "Ciudad": ciudad_cli,
                    "Telefono": telefono_cli,
                    "Email": email_cli
                })

            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
    
    # Crear DataFrame
    columnas = [
        "nit", "nombre", "Razon_Social", "Direccion", "departamento", "Ciudad", "Telefono", "Email"
    ]
    return pd.DataFrame(registros, columns=columnas)




def generar_abanits(carpeta: str, proveedor: bool) -> pd.DataFrame:
    if proveedor:
        # Extraer proveedores
        df_proveedores = extraer_proveedores(carpeta)

        # Normalizar primero
        for col in ["nit", "nombre", "Razon_Social", "Direccion", "departamento", "Ciudad", "Telefono", "Email"]:
            df_proveedores[col] = df_proveedores[col].apply(normalizar_texto)

        # Eliminar duplicados por NIT
        df_proveedores = df_proveedores.drop_duplicates(subset=["nit"], keep="first")

        # Guardar en CSV
        #df_proveedores.to_csv("proveedores.csv", index=False, sep=",", encoding="utf-8")
        return df_proveedores

    else:
        # Extraer clientes
        df_clientes = extraer_clientes(carpeta)

        # Normalizar primero
        for col in ["nit", "nombre", "Razon_Social", "Direccion", "departamento", "Ciudad", "Telefono", "Email"]:
            df_clientes[col] = df_clientes[col].apply(normalizar_texto)

        for col in ["nit", "nombre", "Razon_Social", "Direccion", "departamento", "Ciudad", "Telefono", "Email"]:
            df_clientes[col] = df_clientes[col].apply(normalizar_texto)

        # Eliminar duplicados por NIT
        df_clientes = df_clientes.drop_duplicates(subset=["nit"], keep="first")

        return df_clientes