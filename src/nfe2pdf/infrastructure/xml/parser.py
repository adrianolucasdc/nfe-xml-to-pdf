"""XML Parser implementation for NF-e using lxml with namespace support."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from lxml import etree

from nfe2pdf.domain.models import (
    NFeData,
    Header,
    Emitter,
    Recipient,
    Detail,
    Product,
    Taxes,
    Totals,
    Transport,
    Payment,
    Address,
    ICMS,
    IPI,
    PIS,
    COFINS,
    AdditionalInfo,
    NFVersion,
    NFType,
    NFEnvironment,
    NFProcessType,
    NFEmissionType,
    NFIndicatorFinal,
    NFIndicatorPresence,
)
from nfe2pdf.domain.exceptions import (
    InvalidXmlError,
    NotNFeError,
    InvalidNFeVersionError,
    MissingRequiredFieldError,
)
from nfe2pdf.domain.ports import XMLParser


# NF-e namespace
NFE_NAMESPACE = "http://www.portalfiscal.inf.br/nfe"
NS = {"nfe": NFE_NAMESPACE}


class NFexmlParser:
    """NF-e XML Parser using lxml with proper namespace handling."""

    def __init__(self) -> None:
        # Parser seguro contra XXE e bilhões de expansões de entidade
        self._parser = etree.XMLParser(
            remove_blank_text=True,
            resolve_entities=False,  # Previne XXE
            huge_tree=False,         # Limita tamanho da árvore
        )

    def parse(self, xml_content: bytes) -> NFeData:
        """Parse XML bytes and return structured NFeData."""
        try:
            root = etree.fromstring(xml_content, parser=self._parser)
        except etree.XMLSyntaxError as e:
            raise InvalidXmlError(f"XML malformado: {e}", original_error=e)

        # Valida se é NF-e (namespace correto)
        self._validate_nfe_root(root)

        # Extrai a infNFe (pode estar em nfeProc/NFe/infNFe ou direto em NFe/infNFe)
        inf_nfe = self._find_inf_nfe(root)
        if inf_nfe is None:
            raise MissingRequiredFieldError("Elemento infNFe não encontrado", field_path="infNFe")

        # Valida versão
        version = inf_nfe.get("versao")
        self._validate_version(version)

        # Parse ID
        nfe_id = inf_nfe.get("Id", "").replace("NFe", "")

        # Parse cada seção
        header = self._parse_header(inf_nfe)
        emitter = self._parse_emitter(inf_nfe)
        recipient = self._parse_recipient(inf_nfe)
        details = self._parse_details(inf_nfe)
        totals = self._parse_totals(inf_nfe)
        transport = self._parse_transport(inf_nfe)
        payment = self._parse_payment(inf_nfe)
        additional_info = self._parse_additional_info(inf_nfe)

        # Parse protNFe (autorização) - pode estar em nfeProc/protNFe
        prot_nfe = root.find(".//nfe:protNFe", namespaces=NS)
        access_key = None
        protocol_number = None
        protocol_date = None
        status_code = None
        status_message = None

        if prot_nfe is not None:
            inf_prot = prot_nfe.find("nfe:infProt", namespaces=NS)
            if inf_prot is not None:
                access_key = self._get_text(inf_prot, "nfe:chNFe")
                protocol_number = self._get_text(inf_prot, "nfe:nProt")
                dh_recbto = self._get_text(inf_prot, "nfe:dhRecbto")
                if dh_recbto:
                    protocol_date = self._parse_datetime(dh_recbto)
                c_stat = self._get_text(inf_prot, "nfe:cStat")
                if c_stat:
                    status_code = int(c_stat)
                status_message = self._get_text(inf_prot, "nfe:xMotivo")

        return NFeData(
            Id=f"NFe{nfe_id}",
            versao=NFVersion(version) if version else NFVersion.V400,
            ide=header,
            emit=emitter,
            dest=recipient,
            det=details,
            total=totals,
            transp=transport,
            pag=payment,
            infAdic=additional_info,
            access_key=access_key,
            protocol_number=protocol_number,
            protocol_date=protocol_date,
            status_code=status_code,
            status_message=status_message,
        )

    def parse_file(self, xml_path: Path) -> NFeData:
        """Parse XML file and return structured NFeData."""
        try:
            xml_content = xml_path.read_bytes()
        except OSError as e:
            raise InvalidXmlError(f"Erro ao ler arquivo {xml_path}: {e}", original_error=e)
        return self.parse(xml_content)

    def _validate_nfe_root(self, root: etree._Element) -> None:
        """Valida se o XML é NF-e (namespace correto)."""
        # Verifica namespace do root
        if NFE_NAMESPACE not in (root.nsmap.values() if root.nsmap else []):
            # Tenta encontrar namespace no tag
            tag = root.tag
            if not (tag.startswith("{http://www.portalfiscal.inf.br/nfe}") or
                    tag in ("nfeProc", "NFe", "protNFe")):
                raise NotNFeError(
                    "XML não é uma NF-e (namespace incorreto)",
                    root_tag=tag,
                    namespace=root.nsmap.get("nfe") if root.nsmap else None,
                )

    def _find_inf_nfe(self, root: etree._Element) -> Optional[etree._Element]:
        """Encontra o elemento infNFe independentemente da estrutura (nfeProc ou NFe direto)."""
        # Tenta nfeProc/NFe/infNFe
        inf_nfe = root.find(".//nfe:NFe/nfe:infNFe", namespaces=NS)
        if inf_nfe is not None:
            return inf_nfe
        # Tenta NFe/infNFe (root direto)
        inf_nfe = root.find(".//nfe:infNFe", namespaces=NS)
        return inf_nfe

    def _validate_version(self, version: Optional[str]) -> None:
        """Valida se a versão é suportada."""
        if version != "4.00":
            raise InvalidNFeVersionError(
                f"Versão NF-e não suportada: {version}. Apenas 4.00 é suportada.",
                found_version=version,
            )

    def _get_text(self, parent: etree._Element, xpath: str, default: str = "") -> str:
        """Extrai texto de um elemento via XPath com namespace."""
        elem = parent.find(xpath, namespaces=NS)
        if elem is not None and elem.text:
            return elem.text.strip()
        return default

    def _get_decimal(self, parent: etree._Element, xpath: str) -> Optional[float]:
        """Extrai valor decimal via XPath."""
        text = self._get_text(parent, xpath)
        if text:
            try:
                return float(text)
            except ValueError:
                return None
        return None

    def _parse_datetime(self, text: str) -> Optional[datetime]:
        """Parse datetime ISO 8601 com timezone."""
        try:
            # lxml retorna string, precisamos parsear
            # Formato: 2024-01-15T10:00:00-03:00
            from datetime import datetime
            return datetime.fromisoformat(text)
        except (ValueError, AttributeError):
            return None

    def _parse_header(self, inf_nfe: etree._Element) -> Header:
        """Parse ide (header)."""
        ide = inf_nfe.find("nfe:ide", namespaces=NS)
        if ide is None:
            raise MissingRequiredFieldError("Elemento ide não encontrado", field_path="ide")

        return Header(
            cUF=int(self._get_text(ide, "nfe:cUF")),
            nNF=int(self._get_text(ide, "nfe:nNF")),
            serie=int(self._get_text(ide, "nfe:serie")),
            natOp=self._get_text(ide, "nfe:natOp"),
            mod=int(self._get_text(ide, "nfe:mod")),
            dhEmi=self._parse_datetime(self._get_text(ide, "nfe:dhEmi")) or datetime.now(),
            tpNF=NFType(int(self._get_text(ide, "nfe:tpNF"))),
            idDest=int(self._get_text(ide, "nfe:idDest")),
            cMunFG=int(self._get_text(ide, "nfe:cMunFG")),
            tpImp=int(self._get_text(ide, "nfe:tpImp")),
            tpEmis=NFEmissionType(int(self._get_text(ide, "nfe:tpEmis"))),
            cDV=int(self._get_text(ide, "nfe:cDV")),
            tpAmb=NFEnvironment(int(self._get_text(ide, "nfe:tpAmb"))),
            finNFe=int(self._get_text(ide, "nfe:finNFe")),
            indFinal=NFIndicatorFinal(int(self._get_text(ide, "nfe:indFinal"))),
            indPres=NFIndicatorPresence(int(self._get_text(ide, "nfe:indPres"))),
            procEmi=NFProcessType(int(self._get_text(ide, "nfe:procEmi"))),
            verProc=self._get_text(ide, "nfe:verProc"),
        )

    def _parse_emitter(self, inf_nfe: etree._Element) -> Emitter:
        """Parse emit (emitente)."""
        emit = inf_nfe.find("nfe:emit", namespaces=NS)
        if emit is None:
            raise MissingRequiredFieldError("Elemento emit não encontrado", field_path="emit")

        ender_emit = emit.find("nfe:enderEmit", namespaces=NS)
        address = self._parse_address(ender_emit) if ender_emit is not None else Address(
            street="", number="", neighborhood="", city_code="", city_name="",
            state="", zip_code="", country_code="1058", country_name="BRASIL"
        )

        return Emitter(
            CNPJ=self._get_text(emit, "nfe:CNPJ") or None,
            CPF=self._get_text(emit, "nfe:CPF") or None,
            xNome=self._get_text(emit, "nfe:xNome"),
            xFant=self._get_text(emit, "nfe:xFant") or None,
            enderEmit=address,
            IE=self._get_text(emit, "nfe:IE") or None,
            IM=self._get_text(emit, "nfe:IM") or None,
            CRT=int(self._get_text(emit, "nfe:CRT", "3")),
        )

    def _parse_recipient(self, inf_nfe: etree._Element) -> Recipient:
        """Parse dest (destinatário)."""
        dest = inf_nfe.find("nfe:dest", namespaces=NS)
        if dest is None:
            raise MissingRequiredFieldError("Elemento dest não encontrado", field_path="dest")

        ender_dest = dest.find("nfe:enderDest", namespaces=NS)
        address = self._parse_address(ender_dest) if ender_dest is not None else None

        return Recipient(
            CNPJ=self._get_text(dest, "nfe:CNPJ") or None,
            CPF=self._get_text(dest, "nfe:CPF") or None,
            idEstrangeiro=self._get_text(dest, "nfe:idEstrangeiro") or None,
            xNome=self._get_text(dest, "nfe:xNome"),
            enderDest=address,
            indIEDest=int(self._get_text(dest, "nfe:indIEDest", "9")),
            IE=self._get_text(dest, "nfe:IE") or None,
            email=self._get_text(dest, "nfe:email") or None,
        )

    def _parse_address(self, ender: etree._Element) -> Address:
        """Parse endereço (enderEmit, enderDest, etc.)."""
        return Address(
            xLgr=self._get_text(ender, "nfe:xLgr"),
            nro=self._get_text(ender, "nfe:nro"),
            xCpl=self._get_text(ender, "nfe:xCpl") or None,
            xBairro=self._get_text(ender, "nfe:xBairro"),
            cMun=self._get_text(ender, "nfe:cMun"),
            xMun=self._get_text(ender, "nfe:xMun"),
            UF=self._get_text(ender, "nfe:UF"),
            CEP=self._get_text(ender, "nfe:CEP"),
            cPais=self._get_text(ender, "nfe:cPais", "1058"),
            xPais=self._get_text(ender, "nfe:xPais", "BRASIL"),
            fone=self._get_text(ender, "nfe:fone") or None,
        )

    def _parse_details(self, inf_nfe: etree._Element) -> list[Detail]:
        """Parse det (itens/produtos)."""
        details = []
        for det in inf_nfe.findall("nfe:det", namespaces=NS):
            n_item = int(det.get("nItem", "0"))
            prod = det.find("nfe:prod", namespaces=NS)
            imposto = det.find("nfe:imposto", namespaces=NS)

            if prod is None:
                continue

            product = self._parse_product(prod, n_item)
            taxes = self._parse_taxes(imposto) if imposto is not None else None

            details.append(Detail(nItem=n_item, prod=product, imposto=taxes))

        return details

    def _parse_product(self, prod: etree._Element, n_item: int) -> Product:
        """Parse prod (produto)."""
        return Product(
            nItem=n_item,
            cProd=self._get_text(prod, "nfe:cProd"),
            cEAN=self._get_text(prod, "nfe:cEAN") or None,
            xProd=self._get_text(prod, "nfe:xProd"),
            NCM=self._get_text(prod, "nfe:NCM"),
            CEST=self._get_text(prod, "nfe:CEST") or None,
            CFOP=self._get_text(prod, "nfe:CFOP"),
            uCom=self._get_text(prod, "nfe:uCom"),
            qCom=float(self._get_text(prod, "nfe:qCom", "0")),
            vUnCom=float(self._get_text(prod, "nfe:vUnCom", "0")),
            vProd=float(self._get_text(prod, "nfe:vProd", "0")),
            cEANTrib=self._get_text(prod, "nfe:cEANTrib") or None,
            uTrib=self._get_text(prod, "nfe:uTrib"),
            qTrib=float(self._get_text(prod, "nfe:qTrib", "0")),
            vUnTrib=float(self._get_text(prod, "nfe:vUnTrib", "0")),
            vFrete=self._get_decimal(prod, "nfe:vFrete"),
            vSeg=self._get_decimal(prod, "nfe:vSeg"),
            vDesc=self._get_decimal(prod, "nfe:vDesc"),
            vOutro=self._get_decimal(prod, "nfe:vOutro"),
            indTot=int(self._get_text(prod, "nfe:indTot", "1")),
            infAdProd=self._get_text(prod, "nfe:infAdProd") or None,
        )

    def _parse_taxes(self, imposto: etree._Element) -> Taxes:
        """Parse imposto (impostos do item)."""
        v_tot_trib = self._get_decimal(imposto, "nfe:vTotTrib")

        # ICMS
        icms = None
        icms_elem = imposto.find("nfe:ICMS", namespaces=NS)
        if icms_elem is not None:
            # ICMS pode ter vários tipos (ICMS00, ICMS10, ICMS20, etc.)
            for child in icms_elem:
                if child.tag.endswith("}" + "ICMS00") or "ICMS" in child.tag:
                    icms = ICMS(
                        CST=self._get_text(child, "nfe:CST"),
                        orig=int(self._get_text(child, "nfe:orig", "0")),
                        modBC=self._get_int(child, "nfe:modBC"),
                        vBC=self._get_decimal(child, "nfe:vBC"),
                        pICMS=self._get_decimal(child, "nfe:pICMS"),
                        vICMS=self._get_decimal(child, "nfe:vICMS"),
                        vBCST=self._get_decimal(child, "nfe:vBCST"),
                        pST=self._get_decimal(child, "nfe:pST"),
                        vICMSST=self._get_decimal(child, "nfe:vICMSST"),
                        pFCP=self._get_decimal(child, "nfe:pFCP"),
                        vFCP=self._get_decimal(child, "nfe:vFCP"),
                        vFCPST=self._get_decimal(child, "nfe:vFCPST"),
                        vBCFCPST=self._get_decimal(child, "nfe:vBCFCPST"),
                    )
                    break

        # IPI
        ipi = None
        ipi_elem = imposto.find("nfe:IPI", namespaces=NS)
        if ipi_elem is not None:
            ipi_child = ipi_elem.find("./*", namespaces=NS)  # IPITrib, IPINT, etc.
            if ipi_child is not None:
                ipi = IPI(
                    CST=self._get_text(ipi_child, "nfe:CST"),
                    cEnq=self._get_text(ipi_child, "nfe:cEnq") or None,
                    vBC=self._get_decimal(ipi_child, "nfe:vBC"),
                    pIPI=self._get_decimal(ipi_child, "nfe:pIPI"),
                    vIPI=self._get_decimal(ipi_child, "nfe:vIPI"),
                )

        # PIS
        pis = None
        pis_elem = imposto.find("nfe:PIS", namespaces=NS)
        if pis_elem is not None:
            pis_child = pis_elem.find("./*", namespaces=NS)
            if pis_child is not None:
                pis = PIS(
                    CST=self._get_text(pis_child, "nfe:CST"),
                    vBC=self._get_decimal(pis_child, "nfe:vBC"),
                    pPIS=self._get_decimal(pis_child, "nfe:pPIS"),
                    vPIS=self._get_decimal(pis_child, "nfe:vPIS"),
                    qBCProd=self._get_decimal(pis_child, "nfe:qBCProd"),
                    vAliqProd=self._get_decimal(pis_child, "nfe:vAliqProd"),
                )

        # COFINS
        cofins = None
        cofins_elem = imposto.find("nfe:COFINS", namespaces=NS)
        if cofins_elem is not None:
            cofins_child = cofins_elem.find("./*", namespaces=NS)
            if cofins_child is not None:
                cofins = COFINS(
                    CST=self._get_text(cofins_child, "nfe:CST"),
                    vBC=self._get_decimal(cofins_child, "nfe:vBC"),
                    pCOFINS=self._get_decimal(cofins_child, "nfe:pCOFINS"),
                    vCOFINS=self._get_decimal(cofins_child, "nfe:vCOFINS"),
                    qBCProd=self._get_decimal(cofins_child, "nfe:qBCProd"),
                    vAliqProd=self._get_decimal(cofins_child, "nfe:vAliqProd"),
                )

        return Taxes(
            vTotTrib=v_tot_trib,
            ICMS=icms,
            IPI=ipi,
            PIS=pis,
            COFINS=cofins,
        )

    def _parse_totals(self, inf_nfe: etree._Element) -> Totals:
        """Parse total/ICMSTot."""
        total = inf_nfe.find("nfe:total", namespaces=NS)
        if total is None:
            raise MissingRequiredFieldError("Elemento total não encontrado", field_path="total")

        icms_tot = total.find("nfe:ICMSTot", namespaces=NS)
        if icms_tot is None:
            raise MissingRequiredFieldError("Elemento ICMSTot não encontrado", field_path="total/ICMSTot")

        return Totals(
            vBC=self._get_decimal(icms_tot, "nfe:vBC", 0.0),
            vICMS=self._get_decimal(icms_tot, "nfe:vICMS", 0.0),
            vICMSDeson=self._get_decimal(icms_tot, "nfe:vICMSDeson"),
            vFCPUFDest=self._get_decimal(icms_tot, "nfe:vFCPUFDest"),
            vICMSUFDest=self._get_decimal(icms_tot, "nfe:vICMSUFDest"),
            vICMSUFRemet=self._get_decimal(icms_tot, "nfe:vICMSUFRemet"),
            vFCP=self._get_decimal(icms_tot, "nfe:vFCP"),
            vBCST=self._get_decimal(icms_tot, "nfe:vBCST"),
            vST=self._get_decimal(icms_tot, "nfe:vST"),
            vProd=self._get_decimal(icms_tot, "nfe:vProd", 0.0),
            vFrete=self._get_decimal(icms_tot, "nfe:vFrete"),
            vSeg=self._get_decimal(icms_tot, "nfe:vSeg"),
            vDesc=self._get_decimal(icms_tot, "nfe:vDesc"),
            vII=self._get_decimal(icms_tot, "nfe:vII"),
            vIPI=self._get_decimal(icms_tot, "nfe:vIPI"),
            vIPIDevol=self._get_decimal(icms_tot, "nfe:vIPIDevol"),
            vPIS=self._get_decimal(icms_tot, "nfe:vPIS"),
            vCOFINS=self._get_decimal(icms_tot, "nfe:vCOFINS"),
            vOutro=self._get_decimal(icms_tot, "nfe:vOutro"),
            vNF=self._get_decimal(icms_tot, "nfe:vNF", 0.0),
            vTotTrib=self._get_decimal(icms_tot, "nfe:vTotTrib"),
        )

    def _parse_transport(self, inf_nfe: etree._Element) -> Optional[Transport]:
        """Parse transp (transporte)."""
        transp = inf_nfe.find("nfe:transp", namespaces=NS)
        if transp is None:
            return None

        mod_frete = self._get_text(transp, "nfe:modFrete", "0")

        return Transport(
            modFrete=int(mod_frete),
            transporta=None,  # Simplificado
            vol=None,
        )

    def _parse_payment(self, inf_nfe: etree._Element) -> Optional[list[Payment]]:
        """Parse pag (pagamento)."""
        pag = inf_nfe.find("nfe:pag", namespaces=NS)
        if pag is None:
            return None

        payments = []
        for det_pag in pag.findall("nfe:detPag", namespaces=NS):
            payments.append(Payment(
                tPag=int(self._get_text(det_pag, "nfe:tPag", "90")),
                vPag=self._get_decimal(det_pag, "nfe:vPag", 0.0),
                card=None,
            ))
        return payments if payments else None

    def _parse_additional_info(self, inf_nfe: etree._Element) -> Optional[AdditionalInfo]:
        """Parse infAdic (informações adicionais)."""
        inf_adic = inf_nfe.find("nfe:infAdic", namespaces=NS)
        if inf_adic is None:
            return None

        return AdditionalInfo(
            infCpl=self._get_text(inf_adic, "nfe:infCpl") or None,
            infAdFisco=self._get_text(inf_adic, "nfe:infAdFisco") or None,
        )

    def _get_int(self, parent: etree._Element, xpath: str) -> Optional[int]:
        """Extrai inteiro via XPath."""
        text = self._get_text(parent, xpath)
        if text:
            try:
                return int(text)
            except ValueError:
                return None
        return None

    def _get_decimal(self, parent: etree._Element, xpath: str, default: float = 0.0) -> float:
        """Extrai decimal via XPath com default."""
        text = self._get_text(parent, xpath)
        if text:
            try:
                return float(text)
            except ValueError:
                return default
        return default