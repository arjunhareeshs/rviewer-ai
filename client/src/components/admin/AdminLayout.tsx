import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Users, Upload, LogOut } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

export function AdminLayout() {
  const { logout, user } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-cream">
      {/* Sidebar */}
      <div className="w-64 bg-surface border-r border-border flex flex-col justify-between">
        <div>
          <div className="p-6">
            <h1 className="font-display font-black text-2xl tracking-tight text-text-primary">
              RViewer<span className="text-accent">.ai</span>
            </h1>
            <p className="text-xs font-bold uppercase tracking-widest text-text-muted mt-1">Admin Panel</p>
          </div>
          <nav className="px-4 space-y-2 mt-4">
            <NavLink
              to="/admin/candidates"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all duration-200 ${
                  isActive
                    ? 'bg-text-primary text-white shadow-lg shadow-text-primary/20'
                    : 'text-text-secondary hover:bg-cream hover:text-text-primary'
                }`
              }
            >
              <Users size={20} />
              Candidates
            </NavLink>
            <NavLink
              to="/admin/upload"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all duration-200 ${
                  isActive
                    ? 'bg-text-primary text-white shadow-lg shadow-text-primary/20'
                    : 'text-text-secondary hover:bg-cream hover:text-text-primary'
                }`
              }
            >
              <Upload size={20} />
              Bulk Upload
            </NavLink>
          </nav>
        </div>

        <div className="p-4 border-t border-border">
          <div className="mb-4 px-4">
            <p className="text-sm font-bold text-text-primary truncate">{user?.name}</p>
            <p className="text-xs font-medium text-text-secondary truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2 text-sm font-bold text-danger hover:bg-danger-soft rounded-lg transition-colors"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative">
        <Outlet />
      </div>
    </div>
  );
}
