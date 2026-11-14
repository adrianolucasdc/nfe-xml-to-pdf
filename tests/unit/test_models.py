"""Unit tests for domain models."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from nfe2pdf.domain.models import (
    COFINS,
    ICMS,
    IPI,
    PIS,
    Address,
    Emitter,
    Header,
    NFEnvironment,
    NFIndicatorFinal,
    NFIndicatorPresence,
    NFProcessType,
    NFVersion,
    Product,
    Recipient,
    Totals,
    Transport,
)


class TestEnums:
    """Test enum values."""

    def test_nf_version(self):
        assert NFVersion.V400 == "4.00"

    def test_nf_environment(self):
        assert NFEnvironment.PRODUCAO == 1
        assert NFEnvironment.HOMOLOGACAO == 2

    def test_nf_type(self):
        from nfe2pdf.domain.models import NFType

        assert NFType.ENTRADA == 0
        assert NFType.SAIDA == 1

    def test_nf_indicator_final(self):
        assert NFIndicatorFinal.NAO == 0
        assert NFIndicatorFinal.SIM == 1

    def test_nf_indicator_presence(self):
        assert NFIndicatorPresence.NAO_SE_APLICA == 0
        assert NFIndicatorPresence.PRESENCIAL == 1
        assert NFIndicatorPresence.INTERNET == 2
        assert NFIndicatorPresence.TELEATENDIMENTO == 3
        assert NFIndicatorPresence.NFC_E == 4
        assert NFIndicatorPresence.OUTROS == 9

    def test_nf_process_type(self):
        assert NFProcessType.NORMAL == 0
        assert NFProcessType.CONTINGENCIA_FS == 1
        assert NFProcessType.CONTINGENCIA_OFFLINE == 9


class TestAddress:
    """Test Address model."""

    def test_valid_address(self):
        addr = Address(
            street="RUA EXEMPLO",
            number="100",
            neighborhood="CENTRO",
            city_code="3550308",
            city_name="SAO PAULO",
            state="SP",
            zip_code="01000000",
            country_code="1058",
            country_name="BRASIL",
        )
        assert addr.street == "RUA EXEMPLO"
        assert addr.number == "100"

    def test_address_optional_fields(self):
        addr = Address(
            street="RUA EXEMPLO",
            number="100",
            neighborhood="CENTRO",
            city_code="3550308",
            city_name="SAO PAULO",
            state="SP",
            zip_code="01000000",
            country_code="1058",
            country_name="BRASIL",
            complement="SALA 101",
        )
        assert addr.complement == "SALA 101"


class TestEmitter:
    """Test Emitter model."""

    def test_valid_emitter(self):
        emitter = Emitter(
            cnpj="12345678000123",
            company_name="EMPRESA EXEMPLO LTDA",
            trade_name="EMPRESA EXEMPLO",
            address=Address(
                street="RUA EXEMPLO",
                number="100",
                neighborhood="CENTRO",
                city_code="3550308",
                city_name="SAO PAULO",
                state="SP",
                zip_code="01000000",
                country_code="1058",
                country_name="BRASIL",
            ),
            state_registration="123456789012",
            crt=3,
        )
        assert emitter.cnpj == "12345678000123"
        assert emitter.company_name == "EMPRESA EXEMPLO LTDA"
        assert emitter.crt == 3


class TestRecipient:
    """Test Recipient model."""

    def test_valid_recipient(self):
        recipient = Recipient(
            cnpj="98765432000198",
            name="CLIENTE EXEMPLO LTDA",
            address=Address(
                street="AV TESTE",
                number="200",
                neighborhood="JARDINS",
                city_code="3550308",
                city_name="SAO PAULO",
                state="SP",
                zip_code="01400000",
                country_code="1058",
                country_name="BRASIL",
            ),
            ie_indicator=1,
            state_registration="987654321098",
        )
        assert recipient.cnpj == "98765432000198"
        assert recipient.name == "CLIENTE EXEMPLO LTDA"


class TestProduct:
    """Test Product model."""

    def test_valid_product(self):
        prod = Product(
            item_number=1,
            product_code="001",
            ean=None,
            description="PRODUTO EXEMPLO",
            ncm="12345678",
            cest=None,
            cfop="5102",
            unit_commercial="UN",
            quantity_commercial=Decimal("1.0000"),
            unit_value_commercial=Decimal("100.00"),
            product_value=Decimal("100.00"),
            ean_trib=None,
            unit_trib="UN",
            quantity_trib=Decimal("1.0000"),
            unit_value_trib=Decimal("100.00"),
            freight_value=None,
            insurance_value=None,
            discount_value=None,
            other_value=None,
            total_indicator=1,
            additional_info=None,
        )
        assert prod.item_number == 1
        assert prod.product_value == Decimal("100.00")


class TestTaxModels:
    """Test tax models."""

    def test_icms(self):
        icms = ICMS(
            cst="00",
            origin=0,
            mod_bc=3,
            v_bc=Decimal("100.00"),
            p_icms=Decimal("18.00"),
            v_icms=Decimal("18.00"),
        )
        assert icms.cst == "00"
        assert icms.v_icms == Decimal("18.00")

    def test_ipi(self):
        ipi = IPI(
            cst="53",
            enq="999",
        )
        assert ipi.cst == "53"

    def test_pis(self):
        pis = PIS(
            cst="01",
            v_bc=Decimal("100.00"),
            p_pis=Decimal("1.65"),
            v_pis=Decimal("1.65"),
        )
        assert pis.v_pis == Decimal("1.65")

    def test_cofins(self):
        cofins = COFINS(
            cst="01",
            v_bc=Decimal("100.00"),
            p_cofins=Decimal("7.60"),
            v_cofins=Decimal("7.60"),
        )
        assert cofins.v_cofins == Decimal("7.60")


class TestTotals:
    """Test Totals model."""

    def test_valid_totals(self):
        totals = Totals(
            v_bc=Decimal("100.00"),
            v_icms=Decimal("18.00"),
            v_prod=Decimal("100.00"),
            v_nf=Decimal("100.00"),
        )
        assert totals.v_nf == Decimal("100.00")


class TestTransport:
    """Test Transport model."""

    def test_valid_transport(self):
        transport = Transport(
            freight_modality=0,
        )
        assert transport.freight_modality == 0


class TestHeader:
    """Test Header model."""

    def test_valid_header(self):
        from datetime import datetime

        header = Header(
            state_code=35,
            nf_number=1,
            series=1,
            nature_operation="VENDA",
            model=55,
            issue_date=datetime(2024, 1, 15, 10, 0, 0),
            nf_type=1,
            destination_id=1,
            municipality_code=3550308,
            print_format=1,
            emission_type=1,
            check_digit=0,
            environment=2,
            finality=1,
            process_type=0,
            process_version="1.0",
            final_consumer=1,
            presence_indicator=1,
        )
        assert header.nf_number == 1
        assert header.environment == 2


class TestNFeData:
    """Test main NFeData model."""

    def test_formatted_access_key(self):
        from nfe2pdf.domain.models import NFeData

        nfe = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            access_key="35240112345678000123550010000000011234567890",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
        )
        # formatted_access_key groups by 4 chars
        expected = "3524 0112 3456 7800 0123 5500 1000 0000 0112 3456 7890"
        assert nfe.formatted_access_key == expected

    def test_is_cancelled(self):
        from nfe2pdf.domain.models import NFeData

        nfe = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
            status_code=101,  # Cancelled
        )
        assert nfe.is_cancelled is True

    def test_is_not_cancelled(self):
        from nfe2pdf.domain.models import NFeData

        nfe = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
            status_code=100,  # Authorized
        )
        assert nfe.is_cancelled is False