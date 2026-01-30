import { useState, useEffect, useCallback } from 'react';
import { getTrades, createTrade, updateTrade, getAlerts } from '../services/api';

/**
 * Custom hook for trades data management
 * Provides loading, error, and CRUD operations
 */
export function useTrades(userId, options = {}) {
    const { limit = 50, autoFetch = true } = options;

    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    // Fetch trades from API
    const fetchTrades = useCallback(async () => {
        if (!userId) return;

        setLoading(true);
        setError(null);

        try {
            const data = await getTrades(userId, limit);
            setTrades(data);
            setLastUpdated(new Date());
        } catch (err) {
            console.error('Failed to fetch trades:', err);
            setError(err.message || 'Failed to load trades');
        } finally {
            setLoading(false);
        }
    }, [userId, limit]);

    // Create a new trade
    const addTrade = useCallback(async (tradeData) => {
        setLoading(true);
        setError(null);

        try {
            const result = await createTrade({
                ...tradeData,
                user_id: userId
            });

            // Add to local state
            if (result.trade) {
                setTrades(prev => [result.trade, ...prev]);
            }

            return result;
        } catch (err) {
            console.error('Failed to create trade:', err);
            setError(err.message || 'Failed to create trade');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [userId]);

    // Close/update a trade
    const closeTrade = useCallback(async (tradeId, exitData) => {
        setLoading(true);
        setError(null);

        try {
            const updatedTrade = await updateTrade(tradeId, exitData);

            // Update local state
            setTrades(prev => prev.map(t =>
                t.id === tradeId ? { ...t, ...updatedTrade } : t
            ));

            return updatedTrade;
        } catch (err) {
            console.error('Failed to close trade:', err);
            setError(err.message || 'Failed to close trade');
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Calculate summary stats
    const stats = {
        total: trades.length,
        open: trades.filter(t => !t.exit_price).length,
        closed: trades.filter(t => t.exit_price).length,
        wins: trades.filter(t => t.pnl && t.pnl > 0).length,
        losses: trades.filter(t => t.pnl && t.pnl < 0).length,
        winRate: (() => {
            const closed = trades.filter(t => t.pnl !== null);
            if (closed.length === 0) return 0;
            const wins = closed.filter(t => t.pnl > 0).length;
            return (wins / closed.length * 100).toFixed(1);
        })(),
        totalPnl: trades.reduce((sum, t) => sum + (t.pnl || 0), 0).toFixed(2),
        avgPnlPct: (() => {
            const closed = trades.filter(t => t.pnl_pct !== null);
            if (closed.length === 0) return 0;
            return (closed.reduce((sum, t) => sum + t.pnl_pct, 0) / closed.length).toFixed(2);
        })()
    };

    // Auto-fetch on mount if enabled
    useEffect(() => {
        if (autoFetch && userId) {
            fetchTrades();
        }
    }, [autoFetch, userId, fetchTrades]);

    return {
        trades,
        loading,
        error,
        lastUpdated,
        stats,
        fetchTrades,
        addTrade,
        closeTrade,
        setTrades
    };
}

/**
 * Custom hook for alerts data
 */
export function useAlertsData(userId, options = {}) {
    const { activeOnly = false, limit = 50 } = options;

    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchAlerts = useCallback(async () => {
        if (!userId) return;

        setLoading(true);
        try {
            const data = await getAlerts(userId, activeOnly);
            setAlerts(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [userId, activeOnly]);

    useEffect(() => {
        fetchAlerts();
    }, [fetchAlerts]);

    return {
        alerts,
        loading,
        error,
        fetchAlerts
    };
}

export default useTrades;
