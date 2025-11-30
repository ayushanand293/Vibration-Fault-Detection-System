# Vibration Fault Detection Machine Learning Module

This directory contains the machine learning components of the Vibration Fault Detection project. The machine learning module is responsible for training, evaluating, and utilizing models to detect faults based on vibration data.

## Directory Structure

- **data/**: Contains datasets used for training and evaluation. This directory is currently empty and is kept for version control.
- **models/**: This directory is intended to store trained machine learning models. It is currently empty and is kept for version control.
- **notebooks/**: Contains Jupyter notebooks for training and evaluating machine learning models. The `training.ipynb` notebook includes code for data loading, preprocessing, and model evaluation.
- **src/**: Contains the source code for the machine learning module.
  - **train.py**: Logic for training machine learning models, including RandomForest and 1D CNN or MLP.
  - **evaluate.py**: Implements evaluation metrics and confusion matrix generation for the trained models.
  - **features.py**: Functions for feature extraction from the vibration data.

## Setup Instructions

1. **Install Dependencies**: Navigate to the `ml` directory and install the required packages using:
   ```
   pip install -r requirements.txt
   ```

2. **Training the Model**: Use the `training.ipynb` notebook to train the machine learning models. Follow the instructions within the notebook for data loading and preprocessing.

3. **Evaluating the Model**: After training, use the `evaluate.py` script to assess the performance of the trained models.

4. **Feature Extraction**: Utilize the functions in `features.py` to extract relevant features from new vibration data for prediction.

## Usage

Once the models are trained and evaluated, they can be integrated with the FastAPI backend for real-time fault detection. The trained models will be loaded in the backend to make predictions based on incoming vibration data.

## Contribution

Contributions to improve the machine learning module are welcome. Please follow the project's contribution guidelines for submitting changes or enhancements.