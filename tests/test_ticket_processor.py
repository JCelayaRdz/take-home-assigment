import pytest
import pandas as pd
import os
from ticket_processor import TicketProcessor

class TestTicketProcessor:
    @pytest.fixture
    def processor(self, tmp_path):
        input_csv = tmp_path / "tickets.csv"
        output_csv = tmp_path / "tickets_evaluated.csv"
        
        df = pd.DataFrame({
            "ticket": ["My order is late"],
            "reply": ["We are working on it"]
        })
        df.to_csv(input_csv, index=False)
        
        return TicketProcessor(str(input_csv), str(output_csv))

    def test_load_tickets_returns_list_of_dicts(self, processor):
        rows = processor.load_tickets()
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0]["ticket"] == "My order is late"

    def test_save_results_creates_correct_csv(self, processor):
        results = [{
            "ticket": "T1", 
            "reply": "R1", 
            "content_score": 4.5, 
            "content_explanation": "Good",
            "format_score": 5.0, 
            "format_explanation": "Perfect"
        }]
        processor.save_results(results)
        
        assert os.path.exists(processor.output_path)
        saved_df = pd.read_csv(processor.output_path)
        
        expected_cols = ["ticket", "reply", "content_score", "content_explanation", "format_score", "format_explanation"]
        assert list(saved_df.columns) == expected_cols
        assert saved_df.iloc[0]["content_score"] == 4.5