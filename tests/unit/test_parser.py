"""Unit tests for XML parser."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from nfe2pdf.domain.exceptions import InvalidXmlError, NotNFeError
from nfe2pdf.infrastructure.xml.parser import NFexmlParser

# Sample valid NF-e XML (minimal)
SAMPLE_NFE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
  <NFe>
    <infNFe Id="NFe35240112345678000123550010000000011234567890" versao="4.00">
      <ide>
        <cUF>35</cUF>
        <cNF>12345678</cNF>
        <natOp>VENDA</natOp>
        <mod>55</mod>
        <serie>1</serie>
        <nNF>1</nNF>
        <dhEmi>2024-01-15T10:00:00-03:00</dhEmi>
        <tpNF>1</tpNF>
        <idDest>1</idDest>
        <cMunFG>3550308</cMunFG>
        <tpImp>1</tpImp>
        <tpEmis>1</tpEmis>
        <cDV>0</cDV>
        <tpAmb>2</tpAmb>
        <finNFe>1</finNFe>
        <indFinal>1</indFinal>
        <indPres>1</indPres>
        <procEmi>0</procEmi>
        <verProc>1.0</verProc>
      </ide>
      <emit>
        <CNPJ>12345678000123</CNPJ>
        <xNome>EMPRESA EXEMPLO LTDA</xNome>
        <xFant>EMPRESA EXEMPLO</xFant>
        <enderEmit>
          <xLgr>RUA EXEMPLO</xLgr>
          <nro>100</nro>
          <xBairro>CENTRO</xBairro>
          <cMun>3550308</cMun>
          <xMun>SAO PAULO</xMun>
          <UF>SP</UF>
          <CEP>01000000</CEP>
          <cPais>1058</cPais>
          <xPais>BRASIL</xPais>
        </enderEmit>
        <IE>123456789012</IE>
        <CRT>3</CRT>
      </emit>
      <dest>
        <CNPJ>98765432000198</CNPJ>
        <xNome>CLIENTE EXEMPLO LTDA</xNome>
        <enderDest>
          <xLgr>AV TESTE</xLgr>
          <nro>200</nro>
          <xBairro>JARDINS</xBairro>
          <cMun>3550308</cMun>
          <xMun>SAO PAULO</xMun>
          <UF>SP</UF>
          <CEP>01400000</CEP>
          <cPais>1058</cPais>
          <xPais>BRASIL</xPais>
        </enderDest>
        <indIEDest>1</indIEDest>
        <IE>987654321098</IE>
      </dest>
      <det nItem="1">
        <prod>
          <cProd>001</cProd>
          <xProd>PRODUTO EXEMPLO</xProd>
          <NCM>12345678</NCM>
          <CFOP>5102</CFOP>
          <uCom>UN</uCom>
          <qCom>1.0000</qCom>
          <vUnCom>100.00</vUnCom>
          <vProd>100.00</vProd>
          <uTrib>UN</uTrib>
          <qTrib>1.0000</qTrib>
          <vUnTrib>100.00</vUnTrib>
          <indTot>1</indTot>
        </prod>
        <imposto>
          <vTotTrib>25.00</vTotTrib>
          <ICMS>
            <ICMS00>
              <orig>0</orig>
              <CST>00</CST>
              <modBC>3</modBC>
              <vBC>100.00</vBC>
              <pICMS>18.00</pICMS>
              <vICMS>18.00</vICMS>
            </ICMS00>
          </ICMS>
          <IPI>
            <cEnq>999</cEnq>
            <IPINT>
              <CST>53</CST>
            </IPINT>
          </IPI>
          <PIS>
            <PISAliq>
              <CST>01</CST>
              <vBC>100.00</vBC>
              <pPIS>1.65</pPIS>
              <vPIS>1.65</vPIS>
            </PISAliq>
          </PIS>
          <COFINS>
            <COFINSAliq>
              <CST>01</CST>
              <vBC>100.00</vBC>
              <pCOFINS>7.60</pCOFINS>
              <vCOFINS>7.60</vCOFINS>
            </COFINSAliq>
          </COFINS>
        </imposto>
      </det>
      <total>
        <ICMSTot>
          <vBC>100.00</vBC>
          <vICMS>18.00</vICMS>
          <vICMSDeson>0.00</vICMSDeson>
          <vFCPUFDest>0.00</vFCPUFDest>
          <vICMSUFDest>0.00</vICMSUFDest>
          <vICMSUFRemet>0.00</vICMSUFRemet>
          <vFCP>0.00</vFCP>
          <vBCST>0.00</vBCST>
          <vST>0.00</vST>
          <vProd>100.00</vProd>
          <vFrete>0.00</vFrete>
          <vSeg>0.00</vSeg>
          <vDesc>0.00</vDesc>
          <vII>0.00</vII>
          <vIPI>0.00</vIPI>
          <vIPIDevol>0.00</vIPIDevol>
          <vPIS>1.65</vPIS>
          <vCOFINS>7.60</vCOFINS>
          <vOutro>0.00</vOutro>
          <vNF>100.00</vNF>
          <vTotTrib>25.00</vTotTrib>
        </ICMSTot>
      </total>
      <transp>
        <modFrete>0</modFrete>
      </transp>
      <pag>
        <detPag>
          <tPag>01</tPag>
          <vPag>100.00</vPag>
        </detPag>
      </pag>
    </infNFe>
  </NFe>
  <protNFe versao="4.00">
    <infProt>
      <tpAmb>2</tpAmb>
      <verAplic>1.0</verAplic>
      <chNFe>35240112345678000123550010000000011234567890</chNFe>
      <dhRecbto>2024-01-15T10:00:00-03:00</dhRecbto>
      <nProt>123456789012345</nProt>
      <digVal>abcdef1234567890abcdef1234567890</digVal>
      <cStat>100</cStat>
      <xMotivo>Autorizado o uso da NF-e</xMotivo>
    </infProt>
  </protNFe>
</nfeProc>"""


