# Pharmacy Data Analysis Project

A comprehensive Python project for analyzing pharmacy data through API integration and exploratory data analysis (EDA). This project demonstrates effective data fetching from public APIs, robust error handling with fallback mechanisms, and insightful visualizations of drug enforcement reports.

## Features

- **API Integration**: Fetches real-time drug enforcement data from the openFDA API
- **Fallback System**: Includes sample data fallback when API is unavailable
- **Data Analysis**: Performs exploratory data analysis with visualizations
- **Error Handling**: Robust debugging and error resolution capabilities
- **Professional Structure**: Well-organized codebase with clear documentation

## Project Structure

```
pharmacy_data/
├── api_utils.py          # API fetching utilities
├── eda_script.py         # Main EDA script
├── eda_notebook.ipynb    # Jupyter notebook version
├── test_api.py          # API testing module
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore         # Git ignore rules
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/robert-nextmoveso/pharmacy-data-analysis.git
cd pharmacy-data-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the EDA Script
```bash
python eda_script.py
```

### Running the Jupyter Notebook
```bash
jupyter notebook eda_notebook.ipynb
```

### Testing the API
```bash
python test_api.py
```

## API Integration

The project integrates with the [openFDA Drug Enforcement API](https://open.fda.gov/apis/drug/enforcement/) to fetch drug recall and enforcement data. Key features:

- Dynamic date range filtering
- Configurable data limits
- Automatic data transformation and cleaning
- Fallback to sample data on API failure

## Data Analysis

The EDA includes:
- Time series analysis of drug recalls
- Product category analysis
- Correlation analysis
- Interactive visualizations using Plotly
- Statistical summaries

## Dependencies

- pandas
- numpy
- matplotlib
- seaborn
- plotly
- requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Robert - [GitHub Profile](https://github.com/robert-nextmoveso)

## Acknowledgments

- Data provided by [openFDA](https://open.fda.gov/)
- Built with Python data science stack