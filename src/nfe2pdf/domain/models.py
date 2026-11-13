"""Domain models for NF-e data structures using Pydantic v2."""
from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class NFVersion(str, Enum):
    """Supported NF-e versions."""
    V400 = "4.00"


class NFType(int, Enum):
    """NF-e type: 0=Entrada, 1=Saída."""
    ENTRADA = 0
    SAIDA = 1


class NFEnvironment(int, Enum):
    """Environment: 1=Produção, 2=Homologação."""
    PRODUCAO = 1
    HOMOLOGACAO = 2


class NFProcessType(int, Enum):
    """Process emission type: 0=Normal, 1=Contingência FS, 2=Contingência SCAN, 3=Contingência DPEC, 4=Contingência EPEC, 5=Contingência FS-DA, 6=Contingência SVC-AN, 7=Contingência SVC-RS, 9=Contingência off-line."""
    NORMAL = 0
    CONTINGENCIA_FS = 1
    CONTINGENCIA_SCAN = 2
    CONTINGENCIA_DPEC = 3
    CONTINGENCIA_EPEC = 4
    CONTINGENCIA_FS_DA = 5
    CONTINGENCIA_SVC_AN = 6
    CONTINGENCIA_SVC_RS = 7
    CONTINGENCIA_OFFLINE = 9


class NFEmissionType(int, Enum):
    """Emission type: 1=Normal, 2=Contingência FS-IA, 3=Contingência SCAN, 4=Contingência DPEC, 5=Contingência FS-DA, 6=Contingência SVC-AN, 7=Contingência SVC-RS, 9=Contingência off-line."""
    NORMAL = 1
    CONTINGENCIA_FS_IA = 2
    CONTINGENCIA_SCAN = 3
    CONTINGENCIA_DPEC = 4
    CONTINGENCIA_FS_DA = 5
    CONTINGENCIA_SVC_AN = 6
    CONTINGENCIA_SVC_RS = 7
    CONTINGENCIA_OFFLINE = 9


class NFIndicatorFinal(int, Enum):
    """Final consumer indicator: 0=Não, 1=Consumidor final."""
    NAO = 0
    SIM = 1


class NFIndicatorPresence(int, Enum):
    """Presence indicator: 0=Não se aplica, 1=Presencial, 2=Internet, 3=Teleatendimento, 4=NFC-e, 9=Outros."""
    NAO_SE_APLICA = 0
    PRESENCIAL = 1
    INTERNET = 2
    TELEATENDIMENTO = 3
    NFC_E = 4
    OUTROS = 9


class Address(BaseModel):
    """Address model for emitter, recipient, delivery, etc."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    street: str = Field(alias="xLgr", description="Logradouro")
    number: str = Field(alias="nro", description="Número")
    complement: Optional[str] = Field(default=None, alias="xCpl", description="Complemento")
    neighborhood: str = Field(alias="xBairro", description="Bairro")
    city_code: str = Field(alias="cMun", description="Código do município (IBGE)")
    city_name: str = Field(alias="xMun", description="Nome do município")
    state: str = Field(alias="UF", description="Sigla da UF")
    zip_code: str = Field(alias="CEP", description="CEP")
    country_code: str = Field(alias="cPais", description="Código do país")
    country_name: str = Field(alias="xPais", description="Nome do país")
    phone: Optional[str] = Field(default=None, alias="fone", description="Telefone")


class Emitter(BaseModel):
    """Emitter (emitente) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cnpj: Optional[str] = Field(default=None, alias="CNPJ", description="CNPJ do emitente")
    cpf: Optional[str] = Field(default=None, alias="CPF", description="CPF do emitente (se pessoa física)")
    company_name: str = Field(alias="xNome", description="Razão social")
    trade_name: Optional[str] = Field(default=None, alias="xFant", description="Nome fantasia")
    address: Address = Field(alias="enderEmit")
    state_registration: Optional[str] = Field(default=None, alias="IE", description="Inscrição Estadual")
    municipal_registration: Optional[str] = Field(default=None, alias="IM", description="Inscrição Municipal")
    crt: int = Field(alias="CRT", description="Código de Regime Tributário: 1=Simples Nacional, 2=Simples excesso sublimite, 3=Regime Normal")


