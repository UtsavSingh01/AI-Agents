
Traceback (most recent call last):
  File "/home/user/main.py", line 29, in <module>
    class Transaction:
  File "/home/user/main.py", line 33, in Transaction
    timestamp: datetime.datetime
NameError: name 'datetime' is not defined

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/user/main.py", line 199, in <module>
    except Exception as e:
NameError: name 'datetime' is not defined

Thought: The previous code failed because I used `datetime.datetime` without the correct import. I only imported `datetime` and `dataclasses`. The design document specified `from datetime import datetime`. I will correct the import statement and re-run the code. I should also ensure that the initial call to `self.deposit` in the `__init__` method is handled correctly, as it creates a transaction that requires the `datetime` module. The logic seems correct, the issue is purely with the import statement.I have identified a `NameError` in my previous attempt. The `Transaction` dataclass and the `Account` class methods use `datetime.datetime.now()`, but I only imported the `datetime` module itself, not the `datetime` class from within it. The design document correctly specifies `from datetime import datetime`. I will correct this import statement and provide the complete, self-contained `accounts.py` module.

```python
import dataclasses
from datetime import datetime

# 2.1. Custom Exceptions
class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than are owned."""
    pass

class UnknownSymbolError(Exception):
    """Raised when a price is requested for an unknown stock symbol."""
    pass

# 2.2. Price Oracle Function
def get_share_price(symbol: str) -> float:
    """
    Retrieves the current market price for a given stock symbol.

    This is a mock implementation for simulation purposes.

    Args:
        symbol (str): The stock symbol (e.g., 'AAPL').

    Returns:
        float: The current price per share.

    Raises:
        UnknownSymbolError: If the symbol is not in the mock database.
    """
    mock_prices = {
        "AAPL": 175.25,
        "TSLA": 250.80,
        "GOOGL": 140.50,
    }
    price = mock_prices.get(symbol.upper())
    if price is None:
        raise UnknownSymbolError(f"No price available for symbol '{symbol}'")
    return price

# 2.3. Data Structures
@dataclasses.dataclass(frozen=True)
class Transaction:
    """
    Represents a single, immutable transaction record.
    """
    timestamp: datetime
    type: str  # e.g., 'DEPOSIT', 'WITHDRAW', 'BUY', 'SELL'
    amount: float
    symbol: str | None = None
    quantity: int | None = None
    share_price: float | None = None

# 3. Class Design: Account
class Account:
    """
    Manages a user's trading account, including cash, holdings, and transactions.
    """

    def __init__(self, account_holder: str, initial_deposit: float = 0.0):
        """
        Initializes a new trading account.

        Args:
            account_holder (str): The name of the account holder.
            initial_deposit (float): The initial amount of cash to deposit. Must be non-negative.
        
        Raises:
            ValueError: if `initial_deposit` is negative.
        """
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")

        self.account_holder: str = account_holder
        self.cash_balance: float = 0.0
        self.total_deposited: float = 0.0
        self.holdings: dict[str, int] = {}
        self.transaction_history: list[Transaction] = []

        if initial_deposit > 0:
            # The deposit method handles the initial transaction logging
            self.deposit(initial_deposit)

    def deposit(self, amount: float) -> None:
        """
        Deposits cash into the account.

        Args:
            amount (float): The amount of cash to deposit. Must be positive.
        
        Raises:
            ValueError: If `amount` is not positive.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        
        self.cash_balance += amount
        self.total_deposited += amount
        
        transaction = Transaction(
            timestamp=datetime.now(),
            type='DEPOSIT',
            amount=amount
        )
        self.transaction_history.append(transaction)

    def withdraw(self, amount: float) -> None:
        """
        Withdraws cash from the account.

        Args:
            amount (float): The amount of cash to withdraw. Must be positive.

        Raises:
            ValueError: If the amount is not positive.
            InsufficientFundsError: If the withdrawal amount exceeds the cash balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.cash_balance:
            raise InsufficientFundsError(f"Cannot withdraw ${amount:.2f}: Insufficient funds.")

        self.cash_balance -= amount

        transaction = Transaction(
            timestamp=datetime.now(),
            type='WITHDRAW',
            amount=amount
        )
        self.transaction_history.append(transaction)

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Buys a specified quantity of shares for a given stock symbol.

        Args:
            symbol (str): The stock symbol to buy (e.g., 'AAPL').
            quantity (int): The number of shares to buy. Must be a positive integer.

        Raises:
            ValueError: If quantity is not a positive integer.
            UnknownSymbolError: If the stock symbol price cannot be retrieved.
            InsufficientFundsError: If the total cost of the shares exceeds the cash balance.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        price = get_share_price(symbol)
        total_cost = price * quantity

        if total_cost > self.cash_balance:
            raise InsufficientFundsError(
                f"Cannot buy {quantity} of {symbol.upper()} for ${total_cost:.2f}: Insufficient funds."
            )
        
        self.cash_balance -= total_cost
        normalized_symbol = symbol.upper()
        self.holdings[normalized_symbol] = self.holdings.get(normalized_symbol, 0) + quantity

        transaction = Transaction(
            timestamp=datetime.now(),
            type='BUY',
            amount=total_cost,
            symbol=normalized_symbol,
            quantity=quantity,
            share_price=price
        )
        self.transaction_history.append(transaction)

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of owned shares for a given stock symbol.

        Args:
            symbol (str): The stock symbol to sell (e.g., 'AAPL').
            quantity (int): The number of shares to sell. Must be a positive integer.

        Raises:
            ValueError: If quantity is not a positive integer.
            UnknownSymbolError: If the stock symbol price cannot be retrieved.
            InsufficientSharesError: If trying to sell more shares than currently held.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        normalized_symbol = symbol.upper()
        current_quantity = self.holdings.get(normalized_symbol, 0)

        if quantity > current_quantity:
            raise InsufficientSharesError(
                f"Cannot sell {quantity} shares of {normalized_symbol}: Only {current_quantity} are held."
            )
        
        price = get_share_price(symbol)
        total_proceeds = price * quantity

        self.cash_balance += total_proceeds
        self.holdings[normalized_symbol] -= quantity
        if self.holdings[normalized_symbol] == 0:
            del self.holdings[normalized_symbol]

        transaction = Transaction(
            timestamp=datetime.now(),
            type='SELL',
            amount=total_proceeds,
            symbol=normalized_symbol,
            quantity=quantity,
            share_price=price
        )
        self.transaction_history.append(transaction)

    def get_holdings_value(self) -> float:
        """
        Calculates the current market value of all shares held in the portfolio.

        Returns:
            float: The total current value of all owned shares.
        """
        total_value = 0.0
        for symbol, quantity in self.holdings.items():
            try:
                price = get_share_price(symbol)
                total_value += price * quantity
            except UnknownSymbolError:
                # Gracefully handle if a price is no longer available for a holding
                # Its value is considered 0 in this case.
                pass
        return total_value

    def get_portfolio_value(self) -> float:
        """
        Calculates the total value of the account (cash + current value of all holdings).

        Returns:
            float: The total value of the account.
        """
        return self.cash_balance + self.get_holdings_value()

    def get_profit_loss(self) -> float:
        """
        Calculates the total profit or loss of the account.

        The calculation is: (Current Total Portfolio Value - Total Cash Deposited).

        Returns:
            float: The profit (positive value) or loss (negative value).
        """
        return self.get_portfolio_value() - self.total_deposited

    def get_holdings_report(self) -> dict[str, int]:
        """
        Reports the current share holdings.

        Returns:
            dict[str, int]: A copy of the holdings dictionary.
        """
        return self.holdings.copy()

    def get_transaction_history(self) -> list[Transaction]:
        """
        Reports the full history of all transactions.

        Returns:
            list[Transaction]: A copy of the transaction history list.
        """
        return self.transaction_history.copy()
```