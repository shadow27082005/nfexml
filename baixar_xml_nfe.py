import os
import base64
import getpass
from lxml import etree
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, NoEncryption, PrivateFormat
from cryptography.hazmat.backends import default_backend

# ============ CONFIGURAÇÕES ============

CERT_PATH = 'certificado.pfx'
CHAVES_FILE = 'chaves.txt'
OUTPUT_DIR = 'xmls'
WSDL_URL = 'https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx?WSDL'
SERVICE_URL = 'https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx'

# ============ FUNÇÕES ============

def carregar_certificado_pfx(pfx_path, senha):
    with open(pfx_path, 'rb') as f:
        pfx_data = f.read()

    private_key, cert, _ = pkcs12.load_key_and_certificates(
        pfx_data,
        password=senha.encode(),
        backend=default_backend()
    )

    cert_file = 'temp_cert.pem'
    key_file = 'temp_key.pem'

    with open(cert_file, 'wb') as f:
        f.write(cert.public_bytes(Encoding.PEM))

    with open(key_file, 'wb') as f:
        f.write(private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            NoEncryption()
        ))

    return cert_file, key_file


def montar_requisicao_xml(chave_nfe, cnpj):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
  <tpAmb>1</tpAmb>
  <cUFAutor>35</cUFAutor>
  <CNPJ>{cnpj}</CNPJ>
  <consChNFe>
    <chNFe>{chave_nfe}</chNFe>
  </consChNFe>
</distDFeInt>"""


def baixar_xmls():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    senha = getpass.getpass("Digite a senha do certificado: ")
    cnpj = input("Digite o CNPJ do destinatário (somente números): ")

    cert_file, key_file = carregar_certificado_pfx(CERT_PATH, senha)

    session = Session()
    session.cert = (cert_file, key_file)
    transport = Transport(session=session)
    settings = Settings(strict=False, xml_huge_tree=True)

    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)
    service = client.create_service(
        '{http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe}NFeDistribuicaoDFeSoap',
        SERVICE_URL
    )

    with open(CHAVES_FILE, 'r') as f:
        chaves = [linha.strip() for linha in f if linha.strip()]

    for chave in chaves:
        print(f"🔍 Consultando chave: {chave}")
        xml_requisicao = montar_requisicao_xml(chave, cnpj)
        envelope = etree.fromstring(xml_requisicao.encode('utf-8'))

        try:
            resposta = service.nfeDistDFeInteresse(nfeDadosMsg={'_value_1': envelope})

            if hasattr(resposta, 'loteDistDFeInt') and resposta.loteDistDFeInt is not None:
                for docZip in resposta.loteDistDFeInt.docZip:
                    nome = docZip.attrib.get('NSU') or chave
                    conteudo = base64.b64decode(docZip._value_1)
                    with open(f"{OUTPUT_DIR}/{nome}.xml", "wb") as f:
                        f.write(conteudo)
                    print(f"✅ XML salvo: {nome}.xml")
            else:
                print(f"⚠️ Nenhum XML retornado para {chave}")

        except Exception as e:
            print(f"❌ Erro ao consultar {chave}: {str(e)}")

    os.remove(cert_file)
    os.remove(key_file)
    print("✅ Finalizado com sucesso.")

# ============ EXECUÇÃO ============

if __name__ == '__main__':
    baixar_xmls()
