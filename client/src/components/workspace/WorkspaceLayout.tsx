import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { useResumeStore } from '../../stores/resumeStore';
import { motion } from 'framer-motion';

export function WorkspaceLayout() {
  const { user, logout } = useAuthStore();
  const { activeResume } = useResumeStore();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getPageTitle = () => {
    if (location.pathname.includes('/analysis')) return 'Resume Intelligence';
    if (location.pathname.includes('/builder')) return 'Resume Builder';
    if (location.pathname.includes('/interview')) return 'Interview Session';
    return 'Workspace';
  };

  const analysisTarget = activeResume?.id 
    ? `/workspace/analysis/overview?id=${activeResume.id}`
    : `/workspace/analysis/overview${location.search}`;

  return (
    <div className="min-h-screen bg-cream flex flex-col">
      {/* Top Navigation Bar */}
      <header className="bg-surface border-b border-border h-16 flex items-center justify-between px-6 flex-none z-10 shadow-sm">
        
        {/* Left: Branding & Title */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white font-bold">R</div>
          </div>
          <div className="h-6 w-px bg-border"></div>
          <h1 className="font-display font-bold text-xl text-text-primary tracking-tight">
            {getPageTitle()}
          </h1>
        </div>

        {/* Center: Tabs */}
        <div className="absolute left-1/2 -translate-x-1/2 flex bg-cream p-1 rounded-xl border border-border">
          <NavLink 
            to={analysisTarget}
            className={({ isActive }) => `relative px-6 py-1.5 rounded-lg text-sm font-bold transition-colors z-10 ${isActive || location.pathname.includes('/analysis') ? 'text-accent' : 'text-text-secondary hover:text-text-primary'}`}
          >
            {location.pathname.includes('/analysis') && (
              <motion.div layoutId="activeTab" className="absolute inset-0 bg-white shadow-sm rounded-lg border border-border z-[-1]" />
            )}
            Analysis
          </NavLink>
          <NavLink 
            to="/workspace/builder"
            className={({ isActive }) => `relative px-6 py-1.5 rounded-lg text-sm font-bold transition-colors z-10 ${isActive ? 'text-accent' : 'text-text-secondary hover:text-text-primary'}`}
          >
            {location.pathname === '/workspace/builder' && (
              <motion.div layoutId="activeTab" className="absolute inset-0 bg-white shadow-sm rounded-lg border border-border z-[-1]" />
            )}
            Builder
          </NavLink>
          <NavLink 
            to="/workspace/interview"
            className={({ isActive }) => `relative px-6 py-1.5 rounded-lg text-sm font-bold transition-colors z-10 ${isActive || location.pathname.includes('/interview') ? 'text-accent' : 'text-text-secondary hover:text-text-primary'}`}
          >
            {location.pathname.includes('/interview') && (
              <motion.div layoutId="activeTab" className="absolute inset-0 bg-white shadow-sm rounded-lg border border-border z-[-1]" />
            )}
            Interview
          </NavLink>
        </div>

        {/* Right: User menu */}
        <div className="flex items-center gap-4">
          <div className="text-sm font-semibold text-text-primary hidden sm:block">
            {user?.name}
          </div>
          <button 
            onClick={handleLogout}
            className="text-sm font-bold text-text-secondary hover:text-danger transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Secondary Sub-Navigation Bar for Analysis */}
      {location.pathname.includes('/analysis') && (
        <div className="bg-surface border-b border-border py-3 px-6 flex items-center gap-6 flex-none shadow-sm z-10">
          <NavLink 
            to={`/workspace/analysis/overview${location.search || (activeResume?.id ? `?id=${activeResume.id}` : '')}`}
            className={({ isActive }) => `text-sm font-bold transition-colors ${isActive ? 'text-accent border-b-2 border-accent pb-1' : 'text-text-secondary hover:text-text-primary pb-1'}`}
          >
            Overview
          </NavLink>
          <NavLink 
            to={`/workspace/analysis/full${location.search || (activeResume?.id ? `?id=${activeResume.id}` : '')}`}
            className={({ isActive }) => `text-sm font-bold transition-colors ${isActive ? 'text-accent border-b-2 border-accent pb-1' : 'text-text-secondary hover:text-text-primary pb-1'}`}
          >
            Full Analysis
          </NavLink>
          <NavLink 
            to={`/workspace/analysis/links${location.search || (activeResume?.id ? `?id=${activeResume.id}` : '')}`}
            className={({ isActive }) => `text-sm font-bold transition-colors ${isActive ? 'text-accent border-b-2 border-accent pb-1' : 'text-text-secondary hover:text-text-primary pb-1'}`}
          >
            Link Analysis
          </NavLink>
          <NavLink 
            to={`/workspace/analysis/roadmap${location.search || (activeResume?.id ? `?id=${activeResume.id}` : '')}`}
            className={({ isActive }) => `text-sm font-bold transition-colors ${isActive ? 'text-accent border-b-2 border-accent pb-1' : 'text-text-secondary hover:text-text-primary pb-1'}`}
          >
            Career Roadmap
          </NavLink>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto relative">
        <Outlet />
      </main>
    </div>
  );
}
