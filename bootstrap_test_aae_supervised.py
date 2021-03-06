#!/usr/bin/env python3
"""Inference the predictions of the clinical datasets using the supervised model."""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tqdm import tqdm

from utils import COLUMNS_NAME, load_dataset

PROJECT_ROOT = Path.cwd()


def main(dataset_name):
    """Make predictions using trained normative models."""
    # ----------------------------------------------------------------------------
    n_bootstrap = 1000
    model_name = 'supervised_aae'

    participants_path = PROJECT_ROOT / 'data' / dataset_name / 'participants.tsv'
    freesurfer_path = PROJECT_ROOT / 'data' / dataset_name / 'freesurferData.csv'

    # ----------------------------------------------------------------------------
    # Create directories structure
    outputs_dir = PROJECT_ROOT / 'outputs'
    bootstrap_dir = outputs_dir / 'bootstrap_analysis'
    model_dir = bootstrap_dir / model_name
    ids_path = outputs_dir / (dataset_name + '_homogeneous_ids.csv')

    # ----------------------------------------------------------------------------
    # Set random seed
    random_seed = 42
    tf.random.set_seed(random_seed)
    np.random.seed(random_seed)

    # ----------------------------------------------------------------------------
    for i_bootstrap in tqdm(range(n_bootstrap)):
        bootstrap_model_dir = model_dir / '{:03d}'.format(i_bootstrap)

        output_dataset_dir = bootstrap_model_dir / dataset_name
        output_dataset_dir.mkdir(exist_ok=True)

        # ----------------------------------------------------------------------------
        # Loading data
        clinical_df = load_dataset(participants_path, ids_path, freesurfer_path)

        x_dataset = clinical_df[COLUMNS_NAME].values

        tiv = clinical_df['EstimatedTotalIntraCranialVol'].values
        tiv = tiv[:, np.newaxis]

        x_dataset = (np.true_divide(x_dataset, tiv)).astype('float32')
        # ----------------------------------------------------------------------------
        encoder = keras.models.load_model(bootstrap_model_dir / 'encoder.h5', compile=False)
        decoder = keras.models.load_model(bootstrap_model_dir / 'decoder.h5', compile=False)

        scaler = joblib.load(bootstrap_model_dir / 'scaler.joblib')

        enc_age = joblib.load(bootstrap_model_dir / 'age_encoder.joblib')
        enc_gender = joblib.load(bootstrap_model_dir / 'gender_encoder.joblib')

        # ----------------------------------------------------------------------------
        x_normalized = scaler.transform(x_dataset)

        normalized_df = pd.DataFrame(columns=['participant_id'] + COLUMNS_NAME)
        normalized_df['participant_id'] = clinical_df['participant_id']
        normalized_df[COLUMNS_NAME] = x_normalized
        normalized_df.to_csv(output_dataset_dir / 'normalized.csv', index=False)

        # ----------------------------------------------------------------------------
        age = clinical_df['Age'].values[:, np.newaxis].astype('float32')
        one_hot_age = enc_age.transform(age)

        gender = clinical_df['Gender'].values[:, np.newaxis].astype('float32')
        one_hot_gender = enc_gender.transform(gender)

        y_data = np.concatenate((one_hot_age, one_hot_gender), axis=1).astype('float32')

        # ----------------------------------------------------------------------------
        encoded = encoder(x_normalized, training=False)
        reconstruction = decoder(tf.concat([encoded, y_data], axis=1), training=False)

        reconstruction_df = pd.DataFrame(columns=['participant_id'] + COLUMNS_NAME)
        reconstruction_df['participant_id'] = clinical_df['participant_id']
        reconstruction_df[COLUMNS_NAME] = reconstruction.numpy()
        reconstruction_df.to_csv(output_dataset_dir / 'reconstruction.csv', index=False)

        encoded_df = pd.DataFrame(columns=['participant_id'] + list(range(encoded.shape[1])))
        encoded_df['participant_id'] = clinical_df['participant_id']
        encoded_df[list(range(encoded.shape[1]))] = encoded.numpy()
        encoded_df.to_csv(output_dataset_dir / 'encoded.csv', index=False)

        # ----------------------------------------------------------------------------
        reconstruction_error = np.mean((x_normalized - reconstruction) ** 2, axis=1)

        reconstruction_error_df = pd.DataFrame(columns=['participant_id', 'Reconstruction error'])
        reconstruction_error_df['participant_id'] = clinical_df['participant_id']
        reconstruction_error_df['Reconstruction error'] = reconstruction_error
        reconstruction_error_df.to_csv(output_dataset_dir / 'reconstruction_error.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--dataset_name',
                        dest='dataset_name',
                        help='Dataset name to calculate deviations.')
    args = parser.parse_args()

    main(args.dataset_name)