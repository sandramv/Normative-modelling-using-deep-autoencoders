#!/usr/bin/env python3
"""Script to create an homogeneous sample for the ADNI dataset.

Labels encoding
"1": "Healthy Controls",
"27": "Early mild cognitive impairment (EMCI)"
"28": "Late mild cognitive impairment (LMCI)"
"17": "Alzheimer's Disease",

excluded (low number of subjects)
"18": "Mild Cognitive Impairment"

excluded (not the focus of the study)
"26": "Significant Memory Concern (SMC)"
"""
from pathlib import Path

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind, f_oneway

from utils import load_dataset

PROJECT_ROOT = Path.cwd()


def main():
    """Verify age and gender balance along the groups from the ADNI dataset."""
    # ----------------------------------------------------------------------------------------
    dataset_name = 'ADNI'

    participants_path = PROJECT_ROOT / 'data' / dataset_name / 'participants.tsv'
    freesurfer_path = PROJECT_ROOT / 'data' / dataset_name / 'freesurferData.csv'

    # ----------------------------------------------------------------------------------------
    outputs_dir = PROJECT_ROOT / 'outputs'
    ids_path = outputs_dir / (dataset_name + '_cleaned_ids.csv')

    dataset_df = load_dataset(participants_path, ids_path, freesurfer_path)
    print(dataset_df.groupby('Diagn').count())

    contingency_table = pd.crosstab(dataset_df.Gender, dataset_df.Diagn)

    _, p_value, _, _ = chi2_contingency(contingency_table[[1, 17]], correction=False)
    print('Gender - HC vs AD p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[1, 26]], correction=False)
    print('Gender - HC vs SMC p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[1, 27]], correction=False)
    print('Gender - HC vs EMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[1, 28]], correction=False)
    print('Gender - HC vs LMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[17, 26]], correction=False)
    print('Gender - AD vs SMC p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[17, 27]], correction=False)
    print('Gender - AD vs EMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[17, 28]], correction=False)
    print('Gender - AD vs LMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[26, 27]], correction=False)
    print('Gender - SMC vs EMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[26, 28]], correction=False)
    print('Gender - SMC vs LMCI p value {}'.format(p_value))
    _, p_value, _, _ = chi2_contingency(contingency_table[[27, 28]], correction=False)
    print('Gender - EMCI vs LMCI p value {}'.format(p_value))

    hc_age = dataset_df[dataset_df['Diagn'] == 1].Age.values
    ad_age = dataset_df[dataset_df['Diagn'] == 17].Age.values
    smc_age = dataset_df[dataset_df['Diagn'] == 26].Age.values
    emci_age = dataset_df[dataset_df['Diagn'] == 27].Age.values
    lmci_age = dataset_df[dataset_df['Diagn'] == 28].Age.values

    _, p_value = ttest_ind(hc_age, ad_age)
    print('Age - HC vs AD p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, smc_age)
    print('Age - HC vs SMC p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, emci_age)
    print('Age - HC vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, lmci_age)
    print('Age - HC vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, smc_age)
    print('Age - AD vs SMC p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, emci_age)
    print('Age - AD vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, lmci_age)
    print('Age - AD vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(smc_age, emci_age)
    print('Age - SMC vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(smc_age, lmci_age)
    print('Age - SMC vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(emci_age, lmci_age)
    print('Age - EMCI vs LMCI p value {}'.format(p_value))

    print(hc_age.mean())
    print(ad_age.mean())
    print(smc_age.mean())
    print(emci_age.mean())
    print(lmci_age.mean())

    # emci is too young, dropping some of the youngest
    print(emci_age.argmin())
    print(dataset_df[dataset_df['Diagn'] == 27].iloc[emci_age.argmin()].Age)
    print(dataset_df[dataset_df['Diagn'] == 27].iloc[emci_age.argmin()].name)
    print('')

    dataset_corrected_df = dataset_df.drop(dataset_df[dataset_df['Diagn'] == 27].iloc[emci_age.argmin()].name, axis=0)
    emci_age = np.delete(emci_age, emci_age.argmin(), 0)

    for _ in range(24):
        print(emci_age.argmin())
        print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 27].iloc[emci_age.argmin()].Age)
        print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 27].iloc[emci_age.argmin()].name)
        print(emci_age)
        print('')
        dataset_corrected_df = dataset_corrected_df.drop(
            dataset_corrected_df[dataset_corrected_df['Diagn'] == 27].iloc[emci_age.argmin()].name, axis=0)
        emci_age = np.delete(emci_age, emci_age.argmin(), 0)
        dataset_corrected_df = dataset_corrected_df.reset_index(drop=True)

    # lmci is too young, dropping some of the youngest
    print(lmci_age.argmin())
    print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].Age)
    print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].name)
    print('')

    dataset_corrected_df = dataset_corrected_df.drop(
        dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].name, axis=0)
    lmci_age = np.delete(lmci_age, lmci_age.argmin(), 0)

    for _ in range(8):
        print(lmci_age.argmin())
        print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].Age)
        print(dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].name)
        print(lmci_age)
        print('')
        dataset_corrected_df = dataset_corrected_df.drop(
            dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].iloc[lmci_age.argmin()].name, axis=0)
        lmci_age = np.delete(lmci_age, lmci_age.argmin(), 0)
        dataset_corrected_df = dataset_corrected_df.reset_index(drop=True)

    _, p_value = ttest_ind(hc_age, ad_age)
    print('Age - HC vs AD p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, smc_age)
    print('Age - HC vs SMC p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, emci_age)
    print('Age - HC vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(hc_age, lmci_age)
    print('Age - HC vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, smc_age)
    print('Age - AD vs SMC p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, emci_age)
    print('Age - AD vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(ad_age, lmci_age)
    print('Age - AD vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(smc_age, emci_age)
    print('Age - SMC vs EMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(smc_age, lmci_age)
    print('Age - SMC vs LMCI p value {}'.format(p_value))
    _, p_value = ttest_ind(emci_age, lmci_age)
    print('Age - EMCI vs LMCI p value {}'.format(p_value))

    hc_age = dataset_corrected_df[dataset_corrected_df['Diagn'] == 1].Age.values
    ad_age = dataset_corrected_df[dataset_corrected_df['Diagn'] == 17].Age.values
    emci_age = dataset_corrected_df[dataset_corrected_df['Diagn'] == 27].Age.values
    lmci_age = dataset_corrected_df[dataset_corrected_df['Diagn'] == 28].Age.values

    contingency_table = pd.crosstab(dataset_corrected_df.Gender, dataset_corrected_df.Diagn)
    print(chi2_contingency(contingency_table, correction=False))
    print(f_oneway(hc_age, ad_age, emci_age, lmci_age))

    homogeneous_df = pd.DataFrame(dataset_corrected_df[dataset_corrected_df['Diagn'].isin([1, 17, 27, 28])].Image_ID)
    homogeneous_df.to_csv(outputs_dir / (dataset_name + '_homogeneous_ids.csv'), index=False)


if __name__ == "__main__":
    main()