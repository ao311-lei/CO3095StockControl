from model.return_item import ReturnItem

class ReturnRepo:
    def __init__(self, filename="returns.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def save_return(self, r: ReturnItem):
        # Format:
        # return_id|sku|qty|condition|decision|reason
        with open(self.filename, "a") as file:
            file.write(
                str(r.return_id) + "|" +
                str(r.sku) + "|" +
                str(r.quantity) + "|" +
                str(r.condition) + "|" +
                str(r.decision) + "|" +
                str(r.reason) + "\n"
            )
