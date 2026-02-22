"""
Fraud labels data quality rules: This module contains the business and
integrity expectations for the delayed  fraud confirmation feedback.

It ensures that the labels can be successfully joined back to their
original transactions and that the fraud indicators are valid.
"""


def get_identity_rules():
    """
    Rules to ensure the primary identifier is present.

    Without a valid transaction identifier, a label is useless
    as it cannot be joined  to our features for model training.
    """
    return [
        {
            "name": "valid_lbl_tx_id",
            "constraint": "transaction_id IS NOT NULL",
            "tag": "labels"
        }
    ]


def get_feedback_integrity_rules():
    """
    Rules to validate the actual feedback content: ensuring the fraud
    indicator is a strict binary value and that the availability date is
    logically sound.
    """
    return [
        {
            "name": "valid_fraud_flag",
            "constraint": "is_fraud IS NOT NULL AND is_fraud IN (0, 1)",
            "tag": "labels"
        },
        {
            "name": "valid_lbl_date",
            "constraint": "label_available_date IS NOT NULL",
            "tag": "labels"
        }
    ]


def get_label_rules():
    """
    Main entry point for fraud labels data quality expectations.

    Aggregates all specific rule groups into a single list of dictionaries.
    """
    all_label_rules = []
    all_label_rules.extend(get_identity_rules())
    all_label_rules.extend(get_feedback_integrity_rules())
    
    return all_label_rules