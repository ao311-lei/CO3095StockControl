from model.reservation import Reservation

RESERVATION_FILE = 'src/data/reservations.txt'


class ReservationRepo:
    def save_reservation(self, reservation):
        with open(RESERVATION_FILE, 'a') as file:
            file.write(f"{reservation.reservation_id}|{reservation.order_id}|{reservation.sku}|"
                       f"{reservation.quantity}|{reservation.created_by}|{reservation.created_at}|"
                       f"{reservation.status}|{reservation.price}\n"
                       )

    def get_all_reservations(self):
        reservations = []

        try:
            with open(RESERVATION_FILE, 'r') as file:
                for line in file:
                    parts = line.strip().split("|")
                    if len(parts) != 8:
                        continue

                    reservations.append(Reservation(
                        parts[0], parts[1], parts[2], parts[3],
                        parts[7], parts[4], parts[5], parts[6]
                     ))

        except FileNotFoundError:
            pass


        return reservations


    def get_active_reserved_quantity(self, sku):
        total = 0
        reservations = self.get_all_reservations()

        for r in reservations:
            if r.sku == sku and r.status == "ACTIVE":
                total += r.quantity

        return total


    def cancel_reservation(self, reservation_id):
        try:
            with open(RESERVATION_FILE, "r") as file:
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
            with open(RESERVATION_FILE, "w") as file:
                file.writelines(new_lines)

        return updated
