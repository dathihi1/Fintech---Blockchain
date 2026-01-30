import { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Grid,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Chip,
    LinearProgress,
    Alert
} from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PnLChart from '../components/PnLChart';
import AlertFeed from '../components/AlertFeed';
import { useTrades } from '../hooks/useTrades';
import api from '../services/api';

// Stat Card Component
function StatCard({ title, value, subtitle, color = 'primary', trend }) {
    return (
        <Card sx={{ height: '100%' }}>
            <CardContent>
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
                {trend !== undefined && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        {trend >= 0 ? (
                            <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                        ) : (
                            <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                        )}
                        <Typography variant="caption" color={trend >= 0 ? 'success.main' : 'error.main'}>
                            {trend >= 0 ? '+' : ''}{trend}%
                        </Typography>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}

// Behavioral Pattern Card
function BehavioralPatternCard({ analysis }) {
    if (!analysis) {
        return (
            <Card>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                        🧠 Phân tích hành vi
                    </Typography>
                    <Typography color="text.secondary">
                        Chưa có đủ dữ liệu để phân tích
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                    🧠 Phân tích hành vi
                </Typography>

                {/* Risk Score */}
                <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Risk Score</Typography>
                        <Typography
                            variant="body2"
                            color={analysis.risk_score > 50 ? 'error.main' :
                                analysis.risk_score > 25 ? 'warning.main' : 'success.main'}
                            fontWeight={600}
                        >
                            {analysis.risk_score}/100
                        </Typography>
                    </Box>
                    <LinearProgress
                        variant="determinate"
                        value={analysis.risk_score}
                        color={analysis.risk_score > 50 ? 'error' :
                            analysis.risk_score > 25 ? 'warning' : 'success'}
                        sx={{ height: 8, borderRadius: 4 }}
                    />
                </Box>

                {/* Interval Analysis */}
                {analysis.interval_analysis && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" fontWeight={600} gutterBottom>
                            ⏱️ Trade Intervals
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip
                                size="small"
                                label={`Sau loss: ${analysis.interval_analysis.avg_interval_after_loss?.toFixed(0)}m`}
                                color={analysis.interval_analysis.rushing_after_loss ? 'error' : 'success'}
                            />
                            <Chip
                                size="small"
                                label={`Sau win: ${analysis.interval_analysis.avg_interval_after_win?.toFixed(0)}m`}
                                color="primary"
                                variant="outlined"
                            />
                        </Box>
                        {analysis.interval_analysis.rushing_after_loss && (
                            <Alert severity="warning" sx={{ mt: 1, py: 0 }}>
                                Đang vào lệnh quá nhanh sau loss!
                            </Alert>
                        )}
                    </Box>
                )}

                {/* Sizing Analysis */}
                {analysis.sizing_analysis && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" fontWeight={600} gutterBottom>
                            📊 Position Sizing
                        </Typography>
                        {analysis.sizing_analysis.revenge_pattern_detected && (
                            <Alert severity="error" sx={{ py: 0 }}>
                                Phát hiện Revenge Pattern: Size tăng {((analysis.sizing_analysis.avg_size_increase_after_loss - 1) * 100).toFixed(0)}% sau loss
                            </Alert>
                        )}
                        {!analysis.sizing_analysis.revenge_pattern_detected && (
                            <Chip label="Sizing ổn định ✓" color="success" size="small" />
                        )}
                    </Box>
                )}

                {/* Hold Analysis */}
                {analysis.hold_analysis && (
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" fontWeight={600} gutterBottom>
                            ⏳ Hold Duration
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1. }}>
                            <Chip
                                size="small"
                                label={`Win: ${analysis.hold_analysis.avg_winning_hold_minutes?.toFixed(0)}m`}
                                color="success"
                            />
                            <Chip
                                size="small"
                                label={`Loss: ${analysis.hold_analysis.avg_losing_hold_minutes?.toFixed(0)}m`}
                                color="error"
                            />
                        </Box>
                        {analysis.hold_analysis.loss_aversion_detected && (
                            <Alert severity="warning" sx={{ mt: 1, py: 0 }}>
                                Loss Aversion: Giữ lệnh lỗ lâu hơn {analysis.hold_analysis.loss_aversion_ratio?.toFixed(1)}x
                            </Alert>
                        )}
                    </Box>
                )}

                {/* Recommendations */}
                {analysis.recommendations?.length > 0 && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                        <Typography variant="body2" fontWeight={600} gutterBottom>
                            💡 Đề xuất
                        </Typography>
                        {analysis.recommendations.map((rec, i) => (
                            <Typography key={i} variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                {rec}
                            </Typography>
                        ))}
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}

// Time Performance Card  
function TimePerformanceCard({ analysis }) {
    if (!analysis?.time_analysis) return null;

    const { best_hours, worst_hours, best_days, worst_days } = analysis.time_analysis;

    return (
        <Card>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AccessTimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6" fontWeight={600}>
                        Time Performance
                    </Typography>
                </Box>

                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Best Hours
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {best_hours?.map(h => (
                                <Chip key={h} label={`${h}h`} size="small" color="success" />
                            ))}
                        </Box>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Worst Hours
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {worst_hours?.map(h => (
                                <Chip key={h} label={`${h}h`} size="small" color="error" />
                            ))}
                        </Box>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Best Days
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {best_days?.map(d => (
                                <Chip key={d} label={d.slice(0, 3)} size="small" color="success" variant="outlined" />
                            ))}
                        </Box>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Worst Days
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {worst_days?.map(d => (
                                <Chip key={d} label={d.slice(0, 3)} size="small" color="error" variant="outlined" />
                            ))}
                        </Box>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
}

function Analytics() {
    const userId = 'demo_user';
    const { trades, stats, loading: tradesLoading } = useTrades(userId);
    const [analysis, setAnalysis] = useState(null);
    const [analysisLoading, setAnalysisLoading] = useState(true);

    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
                const response = await api.get('/analysis/passive', {
                    params: { limit: 100 }
                });
                setAnalysis(response.data);
            } catch (err) {
                console.error('Failed to fetch analysis:', err);
            } finally {
                setAnalysisLoading(false);
            }
        };

        fetchAnalysis();
    }, []);

    if (tradesLoading || analysisLoading) {
        return (
            <Container maxWidth="xl" sx={{ py: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
                    <CircularProgress />
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                <AnalyticsIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                    <Typography variant="h4" fontWeight={700}>
                        Analytics
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Phân tích hiệu suất và hành vi giao dịch
                    </Typography>
                </Box>
            </Box>

            {/* Stats Row */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Tổng Trades"
                        value={stats.total}
                        subtitle={`${stats.open} đang mở`}
                        color="primary"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Win Rate"
                        value={`${stats.winRate}%`}
                        subtitle={`${stats.wins}W / ${stats.losses}L`}
                        color={parseFloat(stats.winRate) >= 50 ? 'success' : 'error'}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total P&L"
                        value={`$${stats.totalPnl}`}
                        subtitle={`Avg: ${stats.avgPnlPct}%`}
                        color={parseFloat(stats.totalPnl) >= 0 ? 'success' : 'error'}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Risk Score"
                        value={analysis?.risk_score || 0}
                        subtitle="/ 100"
                        color={analysis?.risk_score > 50 ? 'error' :
                            analysis?.risk_score > 25 ? 'warning' : 'success'}
                    />
                </Grid>
            </Grid>

            {/* Charts and Analysis Row */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={8}>
                    <PnLChart trades={trades} height={350} />
                </Grid>
                <Grid item xs={12} md={4}>
                    <BehavioralPatternCard analysis={analysis} />
                </Grid>
            </Grid>

            {/* Time Performance and Symbol Analysis */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <TimePerformanceCard analysis={analysis} />
                </Grid>
                <Grid item xs={12} md={6}>
                    {analysis?.symbol_analysis && (
                        <Card>
                            <CardContent>
                                <Typography variant="h6" fontWeight={600} gutterBottom>
                                    📈 Symbol Performance
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                    <Typography variant="body2" color="text.secondary">Best:</Typography>
                                    {analysis.symbol_analysis.best_symbols?.map(s => (
                                        <Chip key={s} label={s} size="small" color="success" />
                                    ))}
                                </Box>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <Typography variant="body2" color="text.secondary">Avoid:</Typography>
                                    {analysis.symbol_analysis.worst_symbols?.map(s => (
                                        <Chip key={s} label={s} size="small" color="error" variant="outlined" />
                                    ))}
                                </Box>
                            </CardContent>
                        </Card>
                    )}
                </Grid>
            </Grid>
        </Container>
    );
}

export default Analytics;
