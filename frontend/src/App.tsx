import React, { useState } from 'react';
import { styles } from './AppStyles';
import { RewardsBarChart } from './RewardsBarChart';

function App() {
    const [file, setFile] = useState<File | null>(null);
    const [year, setYear] = useState<number>(new Date().getFullYear());
    const [stakingRewardTotal, setStakingRewardTotal] = useState<number | null>(null);
    const [monthlyStakingReward, setMonthlyStakingReward] = useState<{ [month: number]: number } | null>(null);
    const [realizedGains, setRealizedGains] = useState<number | null>(null);
    const [taxableGains, setTaxableGains] = useState<number | null>(null);
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
        setStakingRewardTotal(null);
        setMonthlyStakingReward(null);
        setRealizedGains(null);
        setTaxableGains(null);
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
            const monthlyData = data.monthly_rewards_eur || null;
            setMonthlyStakingReward(monthlyData);
            // Calculate total from monthly data
            const total = monthlyData ? parseFloat((Object.values(monthlyData) as number[]).reduce((sum: number, val: number) => sum + val, 0).toFixed(2)) : 0;
            setStakingRewardTotal(total);
            setRealizedGains(data.realized_gains_eur ?? null);
            setTaxableGains(data.taxable_gains_eur ?? null);
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
                    <div>
                        <h2 style={styles.title}>BlockTaxer</h2>
                        <p style={styles.subtitle}>Supercharge your crypto tax</p>
                    </div>
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
                {(realizedGains !== null || taxableGains !== null) && (
                    <div>
                        {realizedGains !== null && (
                            <div style={styles.result}>
                                Realized gains: <span style={styles.resultValue}>€{realizedGains}</span>
                            </div>
                        )}
                        {taxableGains !== null && (
                            <div style={styles.result}>
                                Taxable gains: <span style={styles.resultValue}>€{taxableGains}</span>
                                <span
                                    style={styles.infoIcon}
                                    tabIndex={0}
                                    title={'This is the amount you need to declare as capital gains for tax purposes. Gains below €1000 and coins held >1 year are tax-free.'}
                                >
                                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style={styles.infoIconSvg}>
                                        <circle cx="10" cy="10" r="9" fill="#232136" stroke="#fff" strokeWidth="2" />
                                        <text x="10" y="15" textAnchor="middle" fontSize="13" fontWeight="bold" fill="#fff" fontFamily="Arial, sans-serif">i</text>
                                    </svg>
                                </span>
                            </div>
                        )}
                    </div>
                )}
                {stakingRewardTotal !== null && (
                    <div style={{ marginTop: 32, borderTop: '1px solid #312e81' }}>
                        <div style={styles.result}>
                            Total staking rewards: <span style={styles.resultValue}>€{stakingRewardTotal}</span>
                            <span
                                style={styles.infoIcon}
                                tabIndex={0}
                                title={'Add this amount of money to your tax to "Sonstige Einkünfte" in your tax return.'}
                            >
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style={styles.infoIconSvg}>
                                    <circle cx="10" cy="10" r="9" fill="#232136" stroke="#fff" strokeWidth="2" />
                                    <text x="10" y="15" textAnchor="middle" fontSize="13" fontWeight="bold" fill="#fff" fontFamily="Arial, sans-serif">i</text>
                                </svg>
                            </span>
                        </div>
                        {monthlyStakingReward && (
                            <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center' }}>
                                <RewardsBarChart data={monthlyStakingReward} />
                            </div>
                        )}
                    </div>
                )}
                {error && <div style={styles.error}>{error}</div>}
            </div>
        </div>
    );
}

export default App;
