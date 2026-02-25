import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TicketProcessor:
    def __init__(self, 
                 input_path: str, 
                 output_path: str,
                 delimiter: str = ",") -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.delimiter = delimiter
        self.df = None

    def load_tickets(self) -> None:
        try:
            logger.info(f"Trying to read CSV at path: {self.input_path}")
            self.df = pd.read_csv(self.input_path, delimiter=self.delimiter)
            logger.info("CSV read successfully")
        except Exception as e:
            logger.error(f"Unable to load CSV at path: {self.input_path}. Message: {str(e)}")
            raise RuntimeError("Unable to read CSV") from e
    
    def save_tickets(self, evaluated_df: pd.DataFrame) -> None:
        try:
            logger.info(f"Trying to save CSV at path: {self.output_path}")
            evaluated_df.to_csv(self.output_path)
            logger.info("CSV file saved successfully")
        except Exception as e:
            logger.error(f"Unable to save CSV at path: {self.output_path}. Message: {str(e)}")
            raise RuntimeError("Unable to save CSV") from e