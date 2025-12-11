# Data Directory

This directory contains all data files for the project.

## Structure

- `raw/` - Original, immutable data
- `processed/` - Cleaned and transformed data ready for analysis
- `external/` - Data from external sources

## Guidelines

- Never modify files in the `raw/` directory
- Document data sources and transformations
- Use version control for small datasets
- For large datasets, consider using data versioning tools like DVC
