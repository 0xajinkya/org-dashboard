"""This module provides a class to manage session state in Streamlit."""

from typing import Any, Callable, Optional

import streamlit as st


class SessionStateManager:
    def __init__(self, key_builder: Optional[Callable[..., str]] = None):
        """
        If provided, key_builder is a function that constructs dynamic keys
        based on arguments passed to methods.
        """
        self.key_builder = key_builder

    def _resolve_key(self, *args) -> str:
        if self.key_builder:
            return self.key_builder(*args)
        if args:
            raise ValueError("Arguments passed but no key_builder defined.")
        return ""

    def add(self, value: Any, *args) -> None:
        """Add a value to session state."""
        key = self._resolve_key(*args)
        st.session_state[key] = value

    def get(self, *args, default: Any = None) -> Any:
        """Retrieve a value from session state."""
        key = self._resolve_key(*args)
        return st.session_state.get(key, default)

    def update(self, value: Any, *args) -> None:
        """Update an existing value in session state."""
        key = self._resolve_key(*args)
        if key in st.session_state:
            st.session_state[key] = value
        else:
            raise KeyError(f"Key '{key}' not found in session state.")

    def remove(self, *args) -> None:
        """Remove a value from session state."""
        key = self._resolve_key(*args)
        st.session_state.pop(key, None)
