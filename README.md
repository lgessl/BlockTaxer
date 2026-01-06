# BlockTaxer <img src="frontend/src/assets/blocktaxer_logo.svg" align="right" height="100" alt="" />

## A lightweight assistant for German crypto-tax reporting

BlockTaxer is an open-source project to help German individuals with crypto tax reporting. 
It features a modern web frontend and a FastAPI backend.

### Features
- **Coinbase CSV Support**: Imports and processes transaction data directly from Coinbase CSV exports
- **Staking Rewards Calculation**: Computes the total staking rewards earned in EUR for a specified calendar year
- **Monthly Distribution**: Breaks down staking rewards by month for detailed analysis
- **Realized and Taxable Gains**: Calculates realized gains from asset sales and determines taxable gains based on applicable tax rules and holding periods

More features to come in the future!

## Requirements
- Coinbase CSV export file containing transaction history

### Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/lgessl/blocktaxer.git
   cd blocktaxer
   ```

2. Set up the backend (Python, FastAPI):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend (Vite + React + TypeScript):
   ```bash
   cd ../frontend
   npm install
   ```

4. Start the backend server:
   ```bash
   cd ../backend
   uvicorn main:app --reload --port 8000
   ```

5. In a separate terminal, start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

6. Open your browser and navigate to `http://localhost:5173` (or the URL shown in the terminal in the previous step).

### Disclaimer
**This project is provided for informational and educational purposes only.**

- The code and calculations may contain errors or inaccuracies.
- The logic may not reflect the latest or correct interpretation of German tax law.
- The author is **not responsible** for any consequences, financial or otherwise, resulting from the use of this software.
- **No guarantee** is made regarding the correctness, completeness, or suitability of the results for tax filing or any other purpose.
- **Always consult a certified tax advisor** before making any tax-related decisions or filings.

By using this software, you agree that you do so at your own risk and that the author assumes no liability for any damages or losses.

### License
GPLv3