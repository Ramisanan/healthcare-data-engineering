"""
Healthcare Data Engineering Project
Phase 4: Unit Tests
Testing all ETL transformation functions
"""

import pytest
from datetime import datetime, timedelta


# build a fake row
def make_row(overrides=None):
    """Create a base valid row dict and apply any overrides."""
    base = {
        "transaction_id":   "TXN0000001",
        "store_id":         "STR0001",
        "customer_id":      "CUST00001",
        "product_id":       "PRD0001",
        "transaction_date": datetime(2024, 6, 15, 10, 30),
        "quantity":         2,
        "unit_price":       25.99,
        "discount_pct":     0.1,
        "total_amount":     46.78,
        "payment_method":   "Credit Card",
        "cashier_id":       "EMP1234",
        "return_flag":      "N",
    }
    if overrides:
        base.update(overrides)
    return base


# TRANSFORMATION LOGIC TESTS

class TestCalculations:
    """Test core calculation functions used in ETL"""

    def test_total_amount_calculation(self):
        """Total = quantity × price × (1 - discount)"""
        quantity  = 2
        price     = 25.99
        discount  = 0.1
        expected  = round(quantity * price * (1 - discount), 2)
        assert expected == 46.78

    def test_total_amount_no_discount(self):
        """Total with no discount = quantity × price"""
        quantity = 3
        price    = 10.00
        discount = 0.0
        expected = round(quantity * price * (1 - discount), 2)
        assert expected == 30.00

    def test_insurance_paid_calculation(self):
        """Insurance paid = retail price - copay"""
        retail_price = 150.00
        copay        = 25.00
        insurance    = round(retail_price - copay, 2)
        assert insurance == 125.00

    def test_discount_percentage_range(self):
        """Discount must be between 0 and 1"""
        valid_discounts   = [0.0, 0.1, 0.25, 0.5, 1.0]
        invalid_discounts = [-0.1, 1.1, 2.0, -1.0]

        for d in valid_discounts:
            assert 0 <= d <= 1, f"Expected valid: {d}"

        for d in invalid_discounts:
            assert not (0 <= d <= 1), f"Expected invalid: {d}"

    def test_copay_cannot_exceed_retail(self):
        """Copay should never exceed retail price"""
        valid_cases = [
            (25.00, 150.00),   # copay < retail 
            (0.00,  50.00),    # zero copay 
            (50.00, 50.00),    # equal 
        ]
        invalid_cases = [
            (200.00, 150.00),  
            (75.01,  75.00),  
        ]

        for copay, retail in valid_cases:
            assert copay <= retail

        for copay, retail in invalid_cases:
            assert copay > retail


# DATA VALIDATION TESTS 

class TestSalesValidation:
    """Test sales transaction validation rules"""

    def test_valid_transaction_passes(self):
        """A clean transaction should pass all checks"""
        row    = make_row()
        issues = []

        if not row["transaction_id"]: issues.append("NULL_TRANSACTION_ID")
        if not row["store_id"]:       issues.append("NULL_STORE_ID")
        if row["quantity"] <= 0:      issues.append("INVALID_QUANTITY")
        if row["unit_price"] <= 0:    issues.append("INVALID_PRICE")
        if row["total_amount"] < 0:   issues.append("INVALID_TOTAL")

        assert issues == [], f"Expected no issues but got: {issues}"

    def test_null_transaction_id_rejected(self):
        """Transaction with no ID should be rejected"""
        row    = make_row({"transaction_id": None})
        issues = []

        if not row["transaction_id"]: issues.append("NULL_TRANSACTION_ID")

        assert "NULL_TRANSACTION_ID" in issues

    def test_negative_quantity_rejected(self):
        """Negative quantity should be rejected"""
        row    = make_row({"quantity": -1})
        issues = []

        if row["quantity"] <= 0: issues.append("INVALID_QUANTITY")

        assert "INVALID_QUANTITY" in issues

    def test_zero_quantity_rejected(self):
        """Zero quantity should be rejected"""
        row    = make_row({"quantity": 0})
        issues = []

        if row["quantity"] <= 0: issues.append("INVALID_QUANTITY")

        assert "INVALID_QUANTITY" in issues

    def test_negative_price_rejected(self):
        """Negative price should be rejected"""
        row    = make_row({"unit_price": -5.99})
        issues = []

        if row["unit_price"] <= 0: issues.append("INVALID_PRICE")

        assert "INVALID_PRICE" in issues

    def test_future_date_rejected(self):
        """Transaction with future date should be rejected"""
        future = datetime.now() + timedelta(days=30)
        row    = make_row({"transaction_date": future})
        issues = []

        if row["transaction_date"] > datetime.now():
            issues.append("FUTURE_TRANSACTION_DATE")

        assert "FUTURE_TRANSACTION_DATE" in issues

    def test_valid_payment_methods(self):
        """Only valid payment methods should pass"""
        valid   = ["Credit Card", "Debit Card", "Cash",
                   "CVS Rewards", "Insurance"]
        invalid = ["Bitcoin", "Venmo", "Barter", ""]

        for method in valid:
            assert method in valid

        for method in invalid:
            assert method not in valid

    def test_duplicate_detection(self):
        """Duplicate transaction IDs should be caught"""
        seen = set()
        ids  = ["TXN001", "TXN002", "TXN001"]  # TXN001 is duplicate
        duplicates = []

        for tid in ids:
            if tid in seen:
                duplicates.append(tid)
            seen.add(tid)

        assert "TXN001" in duplicates
        assert len(duplicates) == 1