class Recipient(BaseModel):
    """Recipient (destinatário) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cnpj: Optional[str] = Field(default=None, alias="CNPJ", description="CNPJ do destinatário")
    cpf: Optional[str] = Field(default=None, alias="CPF", description="CPF do destinatário")
    id_foreign: Optional[str] = Field(default=None, alias="idEstrangeiro", description="ID estrangeiro")
    name: str = Field(alias="xNome", description="Nome/Razão social")
    address: Optional[Address] = Field(default=None, alias="enderDest")
    ie_indicator: int = Field(alias="indIEDest", description="Indicador IE: 1=Contribuinte ICMS, 2=Isento, 9=Não contribuinte")
    state_registration: Optional[str] = Field(default=None, alias="IE", description="Inscrição Estadual")
    email: Optional[str] = Field(default=None, alias="email", description="E-mail")


class Product(BaseModel):
    """Product/Item (det/prod) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_number: int = Field(alias="nItem", description="Número do item")
    product_code: str = Field(alias="cProd", description="Código do produto")
    ean: Optional[str] = Field(default=None, alias="cEAN", description="GTIN/EAN")
    description: str = Field(alias="xProd", description="Descrição do produto")
    ncm: str = Field(alias="NCM", description="Código NCM")
    cest: Optional[str] = Field(default=None, alias="CEST", description="Código CEST")
    cfop: str = Field(alias="CFOP", description="CFOP")
    unit_commercial: str = Field(alias="uCom", description="Unidade comercial")
    quantity_commercial: Decimal = Field(alias="qCom", description="Quantidade comercial")
    unit_value_commercial: Decimal = Field(alias="vUnCom", description="Valor unitário comercial")
    product_value: Decimal = Field(alias="vProd", description="Valor total do produto")
    ean_trib: Optional[str] = Field(default=None, alias="cEANTrib", description="GTIN/EAN tributável")
    unit_trib: str = Field(alias="uTrib", description="Unidade tributável")
    quantity_trib: Decimal = Field(alias="qTrib", description="Quantidade tributável")
    unit_value_trib: Decimal = Field(alias="vUnTrib", description="Valor unitário tributável")
    freight_value: Optional[Decimal] = Field(default=None, alias="vFrete", description="Valor do frete")
    insurance_value: Optional[Decimal] = Field(default=None, alias="vSeg", description="Valor do seguro")
    discount_value: Optional[Decimal] = Field(default=None, alias="vDesc", description="Valor do desconto")
    other_value: Optional[Decimal] = Field(default=None, alias="vOutro", description="Outras despesas")
    total_indicator: int = Field(alias="indTot", description="Indicador total: 1=Sim, 0=Não")
    additional_info: Optional[str] = Field(default=None, alias="infAdProd", description="Informações adicionais")


