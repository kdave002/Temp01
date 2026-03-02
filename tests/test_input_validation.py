import pytest
from pydantic import ValidationError

from backend.app.models import Column, DriftRequest


def test_rejects_non_identifier_column_name():
    with pytest.raises(ValidationError):
        Column(name="amount; DROP TABLE users;--", type="int")


def test_rejects_duplicate_column_names_in_schema():
    with pytest.raises(ValidationError):
        DriftRequest(
            previous_schema=[Column(name="id", type="int"), Column(name="id", type="int")],
            current_schema=[Column(name="id", type="int")],
            downstream_model_count=0,
        )


def test_rejects_excessive_schema_size():
    oversized = [Column(name=f"col_{i}", type="int") for i in range(501)]
    with pytest.raises(ValidationError):
        DriftRequest(previous_schema=oversized, current_schema=[], downstream_model_count=1)


def test_rejects_negative_downstream_model_count():
    with pytest.raises(ValidationError):
        DriftRequest(previous_schema=[], current_schema=[], downstream_model_count=-1)
