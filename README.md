# AI Software Appraiser

An AI-powered tool for evaluating software quality, maintainability, and value.

## Features

- **Code Quality Analysis**: Evaluate individual code files for best practices, style, and potential issues
- **Project Evaluation**: Comprehensive analysis of entire software projects
- **Multi-language Support**: Works with multiple programming languages
- **API First**: Built with FastAPI for easy integration with other tools
- **Extensible**: Add custom evaluation rules and metrics

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-software-appraiser.git
   cd ai-software-appraiser
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Install development dependencies (optional):
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

### Command Line

```bash
# Evaluate a single file
python -m app.cli evaluate-code path/to/file.py

# Evaluate a project directory
python -m app.cli evaluate-project path/to/project
```

### Python API

```python
from app.core.appraiser import SoftwareAppraiser

# Initialize the appraiser
appraiser = SoftwareAppraiser()

# Evaluate a piece of code
report = appraiser.evaluate_code_quality("def hello():\n    print('Hello, World!')")

# Evaluate an entire project
evaluation = appraiser.evaluate_project("/path/to/project")
```

### Web API

Start the FastAPI server:

```bash
uvicorn app.api.app:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive API documentation.

## Project Structure

```
ai-software-appraiser/
├── app/
│   ├── core/           # Core functionality
│   ├── models/         # Data models
│   ├── utils/          # Utility functions
│   └── api/            # FastAPI application
├── tests/              # Test files
├── data/               # Sample data and resources
├── docs/               # Documentation
├── pyproject.toml      # Project configuration
└── README.md
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- All contributors and users of AI Software Appraiser
