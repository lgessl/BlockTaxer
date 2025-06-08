import React, { useState } from 'react';
import { styles } from './AppStyles';
import { RewardsBarChart } from './RewardsBarChart';

function App() {
    const [file, setFile] = useState<File | null>(null);
    const [year, setYear] = useState<number>(new Date().getFullYear());
    const [result, setResult] = useState<number | null>(null);
    const [monthly, setMonthly] = useState<{ [month: number]: number } | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!file || !year) {
            setError('Please provide all inputs.');
            return;
        }
        setLoading(true);
        setError(null);
        setResult(null);
        setMonthly(null);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('year', year.toString());
        try {
            const res = await fetch('http://localhost:8000/staking-rewards-sum', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) throw new Error('Server error');
            const data = await res.json();
            setResult(data.staking_rewards_eur);
            setMonthly(data.monthly_rewards_eur || null);
        } catch (err) {
            setError('Failed to calculate.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.page}>
            <div style={styles.card}>
                <div style={styles.header}>
                    <img src="/src/assets/blocktaxer_logo.svg" alt="BlockTaxer Logo" style={styles.logo} />
                    <h2 style={styles.title}>BlockTaxer: Annual staking rewards</h2>
                </div>
                <form onSubmit={handleSubmit} style={styles.form}>
                    <div>
                        <label style={styles.label}>Coinbase transactions (CSV)</label>
                        <input type="file" accept=".csv" onChange={e => {
                            const files = e.target.files;
                            if (files && files[0]) setFile(files[0]);
                        }} style={styles.input} />
                    </div>
                    <div>
                        <label style={styles.labelBlock}>Calendar year</label>
                        <select
                            value={year}
                            onChange={e => setYear(Number(e.target.value))}
                            style={styles.select}
                        >
                            {Array.from({ length: new Date().getFullYear() - 2008 }, (_, i) => {
                                const y = new Date().getFullYear() - i;
                                return <option key={y} value={y}>{y}</option>;
                            })}
                        </select>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        style={loading ? { ...styles.button, ...styles.buttonDisabled } : styles.button}
                    >
                        {loading ? 'Calculating...' : 'Calculate'}
                    </button>
                </form>
                {result !== null && (
                    <div style={styles.result}>
                        Total staking rewards: <span style={styles.resultValue}>€{result}</span>
                        <span
                            style={{
                                display: 'inline-block',
                                marginLeft: 10,
                                cursor: 'pointer',
                                color: '#818cf8',
                                position: 'relative',
                                verticalAlign: 'middle',
                                width: 20,
                                height: 20,
                            }}
                            tabIndex={0}
                            title={'Add this amount of money to your tax to "Sonstige Einkünfte" in your tax return.'}
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ display: 'block' }}>
                                <circle cx="10" cy="10" r="9" fill="#232136" stroke="#fff" strokeWidth="2" />
                                <text x="10" y="15" textAnchor="middle" fontSize="13" fontWeight="bold" fill="#fff" fontFamily="Arial, sans-serif">i</text>
                            </svg>
                        </span>
                    </div>
                )}
                {monthly && (
                    <div style={{ marginTop: 32 }}>
                        <RewardsBarChart data={monthly} />
                    </div>
                )}
                {error && <div style={styles.error}>{error}</div>}
            </div>
        </div>
    );
}

export default App;
