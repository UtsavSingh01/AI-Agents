#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from stock_recommendation.crew import StockRecommendation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """Run the StockRecommendation crew."""
    inputs ={
        'sector' :'Technology',
        'current_Date':str(datetime.now())
    }

    result = StockRecommendation().crew().kickoff(
        inputs=inputs,
    )
    print("Crew run completed.")
    print("Result:", result.raw)

if __name__ == "__main__":
    run()