class TestNFexmlParser:
    """Test NFexmlParser."""

    def setup_method(self):
        self.parser = NFexmlParser()

    def test_parse_valid_xml(self):
        """Test parsing valid NF-e XML."""
        nfe_data = self.parser.parse(SAMPLE_NFE_XML)

        # Check header
        assert nfe_data.id == "35240112345678000123550010000000011234567890"
        assert nfe_data.version == "4.00"
        assert nfe_data.header.nf_number == 1
        assert nfe_data.header.series == 1
        assert nfe_data.header.state_code == 35

        # Check emitter
        assert nfe_data.emitter.cnpj == "12345678000123"
        assert nfe_data.emitter.company_name == "EMPRESA EXEMPLO LTDA"
        assert nfe_data.emitter.trade_name == "EMPRESA EXEMPLO"
        assert nfe_data.emitter.state_registration == "123456789012"
        assert nfe_data.emitter.crt == 3
        assert nfe_data.emitter.address.city_name == "SAO PAULO"
        assert nfe_data.emitter.address.state == "SP"

        # Check recipient
        assert nfe_data.recipient.cnpj == "98765432000198"
        assert nfe_data.recipient.name == "CLIENTE EXEMPLO LTDA"
        assert nfe_data.recipient.state_registration == "987654321098"

        # Check details
        assert len(nfe_data.details) == 1
        detail = nfe_data.details[0]
        assert detail.item_number == 1
        assert detail.product.product_code == "001"
        assert detail.product.description == "PRODUTO EXEMPLO"
        assert detail.product.ncm == "12345678"
        assert detail.product.cfop == "5102"
        assert detail.product.quantity_commercial == Decimal("1.0000")
        assert detail.product.product_value == Decimal("100.00")

        # Check taxes
        assert detail.taxes is not None
        assert detail.taxes.icms is not None
        assert detail.taxes.icms.cst == "00"
        assert detail.taxes.icms.v_icms == Decimal("18.00")
        assert detail.taxes.ipi is not None
        assert detail.taxes.ipi.cst == "53"
        assert detail.taxes.pis is not None
        assert detail.taxes.pis.v_pis == Decimal("1.65")
        assert detail.taxes.cofins is not None
        assert detail.taxes.cofins.v_cofins == Decimal("7.60")

        # Check totals
        assert nfe_data.totals.v_prod == Decimal("100.00")
        assert nfe_data.totals.v_nf == Decimal("100.00")
        assert nfe_data.totals.v_icms == Decimal("18.00")

        # Check transport
        assert nfe_data.transport is not None
        assert nfe_data.transport.freight_modality == 0

        # Check payment
        assert nfe_data.payment is not None
        assert len(nfe_data.payment) == 1
        assert nfe_data.payment[0].payment_type == 1
        assert nfe_data.payment[0].value == Decimal("100.00")

        # Check protocol info
        assert nfe_data.access_key == "35240112345678000123550010000000011234567890"
        assert nfe_data.protocol_number == "123456789012345"
        assert nfe_data.status_code == 100
        assert nfe_data.status_message == "Autorizado o uso da NF-e"

    def test_parse_invalid_xml(self):
        """Test parsing malformed XML raises InvalidXmlError."""
        # Truly malformed XML (unclosed tag)
        invalid_xml = b"<xml>malformed</xml"
        with pytest.raises(InvalidXmlError):
            self.parser.parse(invalid_xml)

    def test_parse_not_nfe(self):
        """Test parsing non-NF-e XML raises NotNFeError."""
        not_nfe = b"""<?xml version="1.0"?>
<root xmlns="http://example.com">
  <item>test</item>
</root>"""
        with pytest.raises(NotNFeError):
            self.parser.parse(not_nfe)

    def test_parse_file(self, tmp_path: Path):
        """Test parsing from file."""
        xml_file = tmp_path / "test_nfe.xml"
        xml_file.write_bytes(SAMPLE_NFE_XML)

        nfe_data = self.parser.parse_file(xml_file)
        assert nfe_data.emitter.company_name == "EMPRESA EXEMPLO LTDA"

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(InvalidXmlError):
            self.parser.parse_file(Path("/nonexistent/file.xml"))

    def test_formatted_access_key(self):
        """Test formatted access key property."""
        nfe_data = self.parser.parse(SAMPLE_NFE_XML)
        expected = "3524 0112 3456 7800 0123 5500 1000 0000 0112 3456 7890"
        assert nfe_data.formatted_access_key == expected

    def test_is_cancelled_false(self):
        """Test is_cancelled for authorized NF-e."""
        nfe_data = self.parser.parse(SAMPLE_NFE_XML)
        assert nfe_data.is_cancelled is False