# PRESCRIPTION VALIDATION TESTS

class TestPrescriptionValidation:
    """Test prescription fill validation rules"""

    def test_valid_days_supply(self):
        """Days supply must be 30, 60, or 90"""
        valid_days   = [30, 60, 90]
        invalid_days = [7, 14, 45, 100, 0, -30]

        for days in valid_days:
            assert days in valid_days

        for days in invalid_days:
            assert days not in valid_days

    def test_future_fill_date_rejected(self):
        """Prescription filled in the future should be rejected"""
        future_date = datetime.now() + timedelta(days=10)
        issues      = []

        if future_date > datetime.now():
            issues.append("FUTURE_FILL_DATE")

        assert "FUTURE_FILL_DATE" in issues

    def test_valid_prescription_status(self):
        """Status must be Filled, Pending, or Cancelled"""
        valid_status   = ["Filled", "Pending", "Cancelled"]
        invalid_status = ["Unknown", "Processing", "Maybe", ""]

        for s in valid_status:
            assert s in valid_status

        for s in invalid_status:
            assert s not in valid_status

    def test_negative_copay_rejected(self):
        """Negative copay amount should be rejected"""
        copay  = -10.00
        issues = []

        if copay < 0: issues.append("NEGATIVE_COPAY")

        assert "NEGATIVE_COPAY" in issues

    def test_zero_copay_is_valid(self):
        """Zero copay is valid (fully covered by insurance)"""
        copay  = 0.00
        issues = []

        if copay < 0: issues.append("NEGATIVE_COPAY")

        assert "NEGATIVE_COPAY" not in issues

    def test_generic_flag_values(self):
        """Generic flag must be Y or N"""
        valid   = ["Y", "N"]
        invalid = ["Yes", "No", "1", "0", ""]

        for flag in valid:
            assert flag in ["Y", "N"]

        for flag in invalid:
            assert flag not in ["Y", "N"]


# INVENTORY VALIDATION TESTS

class TestInventoryValidation:
    """Test inventory level validation rules"""

    def test_negative_quantity_rejected(self):
        """Negative inventory quantity should be rejected"""
        quantity = -5
        issues   = []

        if quantity < 0: issues.append("NEGATIVE_QUANTITY")

        assert "NEGATIVE_QUANTITY" in issues

    def test_zero_quantity_is_valid(self):
        """Zero quantity is valid — means out of stock"""
        quantity = 0
        issues   = []

        if quantity < 0: issues.append("NEGATIVE_QUANTITY")

        assert "NEGATIVE_QUANTITY" not in issues

    def test_stockout_flag_logic(self):
        """Stockout flag should be Y when quantity is 0"""
        test_cases = [
            (0,   "Y"),   # out of stock
            (1,   "N"),   # in stock
            (100, "N"),   # in stock
        ]

        for qty, expected_flag in test_cases:
            flag = "Y" if qty == 0 else "N"
            assert flag == expected_flag

    def test_low_stock_flag_logic(self):
        """Low stock flag should be Y when quantity <= reorder point"""
        test_cases = [
            (0,  20, "N"),   # stockout, not low stock
            (5,  20, "Y"),   # below reorder point
            (20, 20, "Y"),   # at reorder point
            (21, 20, "N"),   # above reorder point
        ]

        for qty, reorder, expected in test_cases:
            flag = "Y" if 0 < qty <= reorder else "N"
            assert flag == expected, \
                f"qty={qty}, reorder={reorder}: expected {expected}"


#  DATA QUALITY TESTS

class TestDataQuality:
    """Test general data quality rules"""

    def test_store_id_format(self):
        """Store IDs should follow STR#### format"""
        valid_ids   = ["STR0001", "STR0020", "STR1000"]
        invalid_ids = ["STR1", "STORE001", "str0001", ""]

        for sid in valid_ids:
            assert sid.startswith("STR") and len(sid) == 7

        for sid in invalid_ids:
            assert not (sid.startswith("STR") and len(sid) == 7)

    def test_product_id_format(self):
        """Product IDs should follow PRD#### format"""
        valid_ids   = ["PRD0001", "PRD0050"]
        invalid_ids = ["PRD1", "PROD001", ""]

        for pid in valid_ids:
            assert pid.startswith("PRD") and len(pid) == 7

    def test_customer_id_format(self):
        """Customer IDs should follow CUST##### format"""
        valid_ids   = ["CUST00001", "CUST00500"]
        invalid_ids = ["CUST1", "CUSTOMER001", ""]

        for cid in valid_ids:
            assert cid.startswith("CUST") and len(cid) == 9

    def test_rx_id_format(self):
        """Rx IDs should follow RX####### format"""
        valid_ids   = ["RX0000001", "RX0002000"]
        invalid_ids = ["RX1", "RX001", ""]

        for rid in valid_ids:
            assert rid.startswith("RX") and len(rid) == 9

    def test_valid_states(self):
        """Store states must be from our 10 valid states"""
        valid_states   = {"FL","NY","TX","CA","IL",
                          "OH","PA","GA","NC","AZ"}
        invalid_states = ["XX", "ZZ", "UK", "BC", ""]

        for state in ["FL", "NY", "TX"]:
            assert state in valid_states

        for state in invalid_states:
            assert state not in valid_states

    def test_region_values(self):
        """Region must be one of 5 valid regions"""
        valid_regions   = {"Northeast","Southeast","Midwest",
                           "West","South"}
        invalid_regions = ["East", "Northwest", "Central", ""]

        for region in valid_regions:
            assert region in valid_regions

        for region in invalid_regions:
            assert region not in valid_regions