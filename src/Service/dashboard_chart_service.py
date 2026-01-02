# src/Service/dashboard_chart_service.py

class DashboardChartService:
    def __init__(self, product_repo):
        self.product_repo = product_repo

    def _safe_int(self, value, default=0):
        try:
            return int(value)
        except:
            return default

    def _bar_line(self, label, value, max_value, width=25):
        # Simple text bar: ##### (count)
        if max_value <= 0:
            filled = 0
        else:
            filled = int((value / max_value) * width)

        return f"{label:<18} | " + ("#" * filled) + f" ({value})"

    def get_inventory_status_counts(self, threshold):
        # Inventory status: IN STOCK / LOW STOCK / OUT OF STOCK
        products = self.product_repo.get_all_products()

        in_stock = 0
        low_stock = 0
        out_of_stock = 0

        for p in products:
            # skip inactive if your system supports that
            if getattr(p, "active", True) is False:
                continue

            qty = self._safe_int(p.quantity)

            if qty == 0:
                out_of_stock += 1
            elif qty <= threshold:
                low_stock += 1
            else:
                in_stock += 1

        return {
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        }

    def get_stock_bucket_counts(self):
        # Stock level buckets: 0, 1-5, 6-20, 21+
        products = self.product_repo.get_all_products()
        buckets = {"0": 0, "1-5": 0, "6-20": 0, "21+": 0}

        for p in products:
            if getattr(p, "active", True) is False:
                continue

            qty = self._safe_int(p.quantity)

            if qty == 0:
                buckets["0"] += 1
            elif qty <= 5:
                buckets["1-5"] += 1
            elif qty <= 20:
                buckets["6-20"] += 1
            else:
                buckets["21+"] += 1

        return buckets

    def get_category_counts(self):
        # Category breakdown (all categories)
        products = self.product_repo.get_all_products()
        counts = {}

        for p in products:
            if getattr(p, "active", True) is False:
                continue

            if p.category is None or str(p.category).strip() == "":
                cat = "Uncategorised"
            else:
                cat = str(p.category).strip()

            if cat in counts:
                counts[cat] += 1
            else:
                counts[cat] = 1

        return counts

    def build_dashboard_chart_lines(self, threshold):
        lines = []
        lines.append("\n==============================")
        lines.append("     [ DASHBOARD CHARTS ]")
        lines.append("==============================")
        lines.append("Using low-stock threshold: " + str(threshold))
        lines.append("")

        # Chart 1: Inventory status
        status = self.get_inventory_status_counts(threshold)
        lines.append("--- Inventory Status ---")
        max_status = status["in_stock"]
        if status["low_stock"] > max_status:
            max_status = status["low_stock"]
        if status["out_of_stock"] > max_status:
            max_status = status["out_of_stock"]

        lines.append(self._bar_line("IN STOCK", status["in_stock"], max_status))
        lines.append(self._bar_line("LOW STOCK", status["low_stock"], max_status))
        lines.append(self._bar_line("OUT OF STOCK", status["out_of_stock"], max_status))
        lines.append("")

        # Chart 2: Stock buckets
        buckets = self.get_stock_bucket_counts()
        lines.append("--- Stock Level Buckets ---")
        max_bucket = 0
        for key in buckets:
            if buckets[key] > max_bucket:
                max_bucket = buckets[key]

        # print in a stable order
        lines.append(self._bar_line("0", buckets["0"], max_bucket))
        lines.append(self._bar_line("1-5", buckets["1-5"], max_bucket))
        lines.append(self._bar_line("6-20", buckets["6-20"], max_bucket))
        lines.append(self._bar_line("21+", buckets["21+"], max_bucket))
        lines.append("")

        # Chart 3: Category counts (top 5 to keep it short)
        counts = self.get_category_counts()
        lines.append("--- Product Categories (Top 5) ---")

        # Convert dict -> list of (cat, count) then sort manually (basic)
        items = []
        for cat in counts:
            items.append((cat, counts[cat]))

        # simple sort by count desc (lab-level)
        items.sort(key=lambda x: x[1], reverse=True)

        top = items[:5]
        if len(top) == 0:
            lines.append("(No categories found)")
        else:
            max_cat = 0
            for item in top:
                if item[1] > max_cat:
                    max_cat = item[1]

            for item in top:
                lines.append(self._bar_line(item[0][:18], item[1], max_cat))

        lines.append("==============================")
        return lines
