import { useState, useEffect, useMemo } from 'react';
import { Project, ProjectMetricsSummary } from './types';
import { fetchProjects, fetchProjectMetricsSummary } from './api';
import ProjectList from './components/ProjectList';
import ComparisonView from './components/ComparisonView';
import './App.css';

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [projectData, setProjectData] = useState<Map<string, { summary?: ProjectMetricsSummary }>>(new Map());

  useEffect(() => {
    fetchProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const newData = new Map<string, { summary?: ProjectMetricsSummary }>();
      for (const path of selectedProjects) {
        try {
          const summary = await fetchProjectMetricsSummary(path).catch(() => null);
          newData.set(path, {
            summary: summary ?? undefined
          });
        } catch {
          newData.set(path, {});
        }
      }
      setProjectData(newData);
    };
    if (selectedProjects.size > 0) {
      fetchData();
    }
  }, [selectedProjects]);

  const toggleProject = (path: string) => {
    setSelectedProjects((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const selectAll = () => {
    setSelectedProjects(new Set(projects.map((p) => p.path)));
  };

  const deselectAll = () => {
    setSelectedProjects(new Set());
  };

  const selectedArray = useMemo(() => Array.from(selectedProjects), [selectedProjects]);

  if (loading) return <div className="loading">Loading projects...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="app">
      <header className="header">
        <h1>MET Nonlinear - Project Visualizer</h1>
        <div className="header-stats">
          {projects.length} projects | {selectedProjects.size} selected
        </div>
      </header>
      <main className="main">
        <aside className="sidebar">
          <ProjectList
            projects={projects}
            selectedProjects={selectedProjects}
            onToggle={toggleProject}
            onSelectAll={selectAll}
            onDeselectAll={deselectAll}
          />
        </aside>
        <section className="content">
          {selectedProjects.size > 0 ? (
            <ComparisonView
              projects={selectedArray.map((path) => ({
                name: projects.find((p) => p.path === path)?.name ?? path,
                project: projects.find((p) => p.path === path)!,
                data: projectData.get(path) ?? {}
              }))}
              onRemove={(path) => toggleProject(path)}
            />
          ) : (
            <div className="placeholder">Select projects to compare</div>
          )}
        </section>
      </main>
    </div>
  );
}
