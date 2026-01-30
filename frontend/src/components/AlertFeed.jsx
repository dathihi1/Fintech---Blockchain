import { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Alert,
    AlertTitle,
    IconButton,
    Chip,
    Collapse,
    Button
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { acknowledgeAlert } from '../services/api';

/**
 * Real-time alert feed component
 * Displays behavioral alerts with severity-based styling
 */
function AlertFeed({ alerts = [], onAcknowledge, onClear, showHeader = true }) {
    const [expandedId, setExpandedId] = useState(null);

    const severityConfig = {
        CRITICAL: { color: 'error', icon: '🛑', priority: 4 },
        HIGH: { color: 'warning', icon: '⚠️', priority: 3 },
        MEDIUM: { color: 'info', icon: '📊', priority: 2 },
        LOW: { color: 'success', icon: '💡', priority: 1 },
        INFO: { color: 'success', icon: '✅', priority: 0 }
    };

    const handleAcknowledge = async (alertId) => {
        try {
            await acknowledgeAlert(alertId);
            if (onAcknowledge) {
                onAcknowledge(alertId);
            }
        } catch (err) {
            console.error('Failed to acknowledge alert:', err);
        }
    };

    const sortedAlerts = [...alerts].sort((a, b) => {
        const priorityA = severityConfig[a.severity]?.priority || 0;
        const priorityB = severityConfig[b.severity]?.priority || 0;
        return priorityB - priorityA;
    });

    if (alerts.length === 0) {
        return (
            <Card>
                <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', color: 'success.main' }}>
                        <CheckCircleIcon sx={{ mr: 1 }} />
                        <Typography>Không có cảnh báo nào</Typography>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardContent>
                {showHeader && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                            <Typography variant="h6" fontWeight={600}>
                                Cảnh báo hành vi
                            </Typography>
                            <Chip
                                label={alerts.length}
                                size="small"
                                color="warning"
                                sx={{ ml: 1 }}
                            />
                        </Box>
                        {onClear && (
                            <Button size="small" onClick={onClear}>
                                Xóa tất cả
                            </Button>
                        )}
                    </Box>
                )}

                <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                    {sortedAlerts.map((alert, index) => {
                        const config = severityConfig[alert.severity] || severityConfig.INFO;
                        const isExpanded = expandedId === (alert.id || index);

                        return (
                            <Alert
                                key={alert.id || index}
                                severity={config.color}
                                sx={{
                                    mb: 1,
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        transform: 'translateX(4px)',
                                        boxShadow: 2
                                    }
                                }}
                                onClick={() => setExpandedId(isExpanded ? null : (alert.id || index))}
                                action={
                                    alert.id && (
                                        <IconButton
                                            size="small"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleAcknowledge(alert.id);
                                            }}
                                        >
                                            <CloseIcon fontSize="small" />
                                        </IconButton>
                                    )
                                }
                            >
                                <AlertTitle sx={{ fontWeight: 600 }}>
                                    {config.icon} {alert.alert_type || alert.type} - {alert.severity}
                                    {alert.score && (
                                        <Chip
                                            label={`Score: ${alert.score}`}
                                            size="small"
                                            sx={{ ml: 1 }}
                                        />
                                    )}
                                </AlertTitle>

                                <Typography variant="body2">
                                    {alert.recommendation}
                                </Typography>

                                <Collapse in={isExpanded}>
                                    <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                                        {alert.reasons?.length > 0 && (
                                            <Box sx={{ mb: 1 }}>
                                                <Typography variant="caption" fontWeight={600}>
                                                    Lý do:
                                                </Typography>
                                                <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                                                    {alert.reasons.map((reason, i) => (
                                                        <li key={i}>
                                                            <Typography variant="caption">
                                                                {reason}
                                                            </Typography>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </Box>
                                        )}
                                        {alert.created_at && (
                                            <Typography variant="caption" color="text.secondary">
                                                {new Date(alert.created_at).toLocaleString('vi-VN')}
                                            </Typography>
                                        )}
                                    </Box>
                                </Collapse>
                            </Alert>
                        );
                    })}
                </Box>
            </CardContent>
        </Card>
    );
}

export default AlertFeed;
