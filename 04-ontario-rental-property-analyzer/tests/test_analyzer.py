import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analyzer import monthly_payment, Property, analyze, break_even_rent


def base(**kw):
    d = dict(purchase_price=500_000, down_payment_pct=0.2, mortgage_rate=0.05,
             amortization_years=25, monthly_rent=3000, vacancy_pct=0.05,
             annual_property_tax=3000, annual_insurance=1200,
             monthly_maintenance_pct=0.08, monthly_utilities=0)
    d.update(kw)
    return Property(**d)


class TestAnalyzer(unittest.TestCase):
    def test_zero_principal(self):
        self.assertEqual(monthly_payment(0, 0.05), 0.0)

    def test_canadian_compounding_is_cheaper_than_monthly(self):
        principal, rate, n = 500_000, 0.05, 300
        mr = rate / 12
        monthly_compounded = principal * mr / (1 - (1 + mr) ** -n)
        self.assertLess(monthly_payment(principal, rate, 25), monthly_compounded)

    def test_known_payment(self):
        self.assertAlmostEqual(monthly_payment(500_000, 0.05, 25), 2908, delta=5)

    def test_cap_rate_math(self):
        p = base(purchase_price=1_000_000, monthly_rent=5000, vacancy_pct=0.0,
                 annual_property_tax=0, annual_insurance=0, monthly_maintenance_pct=0)
        self.assertEqual(analyze(p)["cap_rate_pct"], 6.0)

    def test_brrrr_cash_out(self):
        p = base(rehab_cost=30_000, after_repair_value=600_000)
        r = analyze(p)["brrrr"]
        self.assertEqual(r["refinance_loan"], 480_000)
        self.assertEqual(r["cash_pulled_out"], 80_000)

    def test_break_even_rent_gives_zero_cash_flow(self):
        p = base()
        be = break_even_rent(p)
        q = base(monthly_rent=be)
        self.assertAlmostEqual(analyze(q)["annual_cash_flow"], 0, delta=60)


if __name__ == "__main__":
    unittest.main()
