import { useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';
import FigureStudioPage from './pages/FigureStudioPage';
import HomePage from './pages/HomePage';
import PaperEditorPage from './pages/PaperEditorPage';
import ProjectVisualizerPage from './pages/ProjectVisualizerPage';

type AppRoute = '/' | '/projects' | '/paper-figures' | '/paper-editor';

interface RouteLink {
  path: AppRoute;
  label: string;
  caption: string;
}

const ROUTE_LINKS: RouteLink[] = [
  { path: '/', label: 'Home', caption: 'Switch workspace' },
  { path: '/projects', label: 'Projects', caption: 'Compare experiments' },
  { path: '/paper-editor', label: 'Paper Editor', caption: 'Edit and preview LaTeX' },
  { path: '/paper-figures', label: 'Figure Studio', caption: 'Tune paper bitmaps' },
];

function normalizeRoute(pathname: string): AppRoute {
  if (pathname === '/projects' || pathname.startsWith('/projects/')) {
    return '/projects';
  }
  if (pathname === '/paper-figures' || pathname.startsWith('/paper-figures/')) {
    return '/paper-figures';
  }
  if (pathname === '/paper-editor' || pathname.startsWith('/paper-editor/')) {
    return '/paper-editor';
  }
  return '/';
}

function renderRoute(route: AppRoute, onNavigate: (path: string) => void) {
  if (route === '/projects') {
    return <ProjectVisualizerPage />;
  }
  if (route === '/paper-editor') {
    return <PaperEditorPage />;
  }
  if (route === '/paper-figures') {
    return <FigureStudioPage />;
  }
  return <HomePage onNavigate={onNavigate} />;
}

export default function App() {
  const [route, setRoute] = useState<AppRoute>(() => normalizeRoute(window.location.pathname));
  const [navCollapsed, setNavCollapsed] = useState(() => normalizeRoute(window.location.pathname) !== '/');

  useEffect(() => {
    const handlePopState = () => setRoute(normalizeRoute(window.location.pathname));
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  useEffect(() => {
    const normalized = normalizeRoute(window.location.pathname);
    if (normalized !== window.location.pathname) {
      window.history.replaceState({}, '', normalized);
    }
  }, []);

  const navigate = useCallback((nextPath: string) => {
    const nextRoute = normalizeRoute(nextPath);
    if (nextRoute !== window.location.pathname) {
      window.history.pushState({}, '', nextRoute);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setRoute(nextRoute);
    setNavCollapsed(nextRoute !== '/');
  }, []);

  const activeRoute = useMemo(() => normalizeRoute(route), [route]);

  return (
    <div className={`route-shell route-shell--${activeRoute === '/' ? 'home' : 'workspace'}`}>
      <nav className={`route-rail ${navCollapsed ? 'is-collapsed' : ''}`} aria-label="Workspace navigation">
        {navCollapsed ? (
          <button
            type="button"
            className="route-rail__bubble"
            data-testid="route-nav-toggle"
            title="Open navigation"
            onClick={() => setNavCollapsed(false)}
          >
            MET
          </button>
        ) : (
          <>
            <span className="route-rail__brand">MET Nonlinear</span>
            {ROUTE_LINKS.map((link) => (
              <button
                key={link.path}
                type="button"
                className={`route-rail__link ${activeRoute === link.path ? 'is-active' : ''}`}
                data-testid={`route-${link.label.toLowerCase().replace(/\s+/g, '-')}`}
                onClick={() => navigate(link.path)}
              >
                <strong>{link.label}</strong>
                <span>{link.caption}</span>
              </button>
            ))}
            <button
              type="button"
              className="route-rail__collapse"
              data-testid="route-nav-collapse"
              title="Collapse navigation"
              onClick={() => setNavCollapsed(true)}
            >
              -
            </button>
          </>
        )}
      </nav>
      {renderRoute(activeRoute, navigate)}
    </div>
  );
}
