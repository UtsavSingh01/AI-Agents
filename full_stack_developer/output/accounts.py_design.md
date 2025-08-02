# Design Document: `accounts.py` Module

**Author:** Engineering Lead
**Date:** 2023-10-27
**Version:** 1.0

## 1. Overview

This document provides the detailed design for the `accounts.py` module. This module will serve as a self-contained backend for a simple trading simulation platform. It provides an `Account` class to manage user funds, share trading, and reporting. The entire system is encapsulated within this single Python module, making it easy to integrate, test, or build a UI upon.

The design includes the main `Account` class, custom exception classes for clear error handling, a data class for transaction records, and a mock function for retrieving share prices.

## 2. Module Contents: `accounts.py`

The module will be structured as follows:

1.  **Imports**: Necessary libraries (`datetime`, `dataclasses`).
2.  **Custom Exceptions**: Custom exception classes for specific error conditions.
3.  **Price Oracle Function**: `get_share_price(symbol)` function.
4.  **Data Structures**: A `Transaction` dataclass to represent financial activities.
5.  **Main Class**: The `Account` class, which encapsulates all core logic.

---

### 2.1. Custom Exceptions

To provide specific and catchable errors, we will define the following custom exception classes inheriting from `Exception`.

```python
class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to lack of cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when trying to sell more shares than are owned."""
    pass

class UnknownSymbolError(Exception):
    """Raised when a price is requested for an unknown stock symbol."""
    pass
```

### 2.2. Price Oracle Function

This function simulates an external service that provides stock prices. It's defined at the module level. For this version, it returns fixed prices for a few known symbols.

```python
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
    # Test implementation with fixed prices
    mock_prices = {
        "AAPL": 175.25,
        "TSLA": 250.80,
        "GOOGL": 140.50,
    }
    price = mock_prices.get(symbol.upper())
    if price is None:
        raise UnknownSymbolError(f"No price available for symbol '{symbol}'")
    return price
```

### 2.3. Data Structures

We will use a `dataclass` to represent a single transaction. This provides a clean, immutable structure for our transaction history log.

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
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
```

---

## 3. Class Design: `Account`

This class is the core of the module. An instance of `Account` represents a single user's portfolio, including their cash balance, share holdings, and transaction history.

### 3.1. Class Definition

```python
class Account:
    """
    Manages a user's trading account, including cash, holdings, and transactions.
    """
```

### 3.2. Instance Attributes

| Attribute Name        | Type                 | Description                                                                                              |
| --------------------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| `account_holder`      | `str`                | The name of the person who owns the account.                                                             |
| `cash_balance`        | `float`              | The current amount of cash available for trading or withdrawal.                                          |
| `total_deposited`     | `float`              | The cumulative total of all cash ever deposited into the account. Used for P/L calculation.              |
| `holdings`            | `dict[str, int]`     | A dictionary mapping stock symbols to the quantity of shares owned. e.g., `{'AAPL': 100}`.               |
| `transaction_history` | `list[Transaction]`  | A chronological list of all `Transaction` objects associated with this account.                          |

### 3.3. Methods

#### 3.3.1. `__init__`

```python
def __init__(self, account_holder: str, initial_deposit: float = 0.0):
    """
    Initializes a new trading account.

    Args:
        account_holder (str): The name of the account holder.
        initial_deposit (float): The initial amount of cash to deposit. Must be non-negative.
    """
```

*   **Description**: Creates a new account, sets the initial state for all attributes, and logs the initial deposit (if any) as the first transaction.
*   **Raises**: `ValueError` if `initial_deposit` is negative.

#### 3.3.2. `deposit`

```python
def deposit(self, amount: float) -> None:
    """
    Deposits cash into the account.

    Args:
        amount (float): The amount of cash to deposit. Must be positive.
    """
```

*   **Description**: Increases the `cash_balance` and `total_deposited`. It logs a 'DEPOSIT' transaction.
*   **Raises**: `ValueError` if `amount` is not positive.

#### 3.3.3. `withdraw`

```python
def withdraw(self, amount: float) -> None:
    """
    Withdraws cash from the account.

    Args:
        amount (float): The amount of cash to withdraw. Must be positive.

    Raises:
        ValueError: If the amount is not positive.
        InsufficientFundsError: If the withdrawal amount exceeds the cash balance.
    """
```

*   **Description**: Decreases the `cash_balance`. It validates that the withdrawal does not result in a negative balance. It logs a 'WITHDRAW' transaction. Note: This does **not** affect `total_deposited`.

#### 3.3.4. `buy_shares`

```python
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
```

*   **Description**:
    1.  Fetches the current price using `get_share_price(symbol)`.
    2.  Calculates the total cost (`price * quantity`).
    3.  Checks if `cash_balance` is sufficient.
    4.  If sufficient, it subtracts the cost from `cash_balance`, adds/updates the shares in the `holdings` dictionary, and logs a 'BUY' transaction.

#### 3.3.5. `sell_shares`

```python
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
```

*   **Description**:
    1.  Checks if the symbol exists in `holdings` and if the owned quantity is sufficient.
    2.  Fetches the current price using `get_share_price(symbol)`.
    3.  Calculates the total proceeds (`price * quantity`).
    4.  Increases `cash_balance` by the proceeds, reduces the share count in `holdings` (and removes the symbol if quantity becomes zero), and logs a 'SELL' transaction.

#### 3.3.6. `get_holdings_value`

```python
def get_holdings_value(self) -> float:
    """
    Calculates the current market value of all shares held in the portfolio.

    Returns:
        float: The total current value of all owned shares.
    """
```
*   **Description**: Iterates through the `holdings` dictionary. For each symbol, it fetches the current price via `get_share_price()` and multiplies it by the quantity owned. It sums these values to get the total market value of the equity portfolio. It gracefully handles any symbols in holdings that may no longer have a price available (treats their value as 0).

#### 3.3.7. `get_portfolio_value`

```python
def get_portfolio_value(self) -> float:
    """
    Calculates the total value of the account (cash + current value of all holdings).

    Returns:
        float: The total value of the account.
    """
```

*   **Description**: Returns the sum of `self.cash_balance` and the result of `self.get_holdings_value()`.

#### 3.3.8. `get_profit_loss`

```python
def get_profit_loss(self) -> float:
    """
    Calculates the total profit or loss of the account.

    The calculation is: (Current Total Portfolio Value - Total Cash Deposited).

    Returns:
        float: The profit (positive value) or loss (negative value).
    """
```

*   **Description**: Calculates P/L by subtracting the `total_deposited` from the current `get_portfolio_value()`. This reflects the overall performance against the capital invested.

#### 3.3.9. `get_holdings_report`

```python
def get_holdings_report(self) -> dict[str, int]:
    """
    Reports the current share holdings.

    Returns:
        dict[str, int]: A copy of the holdings dictionary.
    """
```

*   **Description**: A simple getter method that returns a copy of the `holdings` dictionary to prevent external mutation of the internal state.

#### 3.3.10. `get_transaction_history`

```python
def get_transaction_history(self) -> list[Transaction]:
    """
    Reports the full history of all transactions.

    Returns:
        list[Transaction]: A copy of the transaction history list.
    """
```

*   **Description**: A simple getter method that returns a copy of the `transaction_history` list.