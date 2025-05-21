import pytest

from app.formulas import (
    lorentz_rec_weight, broca_brugsch_rec_weight,
    weight_loss_pct, high_nutritional_risk,
    bsa_mosteller, bsa_shuter,
    bmi, bmi_with_amputation, bmi_category,
    waist_status, whr, whr_status,
    bmr_mifflin, bmr_harris, bmr_katch,
    fat_percent, fat_mass_index, ffm_index,
    body_water_percent, ecw_ratio,
    Sex
)


class TestFormulas:
    def test_lorentz_rec_weight(self):
        assert pytest.approx(lorentz_rec_weight(170, Sex.MALE), rel=1e-3) == 48 + (170 - 152) * 1.1
        assert pytest.approx(lorentz_rec_weight(160, Sex.FEMALE), rel=1e-3) == 45 + (160 - 152) * 0.9

    @pytest.mark.parametrize("h,expected", [
        (160, 60), (170, 65), (180, 70)
    ])
    def test_broca_brugsch_rec_weight(self, h, expected):
        assert broca_brugsch_rec_weight(h) == expected

    def test_weight_loss_and_risk(self):
        pct = weight_loss_pct(80, 76)
        assert pytest.approx(pct, rel=1e-6) == 5.0
        assert not high_nutritional_risk(pct, 1)
        assert high_nutritional_risk(8.0, 3)

    def test_bsa(self):
        assert pytest.approx(bsa_mosteller(70, 170), rel=1e-6) == (70 * 170 / 3600) ** 0.5
        assert pytest.approx(bsa_shuter(70, 170), rel=1e-6) == 0.00949 * 70 ** 0.441 * 170 ** 0.655

    def test_bmi_and_categories(self):
        value = bmi(65, 170)
        assert pytest.approx(value, rel=1e-6) == 100 * 65 / 170 ** 2
        assert bmi_category(15) == "Выраженный дефицит"
        assert bmi_category(22) == "Норма"
        assert bmi_category(27) == "Предожирение"

    def test_bmi_with_amputation(self):
        base = 65 / 1.7 ** 2
        assert pytest.approx(bmi_with_amputation(65, 1.7, 0.065), rel=1e-6) == base + 0.065 * base

    def test_waist_and_whr(self):
        assert waist_status(90, Sex.MALE) == "Норма"
        assert waist_status(85, Sex.FEMALE) == "Профилактика предотвращения набора веса"
        ratio = whr(90, 100)
        assert ratio == 0.9
        assert whr_status(ratio, Sex.FEMALE) == "Абдоминальное ожирение"

    def test_bmr(self):
        assert pytest.approx(bmr_mifflin(65, 170, 30, Sex.MALE), rel=1e-6) == 10 * 65 + 6.25 * 170 - 5 * 30 + 5
        assert pytest.approx(bmr_harris(65, 170, 30, Sex.FEMALE),
                             rel=1e-6) == 447.593 + 9.247 * 65 + 3.098 * 170 - 4.330 * 30
        assert bmr_katch(50) == 370 + 21.6 * 50

    def test_bio_impedance(self):
        assert pytest.approx(fat_percent(15, 75), rel=1e-6) == 15 / 75 * 100
        assert pytest.approx(fat_mass_index(15, 1.75), rel=1e-6) == 15 / 1.75 ** 2
        assert pytest.approx(ffm_index(55, 1.75), rel=1e-6) == 55 / 1.75 ** 2
        assert pytest.approx(body_water_percent(40, 70), rel=1e-6) == 40 / 70 * 100
        assert pytest.approx(ecw_ratio(15, 40), rel=1e-6) == 15 / 40
