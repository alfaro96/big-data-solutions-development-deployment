"""
The purpose of this script is to build the `Spine` table of our `Medallion`
architecture. It takes the clean events from the `Silver` layer and prepares
the foundational dataset (entities, timestamps, and real-time features) used
by the `Feature Store` to orchestrate point-in-time correct joins during
training and inference.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp
from pyspark.sql.functions import col, date_format, to_timestamp


###############################################################################
# Feature engineering (`Spine` creation)
###############################################################################

gold_spine_table_name = "gold_fraud_spine"
gold_spine_comment = """
This managed table acts as the `Spine DataFrame` for machine learning.
It contains the primary keys (`customer_id`), event times (`timestamp`),
real-time transactional features, and the target label (`is_fraud`).
"""

silver_events_source = "silver_fraud_events"


@dp.table(name = gold_spine_table_name, comment = gold_spine_comment)
def gold_fraud_spine():
    """
    Reads the enriched transactions to build the machine learning spine.

    Passes through the primary keys, event timestamps, and real-time
    features necessary for the `Feature Store`'s `PiT` lookups.
    """
    df_events = spark.readStream.table(silver_events_source)

    # Force an irreversible physical transformation to bypass the optimizer:
    # we convert the date to a string with an explicit format and back to a timestamp.
    # This guarantees the removal of the hidden watermark metadata from
    # "label_available_date".
    df_events = df_events.withColumn(
        "label_available_date",
        to_timestamp(date_format(col("label_available_date"), "yyyy-MM-dd HH:mm:ss.SSS"))
    )

    # Select core fields strictly related to the transaction (the spine)
    df_spine = df_events.select(
        # Primary keys & event time column
        col("transaction_id"),
        col("customer_id"),
        col("timestamp"),

        # Labels
        col("is_fraud"),
        col("label_available_date"),

        # Real-time features (available in the payload at serving time)
        col("merchant_id"),
        col("amount"),
        col("currency"),
        col("mcc_code"),
        col("mcc_category"),
        col("cross_border"),
        col("is_tor_or_vpn"),
        col("ip_country_match"),
        col("device_fingerprint_known"),
        col("payment_method"),
        col("device_type"),
        col("three_ds_result"),
        col("merchant_country")
    )

    return df_spine
