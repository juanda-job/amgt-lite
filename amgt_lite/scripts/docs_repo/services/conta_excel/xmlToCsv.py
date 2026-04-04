import os
from lxml import etree
import pandas as pd

# Namespaces UBL 2.1
ns = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
}

def extraer_facturas(carpeta: str) -> pd.DataFrame:
    registros = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xml"):
            ruta = os.path.join(carpeta, archivo)
            try:
                tree = etree.parse(ruta)

                # Datos básicos
                fecha = tree.findtext(".//cbc:IssueDate", namespaces=ns)
                tipo_doc = str(tree.findtext(".//cbc:ProfileID", namespaces=ns)).replace("DIAN 2.1:","").strip()
                numero_doc = tree.findtext(".//cbc:ID", namespaces=ns)
                moneda = tree.findtext(".//cbc:DocumentCurrencyCode", namespaces=ns)

                # Proveedor
                nit_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=ns)
                nombre_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", namespaces=ns)
                direccion_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line", namespaces=ns)
                email_prov = tree.findtext(".//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=ns)

                # Cliente
                nit_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID", namespaces=ns)
                nombre_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name", namespaces=ns)
                direccion_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line", namespaces=ns)
                email_cli = tree.findtext(".//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail", namespaces=ns)

                # Totales
                subtotal = tree.findtext(".//cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces=ns)
                total_sin = tree.findtext(".//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces=ns)
                total_con = tree.findtext(".//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", namespaces=ns)
                total_pagar = tree.findtext(".//cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=ns)

                # Forma de pago
                payment_code = tree.findtext(".//cac:PaymentMeans/cbc:ID", namespaces=ns)
                if payment_code == "1":
                    forma_pago = "Contado"
                elif payment_code == "2":
                    forma_pago = "Crédito"
                else:
                    forma_pago = "Desconocido"

                # Líneas de detalle con múltiples impuestos
                for line in tree.findall(".//cac:InvoiceLine", namespaces=ns):
                    cantidad = line.findtext(".//cbc:InvoicedQuantity", namespaces=ns)
                    detalle = line.findtext(".//cac:Item/cbc:Description", namespaces=ns)
                    precio_unit = line.findtext(".//cac:Price/cbc:PriceAmount", namespaces=ns)
                    valor_linea = line.findtext(".//cbc:LineExtensionAmount", namespaces=ns)

                    tax_subtotals = line.findall(".//cac:TaxSubtotal", namespaces=ns)
                    if tax_subtotals:
                        for tax in tax_subtotals:
                            impuesto_nombre = tax.findtext(".//cac:TaxCategory/cac:TaxScheme/cbc:Name", namespaces=ns)
                            impuesto_pct = tax.findtext(".//cac:TaxCategory/cbc:Percent", namespaces=ns)
                            impuesto_valor = tax.findtext(".//cbc:TaxAmount", namespaces=ns)

                            registros.append([
                                fecha, tipo_doc, numero_doc, moneda,
                                detalle, cantidad, precio_unit, valor_linea,
                                nit_prov, nombre_prov, direccion_prov, email_prov,
                                nit_cli, nombre_cli, direccion_cli, email_cli,
                                subtotal, total_sin, total_con, total_pagar,
                                impuesto_nombre, impuesto_pct, impuesto_valor,
                                forma_pago
                            ])
                    else:
                        registros.append([
                            fecha, tipo_doc, numero_doc, moneda,
                            detalle, cantidad, precio_unit, valor_linea,
                            nit_prov, nombre_prov, direccion_prov, email_prov,
                            nit_cli, nombre_cli, direccion_cli, email_cli,
                            subtotal, total_sin, total_con, total_pagar,
                            "", "", "",
                            forma_pago
                        ])

            except Exception as e:
                print(f"Error procesando {archivo}: {e}")

    # Crear DataFrame
    columnas = [
        "FECHA", "TIPO DOCUMENTO", "NUMERO DOCUMENTO", "MONEDA",
        "DETALLE", "CANTIDAD", "PRECIO UNITARIO", "VALOR LINEA",
        "NIT PROVEEDOR", "NOMBRE PROVEEDOR", "DIRECCION PROVEEDOR", "EMAIL PROVEEDOR",
        "NIT CLIENTE", "NOMBRE CLIENTE", "DIRECCION CLIENTE", "EMAIL CLIENTE",
        "SUBTOTAL", "TOTAL SIN IMPUESTOS", "TOTAL CON IMPUESTOS", "TOTAL A PAGAR",
        "IMPUESTO NOMBRE", "PORCENTAJE IMPUESTO", "IMPUESTO VALOR",
        "FORMA DE PAGO"
    ]
    return pd.DataFrame(registros, columns=columnas)



