import { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Container,
    Grid,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    MenuItem,
    Alert,
    CircularProgress,
    Collapse,
    Autocomplete,
    debounce,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import BookIcon from '@mui/icons-material/Book';
import RefreshIcon from '@mui/icons-material/Refresh';
import { createTrade, searchSymbols, getPopularSymbols, getTrades, closeTrade } from '../services/api';

function TradeJournal() {
    const userId = 'demo_user';

    // Trades state - load from API
    const [trades, setTrades] = useState([]);
    const [tradesLoading, setTradesLoading] = useState(true);

    // Form state
    const [showForm, setShowForm] = useState(false);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        user_id: userId,
        symbol: '',
        side: 'long',
        entry_price: '',
        quantity: '',
        notes: ''
    });
    const [submitResult, setSubmitResult] = useState(null);

    // Close trade dialog state
    const [closeDialog, setCloseDialog] = useState({
        open: false,
        trade: null,
        exitPrice: '',
        exitNotes: ''
    });

    // Symbol autocomplete state
    const [symbolOptions, setSymbolOptions] = useState([]);
    const [symbolLoading, setSymbolLoading] = useState(false);
    const [symbolInputValue, setSymbolInputValue] = useState('');

    // Fetch trades from API on mount
    useEffect(() => {
        fetchTrades();
    }, []);

    const fetchTrades = async () => {
        setTradesLoading(true);
        try {
            const data = await getTrades(userId, 50);
            setTrades(data);
        } catch (err) {
            console.error('Failed to fetch trades:', err);
        } finally {
            setTradesLoading(false);
        }
    };

    // Calculate estimated PnL
    const calculateEstimatedPnL = (trade, exitPrice) => {
        if (!trade || !exitPrice) return null;
        
        const entry = parseFloat(trade.entry_price);
        const exit = parseFloat(exitPrice);
        const qty = parseFloat(trade.quantity);
        
        let pnlUsd, pnlPct;
        
        if (trade.side === 'long') {
            pnlUsd = (exit - entry) * qty;
            pnlPct = ((exit - entry) / entry) * 100;
        } else {
            pnlUsd = (entry - exit) * qty;
            pnlPct = ((entry - exit) / entry) * 100;
        }
        
        const sign = pnlPct >= 0 ? '+' : '';
        return `${sign}$${pnlUsd.toFixed(2)} (${sign}${pnlPct.toFixed(2)}%)`;
    };

    // Open close dialog
    const handleOpenCloseDialog = (trade) => {
        setCloseDialog({
            open: true,
            trade,
            exitPrice: '',
            exitNotes: ''
        });
    };

    // Handle close trade
    const handleCloseTrade = async () => {
        const { trade, exitPrice, exitNotes } = closeDialog;
        
        if (!exitPrice || parseFloat(exitPrice) <= 0) {
            alert('Vui lòng nhập exit price hợp lệ');
            return;
        }

        try {
            await closeTrade(trade.id, parseFloat(exitPrice), exitNotes || null);
            
            // Close dialog
            setCloseDialog({ open: false, trade: null, exitPrice: '', exitNotes: '' });
            
            // Refresh trades to get updated data
            fetchTrades();
        } catch (err) {
            console.error('Failed to close trade:', err);
            alert('Không thể đóng trade. Vui lòng thử lại.');
        }
    };

    // Load popular symbols on mount
    useEffect(() => {
        const loadPopular = async () => {
            try {
                const popular = await getPopularSymbols(20);
                setSymbolOptions(popular);
            } catch (err) {
                console.error('Failed to load popular symbols:', err);
            }
        };
        loadPopular();
    }, []);

    // Debounced symbol search
    const debouncedSearch = useCallback(
        debounce(async (query) => {
            if (!query || query.length < 1) {
                const popular = await getPopularSymbols(20);
                setSymbolOptions(popular);
                return;
            }

            setSymbolLoading(true);
            try {
                const results = await searchSymbols(query, 15);
                setSymbolOptions(results);
            } catch (err) {
                console.error('Symbol search failed:', err);
            } finally {
                setSymbolLoading(false);
            }
        }, 300),
        []
    );

    const handleSymbolInputChange = (event, newInputValue) => {
        setSymbolInputValue(newInputValue);
        debouncedSearch(newInputValue);
    };

    const handleSymbolChange = (event, newValue) => {
        if (newValue) {
            setFormData(prev => ({
                ...prev,
                symbol: typeof newValue === 'string' ? newValue : newValue.symbol
            }));
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSubmitResult(null);

        try {
            const result = await createTrade({
                ...formData,
                entry_price: parseFloat(formData.entry_price),
                quantity: parseFloat(formData.quantity)
            });

            setSubmitResult(result);

            // Add to local list
            if (result.trade) {
                setTrades(prev => [{
                    id: result.trade.id,
                    symbol: result.trade.symbol,
                    side: result.trade.side,
                    entry_price: result.trade.entry_price,
                    exit_price: null,
                    pnl_pct: null,
                    notes: result.trade.notes,
                    nlp_quality_score: result.trade.nlp_quality_score,
                    behavioral_flags: result.trade.behavioral_flags || [],
                    entry_time: new Date().toLocaleString('vi-VN')
                }, ...prev]);
            }

            // Reset form
            setFormData({
                user_id: userId,
                symbol: '',
                side: 'long',
                entry_price: '',
                quantity: '',
                notes: ''
            });
            setSymbolInputValue('');
        } catch (err) {
            console.error(err);
            setSubmitResult({ error: 'Không thể kết nối server' });
        }

        setLoading(false);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BookIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                        <Typography variant="h4" fontWeight={700}>
                            Trade Journal
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Ghi nhận và phân tích giao dịch
                        </Typography>
                    </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={fetchTrades}
                        disabled={tradesLoading}
                    >
                        Refresh
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={showForm ? <ExpandLessIcon /> : <AddIcon />}
                        onClick={() => setShowForm(!showForm)}
                    >
                        {showForm ? 'Ẩn form' : 'Thêm Trade'}
                    </Button>
                </Box>
            </Box>

            {/* Add Trade Form */}
            <Collapse in={showForm}>
                <Card sx={{ mb: 3 }}>
                    <CardContent>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                            Thêm giao dịch mới
                        </Typography>

                        <Box component="form" onSubmit={handleSubmit}>
                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Autocomplete
                                        freeSolo
                                        options={symbolOptions}
                                        getOptionLabel={(option) =>
                                            typeof option === 'string' ? option : option.symbol
                                        }
                                        renderOption={(props, option) => (
                                            <Box component="li" {...props}>
                                                <Typography fontWeight={600} sx={{ mr: 1 }}>
                                                    {option.symbol}
                                                </Typography>
                                                <Typography variant="body2" color="text.secondary">
                                                    {option.display || `${option.base_asset}/${option.quote_asset}`}
                                                </Typography>
                                            </Box>
                                        )}
                                        loading={symbolLoading}
                                        inputValue={symbolInputValue}
                                        onInputChange={handleSymbolInputChange}
                                        onChange={handleSymbolChange}
                                        renderInput={(params) => (
                                            <TextField
                                                {...params}
                                                label="Symbol"
                                                placeholder="Gõ BTC, ETH..."
                                                required
                                                InputProps={{
                                                    ...params.InputProps,
                                                    endAdornment: (
                                                        <>
                                                            {symbolLoading ? <CircularProgress size={20} /> : null}
                                                            {params.InputProps.endAdornment}
                                                        </>
                                                    ),
                                                }}
                                            />
                                        )}
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6} md={2}>
                                    <TextField
                                        name="side"
                                        label="Side"
                                        select
                                        value={formData.side}
                                        onChange={handleInputChange}
                                        fullWidth
                                        required
                                    >
                                        <MenuItem value="long">Long</MenuItem>
                                        <MenuItem value="short">Short</MenuItem>
                                    </TextField>
                                </Grid>
                                <Grid item xs={12} sm={6} md={2}>
                                    <TextField
                                        name="entry_price"
                                        label="Entry Price"
                                        type="number"
                                        value={formData.entry_price}
                                        onChange={handleInputChange}
                                        fullWidth
                                        required
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6} md={2}>
                                    <TextField
                                        name="quantity"
                                        label="Quantity"
                                        type="number"
                                        value={formData.quantity}
                                        onChange={handleInputChange}
                                        fullWidth
                                        required
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        name="notes"
                                        label="Notes (sẽ được phân tích NLP)"
                                        value={formData.notes}
                                        onChange={handleInputChange}
                                        multiline
                                        rows={2}
                                        fullWidth
                                        placeholder="Lý do vào lệnh, cảm xúc, nhận định..."
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <Button
                                        type="submit"
                                        variant="contained"
                                        disabled={loading}
                                        endIcon={loading ? <CircularProgress size={20} /> : null}
                                    >
                                        {loading ? 'Đang xử lý...' : 'Thêm Trade'}
                                    </Button>
                                </Grid>
                            </Grid>
                        </Box>

                        {/* Submit Result */}
                        {submitResult && !submitResult.error && (
                            <Box sx={{ mt: 2 }}>
                                {submitResult.warnings?.length > 0 && (
                                    <Box>
                                        {submitResult.warnings.map((w, i) => (
                                            <Alert key={i} severity="warning" sx={{ mb: 1 }}>
                                                {w}
                                            </Alert>
                                        ))}
                                    </Box>
                                )}
                                {!submitResult.should_proceed && (
                                    <Alert severity="error">
                                        ⚠️ Khuyến nghị: KHÔNG nên vào lệnh này!
                                    </Alert>
                                )}
                            </Box>
                        )}

                        {submitResult?.error && (
                            <Alert severity="error" sx={{ mt: 2 }}>
                                {submitResult.error}
                            </Alert>
                        )}
                    </CardContent>
                </Card>
            </Collapse>

            {/* Trades Table */}
            <Card>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6" fontWeight={600}>
                            Lịch sử giao dịch
                        </Typography>
                        <Chip label={`${trades.length} trades`} size="small" />
                    </Box>

                    {tradesLoading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                            <CircularProgress />
                        </Box>
                    ) : trades.length === 0 ? (
                        <Alert severity="info">
                            Chưa có giao dịch nào. Bấm "Thêm Trade" để bắt đầu!
                        </Alert>
                    ) : (
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Thời gian</TableCell>
                                        <TableCell>Symbol</TableCell>
                                        <TableCell>Side</TableCell>
                                        <TableCell align="right">Quantity</TableCell>
                                        <TableCell align="right">Entry</TableCell>
                                        <TableCell align="right">Exit</TableCell>
                                        <TableCell align="right">P&L</TableCell>
                                        <TableCell>Quality</TableCell>
                                        <TableCell>Flags</TableCell>
                                        <TableCell>Notes</TableCell>
                                        <TableCell align="center">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {trades.map((trade) => (
                                        <TableRow key={trade.id} hover>
                                            <TableCell>
                                                <Typography variant="body2" color="text.secondary">
                                                    {trade.entry_time ? new Date(trade.entry_time).toLocaleString('vi-VN') : '-'}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography fontWeight={600}>{trade.symbol}</Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={trade.side?.toUpperCase()}
                                                    size="small"
                                                    color={trade.side === 'long' ? 'success' : 'error'}
                                                />
                                            </TableCell>
                                            <TableCell align="right">
                                                <Typography variant="body2" fontWeight={500}>
                                                    {trade.quantity?.toLocaleString()}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="right">${trade.entry_price?.toLocaleString()}</TableCell>
                                            <TableCell align="right">
                                                {trade.exit_price ? `$${trade.exit_price.toLocaleString()}` : '-'}
                                            </TableCell>
                                            <TableCell align="right">
                                                {trade.pnl_pct !== null && trade.pnl_pct !== undefined ? (
                                                    <Typography
                                                        color={trade.pnl_pct >= 0 ? 'success.main' : 'error.main'}
                                                        fontWeight={600}
                                                    >
                                                        {trade.pnl_pct >= 0 ? '+' : ''}{trade.pnl_pct?.toFixed(2)}%
                                                    </Typography>
                                                ) : '-'}
                                            </TableCell>
                                            <TableCell>
                                                {trade.nlp_quality_score && (
                                                    <Chip
                                                        label={`${Math.round(trade.nlp_quality_score * 100)}%`}
                                                        size="small"
                                                        color={trade.nlp_quality_score > 0.6 ? 'success' : 'warning'}
                                                        variant="outlined"
                                                    />
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                {trade.behavioral_flags && trade.behavioral_flags.length > 0 ? (
                                                    trade.behavioral_flags.map((flag, i) => (
                                                        <Chip
                                                            key={i}
                                                            label={flag}
                                                            size="small"
                                                            color="error"
                                                            sx={{ mr: 0.5, mb: 0.5 }}
                                                        />
                                                    ))
                                                ) : (
                                                    <Typography variant="body2" color="text.secondary">
                                                        -
                                                    </Typography>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Typography
                                                    variant="body2"
                                                    sx={{
                                                        maxWidth: 200,
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap'
                                                    }}
                                                    title={trade.notes}
                                                >
                                                    {trade.notes}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                                {!trade.exit_price ? (
                                                    <Button
                                                        size="small"
                                                        variant="outlined"
                                                        color="primary"
                                                        onClick={() => handleOpenCloseDialog(trade)}
                                                    >
                                                        Close
                                                    </Button>
                                                ) : (
                                                    <Chip label="Closed" size="small" color="default" variant="outlined" />
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </CardContent>
            </Card>

            {/* Close Trade Dialog */}
            <Dialog 
                open={closeDialog.open} 
                onClose={() => setCloseDialog({ ...closeDialog, open: false })}
                maxWidth="md"
                fullWidth
                PaperProps={{
                    sx: {
                        borderRadius: 3,
                        boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
                    }
                }}
            >
                <DialogTitle sx={{ pb: 1, pt: 3, px: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box>
                            <Typography variant="h5" fontWeight={700} gutterBottom>
                                Close Trade
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Chip 
                                    label={closeDialog.trade?.symbol} 
                                    color="primary" 
                                    size="small"
                                    sx={{ fontWeight: 600 }}
                                />
                                <Chip 
                                    label={closeDialog.trade?.side?.toUpperCase()} 
                                    color={closeDialog.trade?.side === 'long' ? 'success' : 'error'}
                                    size="small"
                                />
                            </Box>
                        </Box>
                    </Box>
                </DialogTitle>
                <DialogContent sx={{ px: 3, pb: 2 }}>
                    <Box sx={{ pt: 2 }}>
                        {/* Trade Info Card */}
                        <Card variant="outlined" sx={{ mb: 3, bgcolor: 'primary.50', borderColor: 'primary.200' }}>
                            <CardContent>
                                <Grid container spacing={3}>
                                    <Grid item xs={6}>
                                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                            Entry Price
                                        </Typography>
                                        <Typography variant="h5" fontWeight={700} color="primary.main">
                                            ${closeDialog.trade?.entry_price?.toLocaleString()}
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                            Quantity
                                        </Typography>
                                        <Typography variant="h5" fontWeight={700}>
                                            {closeDialog.trade?.quantity?.toLocaleString()}
                                        </Typography>
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                        
                        {/* Exit Price Input */}
                        <TextField
                            label="Exit Price"
                            type="number"
                            value={closeDialog.exitPrice}
                            onChange={(e) => setCloseDialog({ ...closeDialog, exitPrice: e.target.value })}
                            fullWidth
                            required
                            sx={{ 
                                mb: 2,
                                '& .MuiOutlinedInput-root': {
                                    fontSize: '1.25rem',
                                    fontWeight: 600
                                }
                            }}
                            inputProps={{ step: 0.01, min: 0 }}
                            placeholder="Nhập giá exit..."
                        />
                        
                        {/* P&L Preview */}
                        {closeDialog.exitPrice && closeDialog.trade && (
                            <Alert 
                                severity={parseFloat(closeDialog.exitPrice) > parseFloat(closeDialog.trade.entry_price) && closeDialog.trade.side === 'long' ? 'success' : parseFloat(closeDialog.exitPrice) < parseFloat(closeDialog.trade.entry_price) && closeDialog.trade.side === 'short' ? 'success' : 'error'}
                                icon={false}
                                sx={{ 
                                    mb: 2,
                                    py: 2,
                                    '& .MuiAlert-message': {
                                        width: '100%'
                                    }
                                }}
                            >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Typography variant="body1" fontWeight={600}>
                                        💰 Estimated P&L
                                    </Typography>
                                    <Typography variant="h5" fontWeight={700}>
                                        {calculateEstimatedPnL(closeDialog.trade, closeDialog.exitPrice)}
                                    </Typography>
                                </Box>
                            </Alert>
                        )}
                        
                        {/* Exit Notes */}
                        <TextField
                            label="Exit Notes (optional)"
                            value={closeDialog.exitNotes}
                            onChange={(e) => setCloseDialog({ ...closeDialog, exitNotes: e.target.value })}
                            multiline
                            rows={3}
                            fullWidth
                            placeholder="Lý do đóng lệnh: Chốt lời, cắt lỗ, trailing stop..."
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    bgcolor: 'grey.50'
                                }
                            }}
                        />
                    </Box>
                </DialogContent>
                <DialogActions sx={{ px: 3, py: 2.5, bgcolor: 'grey.50' }}>
                    <Button 
                        onClick={() => setCloseDialog({ open: false, trade: null, exitPrice: '', exitNotes: '' })}
                        size="large"
                        sx={{ px: 3 }}
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleCloseTrade}
                        variant="contained"
                        size="large"
                        disabled={!closeDialog.exitPrice || parseFloat(closeDialog.exitPrice) <= 0}
                        sx={{ px: 4, fontWeight: 600 }}
                    >
                        Close Trade
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
}

export default TradeJournal;
