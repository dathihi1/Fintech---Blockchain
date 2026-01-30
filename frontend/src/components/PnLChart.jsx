import { useMemo } from 'react';
import { Box, Card, CardContent, Typography, useTheme } from '@mui/material';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Area,
    ComposedChart
} from 'recharts';

/**
 * P&L Chart Component
 * Displays cumulative P&L over trades as an equity curve
 */
function PnLChart({ trades = [], height = 300, showGrid = true }) {
    const theme = useTheme();

    // Calculate cumulative P&L data
    const chartData = useMemo(() => {
        if (!trades || trades.length === 0) return [];

        // Sort by entry time and filter closed trades
        const sortedTrades = [...trades]
            .filter(t => t.pnl !== null && t.pnl !== undefined)
            .sort((a, b) => new Date(a.entry_time) - new Date(b.entry_time));

        let cumulative = 0;
        return sortedTrades.map((trade, index) => {
            cumulative += trade.pnl || 0;
            return {
                index: index + 1,
                date: new Date(trade.entry_time).toLocaleDateString('vi-VN'),
                symbol: trade.symbol,
                pnl: trade.pnl,
                cumulative: parseFloat(cumulative.toFixed(2)),
                pnlPct: trade.pnl_pct
            };
        });
    }, [trades]);

    // Calculate stats
    const stats = useMemo(() => {
        if (chartData.length === 0) return { max: 0, min: 0, current: 0 };
        const values = chartData.map(d => d.cumulative);
        return {
            max: Math.max(...values),
            min: Math.min(...values),
            current: values[values.length - 1] || 0
        };
    }, [chartData]);

    if (chartData.length === 0) {
        return (
            <Card>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                        📈 Equity Curve
                    </Typography>
                    <Box
                        sx={{
                            height: height,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'text.secondary'
                        }}
                    >
                        <Typography>Chưa có dữ liệu giao dịch đã đóng</Typography>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <Box
                    sx={{
                        bgcolor: 'background.paper',
                        p: 1.5,
                        borderRadius: 1,
                        boxShadow: 3,
                        border: '1px solid',
                        borderColor: 'divider'
                    }}
                >
                    <Typography variant="body2" fontWeight={600}>
                        Trade #{data.index} - {data.symbol}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {data.date}
                    </Typography>
                    <Typography
                        variant="body2"
                        color={data.pnl >= 0 ? 'success.main' : 'error.main'}
                    >
                        P&L: {data.pnl >= 0 ? '+' : ''}{data.pnl?.toFixed(2)}
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                        Tổng: {data.cumulative >= 0 ? '+' : ''}{data.cumulative}
                    </Typography>
                </Box>
            );
        }
        return null;
    };

    return (
        <Card>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" fontWeight={600}>
                        📈 Equity Curve
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                                Hiện tại
                            </Typography>
                            <Typography
                                variant="body1"
                                fontWeight={700}
                                color={stats.current >= 0 ? 'success.main' : 'error.main'}
                            >
                                {stats.current >= 0 ? '+' : ''}{stats.current}
                            </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                                Cao nhất
                            </Typography>
                            <Typography variant="body1" fontWeight={700} color="success.main">
                                +{stats.max.toFixed(2)}
                            </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                                Thấp nhất
                            </Typography>
                            <Typography variant="body1" fontWeight={700} color="error.main">
                                {stats.min.toFixed(2)}
                            </Typography>
                        </Box>
                    </Box>
                </Box>

                <ResponsiveContainer width="100%" height={height}>
                    <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        {showGrid && (
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke={theme.palette.divider}
                            />
                        )}
                        <XAxis
                            dataKey="index"
                            tick={{ fontSize: 12 }}
                            stroke={theme.palette.text.secondary}
                        />
                        <YAxis
                            tick={{ fontSize: 12 }}
                            stroke={theme.palette.text.secondary}
                            tickFormatter={(value) => value >= 0 ? `+${value}` : value}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <ReferenceLine y={0} stroke={theme.palette.divider} strokeWidth={2} />
                        <Area
                            type="monotone"
                            dataKey="cumulative"
                            fill={stats.current >= 0 ? theme.palette.success.light : theme.palette.error.light}
                            fillOpacity={0.3}
                            stroke="none"
                        />
                        <Line
                            type="monotone"
                            dataKey="cumulative"
                            stroke={stats.current >= 0 ? theme.palette.success.main : theme.palette.error.main}
                            strokeWidth={2}
                            dot={{ r: 3 }}
                            activeDot={{ r: 6 }}
                        />
                    </ComposedChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

export default PnLChart;
