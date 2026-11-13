# nfe2pdf — Conversor NF-e XML → PDF (DANFE)

[![Build Status](https://img.shields.io/github/actions/workflow/status/adrianolucasdc/nfe-xml-to-pdf/ci.yml?branch=main&logo=github&label=CI)](https://github.com/adrianolucasdc/nfe-xml-to-pdf/actions)
[![Coverage](https://img.shields.io/codecov/c/github/adrianolucasdc/nfe-xml-to-pdf?logo=codecov)](https://codecov.io/gh/adrianolucasdc/nfe-xml-to-pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows)](https://www.microsoft.com/windows)

> **Problema real**: Escritórios de contabilidade no Brasil processam **centenas de XMLs de NF-e por dia**. O fluxo manual (abrir no navegador → imprimir → salvar como PDF) consome horas e gera erros.
>
> **Solução**: Instale o `nfe2pdf`, associe `.xml` no Windows e **duplo-clique no arquivo XML gera o DANFE oficial (PDF) na mesma pasta**, com layout NT 2026.010, logo da empresa, marca d'água "CANCELADA" e canhoto do transportador.

---

## ✨ Features

| Feature | Descrição |
|---------|-----------|
| **Layout Oficial NT 2026.010** | Obrigatório para NF-e emitidas a partir de 01/12/2026 (fallback automático para MOC 7.0 em XMLs antigos) |
| **Associação Nativa `.xml`** | Instalador registra o `.exe` no Windows — duplo-clique = PDF pronto |
| **Logo da Empresa** | PNG/JPG configurável via YAML ou variável de ambiente |
| **Marca d'água "CANCELADA"** | Detecta automaticamente NF-e cancelada (`protNFe/cStat=101`) |
| **Canhoto Transportador** | Opcional, posicionável (topo, base, lateral) |
| **Configuração Externa** | `config.yaml` em `%APPDATA%\nfe2pdf\` + override via `NFE2PDF_*` env vars |
| **Executável Standalone** | ~15 MB, single-file, sem Python instalado no cliente (PyInstaller) |
| **Instalador Windows** | Inno Setup: `Program Files\nfe2pdf\`, atalho Menu Iniciar, desinstalador limpo |

---

## 🏗️ Arquitetura

**Clean Architecture** com separação estrita de responsabilidades:

```
src/nfe2pdf/
├── domain/              # Regras de negócio puras (zero deps externas)
│   ├── models.py        # Pydantic v2: NFeData, Emit, Dest, Prod, Imposto...
│   ├── exceptions.py    # InvalidXmlError, NotNFeError, PDFGenerationError
│   └── ports.py         # Interfaces: XMLParser, PDFGenerator (Strategy)
├── application/         # Casos de uso (orquestração)
│   ├── use_cases.py     # GenerateDanfeUseCase, InstallAssociationUseCase
│   └── dto.py           # Data Transfer Objects
├── infrastructure/      # Adapters concretos (I/O real)
│   ├── pdf/bfr_adapter.py   # Adapter p/ BrazilFiscalReport (LGPL-3.0)
│   ├── xml/parser.py        # lxml + namespaces NF-e 4.00
│   └── windows/registry.py  # Registro Windows (associação .xml)
├── cli.py               # Click CLI: generate, config, install
├── config.py            # Pydantic Settings (YAML + env vars)
└── utils/paths.py       # Paths: AppData, ProgramFiles, _MEIPASS (PyInstaller)
```

**Por que isso importa**:
- **Testável**: Domain/Application testados unitariamente com mocks (zero I/O)
- **Trocável**: `PDFGenerator` é uma interface — futuramente `reportlab`/`weasyprint` sem tocar domínio
- **Licença isolada**: `BrazilFiscalReport` (LGPL-3.0) encapsulado no adapter → migração futura remove restrição LGPL do executável final

---

## 🚀 Instalação (Usuário Final)

### Opção 1: Instalador (Recomendado)
```bash
# Baixe da página de Releases
# https://github.com/adrianolucasdc/nfe-xml-to-pdf/releases/latest
# Execute: nfe2pdf-setup.exe → Next → Next → Concluir
```
O instalador:
1. Copia `nfe2pdf.exe` para `C:\Program Files\nfe2pdf\`
2. Cria atalho no Menu Iniciar
3. **Registra associação `.xml`** no Windows Registry
4. Inclui licenças MIT + LGPL-3.0

### Opção 2: Executável Standalone
```bash
# Baixe nfe2pdf.exe da Release
# Coloque em qualquer pasta (ex: C:\Ferramentas\)
# Execute uma vez: nfe2pdf.exe --install-association  (precisa Admin)
```

---

## 💻 Desenvolvimento

### Pré-requisitos
- Python 3.11+
- Git
- (Opcional) Inno Setup 6+ para build do instalador

### Setup Local
```bash
# Clone
git clone https://github.com/adrianolucasdc/nfe-xml-to-pdf.git
cd nfe-xml-to-pdf

# Ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell
# source .venv/bin/activate # Linux/Mac

# Dependências de dev (inclui pytest, ruff, mypy, pyinstaller)
pip install -e ".[dev]"

# Verificações rápidas
ruff check . && mypy src/nfe2pdf && pytest -q
```

### Comandos Úteis
```bash
# Testes
pytest                                    # Todos
pytest -m unit -q                         # Só unitários (rápido)
pytest -m integration -v                  # Integração (precisa fixtures)
pytest --cov=nfe2pdf --cov-report=html    # Coverage + relatório HTML

# Qualidade
ruff check . --fix && ruff format .       # Lint + format auto
mypy src/nfe2pdf                          # Type check estrito

# Build
python scripts/build_exe.py               # Gera dist/nfe2pdf.exe
iscc scripts/build_installer.iss          # Gera dist/nfe2pdf-setup.exe (requer Inno Setup)

# CLI em dev
python -m nfe2pdf --help
python -m nfe2pdf generate tests/fixtures/nfe_v400_valid.xml
```

---

## 🧪 Testes

```
tests/
├── conftest.py              # Fixtures + sample NF-e 4.00 embutido (dados 100% fictícios)
├── unit/
│   ├── test_models.py       # Pydantic validation: CNPJ, datas, decimais, enums
│   ├── test_parser.py       # XPath, namespaces, XML malformado, não-NFe
│   ├── test_use_cases.py    # Orquestração com mocks de ports
│   └── test_adapters.py     # BFRAdapter: XML fixture → bytes PDF
├── integration/
│   ├── test_cli.py          # subprocess.run CLI → exit code, stdout, arquivo gerado
│   └── test_e2e_generate.py # XML → PDF → extrai texto (pdfminer) → assert
└── fixtures/
    ├── nfe_v400_valid.xml   # NF-e 4.00 completa (valores redondos p/ assert fácil)
    ├── nfe_cancelled.xml    # Com protNFe cStat=101
    ├── nfe_invalid.xml      # Malformado (tag não fechada)
    └── nfe_not_nfe.xml      # Namespace diferente (ex: NFS-e)
```

**Princípios**:
- Zero dados reais — CNPJs `00.000.000/0000-00`, nomes genéricos
- Unitários puros (sem I/O) > 80% coverage
- Integração com fixtures estáticas
- Snapshot de PDF via `pdfminer.six` (compara texto extraído)

---

## ⚙️ Configuração

Arquivo: `%APPDATA%\nfe2pdf\config.yaml` (criado no primeiro run)

```yaml
danfe:
  layout: "auto"                    # auto | nt_2026_010 | moc_7_0
  logo: null                        # caminho absoluto .png/.jpg ou null
  margins: {top: 5, right: 5, bottom: 5, left: 5}
  font_type: "times"                # times | courier
  font_size: "small"                # small | big
  tax_configuration: "standard_icms_ipi"
  invoice_display: "full_details"
  display_pis_cofins: false
  watermark_cancelled: true
  # ... demais opções espelham BrazilFiscalReport.DanfeConfig

logging:
  level: "INFO"
  file: null
  rotation: "10 MB"
  retention: "7 days"

output:
  default_dir: null                 # null = mesma pasta do XML
  overwrite: false
```

**Override via Environment Variables** (útil para automação/CI):
```powershell
$env:NFE2PDF_DANFE__LAYOUT = "nt_2026_010"
$env:NFE2PDF_DANFE__LOGO = "C:\Logos\empresa.png"
$env:NFE2PDF_LOGGING__LEVEL = "DEBUG"
```

---

## 📦 Build & Distribuição

### Executável (PyInstaller)
```bash
python scripts/build_exe.py
# Gera: dist/nfe2pdf.exe (~15-20 MB)
# Inclui: --onefile, --noconsole, --add-data assets/logo.png, --hidden-import brazilfiscalreport.*
```

### Instalador (Inno Setup)
```bash
iscc scripts/build_installer.iss
# Gera: dist/nfe2pdf-setup.exe (~20 MB)
# Tasks: associate_xml, desktop_icon
# Run: nfe2pdf.exe --install-association (pós-install)
```

---

## 🔒 Licenciamento

| Componente | Licença | Implicação Prática |
|------------|---------|-------------------|
| **Nosso código** | [MIT](LICENSE) | Uso comercial livre, modificação, distribuição |
| **BrazilFiscalReport** | LGPL-3.0 | Executável final é **obra derivada combinada** → herda LGPL |

**O que isso significa**:
- ✅ Pode usar, vender, modificar o instalador comercialmente
- ✅ Dynamic linking do Python já satisfaz "permite relink" da LGPL
- ⚠️ Instalador **deve** incluir `LGPL-3.0.txt` + nota de que a lib pode ser substituída
- ⚠️ Não pode ofuscar/estaticamente linkar a lib de forma que impeça substituição

> Decisão arquitetural: `BFRAdapter` isola a dependência LGPL atrás de `PDFGenerator` (Strategy Pattern). Migração futura para `reportlab` (BSD-3-Clause) remove restrição LGPL do executável.

---

## 🤝 Contribuindo

1. Fork → Branch (`feat/nova-feature` ou `fix/corrigir-bug`)
2. `ruff check . && mypy src/nfe2pdf && pytest` — CI deve passar
3. Commits **Conventional Commits**: `feat:`, `fix:`, `test:`, `build:`, `docs:`, `chore:`, `refactor:`
4. PR para `main` — revisão + CI verde → merge squash

---

## 📚 Recursos Oficiais

| Documento | Finalidade |
|-----------|------------|
| [Portal NF-e - Layouts](https://www.nfe.fazenda.gov.br/portal/principal.aspx) | XSDs oficiais NF-e 4.00 |
| [Manual DANFE NT 2026.010](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=9hd38oni4aU=) | Regras de layout obrigatório (dez/2026+) |
| [BrazilFiscalReport GitHub](https://github.com/Engenere/BrazilFiscalReport) | Source, issues, exemplos da lib |
| [lxml XPath + Namespaces](https://lxml.de/xpathxslt.html) | Parsing robusto do XML NF-e |

---

## 📞 Autor

**Adriano Lucas** — Engenheiro de Software  
🔗 GitHub: [@adrianolucasdc](https://github.com/adrianolucasdc)  
💼 LinkedIn: [linkedin.com/in/adrianolucasdc](https://linkedin.com/in/adrianolucasdc)

---

> **Este projeto nasceu de uma dor real de escritórios de contabilidade.**  
> Se você já perdeu tempo abrindo XML no navegador para "imprimir como PDF", esta ferramenta é para você.