# Custom Exceptions
class OrderError(Exception):
    """Base class for order processing errors."""
    pass

class OutOfStockError(OrderError):
    """Raised when a product is out of stock."""
    def __init__(self, product_id, requested, available):
        message = (f"Product {product_id} is out of stock: "
                   f"requested {requested}, available {available}.")
        super().__init__(message)

class PaymentDeclinedError(OrderError):
    """Raised when a payment is declined by the payment gateway."""
    def __init__(self, reason):
        message = f"Payment declined: {reason}"
        super().__init__(message)

class InvalidShippingAddressError(OrderError):
    """Raised when the shipping address is invalid."""
    def __init__(self, address):
        message = f"Invalid shipping address: '{address}'."
        super().__init__(message)


# System Components
class Inventory:
    def __init__(self, stock):
        # stock: dict mapping product_id to quantity available
        self.stock = stock

    def reserve(self, product_id, quantity):
        available = self.stock.get(product_id, 0)
        if quantity > available:
            raise OutOfStockError(product_id, quantity, available)
        self.stock[product_id] -= quantity
        print(f"[Inventory] Reserved {quantity} unit(s) of {product_id}.")

class PaymentProcessor:
    def __init__(self, user_balance):
        self.user_balance = user_balance

    def charge(self, amount):
        # Simulate external payment gateway call
        if amount > self.user_balance:
            raise PaymentDeclinedError("Insufficient funds")
        # Could also decline for expired card, fraud, etc.
        self.user_balance -= amount
        print(f"[Payment] Charged ${amount:.2f}. Remaining balance: ${self.user_balance:.2f}.")

class ShippingService:
    def validate_address(self, address):
        # Simple validation: must contain a house number and a postal code
        parts = address.strip().split()
        if len(parts) < 2 or not parts[-1].isdigit():
            raise InvalidShippingAddressError(address)
        print(f"[Shipping] Address '{address}' is valid.")


# Order Processing Function
def process_order(product_id, qty, price_per_unit, shipping_address,
                  inventory, payment_processor, shipping_service):
    try:
        # 1. Check and reserve stock
        inventory.reserve(product_id, qty)

        # 2. Validate shipping address
        shipping_service.validate_address(shipping_address)

        # 3. Charge payment
        total = qty * price_per_unit
        payment_processor.charge(total)

    except OutOfStockError as e:
        print(f"Order failed: {e}")
    except InvalidShippingAddressError as e:
        print(f"Order failed: {e}")
    except PaymentDeclinedError as e:
        print(f"Order failed: {e}")
    else:
        print("Order succeeded! 🎉")
    finally:
        print("Order process complete.\n")


# Example Execution
if __name__ == "__main__":
    inv = Inventory(stock={"SKU123": 5, "SKU999": 0})
    pay = PaymentProcessor(user_balance=100.00)
    ship = ShippingService()

    # 1. Successful order
    process_order(
        product_id="SKU123",
        qty=2,
        price_per_unit=20.00,
        shipping_address="10 Merdeka St 10110",
        inventory=inv,
        payment_processor=pay,
        shipping_service=ship
    )

    # 2. Out of stock
    process_order(
        product_id="SKU999",
        qty=1,
        price_per_unit=50.00,
        shipping_address="10 Merdeka St 10110",
        inventory=inv,
        payment_processor=pay,
        shipping_service=ship
    )

    # 3. Invalid address
    process_order(
        product_id="SKU123",
        qty=1,
        price_per_unit=20.00,
        shipping_address="Boulevard Raya",
        inventory=inv,
        payment_processor=pay,
        shipping_service=ship
    )

    # 4. Insufficient balance
    process_order(
        product_id="SKU123",
        qty=3,
        price_per_unit=30.00,
        shipping_address="10 Merdeka St 10110",
        inventory=inv,
        payment_processor=pay,
        shipping_service=ship
    )
