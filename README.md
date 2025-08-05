# AI-Course-Generator 🤖🎓

Create full-fledged **Bitcoin SV** courses — from outline to polished DOCX/PDF — in a single command.

---

## ✨ Key Features
- **Standardised AI facade** — switch between OpenAI, Anthropic, Cohere with one flag.
- **Prompt-engineering pipeline** — central templates & rules ensure consistent pedagogy.
- **Knowledge-base integration** — pull authoritative BSV material through MCP endpoints.
- **Markdown → DOCX/PDF** — ready-to-publish hand-outs with optional corporate template.
- **Validation & QA** — offline linting catches structural issues before you ship.

---

## 📂 Project Layout
ai-course-generator/
├─ src/
│ ├─ api/ # Provider adapters + unified facade
│ ├─ core/ # Prompt builder, rule engine, generator
│ ├─ converters/ # Markdown → Word/PDF
│ ├─ templates/ # Course skeletons & Word template
│ ├─ utils/ # Filesystem, scraping, MCP client
│ └─ mcp_integration/ # Knowledge-base sync layer
├─ config/ # YAML prompt & source configs
├─ generated_courses/ # Default output folder (git-ignored)
├─ main.py # CLI entry-point
└─ requirements.txt

---

## 🚀 Quick Start

### 1 . Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

### 2 . Add your API keys
Either export variables or create a `.env` file:
OPENAY_API_KEY=sk-...
ANTHROPIC_API_KEY=...
COHERE_API_KEY=...
DEFAULT_PROVIDER=openai

### 3 . Prepare a course YAML
See `config/bsv_sources.yaml` for a full example. Minimal stub:
course_name: "Bitcoin SV Fundamentals"
topic: "Bitcoin SV basics"
duration: "4 weeks"
difficulty_level: "beginner"

### 4 . Generate!
python main.py my_course.yaml
- provider openai
- docx-template src/templates/word_templates/course_template.docx

Outputs:
generated_courses/
└─ bitcoin_sv_fundamentals.md
└─ bitcoin_sv_fundamentals.docx
└─ bitcoin_sv_fundamentals.pdf # if Pandoc available

---

## ⚙️ Advanced Usage
* **Skip PDF**: `--no-pdf`
* **Custom output dir**: `-o dist/`
* **Debug logs**: `--debug`
* **Switch provider**: `--provider anthropic`

---

## 🤝 Contributing
1. Fork & clone repository.
2. `pre-commit install` to enable linting hooks.
3. Follow the existing coding style (`ruff`, `black`, type-annotated).
4. PRs should include unit tests for new functionality.

---

## 🛡️ License
Apache-2.0. See `LICENSE` file for details.

---

> *Made with ❤️ & Satoshis.*

