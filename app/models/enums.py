from sqlalchemy.dialects.postgresql import ENUM

results = ENUM("win", "lose", name="results")


modes = ENUM("original", "daily", name="modes")


period = ENUM("daily", "weekly", "monthly", "all_time", name="periods")
