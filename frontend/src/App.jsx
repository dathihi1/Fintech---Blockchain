import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import NLPAnalyzer from './pages/NLPAnalyzer';
import TradeJournal from './pages/TradeJournal';
import Analytics from './pages/Analytics';

function App() {
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/nlp" element={<NLPAnalyzer />} />
                    <Route path="/trades" element={<TradeJournal />} />
                    <Route path="/analytics" element={<Analytics />} />
                </Routes>
            </Box>
        </Box>
    );
}

export default App;
