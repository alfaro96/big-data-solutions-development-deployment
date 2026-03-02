"""
The purpose of this script is to build the customer profile feature table.
It takes the `AUTO CDC` (`SCD2`) customer history from the `Silver` layer
and derives static demographic features.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp
from pyspark.sql.functions import col, when


###############################################################################
# Feature engineering (customer profile)
###############################################################################

gold_profile_table_name = "gold_customer_profile"
gold_profile_comment = """
This managed table acts as a **feature table** in the `Feature Store`.
It contains the `SCD2` customer history and derived demographic attributes
(e.g., `age_group`, `income_group`).
"""

# Change Data Feed (CDF) is enabled so that the feature store can track
# row-level changes (inserts, updates, deletes) via the Delta change log
# rather than performing a full table scan on every sync cycle. Without CDF,
# the feature store would need to re-scan the entire table to detect which
# rows changed since the last publish. With CDF, it only reads the Delta
# change log; a much cheaper operation that translates directly into lower
# latency between a new aggregation being computed and that value becoming
# available in the online store.
gold_aggregations_table_properties = {"delta.enableChangeDataFeed": "true"}

# The "PRIMARY KEY" constraint is what makes this Delta table a feature table
# in Unity Catalog. No API registration call is needed: the feature store
# recognizes any streaming table with a primary key constraint automatically.

# The "TIMESERIES" keyword on "__START_AT" designates it as the temporal
# anchor for PiT joins during training, ensuring the feature store always
# retrieves the customer version that was valid at the moment of each
# transaction, without any leakage of future profile changes.
gold_profile_schema = """
    customer_id STRING NOT NULL,
    age INT,
    gender STRING,
    income_bracket STRING,
    country STRING,
    state_region STRING,
    city_tier INT,
    occupation STRING,
    customer_segment STRING,
    card_type STRING,
    join_date DATE,
    num_cards_issued INT,
    two_fa_enabled INT,
    paperless_billing INT,
    email_verified INT,
    phone_verified INT,
    preferred_channel STRING,
    loyalty_points_balance INT,
    __START_AT TIMESTAMP NOT NULL,
    __END_AT TIMESTAMP,
    age_group STRING NOT NULL,
    income_group STRING NOT NULL,
    CONSTRAINT gold_customer_profile_pk PRIMARY KEY (customer_id, __START_AT TIMESERIES)
"""

silver_customers_source = "silver_customers_history"
gold_profile_flow_name = "flow_gold_profile"

dp.create_streaming_table(
    name = gold_profile_table_name,
    comment = gold_profile_comment,
    table_properties = gold_aggregations_table_properties,
    schema = gold_profile_schema
)


@dp.append_flow(target = gold_profile_table_name, name = gold_profile_flow_name)
def gold_customer_profile():
    """
    Reads the historical customer profiles (`SCD2`).

    Derives computable demographic attributes. The temporal validity
    columns (`__START_AT`, `__END_AT`) are preserved for the `Feature Store`
    `PiT` joins.
    """
    df_customers = spark.readStream.table(silver_customers_source)

    df_profile = df_customers.select(
        col("customer_id"),
        col("age"),
        col("gender"),
        col("income_bracket"),
        col("country"),
        col("state_region"),
        col("city_tier"),
        col("occupation"),
        col("customer_segment"),
        col("card_type"),
        col("join_date"),
        col("num_cards_issued"),
        col("two_fa_enabled"),
        col("paperless_billing"),
        col("email_verified"),
        col("phone_verified"),
        col("preferred_channel"),
        col("loyalty_points_balance"),

        # Keeping the SCD2 columns is crucial so the feature store knows
        # exactly which customer version to use at any given moment
        # (PiT join).
        col("__START_AT"),
        col("__END_AT"),

        # Derived static features
        when(col("age") < 30, "young")
        .when((col("age") >= 30) & (col("age") < 55), "adult")
        .otherwise("senior")
        .alias("age_group"),

        when(col("income_bracket").isin(["<25k", "25k-50k"]), "low")
        .when(col("income_bracket").isin(["50k-75k", "75k-100k"]), "medium")
        .otherwise("high")
        .alias("income_group")
    )

    return df_profile
