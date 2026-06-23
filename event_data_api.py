"""
Backward compatibility re-export.

The canonical EventDataAPI now lives in retrieval.event_data_api.
This module re-exports everything for existing imports.
"""

from retrieval.event_data_api import EventDataAPI, EVENT_DB, load_ax_data  # noqa: F401
