"""
This module contains all the business and integrity expectations for customer
master data.

Rules are divided into logical business domains for easier maintenance and
auditing.
"""


###############################################################################
# Functions
###############################################################################

def get_identity_and_time_rules():
    """
    Rules to ensure primary identifiers and temporal keys are present.
    """
    return [
        {
            "name": "valid_customer_id",
            "constraint": "customer_id IS NOT NULL",
            "tag": "customers"
        },
        {
            "name": "valid_updated_at",
            "constraint": "customer_updated_at IS NOT NULL",
            "tag": "customers"
        },
        {
            "name": "valid_join_date",
            "constraint": "join_date IS NOT NULL",
            "tag": "customers"
        }
    ]


def get_demographic_rules():
    """
    Rules to validate the demographic profile of the customer, ensuring values 
    fall into expected categories and are mathematically consistent.
    """
    return [
        {
            "name": "valid_age",
            "constraint": "age IS NULL OR (age >= 18 AND age <= 100)",
            "tag": "customers"
        },
        {
            "name": "valid_gender",
            "constraint": "gender IS NULL OR gender IN ('M', 'F', 'O')",
            "tag": "customers"
        },
        {
            "name": "valid_country",
            "constraint": "country IS NULL OR length(country) = 2",
            "tag": "customers"
        },
        {
            "name": "valid_state_and_city",
            "constraint": "city_tier IS NULL OR city_tier IN (1, 2, 3)",
            "tag": "customers"
        },
        {
            "name": "valid_occupation",
            "constraint": "occupation IS NULL OR length(occupation) > 0",
            "tag": "customers"
        }
    ]


def get_financial_and_account_rules():
    """
    Rules to validate the financial standing and the banking products
    associated with the customer.
    """
    return [
        {
            "name": "valid_income_bracket",
            "constraint": "income_bracket IS NULL OR income_bracket IN ('<25k', '25k-50k', '50k-75k', '75k-100k', '100k-150k', '>150k')",
            "tag": "customers"
        },
        {
            "name": "valid_customer_segment",
            "constraint": "customer_segment IS NULL OR customer_segment IN ('standard', 'premium', 'vip', 'student', 'business')",
            "tag": "customers"
        },
        {
            "name": "valid_card_type",
            "constraint": "card_type IS NULL OR card_type IN ('visa', 'mastercard', 'amex', 'discover')",
            "tag": "customers"
        },
        {
            "name": "valid_credit_score",
            "constraint": "credit_score IS NULL OR (credit_score >= 300 AND credit_score <= 850)",
            "tag": "customers"
        },
        {
            "name": "valid_cards_issued",
            "constraint": "num_cards_issued IS NULL OR num_cards_issued >= 0",
            "tag": "customers"
        },
        {
            "name": "valid_preferred_channel",
            "constraint": "preferred_channel IS NULL OR preferred_channel IN ('online', 'contactless', 'pos', 'atm', 'swipe')",
            "tag": "customers"
        }
    ]


def get_security_and_history_rules():
    """
    Rules to validate security flags, communication preferences,
    and historical risk indicators.
    """
    return [
        {
            "name": "valid_two_fa_enabled",
            "constraint": "two_fa_enabled IS NULL OR two_fa_enabled IN (0, 1)",
            "tag": "customers"
        },
        {
            "name": "valid_paperless_billing",
            "constraint": "paperless_billing IS NULL OR paperless_billing IN (0, 1)",
            "tag": "customers"
        },
        {
            "name": "valid_email_verified",
            "constraint": "email_verified IS NULL OR email_verified IN (0, 1)",
            "tag": "customers"
        },
        {
            "name": "valid_phone_verified",
            "constraint": "phone_verified IS NULL OR phone_verified IN (0, 1)",
            "tag": "customers"
        },
        {
            "name": "valid_loyalty_balance",
            "constraint": "loyalty_points_balance IS NULL OR loyalty_points_balance >= 0",
            "tag": "customers"
        }
    ]


def get_customer_rules():
    """
    Main entry point for customer data quality expectations.

    Aggregates all specific rule groups into a single list of dictionaries.
    """
    all_customer_rules = []
    all_customer_rules.extend(get_identity_and_time_rules())
    all_customer_rules.extend(get_demographic_rules())
    all_customer_rules.extend(get_financial_and_account_rules())
    all_customer_rules.extend(get_security_and_history_rules())

    return all_customer_rules
