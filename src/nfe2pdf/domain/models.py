"""Domain models for NF-e data structures using Pydantic v2."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum, StrEnum

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class NFVersion(StrEnum):
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
    """Process emission type.

    0=Normal, 1=Contingencia FS, 2=Contingencia SCAN,
    3=Contingencia DPEC, 4=Contingencia EPEC, 5=Contingencia FS-DA,
    6=Contingencia SVC-AN, 7=Contingencia SVC-RS, 9=Contingencia off-line.
    """
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
    """Emission type.

    1=Normal, 2=Contingencia FS-IA, 3=Contingencia SCAN,
    4=Contingencia DPEC, 5=Contingencia FS-DA, 6=Contingencia SVC-AN,
    7=Contingencia SVC-RS, 9=Contingencia off-line.
    """
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
    """Presence indicator.

    0=Nao se aplica, 1=Presencial, 2=Internet, 3=Teleatendimento,
    4=NFC-e, 9=Outros.
    """
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
    complement: str | None = Field(default=None, alias="xCpl", description="Complemento")
    neighborhood: str = Field(alias="xBairro", description="Bairro")
    city_code: str = Field(alias="cMun", description="Código do município (IBGE)")
    city_name: str = Field(alias="xMun", description="Nome do município")
    state: str = Field(alias="UF", description="Sigla da UF")
    zip_code: str = Field(alias="CEP", description="CEP")
    country_code: str = Field(alias="cPais", description="Código do país")
    country_name: str = Field(alias="xPais", description="Nome do país")
    phone: str | None = Field(default=None, alias="fone", description="Telefone")


class Emitter(BaseModel):
    """Emitter (emitente) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cnpj: str | None = Field(default=None, alias="CNPJ", description="CNPJ do emitente")
    cpf: str | None = Field(
        default=None, alias="CPF", description="CPF do emitente (pessoa fisica)"
    )
    company_name: str = Field(alias="xNome", description="Razao social")
    trade_name: str | None = Field(default=None, alias="xFant", description="Nome fantasia")
    address: Address = Field(alias="enderEmit")
    state_registration: str | None = Field(
        default=None, alias="IE", description="Inscricao Estadual"
    )
    municipal_registration: str | None = Field(
        default=None, alias="IM", description="Inscricao Municipal"
    )
    crt: int = Field(
        alias="CRT", description="CRT: 1=Simples Nacional, 2=Simples excesso, 3=Normal"
    )


class Recipient(BaseModel):
    """Recipient (destinatario) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cnpj: str | None = Field(default=None, alias="CNPJ", description="CNPJ do destinatario")
    cpf: str | None = Field(default=None, alias="CPF", description="CPF do destinatario")
    id_foreign: str | None = Field(
        default=None, alias="idEstrangeiro", description="ID estrangeiro"
    )
    name: str = Field(alias="xNome", description="Nome/Razao social")
    address: Address | None = Field(default=None, alias="enderDest")
    ie_indicator: int = Field(
        alias="indIEDest",
        description="Indicador IE: 1=Contribuinte ICMS, 2=Isento, 9=Nao contribuinte",
    )
    state_registration: str | None = Field(
        default=None, alias="IE", description="Inscricao Estadual"
    )
    email: str | None = Field(default=None, alias="email", description="E-mail")


class Product(BaseModel):
    """Product/Item (det/prod) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_number: int = Field(alias="nItem", description="Número do item")
    product_code: str = Field(alias="cProd", description="Código do produto")
    ean: str | None = Field(default=None, alias="cEAN", description="GTIN/EAN")
    description: str = Field(alias="xProd", description="Descrição do produto")
    ncm: str = Field(alias="NCM", description="Código NCM")
    cest: str | None = Field(default=None, alias="CEST", description="Código CEST")
    cfop: str = Field(alias="CFOP", description="CFOP")
    unit_commercial: str = Field(alias="uCom", description="Unidade comercial")
    quantity_commercial: Decimal = Field(alias="qCom", description="Quantidade comercial")
    unit_value_commercial: Decimal = Field(alias="vUnCom", description="Valor unitário comercial")
    product_value: Decimal = Field(alias="vProd", description="Valor total do produto")
    ean_trib: str | None = Field(default=None, alias="cEANTrib", description="GTIN/EAN tributável")
    unit_trib: str = Field(alias="uTrib", description="Unidade tributável")
    quantity_trib: Decimal = Field(alias="qTrib", description="Quantidade tributável")
    unit_value_trib: Decimal = Field(alias="vUnTrib", description="Valor unitário tributável")
    freight_value: Decimal | None = Field(
        default=None, alias="vFrete", description="Valor do frete"
    )
    insurance_value: Decimal | None = Field(
        default=None, alias="vSeg", description="Valor do seguro"
    )
    discount_value: Decimal | None = Field(
        default=None, alias="vDesc", description="Valor do desconto"
    )
    other_value: Decimal | None = Field(
        default=None, alias="vOutro", description="Outras despesas"
    )
    total_indicator: int = Field(alias="indTot", description="Indicador total: 1=Sim, 0=Nao")
    additional_info: str | None = Field(
        default=None, alias="infAdProd", description="Informacoes adicionais"
    )


