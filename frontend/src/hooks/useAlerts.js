import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook for real-time WebSocket alerts
 * Connects to backend WebSocket for behavioral alerts
 */
export function useAlerts(userId) {
    const [alerts, setAlerts] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    const connect = useCallback(() => {
        if (!userId) return;

        const wsUrl = `ws://localhost:8000/ws/${userId}`;

        try {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setConnectionError(null);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'pong') {
                        // Heartbeat response, ignore
                        return;
                    }

                    if (data.type === 'analysis_result') {
                        // Handle analysis results
                        if (data.data?.alerts?.length > 0) {
                            setAlerts(prev => [...data.data.alerts, ...prev].slice(0, 50));
                        }
                    } else if (data.alert || data.type === 'alert') {
                        // Direct alert
                        const alert = data.alert || data;
                        setAlerts(prev => [alert, ...prev].slice(0, 50));

                        // Show browser notification if permission granted
                        if (Notification.permission === 'granted') {
                            new Notification('Trading Alert', {
                                body: alert.recommendation || alert.type,
                                icon: '/favicon.ico'
                            });
                        }
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionError('Connection error');
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);

                // Auto-reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    connect();
                }, 3000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            setConnectionError(error.message);
        }
    }, [userId]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    const clearAlerts = useCallback(() => {
        setAlerts([]);
    }, []);

    const sendMessage = useCallback((message) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        }
    }, []);

    // Request quick analysis via WebSocket
    const analyzeNotes = useCallback((notes, tradesLastHour = 0) => {
        sendMessage({
            type: 'analyze',
            notes,
            trades_last_hour: tradesLastHour
        });
    }, [sendMessage]);

    // Connect on mount, disconnect on unmount
    useEffect(() => {
        connect();

        // Request notification permission
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    // Heartbeat to keep connection alive
    useEffect(() => {
        if (!isConnected) return;

        const interval = setInterval(() => {
            sendMessage({ type: 'ping' });
        }, 25000);

        return () => clearInterval(interval);
    }, [isConnected, sendMessage]);

    return {
        alerts,
        isConnected,
        connectionError,
        clearAlerts,
        analyzeNotes,
        disconnect,
        reconnect: connect
    };
}

export default useAlerts;
