```python
import unittest
from unittest.mock import patch, Mock
from datetime import datetime

# Import the module to be tested.
# Assuming the file is named accounts.py and is in the same directory.
from accounts import (
    Account,
    Transaction,
    get_share_price,
    InsufficientFundsError,
    InsufficientSharesError,
    UnknownSymbolError,
)

class TestGetSharePrice(unittest.TestCase):
    """Tests for the get_share_price function."""

    def test_get_known_symbol(self):
        """Test retrieving the price for a known symbol."""
        self.assertEqual(get_share_price("AAPL"), 175.25)
        self.assertEqual(get_share_price("TSLA"), 250.80)

    def test_get_known_symbol_case_insensitive(self):
        """Test that symbol lookup is case-insensitive."""
        self.assertEqual(get_share_price("aapl"), 175.25)
        self.assertEqual(get_share_price("GoOgL"), 140.50)

    def test_get_unknown_symbol(self):
        """Test that UnknownSymbolError is raised for an unknown symbol."""
        with self.assertRaises(UnknownSymbolError):
            get_share_price("XYZ")
        with self.assertRaisesRegex(UnknownSymbolError, "No price available for symbol 'XYZ'"):
            get_share_price("XYZ")


class TestAccount(unittest.TestCase):
    """Tests for the Account class."""

    def setUp(self):
        """Set up a common account instance for tests before each test."""
        self.account = Account("John Doe", initial_deposit=10000)

    # 1. Initialization Tests
    def test_init_success_with_deposit(self):
        """Test successful initialization with an initial deposit."""
        acc = Account("Jane Smith", 500.75)
        self.assertEqual(acc.account_holder, "Jane Smith")
        self.assertEqual(acc.cash_balance, 500.75)
        self.assertEqual(acc.total_deposited, 500.75)
        self.assertEqual(len(acc.transaction_history), 1)
        self.assertEqual(acc.transaction_history[0].type, 'DEPOSIT')
        self.assertEqual(acc.transaction_history[0].amount, 500.75)

    def test_init_success_no_deposit(self):
        """Test successful initialization with no initial deposit."""
        acc = Account("Bob Brown")
        self.assertEqual(acc.account_holder, "Bob Brown")
        self.assertEqual(acc.cash_balance, 0.0)
        self.assertEqual(acc.total_deposited, 0.0)
        self.assertEqual(len(acc.transaction_history), 0)

    def test_init_negative_deposit(self):
        """Test that initialization fails with a negative deposit."""
        with self.assertRaisesRegex(ValueError, "Initial deposit cannot be negative."):
            Account("Bad Actor", -100)

    # 2. Deposit and Withdraw Tests
    def test_deposit_positive_amount(self):
        """Test a valid deposit operation."""
        initial_balance = self.account.cash_balance
        initial_deposited = self.account.total_deposited
        self.account.deposit(500)
        self.assertEqual(self.account.cash_balance, initial_balance + 500)
        self.assertEqual(self.account.total_deposited, initial_deposited + 500)
        self.assertEqual(self.account.transaction_history[-1].type, 'DEPOSIT')
        self.assertEqual(self.account.transaction_history[-1].amount, 500)

    def test_deposit_non_positive_amount(self):
        """Test depositing a zero or negative amount raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            self.account.deposit(0)
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive."):
            self.account.deposit(-100)

    def test_withdraw_valid_amount(self):
        """Test a valid withdrawal operation."""
        initial_balance = self.account.cash_balance
        initial_deposited = self.account.total_deposited # Should not change
        self.account.withdraw(1000)
        self.assertEqual(self.account.cash_balance, initial_balance - 1000)
        self.assertEqual(self.account.total_deposited, initial_deposited)
        self.assertEqual(self.account.transaction_history[-1].type, 'WITHDRAW')
        self.assertEqual(self.account.transaction_history[-1].amount, 1000)

    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds raises InsufficientFundsError."""
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(self.account.cash_balance + 1)

    def test_withdraw_non_positive_amount(self):
        """Test withdrawing a zero or negative amount raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            self.account.withdraw(0)
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive."):
            self.account.withdraw(-50)

    # 3. Share Trading Tests
    def test_buy_shares_success(self):
        """Test a successful share purchase."""
        self.account.buy_shares("AAPL", 10) # Cost = 175.25 * 10 = 1752.5
        self.assertAlmostEqual(self.account.cash_balance, 10000 - 1752.5)
        self.assertEqual(self.account.holdings["AAPL"], 10)

        last_tx = self.account.transaction_history[-1]
        self.assertEqual(last_tx.type, 'BUY')
        self.assertEqual(last_tx.symbol, 'AAPL')
        self.assertEqual(last_tx.quantity, 10)
        self.assertEqual(last_tx.share_price, 175.25)
        self.assertAlmostEqual(last_tx.amount, 1752.5)

    def test_buy_shares_insufficient_funds(self):
        """Test buying shares with insufficient funds raises InsufficientFundsError."""
        with self.assertRaises(InsufficientFundsError):
            self.account.buy_shares("TSLA", 100) # Cost would be > 10000

    def test_buy_shares_unknown_symbol(self):
        """Test buying shares of an unknown symbol raises UnknownSymbolError."""
        with self.assertRaises(UnknownSymbolError):
            self.account.buy_shares("UNKNOWN", 5)

    def test_buy_shares_invalid_quantity(self):
        """Test buying with a non-positive integer quantity raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Quantity must be a positive integer."):
            self.account.buy_shares("AAPL", 0)
        with self.assertRaisesRegex(ValueError, "Quantity must be a positive integer."):
            self.account.buy_shares("AAPL", -5)
        with self.assertRaisesRegex(ValueError, "Quantity must be a positive integer."):
            self.account.buy_shares("AAPL", 2.5)

    def test_sell_shares_success(self):
        """Test a successful share sale."""
        self.account.buy_shares("GOOGL", 5) # Cost = 140.50 * 5 = 702.5
        self.assertAlmostEqual(self.account.cash_balance, 10000 - 702.5)

        self.account.sell_shares("GOOGL", 2) # Proceeds = 140.50 * 2 = 281.0
        self.assertAlmostEqual(self.account.cash_balance, 10000 - 702.5 + 281.0)
        self.assertEqual(self.account.holdings["GOOGL"], 3)

        last_tx = self.account.transaction_history[-1]
        self.assertEqual(last_tx.type, 'SELL')
        self.assertEqual(last_tx.symbol, 'GOOGL')
        self.assertEqual(last_tx.quantity, 2)
        self.assertEqual(last_tx.share_price, 140.50)
        self.assertAlmostEqual(last_tx.amount, 281.0)

    def test_sell_all_shares_removes_from_holdings(self):
        """Test that selling all shares of a stock removes the symbol from holdings."""
        self.account.buy_shares("TSLA", 10)
        self.assertIn("TSLA", self.account.holdings)
        self.account.sell_shares("TSLA", 10)
        self.assertNotIn("TSLA", self.account.holdings)

    def test_sell_shares_insufficient_shares(self):
        """Test selling more shares than owned raises InsufficientSharesError."""
        self.account.buy_shares("AAPL", 5)
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares("AAPL", 6)

    def test_sell_shares_not_owned(self):
        """Test selling shares of a stock that is not owned raises InsufficientSharesError."""
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares("TSLA", 1)

    def test_sell_shares_invalid_quantity(self):
        """Test selling with a non-positive integer quantity raises ValueError."""
        self.account.buy_shares("AAPL", 5)
        with self.assertRaisesRegex(ValueError, "Quantity must be a positive integer."):
            self.account.sell_shares("AAPL", 0)
        with self.assertRaisesRegex(ValueError, "Quantity must be a positive integer."):
            self.account.sell_shares("AAPL", -1)

    # 4. Reporting and Value Calculation Tests
    def test_get_holdings_value(self):
        """Test calculation of total holdings value."""
        # Buy AAPL: 10 * 175.25 = 1752.5
        # Buy GOOGL: 5 * 140.50 = 702.5
        # Total Value = 2455.0
        self.account.buy_shares("AAPL", 10)
        self.account.buy_shares("GOOGL", 5)
        self.assertAlmostEqual(self.account.get_holdings_value(), 2455.0)

    def test_get_holdings_value_no_holdings(self):
        """Test holdings value is zero when no shares are owned."""
        self.assertEqual(self.account.get_holdings_value(), 0)

    @patch('accounts.get_share_price')
    def test_get_holdings_value_with_unknown_symbol_graceful(self, mock_get_price):
        """Test that a held stock with a now-unknown price is valued at 0."""
        self.account.buy_shares("AAPL", 10)
        self.account.buy_shares("GOOGL", 5)
        
        # Simulate GOOGL price becoming unavailable
        def side_effect(symbol):
            if symbol == "GOOGL":
                raise UnknownSymbolError
            return 175.25 # AAPL price

        mock_get_price.side_effect = side_effect
        # Should only return the value of AAPL
        self.assertAlmostEqual(self.account.get_holdings_value(), 1752.5)


    def test_get_portfolio_value(self):
        """Test calculation of total portfolio value (cash + holdings)."""
        self.account.buy_shares("AAPL", 10) # cost = 1752.5, cash = 8247.5
        # Holdings value = 1752.5, Cash = 8247.5 -> Total Portfolio = 10000
        self.assertAlmostEqual(self.account.get_portfolio_value(), 10000.0)

        # Simulate a price change using a mock
        with patch('accounts.get_share_price') as mock_price:
            mock_price.return_value = 200.0
            # Holdings value = 10 * 200 = 2000, Cash = 8247.5 -> Total = 10247.5
            self.assertAlmostEqual(self.account.get_portfolio_value(), 10247.5)

    def test_get_profit_loss(self):
        """Test calculation of profit and loss."""
        # Initial state: portfolio value = 10000, deposited = 10000 -> P/L = 0
        self.assertAlmostEqual(self.account.get_profit_loss(), 0)

        self.account.buy_shares("AAPL", 10) # cash=8247.5, holdings=1752.5
        self.assertAlmostEqual(self.account.get_profit_loss(), 0) # No price change

        # Simulate a price increase
        with patch('accounts.get_share_price') as mock_price:
            mock_price.return_value = 180.0
            # Portfolio value = (10 * 180.0) + 8247.5 = 10047.5
            # P/L = 10047.5 - 10000 = 47.5
            self.assertAlmostEqual(self.account.get_profit_loss(), 47.5)

        # Simulate a price decrease
        with patch('accounts.get_share_price') as mock_price:
            mock_price.return_value = 170.0
            # Portfolio value = (10 * 170.0) + 8247.5 = 9947.5
            # P/L = 9947.5 - 10000 = -52.5
            self.assertAlmostEqual(self.account.get_profit_loss(), -52.5)

    # 5. Getters and Copying Tests
    def test_get_holdings_report_is_copy(self):
        """Test that get_holdings_report returns a copy, not a reference."""
        self.account.buy_shares("AAPL", 1)
        holdings_report = self.account.get_holdings_report()
        self.assertIsNot(holdings_report, self.account.holdings)
        holdings_report["AAPL"] = 999
        self.assertEqual(self.account.holdings["AAPL"], 1)

    def test_get_transaction_history_is_copy(self):
        """Test that get_transaction_history returns a copy, not a reference."""
        history_copy = self.account.get_transaction_history()
        self.assertIsNot(history_copy, self.account.transaction_history)
        
        mock_transaction = Mock(spec=Transaction)
        history_copy.append(mock_transaction)
        # Original should have 1 item (initial deposit), copy has 2.
        self.assertEqual(len(self.account.transaction_history), 1)
        self.assertNotEqual(len(history_copy), len(self.account.transaction_history))

    # 6. Mocking datetime for predictable timestamps
    @patch('accounts.datetime')
    def test_transaction_timestamp(self, mock_datetime):
        """Test that transactions are timestamped correctly using a mocked time."""
        fake_now = datetime(2023, 10, 27, 10, 30, 0)
        mock_datetime.now.return_value = fake_now

        acc = Account("Timestamp Test", 100)
        self.assertEqual(acc.transaction_history[0].timestamp, fake_now)

        acc.withdraw(10)
        self.assertEqual(acc.transaction_history[1].timestamp, fake_now)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```