class ICMS(BaseModel):
    """ICMS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST/CSOSN")
    origin: int = Field(alias="orig", description="Origem da mercadoria")
    # Campos variam conforme CST - simplificado para o essencial
    mod_bc: int | None = Field(default=None, alias="modBC", description="Modalidade base calculo")
    v_bc: Decimal | None = Field(default=None, alias="vBC", description="Valor base calculo")
    p_icms: Decimal | None = Field(default=None, alias="pICMS", description="Aliquota ICMS")
    v_icms: Decimal | None = Field(default=None, alias="vICMS", description="Valor ICMS")
    v_bc_st: Decimal | None = Field(
        default=None, alias="vBCST", description="Valor base calculo ST"
    )
    p_st: Decimal | None = Field(default=None, alias="pST", description="Aliquota ST")
    v_icms_st: Decimal | None = Field(
        default=None, alias="vICMSST", description="Valor ICMS ST"
    )
    p_fcp: Decimal | None = Field(default=None, alias="pFCP", description="Percentual FCP")
    v_fcp: Decimal | None = Field(default=None, alias="vFCP", description="Valor FCP")
    v_fcp_st: Decimal | None = Field(
        default=None, alias="vFCPST", description="Valor FCP ST"
    )
    v_bc_fcp_st: Decimal | None = Field(
        default=None, alias="vBCFCPST", description="Base calculo FCP ST"
    )


class IPI(BaseModel):
    """IPI tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST IPI")
    enq: str | None = Field(default=None, alias="cEnq", description="Codigo enquadramento")
    v_bc: Decimal | None = Field(default=None, alias="vBC", description="Base calculo")
    p_ipi: Decimal | None = Field(default=None, alias="pIPI", description="Aliquota IPI")
    v_ipi: Decimal | None = Field(default=None, alias="vIPI", description="Valor IPI")


class PIS(BaseModel):
    """PIS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST PIS")
    v_bc: Decimal | None = Field(default=None, alias="vBC", description="Base calculo")
    p_pis: Decimal | None = Field(default=None, alias="pPIS", description="Aliquota PIS")
    v_pis: Decimal | None = Field(default=None, alias="vPIS", description="Valor PIS")
    q_bc_prod: Decimal | None = Field(
        default=None, alias="qBCProd", description="Quantidade base calculo"
    )
    v_aliq_prod: Decimal | None = Field(
        default=None, alias="vAliqProd", description="Aliquota em valor"
    )


class COFINS(BaseModel):
    """COFINS tax model (simplified)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    cst: str = Field(alias="CST", description="CST COFINS")
    v_bc: Decimal | None = Field(default=None, alias="vBC", description="Base calculo")
    p_cofins: Decimal | None = Field(default=None, alias="pCOFINS", description="Aliquota COFINS")
    v_cofins: Decimal | None = Field(default=None, alias="vCOFINS", description="Valor COFINS")
    q_bc_prod: Decimal | None = Field(
        default=None, alias="qBCProd", description="Quantidade base calculo"
    )
    v_aliq_prod: Decimal | None = Field(
        default=None, alias="vAliqProd", description="Aliquota em valor"
    )


