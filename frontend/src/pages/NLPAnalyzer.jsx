import { useState } from 'react';
import {
    Box,
    Container,
    Grid,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Chip,
    LinearProgress,
    Alert,
    AlertTitle,
    Divider,
    CircularProgress
} from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import SendIcon from '@mui/icons-material/Send';
import { analyzeText } from '../services/api';

// Emotion colors
const emotionColors = {
    FOMO: 'error',
    FEAR: 'warning',
    GREED: 'error',
    REVENGE: 'error',
    OVERCONFIDENCE: 'warning',
    RATIONAL: 'success',
    CONFIDENT: 'primary',
    DISCIPLINE: 'success'
};

// Example texts
const exampleTexts = [
    { label: 'FOMO', text: 'BTC breakout! Phải vào ngay kẻo lỡ! All in luôn!' },
    { label: 'Revenge', text: 'Thua 3 lệnh rồi, phải gỡ gạc bằng được. Tăng size x2!' },
    { label: 'Rational', text: 'Entry theo plan, RR 1:3, đặt SL 2%, theo trend lớn.' },
    { label: 'Fear', text: 'Sợ quá! Cắt lỗ ngay đi, thị trường sập rồi!' },
];

function NLPAnalyzer() {
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!text.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const data = await analyzeText(text);
            setResult(data);
        } catch (err) {
            setError('Không thể kết nối đến server. Đảm bảo backend đang chạy.');
            console.error(err);
        }

        setLoading(false);
    };

    const handleExampleClick = (exampleText) => {
        setText(exampleText);
    };

    return (
        <Container maxWidth="lg" sx={{ py: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Typography variant="h4" fontWeight={700}>
                        NLP Analyzer
                    </Typography>
                </Box>
                <Typography variant="body1" color="text.secondary">
                    Phân tích sentiment và emotions từ ghi chú giao dịch của bạn
                </Typography>
            </Box>

            <Grid container spacing={3}>
                {/* Input Section */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                Nhập ghi chú giao dịch
                            </Typography>

                            <TextField
                                multiline
                                rows={6}
                                fullWidth
                                placeholder="Ví dụ: Phải vào ngay kẻo lỡ! BTC đang pump mạnh..."
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                sx={{ mb: 2 }}
                            />

                            <Button
                                variant="contained"
                                size="large"
                                fullWidth
                                onClick={handleAnalyze}
                                disabled={loading || !text.trim()}
                                endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                            >
                                {loading ? 'Đang phân tích...' : 'Phân tích'}
                            </Button>

                            <Divider sx={{ my: 3 }} />

                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                Thử với các ví dụ:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {exampleTexts.map((example, index) => (
                                    <Chip
                                        key={index}
                                        label={example.label}
                                        onClick={() => handleExampleClick(example.text)}
                                        color={emotionColors[example.label.toUpperCase()] || 'default'}
                                        variant="outlined"
                                        sx={{ cursor: 'pointer' }}
                                    />
                                ))}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Result Section */}
                <Grid item xs={12} md={6}>
                    <Card sx={{ minHeight: 400 }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                Kết quả phân tích
                            </Typography>

                            {error && (
                                <Alert severity="error" sx={{ mb: 2 }}>
                                    {error}
                                </Alert>
                            )}

                            {!result && !loading && !error && (
                                <Box sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    height: 300,
                                    color: 'text.secondary'
                                }}>
                                    <Typography>
                                        Nhập text và nhấn Phân tích để xem kết quả
                                    </Typography>
                                </Box>
                            )}

                            {loading && (
                                <Box sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    height: 300
                                }}>
                                    <CircularProgress />
                                </Box>
                            )}

                            {result && !loading && (
                                <Box className="fade-in">
                                    {/* Language */}
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Ngôn ngữ:
                                            <Chip
                                                label={result.language === 'vi' ? '🇻🇳 Tiếng Việt' : '🇺🇸 English'}
                                                size="small"
                                                sx={{ ml: 1 }}
                                            />
                                        </Typography>
                                    </Box>

                                    {/* Sentiment */}
                                    <Box sx={{ mb: 3 }}>
                                        <Typography variant="body2" color="text.secondary" gutterBottom>
                                            Sentiment
                                        </Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                            <Chip
                                                label={result.sentiment_label}
                                                color={
                                                    result.sentiment_label === 'positive' ? 'success' :
                                                        result.sentiment_label === 'negative' ? 'error' : 'default'
                                                }
                                            />
                                            <Typography variant="body2">
                                                Score: {result.sentiment_score?.toFixed(2)}
                                            </Typography>
                                        </Box>
                                    </Box>

                                    {/* Quality Score */}
                                    <Box sx={{ mb: 3 }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Chất lượng reasoning
                                            </Typography>
                                            <Typography
                                                variant="body2"
                                                color={result.quality_score > 0.6 ? 'success.main' : 'warning.main'}
                                                fontWeight={600}
                                            >
                                                {Math.round(result.quality_score * 100)}%
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={result.quality_score * 100}
                                            color={result.quality_score > 0.6 ? 'success' : 'warning'}
                                            sx={{ height: 10, borderRadius: 5 }}
                                        />
                                    </Box>

                                    {/* Emotions */}
                                    {result.emotions?.length > 0 && (
                                        <Box sx={{ mb: 3 }}>
                                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                                Emotions detected
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                                {result.emotions.map((emotion, index) => (
                                                    <Chip
                                                        key={index}
                                                        label={`${emotion.type} (${Math.round(emotion.confidence * 100)}%)`}
                                                        color={emotionColors[emotion.type] || 'default'}
                                                        size="small"
                                                    />
                                                ))}
                                            </Box>
                                        </Box>
                                    )}

                                    {/* Behavioral Flags */}
                                    {result.behavioral_flags?.length > 0 && (
                                        <Box sx={{ mb: 3 }}>
                                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                                ⚠️ Behavioral Flags
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                                {result.behavioral_flags.map((flag, index) => (
                                                    <Chip
                                                        key={index}
                                                        label={flag}
                                                        color="error"
                                                        variant="outlined"
                                                        size="small"
                                                    />
                                                ))}
                                            </Box>
                                        </Box>
                                    )}

                                    {/* Warnings */}
                                    {result.warnings?.length > 0 && (
                                        <Box>
                                            {result.warnings.map((warning, index) => (
                                                <Alert
                                                    key={index}
                                                    severity="warning"
                                                    sx={{ mb: 1 }}
                                                >
                                                    {warning}
                                                </Alert>
                                            ))}
                                        </Box>
                                    )}
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
}

export default NLPAnalyzer;
