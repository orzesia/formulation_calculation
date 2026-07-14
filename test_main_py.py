import pytest

from simplified import (
    VIRUS_STOCK_CTS,
    calculate_formulation_from_inputs,
    get_number_of_viruses,
    normalize_virus_name,
)


def test_get_number_of_viruses_rejects_invalid_choices():
    with pytest.raises(ValueError):
        get_number_of_viruses("0")

    with pytest.raises(ValueError):
        get_number_of_viruses("4")

    with pytest.raises(ValueError):
        get_number_of_viruses("abc")


def test_normalize_virus_name_accepts_known_names():
    assert normalize_virus_name("pedv") == "PEDV"
    assert normalize_virus_name("PDCoV") == "PDCoV"
    assert normalize_virus_name("TGEV") == "TGEV"
    assert normalize_virus_name("PRVA") == "PRVA"


def test_calculate_formulation_from_inputs_rejects_duplicate_viruses():
    with pytest.raises(ValueError):
        calculate_formulation_from_inputs(["PEDV", "pedv"], [26.0, 30.0], 50)


def test_calculate_formulation_from_inputs_uses_expected_formula_and_diluent():
    virus_results, diluent_volume_ul = calculate_formulation_from_inputs(
        ["PEDV", "PDCoV"],
        [28.0, 31.0],
        50,
    )

    assert len(virus_results) == 2
    assert diluent_volume_ul > 0
    assert all(result["virus_name"] in VIRUS_STOCK_CTS for result in virus_results)

    first_result = virus_results[0]
    assert first_result["dilution_factor"] == pytest.approx(10 ** ((first_result["desired_ct"] - first_result["stock_ct"]) / 3.3))
    assert first_result["stock_volume_ul"] == pytest.approx((50 / first_result["dilution_factor"]) * 4)

