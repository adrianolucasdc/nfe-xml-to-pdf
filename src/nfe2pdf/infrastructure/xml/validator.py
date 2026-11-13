"""XML Validator for NF-e - basic structural validation before parsing."""
from __future__ import annotations

from pathlib import Path
from lxml import etree


NFE_NAMESPACE = "http://www.portalfiscal.inf.br/nfe"


class NFexmlValidator:
    """Quick structural validator for NF-e XML files.

    Performs lightweight checks before full parsing:
    - Well-formed XML
    - Correct namespace
    - Version 4.00
    - Required elements present
    """

    def __init__(self) -> None:
        self._parser = etree.XMLParser(
            remove_blank_text=True,
            resolve_entities=False,
            huge_tree=False,
        )

    def validate(self, xml_content: bytes) -> tuple[bool, str | None]:
        """Validate XML structure.

        Returns:
            tuple: (is_valid, error_message). error_message is None if valid.
        """
        try:
            root = etree.fromstring(xml_content, parser=self._parser)
        except etree.XMLSyntaxError as e:
            return False, f"XML malformado: {e}"

        # Check namespace
        if not self._has_nfe_namespace(root):
            tag = root.tag
            return False, f"Namespace NF-e não encontrado. Root tag: {tag}"

        # Find infNFe
        inf_nfe = root.find(".//{http://www.portalfiscal.inf.br/nfe}infNFe")
        if inf_nfe is None:
            return False, "Elemento infNFe não encontrado"

        # Check version
        version = inf_nfe.get("versao")
        if version != "4.00":
            return False, f"Versão NF-e não suportada: {version}. Apenas 4.00 é suportada."

        # Check required elements
        required = ["ide", "emit", "dest", "det", "total"]
        for elem_name in required:
            if inf_nfe.find(f"{{{NFE_NAMESPACE}}}{elem_name}") is None:
                return False, f"Elemento obrigatório ausente: {elem_name}"

        return True, None

    def validate_file(self, xml_path: Path) -> tuple[bool, str | None]:
        """Validate XML file."""
        try:
            xml_content = xml_path.read_bytes()
        except OSError as e:
            return False, f"Erro ao ler arquivo: {e}"
        return self.validate(xml_content)

    def _has_nfe_namespace(self, root: etree._Element) -> bool:
        """Check if root or descendants have NF-e namespace."""
        # Check root namespace
        if root.nsmap:
            for ns in root.nsmap.values():
                if ns == NFE_NAMESPACE:
                    return True
        # Check tag
        if root.tag.startswith(f"{{{NFE_NAMESPACE}}}"):
            return True
        # Check descendants (quick check)
        for elem in root.iter():
            if elem.tag.startswith(f"{{{NFE_NAMESPACE}}}"):
                return True
        return False

    def get_version(self, xml_content: bytes) -> str | None:
        """Extract NF-e version without full parsing."""
        try:
            root = etree.fromstring(xml_content, parser=self._parser)
            inf_nfe = root.find(".//{http://www.portalfiscal.inf.br/nfe}infNFe")
            if inf_nfe is not None:
                return inf_nfe.get("versao")
        except etree.XMLSyntaxError:
            pass
        return None

    def is_nfe(self, xml_content: bytes) -> bool:
        """Quick check if XML is NF-e."""
        try:
            root = etree.fromstring(xml_content, parser=self._parser)
            return self._has_nfe_namespace(root)
        except etree.XMLSyntaxError:
            return False

    def is_cancelled(self, xml_content: bytes) -> bool:
        """Check if NF-e is cancelled (cStat=101 in protNFe)."""
        try:
            root = etree.fromstring(xml_content, parser=self._parser)
            prot_nfe = root.find(".//{http://www.portalfiscal.inf.br/nfe}protNFe")
            if prot_nfe is not None:
                inf_prot = prot_nfe.find("{http://www.portalfiscal.inf.br/nfe}infProt")
                if inf_prot is not None:
                    c_stat = inf_prot.find("{http://www.portalfiscal.inf.br/nfe}cStat")
                    if c_stat is not None and c_stat.text:
                        return c_stat.text.strip() == "101"
        except etree.XMLSyntaxError:
            pass
        return False