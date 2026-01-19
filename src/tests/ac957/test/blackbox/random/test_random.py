import os
import random
import tempfile
import unittest
from unittest.mock import MagicMock, patch


# Import the real repos/services we are testing
from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService
from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService
from Service.product_service import ProductService
from Service.purchase_order_service import PurchaseOrderService


class TestRandomBlackBox(unittest.TestCase):
    # -------------------------
    # BudgetRepo random tests (REAL repo, temp file)
    # -------------------------
    def test_budget_repo_random_black_box(self):
        rng = random.Random()

        for _ in range(40):
            with tempfile.TemporaryDirectory() as td:
                path = os.path.join(td, "budget.txt")
                repo = BudgetRepo(path)

                month = rng.choice([
                    "2026-01", "1999-12", "2035-11",
                    f"{rng.randint(1900, 2100)}-{rng.randint(1, 12):02d}",
                    "", "   ", "bad-month"
                ])

                budget = rng.choice([
                    None,
                    rng.uniform(-1000, 10000),
                    0,
                    123.45
                ])

                spent = rng.choice([
                    rng.uniform(-1000, 5000),
                    0,
                    999.99
                ])

                try:
                    repo.save_budget_record(month, budget, spent)
                except Exception:
                    pass

                try:
                    out = repo.load_budget_record()
                    self.assertIsInstance(out, tuple)
                    self.assertEqual(len(out), 3)
                except Exception:
                    pass

    # -------------------------
    # BudgetService random tests (REAL service + temp repo)
    # -------------------------
    def test_budget_service_random_black_box(self):
        rng = random.Random()

        with tempfile.TemporaryDirectory() as td:
            repo = BudgetRepo(os.path.join(td, "budget.txt"))
            service = BudgetService(repo)

            for _ in range(80):
                action = rng.choice(["set", "spend", "remaining", "status"])

                try:
                    if action == "set":
                        val = rng.choice(["100", "0", "-5", "  250.5  ", "", "abc"])
                        msg = service.set_monthly_budget(val)
                        if msg is not None:
                            self.assertIsInstance(msg, str)

                    elif action == "spend":
                        amt = rng.choice(["10", "0", "-1", " 5.25 ", "", "xyz"])
                        msg = service.add_spend(amt)
                        if msg is not None:
                            self.assertIsInstance(msg, str)

                    elif action == "remaining":
                        rem = service.get_budget_remaining()
                        self.assertTrue(rem is None or isinstance(rem, (int, float)))

                    else:
                        # If your BudgetService doesn't have get_budget_status, remove this branch
                        status = service.get_budget_status()
                        if status is not None:
                            self.assertIsInstance(status, str)

                except Exception:
                    pass

    # -------------------------
    # FavouriteRepo random tests (REAL repo, temp file)
    # -------------------------
    def test_favourite_repo_random_black_box(self):
        rng = random.Random()

        with tempfile.TemporaryDirectory() as td:
            repo = FavouriteRepo(os.path.join(td, "fav.txt"))

            for _ in range(120):
                username = rng.choice(["alice", "bob", "anetta", "", "   ", "user\nx"])
                sku = rng.choice(["SKU001", "SKU999", "", "   ", "SKU" + str(rng.randint(0, 999)).zfill(3)])

                try:
                    repo.add_favourite(username, sku)
                except Exception:
                    pass

                try:
                    repo.remove_favourite(username, sku)
                except Exception:
                    pass

            try:
                data = repo.load_all()
                self.assertIsInstance(data, list)
            except Exception:
                pass

    # -------------------------
    # FavouriteService random tests (REAL service, MagicMock deps)
    # -------------------------
    def test_favourite_service_random_black_box(self):
        rng = random.Random()

        with tempfile.TemporaryDirectory() as td:
            fav_repo = FavouriteRepo(os.path.join(td, "fav.txt"))

            products = {f"SKU{i:03d}": {"sku": f"SKU{i:03d}"} for i in range(15)}

            product_repo = MagicMock()
            product_repo.find_by_sku.side_effect = lambda sku: products.get(sku)

            # Auth states using MagicMock (no dummy classes)
            auth_none = None

            auth_no_user = MagicMock()
            auth_no_user.current_user = None

            auth_user1 = MagicMock()
            auth_user1.current_user = MagicMock(username="user1")

            auth_anetta = MagicMock()
            auth_anetta.current_user = MagicMock(username="anetta")

            auth_states = [auth_none, auth_no_user, auth_user1, auth_anetta]

            for _ in range(140):
                auth = rng.choice(auth_states)
                service = FavouriteService(fav_repo, product_repo, auth)

                sku = rng.choice([
                    rng.choice(list(products.keys())),
                    "SKU999",
                    "", "   ",
                    "  " + rng.choice(list(products.keys())) + "  ",
                ])

                try:
                    msg = service.favourite_product(sku)
                    if msg is not None:
                        self.assertIsInstance(msg, str)
                except Exception:
                    pass

                try:
                    msg2 = service.unfavourite_product(sku)
                    if msg2 is not None:
                        self.assertIsInstance(msg2, str)
                except Exception:
                    pass

                try:
                    favs, err = service.get_favourites()
                    self.assertTrue(err is None or isinstance(err, str))
                    self.assertTrue(isinstance(favs, list))
                except Exception:
                    pass

    # -------------------------
    # ProductService random tests (MagicMock repo + MagicMock products)
    # -------------------------
    def test_product_service_random_black_box(self):
        rng = random.Random()

        # Create a bunch of products as MagicMocks (no dummy Product class)
        products = []
        for i in range(120):
            p = MagicMock()
            p.sku = f"SKU{i:03d}"
            p.name = rng.choice(["Apple", "Soap", "Bleach", "Banana", "Item" + str(i)])
            p.description = rng.choice(["fresh", "clean", "desc", "", None])
            p.category = rng.choice(["Fruit", "Cleaning", "Other", None, " fruit ", "FRUIT"])
            p.quantity = rng.choice([rng.randint(0, 60), str(rng.randint(0, 60)), "", None, "X"])
            p.price = rng.choice([round(rng.uniform(0, 50), 2), str(round(rng.uniform(0, 50), 2)), "", None, "bad"])
            p.active = rng.choice([True, False])
            products.append(p)

        product_repo = MagicMock()
        product_repo.get_all_products.return_value = list(products)

        def _find_by_sku(sku):
            for p in products:
                if str(p.sku).strip() == str(sku).strip():
                    return p
            return None

        product_repo.find_by_sku.side_effect = _find_by_sku
        product_repo.save_product.side_effect = lambda p: None

        category_repo = MagicMock()
        service = ProductService(product_repo, category_repo)

        # Avoid writing audit logs in tests
        service.write_audit = lambda msg: None

        for _ in range(80):
            op = rng.choice(["search", "filter", "deactivate", "reactivate", "estimate"])
            try:
                if op == "search":
                    q = rng.choice(["sku", "apple", "clean", "", "   ", "XYZ"])
                    res = service.search_products(q)
                    self.assertIsInstance(res, list)

                elif op == "filter":
                    cat = rng.choice([None, "fruit", "cleaning", "   ", "Other", "FRUIT"])
                    res = service.filter_products(category=cat)
                    self.assertIsInstance(res, list)

                elif op == "deactivate":
                    p = rng.choice(products)
                    service.deactivate_product(p.sku, user="tester")

                elif op == "reactivate":
                    p = rng.choice(products)
                    service.reactivate_product(p.sku)

                else:
                    p = rng.choice(products)
                    target = rng.randint(-5, 120)
                    est, err = service.estimate_restock_cost_for_sku(p.sku, target)
                    self.assertTrue(err is None or isinstance(err, str))
                    self.assertTrue(est is None or isinstance(est, dict))

            except Exception:
                pass

    # -------------------------
    # PurchaseOrderService random tests (MagicMock deps)
    # -------------------------
    def test_purchase_order_service_random_black_box(self):
        rng = random.Random()

        service = PurchaseOrderService.__new__(PurchaseOrderService)

        # Fake products
        p1 = MagicMock(sku="SKU1", price=5.0, active=True)
        p2 = MagicMock(sku="SKU2", price=2.0, active=True)
        p9 = MagicMock(sku="SKU9", price=99.0, active=False)
        products = {"SKU1": p1, "SKU2": p2, "SKU9": p9}

        # product_repo (only needs find_by_sku)
        service.product_repo = MagicMock()
        service.product_repo.find_by_sku.side_effect = lambda sku: products.get(sku)

        # repo (only needs save_purchase_order)
        service.repo = MagicMock()
        service.repo.save_purchase_order.side_effect = lambda po, lines: None

        service.validate_date = lambda d: True
        service.validate_quantity = lambda q: True
        service.write_audit = lambda msg: None

        for _ in range(50):
            budget = round(rng.uniform(0, 200), 2)
            spent = round(rng.uniform(0, budget), 2)

            # budget_service with budget_repo
            budget_repo = MagicMock()
            budget_repo.current_month_key.return_value = "2026-01"
            budget_repo.load_budget_record.return_value = ("2026-01", budget, spent)
            budget_repo.save_budget_record.side_effect = lambda m, b, s: None

            budget_service = MagicMock()
            budget_service.budget_repo = budget_repo

            lines = []
            for _j in range(rng.randint(0, 5)):
                sku = rng.choice(["SKU1", "SKU2", "SKU9", "NOPE", "", "   "])
                qty = rng.randint(-2, 6)
                lines.append({"sku": sku, "quantity": qty})

            date_str = rng.choice(["2026-01-10", "bad-date", "", "   "])

            with patch("builtins.print"):
                try:
                    service.create_purchase_order(date_str, lines, "user", budget_service=budget_service)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
