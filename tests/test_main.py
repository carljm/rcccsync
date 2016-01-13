import pytest

from rcccsync.main import parse_name_and_email as parse


@pytest.mark.parametrize(
    'combined,split',
    [
        ("Foo Bar <foobar@example.com>", ("Foo", "Bar", "foobar@example.com")),
        ("Foo <foo@example.com>", ("Foo", "", "foo@example.com")),
        ("Foo d Bar <foo@example.com>", ("Foo", "d Bar", "foo@example.com")),
        ("foo@example.com", ("", "", "foo@example.com")),
    ]
)
def test_parse_name_and_email(combined, split):
    assert parse(combined) == split