class ICMS(BaseModel):
    """ICMS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST/CSOSN")
    origin: int = Field(alias="orig", description="Origem da mercadoria")
    # Campos variam conforme CST - simplificado para o essencial
    mod_bc: Optional[int] = Field(default=None, alias="modBC", description="Modalidade base de cálculo")
    v_bc: Optional[Decimal] = Field(default=None, alias="vBC", description="Valor da base de cálculo")
    p_icms: Optional[Decimal] = Field(default=None, alias="pICMS", description="Alíquota ICMS")
    v_icms: Optional[Decimal] = Field(default=None, alias="vICMS", description="Valor ICMS")
    v_bc_st: Optional[Decimal] = Field(default=None, alias="vBCST", description="Valor base cálculo ST")
    p_st: Optional[Decimal] = Field(default=None, alias="pST", description="Alíquota ST")
    v_icms_st: Optional[Decimal] = Field(default=None, alias="vICMSST", description="Valor ICMS ST")
    p_fcp: Optional[Decimal] = Field(default=None, alias="pFCP", description="Percentual FCP")
    v_fcp: Optional[Decimal] = Field(default=None, alias="vFCP", description="Valor FCP")
    v_fcp_st: Optional[Decimal] = Field(default=None, alias="vFCPST", description="Valor FCP ST")
    v_bc_fcp_st: Optional[Decimal] = Field(default=None, alias="vBCFCPST", description="Base cálculo FCP ST")


class IPI(BaseModel):
    """IPI tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST IPI")
    enq: Optional[str] = Field(default=None, alias="cEnq", description="Código de enquadramento")
    v_bc: Optional[Decimal] = Field(default=None, alias="vBC", description="Base de cálculo")
    p_ipi: Optional[Decimal] = Field(default=None, alias="pIPI", description="Alíquota IPI")
    v_ipi: Optional[Decimal] = Field(default=None, alias="vIPI", description="Valor IPI")


class PIS(BaseModel):
    """PIS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST PIS")
    v_bc: Optional[Decimal] = Field(default=None, alias="vBC", description="Base de cálculo")
    p_pis: Optional[Decimal] = Field(default=None, alias="pPIS", description="Alíquota PIS")
    v_pis: Optional[Decimal] = Field(default=None, alias="vPIS", description="Valor PIS")
    q_bc_prod: Optional[Decimal] = Field(default=None, alias="qBCProd", description="Quantidade base cálculo")
    v_aliq_prod: Optional[Decimal] = Field(default=None, alias="vAliqProd", description="Alíquota em valor")


class COFINS(BaseModel):
    """COFINS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST COFINS")
    v_bc: Optional[Decimal] = Field(default=None, alias="vBC", description="Base de cálculo")
    p_cofins: Optional[Decimal] = Field(default=None, alias="pCOFINS", description="Alíquota COFINS")
    v_cofins: Optional[Decimal] = Field(default=None, alias="vCOFINS", description="Valor COFINS")
    q_bc_prod: Optional[Decimal] = Field(default=None, alias="qBCProd", description="Quantidade base cálculo")
    v_aliq_prod: Optional[Decimal] = Field(default=None, alias="vAliqProd", description="Alíquota em valor")


class Taxes(BaseModel):
    """Taxes (imposto) model for a product."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_tax_value: Optional[Decimal] = Field(default=None, alias="vTotTrib", description="Valor total aproximado de tributos")
    icms: Optional[ICMS] = Field(default=None)
    ipi: Optional[IPI] = Field(default=None)
    pis: Optional[PIS] = Field(default=None)
    cofins: Optional[COFINS] = Field(default=None)
    issqn: Optional[dict] = Field(default=None, alias="ISSQN", description="ISSQN (simplificado)")


class Detail(BaseModel):
    """Detail item (det) combining product and taxes."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_number: int = Field(alias="nItem", description="Número do item")
    product: Product = Field(alias="prod")
    taxes: Optional[Taxes] = Field(default=None, alias="imposto")


