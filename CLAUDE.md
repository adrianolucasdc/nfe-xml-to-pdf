# CLAUDE.md — Diretrizes de Desenvolvimento e Arquitetura

Manual técnico com as regras de arquitetura, padrões de código, comandos de verificação e decisões de empacotamento deste repositório.

---

## Objetivo Técnico

Utilitário desktop Windows para converter arquivos XML de NF-e (v4.00) em PDF (DANFE) via linha de comando ou duplo-clique ("Abrir com...").

---

## Arquitetura (Clean Architecture Pragmática)

```text
src/nfe2pdf/
├── domain/                  # Regras de negócio puras (sem dependências de I/O)
│   ├── models.py            # Modelos Pydantic v2: NFeData, Emit, Dest, Prod
│   ├── exceptions.py        # InvalidXmlError, NotNFeError, PDFGenerationError
│   └── ports.py             # Interfaces (Protocols/ABCs): XMLParser, PDFGenerator
├── application/             # Casos de uso e orquestração
│   ├── use_cases.py         # GenerateDanfeUseCase, InstallAssociationUseCase
│   └── dto.py               # Objetos de entrada e saída dos casos de uso
├── infrastructure/          # Implementações concretas (detalhes externos)
│   ├── pdf/
│   │   ├── base.py          # Interface base (Strategy Pattern)
│   │   └── bfr_adapter.py   # Adapter para BrazilFiscalReport (LGPL-3.0)
│   ├── xml/
│   │   ├── parser.py        # Leitura com lxml e tratamento de namespaces NF-e
│   │   └── validator.py     # Validação estrutural básica antes de gerar o PDF
│   └── windows/
│       ├── registry.py      # Associação de .xml via HKEY_CURRENT_USER
│       └── installer.py     # Template/script para Inno Setup
├── cli.py                   # Entrypoint Click (CLI + suporte a "Abrir com...")
├── config.py                # Configurações via Pydantic Settings (YAML + env)
└── utils/paths.py           # Resolução de caminhos (AppData, _MEIPASS)
```

### Regras de Dependência

- **Domain** não importa nada de `application`, `infrastructure` ou `cli`.
- **Infrastructure** implementa os contratos definidos em `domain/ports.py`.
- A biblioteca de geração de PDF fica isolada atrás do `BFRAdapter` para evitar acoplamento direto do núcleo da aplicação com terceiros.

---

## Stack e Ferramentas

- **Python 3.11+**: `tomllib` nativo e tipagem moderna.
- **Pydantic v2**: Validação de dados extraídos do XML e gerenciamento de configurações.
- **lxml**: Parsing de XML com suporte eficiente a XPath e namespaces.
- **BrazilFiscalReport**: Motor de renderização do DANFE oficial.
- **Click**: Construção da CLI.
- **PyInstaller & Inno Setup**: Empacotamento em `.exe` standalone e instalador Windows.
- **Ruff, mypy & pytest**: Linting/formatação, checagem estática de tipos e testes automatizados.

---

## Comandos de Verificação

Executar antes de realizar qualquer commit:

```bash
# Lint e formatação
ruff check . --fix && ruff format .

# Checagem de tipos
mypy src/nfe2pdf

# Testes unitários e de integração
pytest -q

# Build local do executável
python scripts/build_exe.py
```

---

## Comportamento Crítico no Windows (CLI vs. Duplo-Clique)

1. **Argumento Direto ("Abrir com..."):** Quando o Windows abre um `.xml` associado ao executável, ele invoca `nfe2pdf.exe "C:\caminho\nota.xml"` sem subcomando. O `cli.py` deve aceitar tanto `nfe2pdf generate arquivo.xml` quanto `nfe2pdf arquivo.xml` diretamente.
2. **Modo `--noconsole`:** Como o `.exe` roda sem janela de terminal para não poluir a tela do usuário, exceções fatais durante o duplo-clique devem exibir um alerta visual nativo (`ctypes.windll.user32.MessageBoxW`) em vez de falhar silenciosamente.
3. **Registro sem Admin:** A associação de extensão `.xml` deve gravar em `HKEY_CURRENT_USER\Software\Classes` para funcionar em computadores corporativos sem exigir privilégios de administrador.

---

## Regras de Testes e Segurança de Dados

- **Zero Dados Reais:** Nunca commitar XMLs de empresas ou clientes reais. O `.gitignore` bloqueia `*.xml` na raiz.
- **Fixtures Anonimizadas:** Todos os arquivos em `tests/fixtures/` devem usar CNPJs fictícios (`00.000.000/0000-00`), chaves de acesso zeradas e valores redondos.
- **Estrutura de Testes:**
  - `tests/unit/`: Testa modelos Pydantic, regras de parsing e casos de uso com mocks (sem tocar no disco).
  - `tests/integration/`: Testa o fluxo completo de ponta a ponta (XML fixture -> PDF gerado -> extração de texto com `pdfminer.six`).

---

## Notas Técnicas e Licenciamento

- **Particularidades da `BrazilFiscalReport`:** A classe `Danfe(xml=...)` exige `bytes` (não `str`), e `output()` retorna `bytes` em memória — o salvamento em disco é responsabilidade da camada de aplicação/infraestrutura.
- **PyInstaller (`_MEIPASS`):** Usar `utils/paths.py` para resolver caminhos de assets (como logo padrão) tanto em ambiente de desenvolvimento quanto dentro do binário empacotado.
- **Conformidade LGPL-3.0:** O código deste repositório é **MIT**, mas a dependência `BrazilFiscalReport` é **LGPL-3.0**. O instalador deve incluir ambos os arquivos de licença (`LICENSE` e `LGPL-3.0.txt`), e o `README.md` deve manter as instruções claras de build para permitir recompilação com versões modificadas da dependência.

---

## Padrão de Git

- Utilizar **Conventional Commits** em inglês (`feat:`, `fix:`, `test:`, `refactor:`, `build:`, `docs:`, `chore:`).
- Commits pequenos e atômicos, sempre com `ruff`, `mypy` e `pytest` passando antes do commit.
- **Regra obrigatória:** Commits **só devem ser feitos com solicitação explícita do usuário**. Não commitar automaticamente após criar/modificar arquivos — aguardar o comando "faça o commit" ou similar.

---

## Fluxo de Trabalho com IA (Claude Code)

1. **Análise e planejamento** → Apresentar plano detalhado (estrutura, arquitetura, lista de commits)
2. **Execução por etapas** → Criar arquivos da etapa atual
3. **Validação** → Rodar linters, type checker, testes
4. **Aprovação do usuário** → "Pode fazer o commit da etapa X?"
5. **Commit** → `git add . && git commit -m "tipo: mensagem"` (Conventional Commits)
6. **Próxima etapa** → Repetir