class Taxes(BaseModel):
    """Taxes (imposto) model for a product."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_tax_value: Decimal | None = Field(
        default=None, alias="vTotTrib", description="Valor total aprox tributos"
    )
    icms: ICMS | None = Field(default=None)
    ipi: IPI | None = Field(default=None)
    pis: PIS | None = Field(default=None)
    cofins: COFINS | None = Field(default=None)
    issqn: dict | None = Field(default=None, alias="ISSQN", description="ISSQN (simplificado)")


class Detail(BaseModel):
    """Detail item (det) combining product and taxes."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_number: int = Field(alias="nItem", description="Número do item")
    product: Product = Field(alias="prod")
    taxes: Taxes | None = Field(default=None, alias="imposto")


class Totals(BaseModel):
    """Total values (total/ICMSTot)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    v_bc: Decimal = Field(alias="vBC", description="Base calculo ICMS")
    v_icms: Decimal = Field(alias="vICMS", description="Valor ICMS")
    v_icms_deson: Decimal | None = Field(
        default=None, alias="vICMSDeson", description="Valor ICMS desonerado"
    )
    v_fcp_uf_dest: Decimal | None = Field(
        default=None, alias="vFCPUFDest", description="Valor FCP UF destino"
    )
    v_icms_uf_dest: Decimal | None = Field(
        default=None, alias="vICMSUFDest", description="Valor ICMS UF destino"
    )
    v_icms_uf_remet: Decimal | None = Field(
        default=None, alias="vICMSUFRemet", description="Valor ICMS UF remetente"
    )
    v_fcp: Decimal | None = Field(default=None, alias="vFCP", description="Valor FCP")
    v_bc_st: Decimal | None = Field(default=None, alias="vBCST", description="Base calculo ST")
    v_st: Decimal | None = Field(default=None, alias="vST", description="Valor ST")
    v_prod: Decimal = Field(alias="vProd", description="Valor total produtos")
    v_frete: Decimal | None = Field(default=None, alias="vFrete", description="Valor frete")
    v_seg: Decimal | None = Field(default=None, alias="vSeg", description="Valor seguro")
    v_desc: Decimal | None = Field(default=None, alias="vDesc", description="Valor desconto")
    v_ii: Decimal | None = Field(default=None, alias="vII", description="Valor II")
    v_ipi: Decimal | None = Field(default=None, alias="vIPI", description="Valor IPI")
    v_ipi_devol: Decimal | None = Field(
        default=None, alias="vIPIDevol", description="Valor IPI devolvido"
    )
    v_pis: Decimal | None = Field(default=None, alias="vPIS", description="Valor PIS")
    v_cofins: Decimal | None = Field(default=None, alias="vCOFINS", description="Valor COFINS")
    v_outro: Decimal | None = Field(default=None, alias="vOutro", description="Outras despesas")
    v_nf: Decimal = Field(alias="vNF", description="Valor total da NF-e")
    v_tot_trib: Decimal | None = Field(
        default=None, alias="vTotTrib", description="Valor total aprox tributos"
    )


class Transport(BaseModel):
    """Transport (transp) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    freight_modality: int = Field(
        alias="modFrete",
        description=(
            "Modalidade frete: 0=Emitente, 1=Destinatario, "
            "2=Terceiros, 3=Proprio, 9=Sem frete"
        ),
    )
    carrier: dict | None = Field(
        default=None, alias="transporta", description="Transportadora (simplificado)"
    )
    volume: list[dict] | None = Field(
        default=None, alias="vol", description="Volumes transportados"
    )


