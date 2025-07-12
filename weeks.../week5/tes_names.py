from names import make_full_name, \
    extract_family_name, extract_given_name
import pytest



def test_make_full_name():
    assert make_full_name("Jasmine", "Brown") == "Brown; Jasmine"
    assert make_full_name("James", "Brown") == "Brown; James"
    assert make_full_name("J", "Ng") == "Ng; J"
    assert make_full_name("", "") == "; "


def test_extract_family_name():
    assert extract_family_name("Brown; Jasmine") == "Brown"
    assert extract_family_name("Brown; James") == "Brown"
    assert extract_family_name("Ng; J") == "Ng"
    assert extract_family_name("; ") == ""


def test_extract_given_name():
    assert extract_given_name("Brown; Jasmine") == "Jasmine"
    assert extract_given_name("Madison; James") == "James"
    assert extract_given_name("Ng; J") == "J"
    assert extract_given_name("; ") == ""

pytest.main(["-v", "--tb=line", "-rN", __file__])