class Totals(BaseModel):
    """Total values (total/ICMSTot)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    v_bc: Decimal = Field(alias="vBC", description="Base cálculo ICMS")
    v_icms: Decimal = Field(alias="vICMS", description="Valor ICMS")
    v_icms_deson: Optional[Decimal] = Field(default=None, alias="vICMSDeson", description="Valor ICMS desonerado")
    v_fcp_uf_dest: Optional[Decimal] = Field(default=None, alias="vFCPUFDest", description="Valor FCP UF destino")
    v_icms_uf_dest: Optional[Decimal] = Field(default=None, alias="vICMSUFDest", description="Valor ICMS UF destino")
    v_icms_uf_remet: Optional[Decimal] = Field(default=None, alias="vICMSUFRemet", description="Valor ICMS UF remetente")
    v_fcp: Optional[Decimal] = Field(default=None, alias="vFCP", description="Valor FCP")
    v_bc_st: Optional[Decimal] = Field(default=None, alias="vBCST", description="Base cálculo ST")
    v_st: Optional[Decimal] = Field(default=None, alias="vST", description="Valor ST")
    v_prod: Decimal = Field(alias="vProd", description="Valor total produtos")
    v_frete: Optional[Decimal] = Field(default=None, alias="vFrete", description="Valor frete")
    v_seg: Optional[Decimal] = Field(default=None, alias="vSeg", description="Valor seguro")
    v_desc: Optional[Decimal] = Field(default=None, alias="vDesc", description="Valor desconto")
    v_ii: Optional[Decimal] = Field(default=None, alias="vII", description="Valor II")
    v_ipi: Optional[Decimal] = Field(default=None, alias="vIPI", description="Valor IPI")
    v_ipi_devol: Optional[Decimal] = Field(default=None, alias="vIPIDevol", description="Valor IPI devolvido")
    v_pis: Optional[Decimal] = Field(default=None, alias="vPIS", description="Valor PIS")
    v_cofins: Optional[Decimal] = Field(default=None, alias="vCOFINS", description="Valor COFINS")
    v_outro: Optional[Decimal] = Field(default=None, alias="vOutro", description="Outras despesas")
    v_nf: Decimal = Field(alias="vNF", description="Valor total da NF-e")
    v_tot_trib: Optional[Decimal] = Field(default=None, alias="vTotTrib", description="Valor total aproximado tributos")


class Transport(BaseModel):
    """Transport (transp) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    freight_modality: int = Field(alias="modFrete", description="Modalidade de frete: 0=Emitente, 1=Destinatário, 2=Terceiros, 3=Próprio, 9=Sem frete")
    carrier: Optional[dict] = Field(default=None, alias="transporta", description="Transportadora (simplificado)")
    volume: Optional[List[dict]] = Field(default=None, alias="vol", description="Volumes transportados")


class Payment(BaseModel):
    """Payment (pag) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    payment_type: int = Field(alias="tPag", description="Forma de pagamento: 01=Dinheiro, 02=Cheque, 03=Cartão Crédito, 04=Cartão Débito, 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente, 13=Vale Combustível, 15=Boleto, 16=Depósito, 17=PIX, 18=Transferência Bancária, 19=Programa Fidelidade, 90=Sem pagamento, 99=Outros")
    value: Decimal = Field(alias="vPag", description="Valor do pagamento")
    card: Optional[dict] = Field(default=None, alias="card", description="Dados do cartão (simplificado)")


class Header(BaseModel):
    """Header (ide) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    state_code: int = Field(alias="cUF", description="Código da UF do emitente")
    nf_number: int = Field(alias="nNF", description="Número da NF-e")
    series: int = Field(alias="serie", description="Série da NF-e")
    nature_operation: str = Field(alias="natOp", description="Natureza da operação")
    model: int = Field(alias="mod", description="Modelo do documento fiscal (55=NF-e, 65=NFC-e)")
    issue_date: datetime = Field(alias="dhEmi", description="Data/hora emissão")
    entry_exit_date: Optional[datetime] = Field(default=None, alias="dhSaiEnt", description="Data/hora saída/entrada")
    nf_type: NFType = Field(alias="tpNF", description="Tipo: 0=Entrada, 1=Saída")
    destination_id: int = Field(alias="idDest", description="Destino: 1=Interna, 2=Interestadual, 3=Exterior")
    municipality_code: int = Field(alias="cMunFG", description="Código município (IBGE)")
    print_format: int = Field(alias="tpImp", description="Formato impressão: 1=Retrato, 2=Paisagem, 3=Simplificado, 4=DANFE NFC-e, 5=DANFE NFC-e msg")
    emission_type: NFEmissionType = Field(alias="tpEmis", description="Tipo de emissão")
    check_digit: int = Field(alias="cDV", description="Dígito verificador chave acesso")
    environment: NFEnvironment = Field(alias="tpAmb", description="Ambiente: 1=Produção, 2=Homologação")
    finality: int = Field(alias="finNFe", description="Finalidade: 1=Normal, 2=Complementar, 3=Ajuste, 4=Devolução")
    process_type: NFProcessType = Field(alias="procEmi", description="Processo de emissão")
    process_version: str = Field(alias="verProc", description="Versão do processo")
    final_consumer: NFIndicatorFinal = Field(alias="indFinal", description="Consumidor final")
    presence_indicator: NFIndicatorPresence = Field(alias="indPres", description="Indicador presença")
    nf_key: Optional[str] = Field(default=None, alias="chNFe", description="Chave de acesso (vem no protNFe)")
    protocol: Optional[str] = Field(default=None, alias="nProt", description="Número do protocolo (vem no protNFe)")
    protocol_date: Optional[datetime] = Field(default=None, alias="dhRecbto", description="Data/hora recebimento (vem no protNFe)")
    status_code: Optional[int] = Field(default=None, alias="cStat", description="Código status (vem no protNFe)")
    status_message: Optional[str] = Field(default=None, alias="xMotivo", description="Mensagem status (vem no protNFe)")