class Payment(BaseModel):
    """Payment (pag) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    payment_type: int = Field(
        alias="tPag",
        description=(
            "Pagamento: 01=Dinheiro, 02=Cheque, 03=Cartao Credito, 04=Cartao Debito, "
            "05=Credito Loja, 10=Vale Alimentacao, 11=Vale Refeicao, 12=Vale Presente, "
            "13=Vale Combustivel, 15=Boleto, 16=Deposito, 17=PIX, 18=Transferencia, "
            "19=Fidelidade, 90=Sem pagto, 99=Outros"
        ),
    )
    value: Decimal = Field(alias="vPag", description="Valor do pagamento")
    card: dict | None = Field(default=None, alias="card", description="Dados cartao (simplificado)")


class Header(BaseModel):
    """Header (ide) model."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    state_code: int = Field(alias="cUF", description="Codigo UF emitente")
    nf_number: int = Field(alias="nNF", description="Numero NF-e")
    series: int = Field(alias="serie", description="Serie NF-e")
    nature_operation: str = Field(alias="natOp", description="Natureza operacao")
    model: int = Field(alias="mod", description="Modelo: 55=NF-e, 65=NFC-e")
    issue_date: datetime = Field(alias="dhEmi", description="Data/hora emissao")
    entry_exit_date: datetime | None = Field(
        default=None, alias="dhSaiEnt", description="Data/hora saida/entrada"
    )
    nf_type: NFType = Field(alias="tpNF", description="Tipo: 0=Entrada, 1=Saida")
    destination_id: int = Field(
        alias="idDest", description="Destino: 1=Interna, 2=Interestadual, 3=Exterior"
    )
    municipality_code: int = Field(alias="cMunFG", description="Cod municipio (IBGE)")
    print_format: int = Field(
        alias="tpImp",
        description=(
            "Formato impressao: 1=Retrato, 2=Paisagem, 3=Simplificado, "
            "4=DANFE NFC-e, 5=DANFE NFC-e msg"
        ),
    )
    emission_type: NFEmissionType = Field(alias="tpEmis", description="Tipo emissao")
    check_digit: int = Field(alias="cDV", description="Digito verificador chave")
    environment: NFEnvironment = Field(
        alias="tpAmb", description="Ambiente: 1=Producao, 2=Homologacao"
    )
    finality: int = Field(
        alias="finNFe", description="Finalidade: 1=Normal, 2=Complementar, 3=Ajuste, 4=Devolucao"
    )
    process_type: NFProcessType = Field(alias="procEmi", description="Processo emissao")
    process_version: str = Field(alias="verProc", description="Versao processo")
    final_consumer: NFIndicatorFinal = Field(alias="indFinal", description="Consumidor final")
    presence_indicator: NFIndicatorPresence = Field(
        alias="indPres", description="Indicador presenca"
    )
    nf_key: str | None = Field(default=None, alias="chNFe", description="Chave acesso (protNFe)")
    protocol: str | None = Field(
        default=None, alias="nProt", description="Numero protocolo (protNFe)"
    )
    protocol_date: datetime | None = Field(
        default=None, alias="dhRecbto", description="Data/hora recebimento (protNFe)"
    )
    status_code: int | None = Field(
        default=None, alias="cStat", description="Codigo status (protNFe)"
    )
    status_message: str | None = Field(
        default=None, alias="xMotivo", description="Mensagem status (protNFe)"
    )


class AdditionalInfo(BaseModel):
    """Additional information (infAdic)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    complementary: str | None = Field(
        default=None, alias="infCpl", description="Informacoes complementares"
    )
    fiscal_interest: str | None = Field(
        default=None, alias="infAdFisco", description="Informacoes interesse Fisco"
    )


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
    details: list[Detail] = Field(alias="det")
    totals: Totals = Field(alias="total")
    transport: Transport | None = Field(default=None, alias="transp")
    payment: list[Payment] | None = Field(default=None, alias="pag")
    additional_info: AdditionalInfo | None = Field(default=None, alias="infAdic")

    # Autorizacao (vem no protNFe)
    access_key: str | None = Field(default=None, description="Chave acesso (44 digitos)")
    protocol_number: str | None = Field(
        default=None, description="Numero protocolo autorizacao"
    )
    protocol_date: datetime | None = Field(default=None, description="Data/hora protocolo")
    status_code: int | None = Field(
        default=None, description="Codigo status (100=Autorizado, 101=Cancelada, etc.)"
    )
    status_message: str | None = Field(default=None, description="Mensagem status")

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