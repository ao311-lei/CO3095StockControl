from model.reservation import Reservation

RESERVATION_FILE = "src/data/reservations.txt"


class ReservationRepo:
    def __init__(self):
        # tests can set this to a temp file path
        self._io_file = None

    def set_io_file(self, path: str):
        """Allow tests to redirect file I/O without changing RESERVATION_FILE."""
        self._io_file = path

    def _path_for_io(self):
        # If tests configured a temp file, use it; otherwise use the default constant.
        return self._io_file or RESERVATION_FILE

    def save_reservation(self, reservation):
        with open(self._path_for_io(), "a", encoding="utf-8") as file:
            file.write(
                f"{reservation.reservation_id}|{reservation.order_id}|{reservation.sku}|"
                f"{reservation.quantity}|{reservation.created_by}|{reservation.created_at}|"
                f"{reservation.status}|{reservation.price}\n"
            )

    def get_all_reservations(self):
        reservations = []
        try:
            with open(self._path_for_io(), "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split("|")
                    if len(parts) != 8:
                        continue
                    reservations.append(
                        Reservation(
                            parts[0], parts[1], parts[2], parts[3],
                            parts[7], parts[4], parts[5], parts[6]
                        )
                    )
        except FileNotFoundError:
            return []
        return reservations

    def get_active_reserved_quantity(self, sku):
        total = 0
        for r in self.get_all_reservations():
            if r.sku == sku and r.status == "ACTIVE":
                total += int(r.quantity)
        return total

    def cancel_reservation(self, reservation_id):
        try:
            with open(self._path_for_io(), "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return False

        updated = False
        new_lines = []

        for line in lines:
            parts = line.strip().split("|")
            if len(parts) != 8:
                new_lines.append(line)
                continue

            if parts[0] == reservation_id and parts[6] == "ACTIVE":
                parts[6] = "CANCELLED"
                updated = True

            new_lines.append("|".join(parts) + "\n")

        if updated:
            with open(self._path_for_io(), "w", encoding="utf-8") as file:
                file.writelines(new_lines)

        return updated