class AdditionalInfo(BaseModel):
    """Additional information (infAdic)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    complementary: Optional[str] = Field(default=None, alias="infCpl", description="Informações complementares")
    fiscal_interest: Optional[str] = Field(default=None, alias="infAdFisco", description="Informações de interesse do Fisco")


class NFeData(BaseModel):
    """Complete NF-e data model (infNFe + protNFe)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Identificação
    id: str = Field(alias="Id", description="ID da NF-e (chave com prefixo 'NFe')")
    version: NFVersion = Field(alias="versao", description="Versão do leiaute")

    # Dados principais
    header: Header = Field(alias="ide")
    emitter: Emitter = Field(alias="emit")
    recipient: Recipient = Field(alias="dest")
    details: List[Detail] = Field(alias="det")
    totals: Totals = Field(alias="total")
    transport: Optional[Transport] = Field(default=None, alias="transp")
    payment: Optional[List[Payment]] = Field(default=None, alias="pag")
    additional_info: Optional[AdditionalInfo] = Field(default=None, alias="infAdic")

    # Autorização (vem no protNFe)
    access_key: Optional[str] = Field(default=None, description="Chave de acesso (44 dígitos)")
    protocol_number: Optional[str] = Field(default=None, description="Número do protocolo de autorização")
    protocol_date: Optional[datetime] = Field(default=None, description="Data/hora do protocolo")
    status_code: Optional[int] = Field(default=None, description="Código do status (100=Autorizado, 101=Cancelada, etc.)")
    status_message: Optional[str] = Field(default=None, description="Mensagem do status")

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v: str) -> str:
        """Extrai o ID removendo o prefixo 'NFe' se vier no atributo Id do XML."""
        if v.startswith("NFe"):
            return v[3:]
        return v

    @property
    def is_cancelled(self) -> bool:
        """Verifica se a NF-e está cancelada (cStat=101)."""
        return self.status_code == 101

    @property
    def is_authorized(self) -> bool:
        """Verifica se a NF-e está autorizada (cStat=100)."""
        return self.status_code == 100

    @property
    def formatted_access_key(self) -> str:
        """Retorna a chave de acesso formatada em grupos de 4 dígitos."""
        if not self.access_key:
            return ""
        key = self.access_key
        return " ".join(key[i:i+4] for i in range(0, len(key), 4))

    @property
    def emitter_cnpj_formatted(self) -> str:
        """CNPJ do emitente formatado."""
        cnpj = self.emitter.cnpj or ""
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj

    @property
    def recipient_cnpj_formatted(self) -> str:
        """CNPJ do destinatário formatado."""
        cnpj = self.recipient.cnpj or ""
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj