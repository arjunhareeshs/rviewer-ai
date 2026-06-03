import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UploadPage from './pages/UploadPage';
import NotFoundPage from './pages/NotFoundPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { WorkspaceLayout } from './components/workspace/WorkspaceLayout';
import OverviewPage from './pages/analysis/OverviewPage';
import FullAnalysisPage from './pages/analysis/FullAnalysisPage';
import LinksPage from './pages/analysis/LinksPage';
import RoadmapPage from './pages/analysis/RoadmapPage';
import BuilderPage from './pages/builder/BuilderPage';
import InterviewLobbyPage from './pages/interview/InterviewLobbyPage';
import InterviewRoomPage from './pages/interview/InterviewRoomPage';
import InterviewReportPage from './pages/interview/InterviewReportPage';
import AdminCandidatesPage from './pages/admin/AdminCandidatesPage';
import AdminUploadPage from './pages/admin/AdminUploadPage';
import { AdminLayout } from './components/admin/AdminLayout';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        <Route path="/upload" element={
          <ProtectedRoute>
            <UploadPage />
          </ProtectedRoute>
        } />
        
        <Route path="/workspace" element={
          <ProtectedRoute>
            <WorkspaceLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="analysis/overview" replace />} />
          <Route path="analysis/overview" element={<OverviewPage />} />
          <Route path="analysis/full" element={<FullAnalysisPage />} />
          <Route path="analysis/links" element={<LinksPage />} />
          <Route path="analysis/roadmap" element={<RoadmapPage />} />
          <Route path="builder" element={<BuilderPage />} />
          <Route path="interview" element={<InterviewLobbyPage />} />
          <Route path="interview/:roomId" element={<InterviewRoomPage />} />
          <Route path="interview/:roomId/report" element={<InterviewReportPage />} />
        </Route>

        <Route path="/admin" element={
          <ProtectedRoute adminOnly>
            <AdminLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="candidates" replace />} />
          <Route path="candidates" element={<AdminCandidatesPage />} />
          <Route path="upload" element={<AdminUploadPage />} />
        </Route>
        
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
