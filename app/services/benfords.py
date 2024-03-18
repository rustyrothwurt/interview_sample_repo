import collections
import math
import random
import numpy as np


BENFORD = [0.3010299956639812, 0.17609125905568124, 0.12493873660829993, 0.09691001300805642, 0.07918124604762482, 0.06694678963061322, 0.05799194697768673, 0.05115252244738129, 0.04575749056067514]
BENFORD_PERCENTAGES = [0, 0.3010299956639812, 0.17609125905568124, 0.12493873660829993, 0.09691001300805642, 0.07918124604762482, 0.06694678963061322, 0.05799194697768673, 0.05115252244738129, 0.04575749056067514]
BENFORD_PERCENTAGES_CDF = [0.3010299956639812, 0.47712125471966244, 0.6020599913279624, 0.6989700043360189, 0.7781512503836436, 0.8450980400142568, 0.9030899869919435, 0.9542425094393249, 1.0]

def validate_and_calculate(data):
    """

    Args:
        data: input list of values

    Returns:
        list[dict]: dict list by value.
    """
    errors = _validate_data(data)
    data_len = len(data)
    first_digits = _get_first_digits(data)
    dig_validate = _validate_numbers(first_digits)
    if len(dig_validate) > 0:
        errors.extend(dig_validate)
    if len(errors) > 0:
        raise ValueError(errors)
    else:
        first_digit_frequencies = collections.Counter(first_digits)
        return _calculate(first_digit_frequencies, data_len)


def test_significance(results):
    firstdigitscdf = _get_first_digits_cdf(results)
    benfordsdigitscdf = _get_benfords_digits_cdf(results)
    ks_val = _get_ks_sig_value(firstdigitscdf, benfordsdigitscdf)
    kuiper_val = _get_kuiper_sig_value(firstdigitscdf, benfordsdigitscdf)
    chi_val = _get_chi_sig_value(results)
    ranges = _get_kuiper_significance(kuiper_val)
    ranges.extend(_get_ks_significance(ks_val))
    ranges.extend(_get_chi_square_significance(chi_val))
    return ranges


def _validate_data(data):
    errors = []
    if len(data) < 1:
        errors.append('input data is empty')
    if isinstance(data, list) is False:
        errors.append('input data not a list!')
    return errors


def _validate_numbers(digits):
    bad_digit_list = []
    for idx, s in enumerate(digits):
        try:
            int(s)
        except ValueError as e:
            bad_digit_list.append({idx:s})
            pass
    return bad_digit_list


def _get_first_digits(data):
    return list(map(lambda n: (str(n).replace('.', '').replace('-', ''))[0], data))


def _calculate(first_digit_frequencies, data_len):
    """
    Calculates a set of values from the numeric list
    input data showing how closely the first digits
    fit the Benford Distribution.
    Results are returned as a list of dictionaries.
    """
    results = []
    for n in range(1, 10):
        data_frequency = first_digit_frequencies[str(n)]
        data_frequency_percent = data_frequency / data_len
        benford_frequency = data_len * BENFORD_PERCENTAGES[n]
        benford_frequency_percent = BENFORD_PERCENTAGES[n]
        difference_frequency = data_frequency - benford_frequency
        difference_frequency_percent = data_frequency_percent - benford_frequency_percent
        data_frequency_cumulative = firstdigitscdf = []
        results.append({"n": n, "data_frequency": data_frequency, "data_frequency_percent": data_frequency_percent,
                        "benford_frequency": benford_frequency, "benford_frequency_percent": benford_frequency_percent,
                        "difference_frequency": difference_frequency,
                        "difference_frequency_percent": difference_frequency_percent})
    return results

def _get_chi_sig_value(results):
    """Return boolean on chi-square test (8 DOF & P-val=0.05)."""
    chi_square_stat = 0; # chi-square test statistic
    obs = list(l["data_frequency"] for l in results)
    exp = list(l["benford_frequency"] for l in results)
    for data, expected in zip(obs, exp):
        chi_square = math.pow(data - expected, 2)
        chi_square_stat += chi_square / expected
    return chi_square_stat


def _get_kuiper_sig_value(firstdigitscdf, benfordsdigitscdf):
    Dplus = np.abs(np.max(np.subtract(benfordsdigitscdf, firstdigitscdf)))
    Dminus = np.abs(np.max(np.subtract(firstdigitscdf, benfordsdigitscdf)))
    V = Dplus + Dminus
    return V


def _get_ks_sig_value(firstdigitscdf, benfordsdigitscdf):
    D = np.max(np.abs(np.subtract(benfordsdigitscdf, firstdigitscdf)))
    D *= 3  # = sqrt(9)
    return D


def _get_chi_square_significance(testval):
    ranges = []
    ranges.append({"sig_value": 0.05, "range":15.51, "test_type":"chi", "significant": 0, "test_value": None})
    for range in ranges:
        range["test_value"] = testval
        if testval < range["range"]:
            range["significant"] = 1
    return ranges


def _get_ks_significance(testval):
    ranges = []
    ranges.append({"sig_value": 0.10, "range":1.012, "test_type":"KS", "significant": 0, "test_value": None})
    ranges.append({"sig_value": 0.05, "range":1.148, "test_type":"KS", "significant": 0, "test_value": None})
    ranges.append({"sig_value": 0.01, "range":1.420, "test_type":"KS", "significant": 0, "test_value": None})
    for range in ranges:
        range["test_value"] = testval
        if testval > range["range"]:
            range["significant"] = 1
    return ranges


def _get_kuiper_significance(testval):
    ranges = []
    ranges.append({"sig_value": 0.10, "range": 1.191, "test_type": "Kuiper", "significant": 0, "test_value": None})
    ranges.append({"sig_value": 0.05, "range": 1.321, "test_type": "Kuiper", "significant": 0, "test_value": None})
    ranges.append({"sig_value": 0.01, "range": 1.579, "test_type": "Kuiper", "significant": 0, "test_value": None})
    for range in ranges:
        range["test_value"] = testval
        if testval > range["range"]:
            range["significant"] = 1
    return ranges


def _get_first_digits_cdf(results):
    firstdigitspdf = list(l["data_frequency_percent"] for l in results)
    firstdigitscdf = []
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        firstdigitscdf += [sum(firstdigitspdf[0:k])]
    return firstdigitscdf


def _get_benfords_digits_cdf(results):
    firstdigitspdf = list(l["benford_frequency_percent"] for l in results)
    firstdigitscdf = []
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        firstdigitscdf += [sum(firstdigitspdf[0:k])]
    return firstdigitscdf



