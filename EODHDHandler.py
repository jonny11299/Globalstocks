import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path


class EODHDHandler:
    def __init__(self):
        """Initialize the EODHD API handler."""
        load_dotenv()
        self._api_key = os.getenv('EODHD_API_KEY')
        self._daily_limit = int(os.getenv('EODHD_DAILY_LIMIT', 19))
        
        # Setup log directory and files
        self._log_dir = Path('logs')
        self._log_dir.mkdir(exist_ok=True)
        
        self._structured_log_file = self._log_dir / 'eodhd_log.json'
        self._raw_log_file = self._log_dir / 'eodhd_log_raw.json'
        self._daily_fields_file = self._log_dir / 'daily_fields.json'
        
        # Initialize log files if they don't exist
        self._initialize_log_files()
        
        # Load current call count
        self._call_count = self._get_today_call_count()
    
    def _initialize_log_files(self):
        """Create log files if they don't exist."""
        if not self._structured_log_file.exists():
            with open(self._structured_log_file, 'w') as f:
                json.dump([], f)
        
        if not self._raw_log_file.exists():
            with open(self._raw_log_file, 'w') as f:
                json.dump([], f)
        
        if not self._daily_fields_file.exists():
            with open(self._daily_fields_file, 'w') as f:
                json.dump({}, f)
    
    def _get_today_date(self):
        """Get today's date in EST as a string (YYYY-MM-DD)."""
        # EST is UTC-5 (no daylight saving)
        from datetime import timezone, timedelta
        est = timezone(timedelta(hours=-5))
        return datetime.now(est).strftime('%Y-%m-%d')
    
    def _get_today_call_count(self):
        """Get the number of API calls made today."""
        today = self._get_today_date()
        
        with open(self._daily_fields_file, 'r') as f:
            daily_data = json.load(f)
        
        if today not in daily_data:
            daily_data[today] = {'eodhd_calls': 0}
            with open(self._daily_fields_file, 'w') as f:
                json.dump(daily_data, f, indent=2)
        
        return daily_data[today].get('eodhd_calls', 0)
    
    def _increment_call_count(self):
        """Increment today's API call count."""
        today = self._get_today_date()
        
        with open(self._daily_fields_file, 'r') as f:
            daily_data = json.load(f)
        
        if today not in daily_data:
            daily_data[today] = {'eodhd_calls': 0}
        
        daily_data[today]['eodhd_calls'] += 1
        
        with open(self._daily_fields_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
        
        self._call_count += 1
    
    def _log_response(self, ticker, response_data, is_error=False):
        """Log the API response to both structured and raw log files."""
        timestamp = datetime.now().isoformat()
        
        # Structured log
        structured_entry = {
            'timestamp': timestamp,
            'ticker': ticker,
            'response': response_data
        }
        
        with open(self._structured_log_file, 'r') as f:
            logs = json.load(f)
        logs.append(structured_entry)
        with open(self._structured_log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        # Raw log
        raw_entry = {
            'timestamp': timestamp,
            'ticker': ticker,
            'raw_response': response_data
        }
        
        with open(self._raw_log_file, 'r') as f:
            raw_logs = json.load(f)
        raw_logs.append(raw_entry)
        with open(self._raw_log_file, 'w') as f:
            json.dump(raw_logs, f, indent=2)
    
    def remaining_calls(self):
        """Return the number of remaining API calls available today."""
        return max(0, self._daily_limit - self._call_count)
    
    def get_ticker_response(self, ticker_symbol):
        """
        Fetch fundamentals data for a given ticker symbol.
        
        Args:
            ticker_symbol (str): The ticker symbol (e.g., "NVDA.US")
        
        Returns:
            dict: The API response data, or None if limit reached or error
        
        Raises:
            Exception: If daily limit is reached
        """
        # Check if we've hit the daily limit
        if self._call_count >= self._daily_limit:
            raise Exception(f"Daily API call limit of {self._daily_limit} reached. "
                          f"Resets at 12am EST.")
        
        # Construct URL
        url = f"https://eodhd.com/api/fundamentals/{ticker_symbol}?api_token={self._api_key}&fmt=json"
        params = {
            'api_token': self._api_key,
            'fmt': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Check if we successfully reached the server
            # Count these status codes toward the limit
            if response.status_code in [200, 400, 401, 429]:
                self._increment_call_count()
            
            response.raise_for_status()  # Raise exception for 4xx/5xx
            
            data = response.json()
            self._log_response(ticker_symbol, data)
            return data
            
        except requests.exceptions.RequestException as e:
            # Network errors, DNS failures, timeouts - don't count
            error_data = {
                'error': str(e),
                'error_type': type(e).__name__
            }
            self._log_response(ticker_symbol, error_data, is_error=True)
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return None