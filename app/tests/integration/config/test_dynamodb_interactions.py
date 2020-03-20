from src.config import Config

def test_uri_map_missing_pretty_uri():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    ugly_uri = config.get_ugly_uri(pretty_uri='/some/missing/uri')
    assert ugly_uri == None

def test_uri_map_is_pretty_uri():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    pretty_uri = '/some-ugly-path/another-ugly-path/biology/biology_book_1.txt'
    ugly_uri = config.get_ugly_uri(pretty_uri=pretty_uri)
    assert ugly_uri == pretty_uri

def test_uri_map_direct_lookup():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    ugly_uri = config.get_ugly_uri(pretty_uri='/biology/vers/2')
    assert ugly_uri == '/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'

def test_uri_map_indirection():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    ugly_uri = config.get_ugly_uri(pretty_uri='/biology/vers/latest')
    assert ugly_uri == '/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'

def test_access_map_missing_ugly_uri():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='teacher',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_5.txt'
    )

    assert is_allowed == False

def test_access_map_no_entries():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='teacher',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_4.txt'
    )

    assert is_allowed == False

def test_access_map_single_entry_allowed():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='teacher',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_3.txt'
    )

    assert is_allowed == True

def test_access_map_single_entry_disallowed():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='student',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_3.txt'
    )

    assert is_allowed == False

def test_access_map_multiple_allowed():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='student',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'
    )

    assert is_allowed == True

def test_access_map_multiple_disallowed():
    config = Config(
        region_name='us-east-1',
        table_name='kevin-pdfdistro-configs',
    )

    is_allowed = config.access_is_allowed(
        user='anonymous',
        ugly_uri='/some-ugly-path/another-ugly-path/biology/biology_book_2.txt'
    )

    assert is_allowed == False
