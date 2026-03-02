"""
his module contains all the business and integrity expectations
for the stream  of credit card transactions.

Rules are divided into logical domains to facilitate auditing
and maintenance by the data engineering and fraud strategy teams.
"""


def get_identity_and_time_rules():
    """
    Rules to ensure primary identifiers, foreign keys, and temporal boundaries 
    are present and logically valid for downstream joins and aggregations.
    """
    return [
        {
            "name": "valid_transaction_id",
            "constraint": "transaction_id IS NOT NULL",
            "tag": "transactions"
        },
        {
            "name": "valid_customer_id",
            "constraint": "customer_id IS NOT NULL",
            "tag": "transactions"
        },
        {
            "name": "valid_merchant_id",
            "constraint": "merchant_id IS NOT NULL",
            "tag": "transactions"
        },
        {
            "name": "valid_timestamp",
            "constraint": "timestamp IS NOT NULL",
            "tag": "transactions"
        }
    ]


def get_financial_and_amount_rules():
    """
    Rules to validate the monetary values associated with the transaction.
    """
    return [
        {
            "name": "valid_amount",
            "constraint": "amount IS NOT NULL AND amount > 0 AND amount < 1000000",
            "tag": "transactions"
        }
    ]


def get_contextual_and_categorical_rules():
    """
    Rules to validate categorical indicators, binary security flags,
    and geographical consistency.
    """
    return [
        {
            "name": "valid_currency",
            "constraint": "currency IS NOT NULL AND length(currency) = 3",
            "tag": "transactions"
        },
        {
            "name": "valid_mcc_category",
            "constraint": "mcc_category IS NULL OR mcc_category IN ('grocery', 'restaurant', 'fuel', 'travel', 'ecommerce', 'electronics', 'healthcare', 'entertainment', 'utilities', 'atm_withdrawal', 'money_transfer')",
            "tag": "transactions"
        },
        {
            "name": "valid_mcc_code",
            "constraint": "mcc_code > 0 AND mcc_code <= 9999",
            "tag": "transactions"
        },
        {
            "name": "valid_merchant_country",
            "constraint": "merchant_country IS NULL OR length(merchant_country) = 2",
            "tag": "transactions"
        },
        {
            "name": "valid_cross_border_flag",
            "constraint": "cross_border IS NULL OR cross_border IN (0, 1)",
            "tag": "transactions"
        },
        {
            "name": "consistent_cross_border",
            "constraint": "(cross_border = 0) OR ((cross_border = 1) AND merchant_country IS NOT NULL) OR cross_border IS NULL",
            "tag": "transactions"
        },
        {
            "name": "valid_payment_method",
            "constraint": "payment_method IS NULL OR payment_method IN ('chip', 'contactless', 'online', 'swipe', 'atm', 'manual_entry')",
            "tag": "transactions"
        },
        {
            "name": "valid_device_type",
            "constraint": "device_type IS NULL OR device_type IN ('mobile', 'desktop', 'pos_terminal', 'atm', 'unknown')",
            "tag": "transactions"
        },
        {
            "name": "valid_ip_country_match_flag",
            "constraint": "ip_country_match IS NULL OR ip_country_match IN (0, 1)",
            "tag": "transactions"
        },
        {
            "name": "valid_device_fingerprint_flag",
            "constraint": "device_fingerprint_known IS NULL OR device_fingerprint_known IN (0, 1)",
            "tag": "transactions"
        },
        {
            "name": "valid_tor_vpn_flag",
            "constraint": "is_tor_or_vpn IS NULL OR is_tor_or_vpn IN (0, 1)",
            "tag": "transactions"
        },
        {
            "name": "valid_security_results",
            "constraint": "three_ds_result IS NULL OR three_ds_result IN ('success', 'failed', 'not_attempted', 'bypass')",
            "tag": "transactions"
        }
    ]


def get_transaction_rules():
    """
    Main entry point for transaction data quality expectations.

    Aggregates all specific rule groups into a single list of dictionaries.
    """
    all_tx_rules = []
    all_tx_rules.extend(get_identity_and_time_rules())
    all_tx_rules.extend(get_financial_and_amount_rules())
    all_tx_rules.extend(get_contextual_and_categorical_rules())
    
    return all_tx_rules
