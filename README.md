# disco-baa-01

A data science project for sheep-related data analysis.

## Project Structure

```
disco-baa-01/
├── data/
│   ├── raw/              # Original, immutable data
│   ├── processed/        # Cleaned and transformed data
│   └── external/         # External data sources
├── notebooks/
│   └── exploratory_analysis.ipynb  # Jupyter notebooks for exploration
├── src/
│   └── disco_baa_01/     # Source code for the project
│       ├── __init__.py
│       └── utils.py      # Utility functions
├── tests/                # Unit tests
│   └── test_utils.py
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or conda for package management

### Installation

1. Clone the repository:
```bash
git clone https://github.com/oakla/disco-baa-01.git
cd disco-baa-01
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode (recommended for development):
```bash
pip install -e .
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running Jupyter Notebooks

```bash
jupyter notebook notebooks/
```

### Running Tests

```bash
pytest tests/
```

## Development

### Code Formatting

This project uses Black for code formatting:
```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

## Features

- Data loading and processing utilities
- Jupyter notebook templates for exploratory data analysis
- Unit tests for code validation
- Structured project organization following best practices

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

## License

This project is open source and available under the MIT License. 
