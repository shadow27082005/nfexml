import os
import tempfile
import requests
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption

# Caminho absoluto do seu PFX
CAMINHO_CERTIFICADO = r"C:\Users\mateu\script\certificado.pfx"
# URL de produção do serviço NFeConsulta2
URL_CONSULTA = "https://nfe.fazenda.gov.br/NFeConsulta2/NFeConsulta2.asmx"

def extrair_certificado_pem(pfx_path: str, senha: str):
    """
    Extrai de um .pfx a chave privada e o(s) certificado(s) em PEM,
    grava em arquivos temporários e retorna (cert_file, key_file).
    """
    with open(pfx_path, 'rb') as f:
        pfx_data = f.read()
    # Carrega PKCS#12
    priv_key, cert, add_certs = pkcs12.load_key_and_certificates(pfx_data, senha.encode())
    # Serializa em PEM
    key_pem = priv_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption()
    )
    cert_pem = cert.public_bytes(Encoding.PEM)
    if add_certs:
        for c in add_certs:
            cert_pem += c.public_bytes(Encoding.PEM)
    # Grava em /tmp (ou %TEMP% no Windows)
    tmp = tempfile.gettempdir()
    key_file = os.path.join(tmp, "nfe_key.pem")
    cert_file = os.path.join(tmp, "nfe_cert.pem")
    with open(key_file, "wb") as f:
        f.write(key_pem)
    with open(cert_file, "wb") as f:
        f.write(cert_pem)
    return cert_file, key_file

def consultar_xml_nfe(chave: str, senha: str):
    """
    Consulta a NFe pela chave e salva o XML em <chave>.xml
    """
    cert_file, key_file = extrair_certificado_pem(CAMINHO_CERTIFICADO, senha)

    # Prepara sessão HTTPS mútua TLS
    session = requests.Session()
    session.cert = (cert_file, key_file)
    session.verify = True  # usa CA do certifi

    # Cabeçalhos SOAP 1.1
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsulta2/nfeConsultaNF2"
    }

    # Envelope SOAP 1.1
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsulta2">
  <soap:Header/>
  <soap:Body>
    <nfe:nfeConsultaNF2>
      <consSitNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
        <tpAmb>1</tpAmb>
        <xServ>CONSULTAR</xServ>
        <chNFe>{chave}</chNFe>
      </consSitNFe>
    </nfe:nfeConsultaNF2>
  </soap:Body>
</soap:Envelope>"""

    print(f"📡 Enviando consulta para a chave {chave}…")
    resp = session.post(URL_CONSULTA, data=envelope.encode("utf-8"), headers=headers, timeout=60)
    resp.raise_for_status()

    xml_out = f"{chave}.xml"
    with open(xml_out, "wb") as f:
        f.write(resp.content)
    print(f"✅ XML salvo em: {xml_out}")

def main():
    senha = input("🔐 Digite a senha do certificado .pfx: ").strip()
    chave = input("🔑 Digite a chave da NFe (44 dígitos): ").strip()
    if len(chave) != 44 or not chave.isdigit():
        print("❌ Chave inválida. Deve ter 44 dígitos numéricos.")
        return
    consultar_xml_nfe(chave, senha)

if __name__ == "__main__":
    main()
