from src.config import Config

import pytest

def test_missing_table_raises_error():
    with pytest.raises(RuntimeError):
        configs = Config.get_configs_from_dynamodb(
            region_name='us-east-1',
            table_name='some-missing-table',
        )

def test_multiple_configs_can_be_returned():
    configs = Config.get_configs_from_dynamodb(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )
    assert len(configs) > 1
