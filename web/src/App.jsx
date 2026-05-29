import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { ThemeProvider } from './context/ThemeContext';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthProvider>
          <ChatProvider>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#111827',
                  color: '#F8FAFC',
                  border: '1px solid rgba(0,229,255,0.2)',
                  borderRadius: '12px',
                  fontFamily: "'Inter', sans-serif",
                  fontSize: '0.875rem',
                  boxShadow: '0 10px 40px rgba(0,0,0,0.4), 0 0 20px rgba(0,229,255,0.05)',
                  padding: '12px 16px',
                },
                success: {
                  iconTheme: { primary: '#22C55E', secondary: '#111827' },
                  style: { borderColor: 'rgba(34,197,94,0.3)' },
                },
                error: {
                  iconTheme: { primary: '#FF3B3B', secondary: '#111827' },
                  style: { borderColor: 'rgba(255,59,59,0.3)' },
                },
              }}
            />
            <AppRoutes />
          </ChatProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
