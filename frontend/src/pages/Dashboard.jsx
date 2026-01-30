import { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Grid,
    Card,
    CardContent,
    Typography,
    Chip,
    LinearProgress,
    Alert,
    AlertTitle,
    CircularProgress
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import PsychologyIcon from '@mui/icons-material/Psychology';
import WarningIcon from '@mui/icons-material/Warning';
import { getTradeStats, getAlerts, getPassiveAnalysis } from '../services/api';

// Stat Card Component
function StatCard({ title, value, subtitle, icon, color = 'primary', trend }) {
    return (
        <Card className="fade-in" sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            {title}
                        </Typography>
                        <Typography variant="h4" fontWeight={700} color={`${color}.main`}>
                            {value}
                        </Typography>
                        {subtitle && (
                            <Typography variant="caption" color="text.secondary">
                                {subtitle}
                            </Typography>
                        )}
                    </Box>
                    <Box
                        sx={{
                            p: 1.5,
                            borderRadius: 2,
                            bgcolor: `${color}.main`,
                            opacity: 0.2,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        {icon}
                    </Box>
                </Box>
                {trend !== undefined && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        {trend >= 0 ? (
                            <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                        ) : (
                            <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                        )}
                        <Typography
                            variant="caption"
                            color={trend >= 0 ? 'success.main' : 'error.main'}
                        >
                            {trend >= 0 ? '+' : ''}{trend}% so với tuần trước
                        </Typography>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}

// Alert Card Component
function AlertCard({ alert }) {
    const severityMap = {
        CRITICAL: 'error',
        HIGH: 'warning',
        MEDIUM: 'info',
        INFO: 'success'
    };

    return (
        <Alert
            severity={severityMap[alert.severity] || 'info'}
            className="slide-in-right"
            sx={{ mb: 1 }}
        >
            <AlertTitle sx={{ fontWeight: 600 }}>
                {alert.alert_type || alert.type} - {alert.severity}
            </AlertTitle>
            {alert.reasons?.[0] || alert.recommendation}
        </Alert>
    );
}

function Dashboard() {
    const userId = 'demo_user';
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        total_trades: 0,
        win_rate: 0,
        total_pnl: 0,
        avg_pnl_pct: 0,
        best_trade: 0,
        worst_trade: 0
    });
    const [alerts, setAlerts] = useState([]);
    const [analysis, setAnalysis] = useState(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            setLoading(true);
            try {
                // Fetch all data in parallel
                const [statsData, alertsData, analysisData] = await Promise.all([
                    getTradeStats(userId).catch(() => null),
                    getAlerts(userId, true).catch(() => []),
                    getPassiveAnalysis(userId).catch(() => null)
                ]);

                if (statsData) {
                    setStats(statsData);
                }
                setAlerts(Array.isArray(alertsData) ? alertsData.slice(0, 5) : []);
                if (analysisData) {
                    setAnalysis(analysisData);
                }
            } catch (err) {
                console.error('Failed to fetch dashboard data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
                <CircularProgress />
            </Box>
        );
    }

    const winRateColor = stats.win_rate >= 0.5 ? 'success' : 'warning';
    const pnlColor = stats.total_pnl >= 0 ? 'success' : 'error';
    // Calculate risk score from analysis or use behavioral patterns
    const riskScore = analysis?.risk_score ? analysis.risk_score * 100 : 0;
    const displayRiskScore = Math.min(Math.max(riskScore, 0), 100); // Clamp between 0-100

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight={700} gutterBottom>
                    Dashboard
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Tổng quan hiệu suất giao dịch và cảnh báo hành vi
                </Typography>
            </Box>

            {/* Stats Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={2.4}>
                    <StatCard
                        title="Tổng số Trades"
                        value={stats.total_trades}
                        subtitle={`${stats.closed_trades || 0} đã đóng`}
                        icon={<TrendingUpIcon sx={{ color: 'primary.main' }} />}
                        color="primary"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                    <StatCard
                        title="Win Rate"
                        value={`${(stats.win_rate * 100).toFixed(1)}%`}
                        subtitle="Mục tiêu: 50%"
                        icon={<TrendingUpIcon sx={{ color: `${winRateColor}.main` }} />}
                        color={winRateColor}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                    <StatCard
                        title="Best Trade"
                        value={`${stats.best_trade >= 0 ? '+' : ''}${stats.best_trade?.toFixed(2)}%`}
                        subtitle="Trade tốt nhất"
                        icon={<TrendingUpIcon sx={{ color: 'success.main' }} />}
                        color="success"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                    <StatCard
                        title="Worst Trade"
                        value={`${stats.worst_trade?.toFixed(2)}%`}
                        subtitle="Trade tệ nhất"
                        icon={<TrendingDownIcon sx={{ color: 'error.main' }} />}
                        color="error"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                    <StatCard
                        title="Risk Score"
                        value={`${riskScore.toFixed(0)}/100`}
                        subtitle="Điểm rủi ro hành vi"
                        icon={<PsychologyIcon sx={{ color: 'info.main' }} />}
                        color={riskScore > 50 ? 'error' : riskScore > 25 ? 'warning' : 'success'}
                    />
                </Grid>
            </Grid>

            {/* Two Column Layout */}
            <Grid container spacing={3}>
                {/* Recent Alerts */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                                <Typography variant="h6" fontWeight={600}>
                                    Cảnh báo gần đây
                                </Typography>
                                {alerts.length > 0 && (
                                    <Chip label={alerts.length} size="small" color="warning" sx={{ ml: 1 }} />
                                )}
                            </Box>

                            {alerts.length === 0 ? (
                                <Alert severity="success">
                                    Không có cảnh báo nào - Giao dịch an toàn! ✓
                                </Alert>
                            ) : (
                                alerts.map((alert, index) => (
                                    <AlertCard key={alert.id || index} alert={alert} />
                                ))
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Behavioral Analysis */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                Phân tích hành vi
                            </Typography>

                            <Box sx={{ mb: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="body2">FOMO Risk</Typography>
                                    <Typography variant="body2" color={displayRiskScore > 50 ? 'error.main' : 'warning.main'}>
                                        {displayRiskScore.toFixed(0)}%
                                    </Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={Math.min(displayRiskScore, 100)}
                                    color={displayRiskScore > 50 ? 'error' : 'warning'}
                                    sx={{ height: 8, borderRadius: 4 }}
                                />
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="body2">Win Rate</Typography>
                                    <Typography variant="body2" color="success.main">
                                        {(stats.win_rate * 100).toFixed(1)}%
                                    </Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={stats.win_rate * 100}
                                    color="success"
                                    sx={{ height: 8, borderRadius: 4 }}
                                />
                            </Box>

                            <Box>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="body2">Discipline Score</Typography>
                                    <Typography variant="body2" color="info.main">
                                        {(100 - displayRiskScore).toFixed(0)}%
                                    </Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={100 - displayRiskScore}
                                    color="info"
                                    sx={{ height: 8, borderRadius: 4 }}
                                />
                            </Box>

                            {analysis?.recommendations?.length > 0 && (
                                <Box sx={{ mt: 3 }}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Đề xuất:
                                    </Typography>
                                    {analysis.recommendations.slice(0, 2).map((rec, i) => (
                                        <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>
                                            💡 {rec}
                                        </Typography>
                                    ))}
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
}

export default Dashboard;
