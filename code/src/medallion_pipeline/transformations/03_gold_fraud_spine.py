"""
The purpose of this script is to build the `Spine` tables of our `Medallion`
architecture. It takes the events from the `Bronze` and `Silver` layers and
prepares the foundational datasets (entities, timestamps, and real-time features)
used by the `Feature Store` to orchestrate point-in-time correct joins during
training and inference.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp
from pyspark.sql.functions import col, date_format, to_timestamp


###############################################################################
# Configuration variables and constants
###############################################################################

# Source for the training spine: includes confirmed fraud labels via the
# stream-stream join watermark, guaranteeing point-in-time correctness.
training_events_source = "silver_fraud_events"

# Source for the inference spine: reads ALL transactions directly from bronze,
# bypassing quality filters and the stream-stream join watermark to guarantee
# that every incoming transaction is available for scoring immediately.
inference_events_source = "bronze_transactions"


###############################################################################
# Training spine
###############################################################################

gold_spine_table_name = "gold_fraud_spine"
gold_spine_comment = """
This managed table acts as the `Spine DataFrame` for machine learning
**training**. It contains the primary keys (`customer_id`), event times
(`timestamp`), real-time transactional features, and the target label
(`is_fraud`). It reads from `silver_fraud_events`, which includes confirmed
fraud labels via the stream-stream join watermark, guaranteeing point-in-time
correctness during training.
"""


@dp.table(name = gold_spine_table_name, comment = gold_spine_comment)
def gold_fraud_spine():
    """
    Reads the enriched transactions from `silver_fraud_events` to build the
    machine learning training spine. Passes through the primary keys, event
    timestamps, confirmed labels and real-time features necessary for the
    `Feature Store`'s `PiT` lookups.
    """
    df_events = spark.readStream.table(training_events_source)

    # Force an irreversible physical transformation to bypass the optimizer:
    # we convert the date to a string with an explicit format and back to a timestamp.
    # This guarantees the removal of the hidden watermark metadata from
    # "label_available_date".
    df_events = df_events.withColumn(
        "label_available_date",
        to_timestamp(date_format(col("label_available_date"), "yyyy-MM-dd HH:mm:ss.SSS"))
    )

    # Select core fields strictly related to the transaction (the spine).
    # Labels are included because this spine is used exclusively for training.
    return df_events.select(
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


###############################################################################
# Inference spine
###############################################################################

gold_inference_spine_table_name = "gold_fraud_inference_spine"
gold_inference_spine_comment = """
This managed table acts as the `Spine DataFrame` for production **inference**.
It reads directly from `bronze_transactions`, bypassing both the silver quality
filters and the stream-stream join watermark, to guarantee that every incoming
transaction is available for scoring immediately regardless of whether it passed
quality checks or its fraud label has arrived yet.

Labels (`is_fraud`, `label_available_date`) are intentionally excluded: they
are not available at serving time and arrive asynchronously via the label
enrichment step in `09_Inference_And_Label_Enrichment`.
"""


@dp.table(name = gold_inference_spine_table_name, comment = gold_inference_spine_comment)
def gold_fraud_inference_spine():
    """
    Reads all incoming transactions directly from `bronze_transactions`, without
    any dependency on the stream-stream join watermark of `silver_fraud_events`
    or the silver quality filters. This guarantees that every transaction is
    available for scoring immediately, regardless of whether it passed quality
    checks or its fraud label has arrived yet.
    """
    return (
        spark.readStream
             .table(inference_events_source)
             .withColumn("timestamp", to_timestamp(col("timestamp")))
             .select(
                 # Primary keys & event time column
                 col("transaction_id"),
                 col("customer_id"),
                 col("timestamp"),

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
    )