class TestNFexmlParserCancelled:
    """Test parsing cancelled NF-e."""

    def setup_method(self):
        self.parser = NFexmlParser()

    def test_parse_cancelled_nfe(self):
        """Test parsing cancelled NF-e (cStat=101)."""
        cancelled_xml = SAMPLE_NFE_XML.replace(
            b"<cStat>100</cStat>", b"<cStat>101</cStat>"
        ).replace(
            b"<xMotivo>Autorizado o uso da NF-e</xMotivo>",
            b"<xMotivo>Cancelamento de NF-e homologado</xMotivo>",
        )
        nfe_data = self.parser.parse(cancelled_xml)
        assert nfe_data.status_code == 101
        assert nfe_data.is_cancelled is True


class TestNFexmlParserDirectNFe:
    """Test parsing NFe without nfeProc wrapper."""

    def setup_method(self):
        self.parser = NFexmlParser()

    def test_parse_direct_nfe(self):
        """Test parsing NFe element directly (without nfeProc)."""
        direct_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
  <infNFe Id="NFe35240112345678000123550010000000011234567890" versao="4.00">
    <ide>
      <cUF>35</cUF>
      <cNF>12345678</cNF>
      <natOp>VENDA</natOp>
      <mod>55</mod>
      <serie>1</serie>
      <nNF>1</nNF>
      <dhEmi>2024-01-15T10:00:00-03:00</dhEmi>
      <tpNF>1</tpNF>
      <idDest>1</idDest>
      <cMunFG>3550308</cMunFG>
      <tpImp>1</tpImp>
      <tpEmis>1</tpEmis>
      <cDV>0</cDV>
      <tpAmb>2</tpAmb>
      <finNFe>1</finNFe>
      <indFinal>1</indFinal>
      <indPres>1</indPres>
      <procEmi>0</procEmi>
      <verProc>1.0</verProc>
    </ide>
    <emit>
      <CNPJ>12345678000123</CNPJ>
      <xNome>EMPRESA EXEMPLO LTDA</xNome>
      <enderEmit>
        <xLgr>RUA EXEMPLO</xLgr>
        <nro>100</nro>
        <xBairro>CENTRO</xBairro>
        <cMun>3550308</cMun>
        <xMun>SAO PAULO</xMun>
        <UF>SP</UF>
        <CEP>01000000</CEP>
        <cPais>1058</cPais>
        <xPais>BRASIL</xPais>
      </enderEmit>
      <IE>123456789012</IE>
      <CRT>3</CRT>
    </emit>
    <dest>
      <CNPJ>98765432000198</CNPJ>
      <xNome>CLIENTE EXEMPLO LTDA</xNome>
      <enderDest>
        <xLgr>AV TESTE</xLgr>
        <nro>200</nro>
        <xBairro>JARDINS</xBairro>
        <cMun>3550308</cMun>
        <xMun>SAO PAULO</xMun>
        <UF>SP</UF>
        <CEP>01400000</CEP>
        <cPais>1058</cPais>
        <xPais>BRASIL</xPais>
      </enderDest>
      <indIEDest>1</indIEDest>
      <IE>987654321098</IE>
    </dest>
    <det nItem="1">
      <prod>
        <cProd>001</cProd>
        <xProd>PRODUTO EXEMPLO</xProd>
        <NCM>12345678</NCM>
        <CFOP>5102</CFOP>
        <uCom>UN</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <uTrib>UN</uTrib>
        <qTrib>1.0000</qTrib>
        <vUnTrib>100.00</vUnTrib>
        <indTot>1</indTot>
      </prod>
      <imposto>
        <vTotTrib>25.00</vTotTrib>
        <ICMS>
          <ICMS00>
            <orig>0</orig>
            <CST>00</CST>
            <modBC>3</modBC>
            <vBC>100.00</vBC>
            <pICMS>18.00</pICMS>
            <vICMS>18.00</vICMS>
          </ICMS00>
        </ICMS>
      </imposto>
    </det>
    <total>
      <ICMSTot>
        <vBC>100.00</vBC>
        <vICMS>18.00</vICMS>
        <vICMSDeson>0.00</vICMSDeson>
        <vFCPUFDest>0.00</vFCPUFDest>
        <vICMSUFDest>0.00</vICMSUFDest>
        <vICMSUFRemet>0.00</vICMSUFRemet>
        <vFCP>0.00</vFCP>
        <vBCST>0.00</vBCST>
        <vST>0.00</vST>
        <vProd>100.00</vProd>
        <vFrete>0.00</vFrete>
        <vSeg>0.00</vSeg>
        <vDesc>0.00</vDesc>
        <vII>0.00</vII>
        <vIPI>0.00</vIPI>
        <vIPIDevol>0.00</vIPIDevol>
        <vPIS>1.65</vPIS>
        <vCOFINS>7.60</vCOFINS>
        <vOutro>0.00</vOutro>
        <vNF>100.00</vNF>
        <vTotTrib>25.00</vTotTrib>
      </ICMSTot>
    </total>
    <transp>
      <modFrete>0</modFrete>
    </transp>
    <pag>
      <detPag>
        <tPag>01</tPag>
        <vPag>100.00</vPag>
      </detPag>
    </pag>
  </infNFe>
</NFe>"""
        nfe_data = self.parser.parse(direct_xml)
        assert nfe_data.emitter.company_name == "EMPRESA EXEMPLO LTDA"
        assert nfe_data.protocol_number is None  # No protNFe
        assert nfe_data.status_code is None