from src.config import Config

import json
from unittest import mock

def create_config(**data):
    from mako.template import Template

    CONFIG_TEMPLATE = """
    {
      "access_map": {
        "M": ${access_map}
      },
      "config_id": {
        "S": ${version}
      },
      "is_current": {
        "BOOL": true
      },
      "uri_map": {
        "M": ${uri_map}
      }
    }
    """

    defaults = {
        'access_map': {},
        'version':    'ver_42',
        'uri_map':    {},
    }

    data          = {**defaults, **data}
    template_text = CONFIG_TEMPLATE

    config_text = Template(template_text).render(**data)
    config = json.loads(config_text)

    return config

def test_highest_config_version_chosen():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(version=json.dumps('ver_1')),
            create_config(version=json.dumps('ver_10')),
            create_config(version=json.dumps('ver_2')),
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        assert config.get_version() == 'ver_10'

def test_uri_map_missing_pretty_uri():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                version = json.dumps('ver_42'),
                uri_map = json.dumps({
                    '/some-pretty-path/pretty-resource': {
                        'S': '/some-ugly-path/ugly-resource'
                    }
                })
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        ugly_uri = config.get_ugly_uri(pretty_uri='/some-missing-path/some-missing-resource')
        assert ugly_uri == None

def test_uri_map_is_pretty_uri():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                version = json.dumps('ver_42'),
                uri_map = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': '/some-ugly-path/ugly-resource'
                    }
                })
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        pretty_uri = '/some-ugly-path/ugly-resource'
        ugly_uri = config.get_ugly_uri(pretty_uri=pretty_uri)
        assert ugly_uri == pretty_uri

def test_uri_map_direct_lookup():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                version = json.dumps('ver_42'),
                uri_map = json.dumps({
                    '/some-pretty-path/pretty-resource': {
                        'S': '/some-ugly-path/ugly-resource'
                    }
                })
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        ugly_uri = config.get_ugly_uri(pretty_uri='/some-pretty-path/pretty-resource')
        assert ugly_uri == '/some-ugly-path/ugly-resource'

def test_uri_map_indirection():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                version = json.dumps('ver_42'),
                uri_map = json.dumps({
                    '/some-pretty-path/pretty-resource': {
                        'S': '/another-pretty-path/another-resource'
                    },
                    '/another-pretty-path/another-resource': {
                        'S': '/some-ugly-path/ugly-resource'
                    }
                })
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        ugly_uri = config.get_ugly_uri(pretty_uri='/some-pretty-path/pretty-resource')
        assert ugly_uri == '/some-ugly-path/ugly-resource'

def test_access_map_missing_ugly_uri():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(version=json.dumps('ver_42')),
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == False

def test_access_map_no_entries():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                access_map = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': '-'
                    }
                }),
                version    = json.dumps('ver_42'),
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == False

def test_access_map_single_entry_allowed():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                access_map  = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': 'user_category -'
                    }
                }),
                version     = json.dumps('ver_42'),
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == True

def test_access_map_single_entry_disallowed():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                access_map = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': 'user_category_1 -'
                    }
                }),
                version    = json.dumps('ver_42'),
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category_2',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == False

def test_access_map_multiple_allowed():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                access_map = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': 'user_category_1 user_category_2 user_category_3 -'
                    }
                }),
                version    = json.dumps('ver_42'),
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category_2',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == True

def test_access_map_multiple_disallowed():
    with mock.patch('src.config.Config.get_configs_from_dynamodb') as mock_dynamo:
        mock_dynamo.return_value = [
            create_config(
                access_map = json.dumps({
                    '/some-ugly-path/ugly-resource': {
                        'S': 'user_category_1 user_category_2 user_category_3 -'
                    }
                }),
                version    = json.dumps('ver_42'),
            )
        ]

        config = Config(
            region_name='some-aws-region',
            table_name='some-dynamodb-table',
        )

        is_allowed = config.access_is_allowed(
            user='user_category_4',
            ugly_uri='/some-ugly-path/ugly-resource'
        )

        assert is_allowed == False
