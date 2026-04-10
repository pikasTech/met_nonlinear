import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Project, ProjectMetricsSummary } from './types';
import { fetchProjects, fetchProjectMetricsSummary, fetchState, saveState, fetchPresets, fetchPreset, savePreset, deletePreset, PresetState, PresetInfo } from './api';
import ProjectList from './components/ProjectList';
import ComparisonView from './components/ComparisonView';
import { SortingState, ColumnFiltersState } from '@tanstack/react-table';
import './App.css';

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [projectData, setProjectData] = useState<Map<string, { summary?: ProjectMetricsSummary }>>(new Map());

  // Table/filter state for preset support
  const [globalFilter, setGlobalFilter] = useState('');
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>({});
  const [showFilters, setShowFilters] = useState(false);
  const [showColumnPanel, setShowColumnPanel] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  // Preset management state
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [presetName, setPresetName] = useState('');
  const [showPresetPanel, setShowPresetPanel] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showStatus = useCallback((msg: string) => {
    setStatusMsg(msg);
    setTimeout(() => setStatusMsg(''), 3000);
  }, []);

  // Load projects on mount
  useEffect(() => {
    fetchProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Load presets list
  useEffect(() => {
    fetchPresets().then((data) => setPresets(data.presets)).catch(() => {});
  }, []);

  // Load saved state on startup
  useEffect(() => {
    const loadSavedState = async () => {
      try {
        const state = await fetchState();
        if (state) {
          setGlobalFilter(state.globalFilter ?? '');
          setColumnFilters(state.columnFilters ?? []);
          setSorting(state.sorting ?? []);
          setColumnVisibility(state.columnVisibility ?? {});
          setShowFilters(state.showFilters ?? false);
          setShowColumnPanel(state.showColumnPanel ?? false);
          setExpandedFolders(new Set(state.expandedFolders ?? []));
        }
      } catch (e) {
        console.error('Failed to load saved state:', e);
      }
    };
    loadSavedState();
  }, []);

  // Auto-save on state change (debounced)
  useEffect(() => {
    if (saveTimerRef.current) {
      clearTimeout(saveTimerRef.current);
    }
    saveTimerRef.current = setTimeout(async () => {
      const state: PresetState = {
        selectedProjects: Array.from(selectedProjects),
        globalFilter,
        columnFilters,
        sorting,
        columnVisibility,
        expandedFolders: Array.from(expandedFolders),
        showFilters,
        showColumnPanel,
      };
      try {
        await saveState(state);
      } catch (e) {
        console.error('Failed to auto-save state:', e);
      }
    }, 1000);
  }, [selectedProjects, globalFilter, columnFilters, sorting, columnVisibility, expandedFolders, showFilters, showColumnPanel]);

  // Load project data for selected projects
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

  // Preset handlers
  const handleSavePreset = async () => {
    if (!presetName.trim()) {
      showStatus('Please enter a preset name');
      return;
    }
    try {
      const state: PresetState = {
        selectedProjects: Array.from(selectedProjects),
        globalFilter,
        columnFilters,
        sorting,
        columnVisibility,
        expandedFolders: Array.from(expandedFolders),
        showFilters,
        showColumnPanel,
      };
      await savePreset(presetName.trim(), state);
      const data = await fetchPresets();
      setPresets(data.presets);
      setPresetName('');
      showStatus(`Preset "${presetName}" saved`);
    } catch (e) {
      showStatus('Failed to save preset');
    }
  };

  const handleUpdatePreset = async (name: string) => {
    try {
      const state: PresetState = {
        selectedProjects: Array.from(selectedProjects),
        globalFilter,
        columnFilters,
        sorting,
        columnVisibility,
        expandedFolders: Array.from(expandedFolders),
        showFilters,
        showColumnPanel,
      };
      await savePreset(name, state);
      showStatus(`Preset "${name}" updated`);
    } catch (e) {
      showStatus('Failed to update preset');
    }
  };

  const handleLoadPreset = async (name: string) => {
    try {
      const data = await fetchPreset(name);
      const state = data.state;
      if (state) {
        // Filter out project paths that don't exist in the current projects list
        const validSelectedProjects = (state.selectedProjects ?? []).filter(
          (path: string) => projects.some((p) => p.path === path)
        );
        const missingProjects = (state.selectedProjects ?? []).filter(
          (path: string) => !projects.some((p) => p.path === path)
        );

        setSelectedProjects(new Set(validSelectedProjects));
        setGlobalFilter(state.globalFilter ?? '');
        setColumnFilters(state.columnFilters ?? []);
        setSorting(state.sorting ?? []);
        setColumnVisibility(state.columnVisibility ?? {});
        setExpandedFolders(new Set(state.expandedFolders ?? []));
        setShowFilters(state.showFilters ?? false);
        setShowColumnPanel(state.showColumnPanel ?? false);

        if (missingProjects.length > 0) {
          showStatus(`Preset "${name}" loaded (${missingProjects.length} project(s) not found)`);
        } else {
          showStatus(`Preset "${name}" loaded`);
        }
        setShowPresetPanel(false);
      }
    } catch (e) {
      showStatus('Failed to load preset');
    }
  };

  const handleDeletePreset = async (name: string) => {
    try {
      await deletePreset(name);
      const data = await fetchPresets();
      setPresets(data.presets);
      showStatus(`Preset "${name}" deleted`);
    } catch (e) {
      showStatus('Failed to delete preset');
    }
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
        <div className="header-actions">
          <button
            className={`btn-preset ${showPresetPanel ? 'active' : ''}`}
            onClick={() => setShowPresetPanel(!showPresetPanel)}
          >
            Presets
          </button>
        </div>
      </header>
      {showPresetPanel && (
        <div className="preset-panel">
          <div className="preset-panel-header">Presets</div>
          <div className="preset-save">
            <input
              type="text"
              placeholder="Preset name..."
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              className="preset-input"
            />
            <button onClick={handleSavePreset} className="btn-save-preset">Save</button>
          </div>
          <div className="preset-list">
            {presets.length === 0 && <div className="preset-empty">No saved presets</div>}
            {presets.map((p) => (
              <div key={p.name} className="preset-item">
                <span className="preset-item-name" onClick={() => handleLoadPreset(p.name)}>
                  {p.name}
                </span>
                <span className="preset-item-date">{new Date(p.createdAt).toLocaleDateString()}</span>
                <button
                  className="btn-update-preset"
                  onClick={() => handleUpdatePreset(p.name)}
                  title="Update preset with current settings"
                >
                  ↻
                </button>
                <button
                  className="btn-delete-preset"
                  onClick={() => handleDeletePreset(p.name)}
                  title="Delete preset"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      {statusMsg && <div className="status-toast">{statusMsg}</div>}
      <main className="main">
        <aside className="sidebar">
          <ProjectList
            projects={projects}
            selectedProjects={selectedProjects}
            onToggle={toggleProject}
            onSelectAll={selectAll}
            onDeselectAll={deselectAll}
            filter={globalFilter}
            onFilterChange={setGlobalFilter}
            expandedFolders={expandedFolders}
            onExpandedFoldersChange={setExpandedFolders}
          />
        </aside>
        <section className="content">
          {selectedProjects.size > 0 ? (
            <ComparisonView
              projects={selectedArray
                .map((path) => {
                  const project = projects.find((p) => p.path === path);
                  if (!project) return null;
                  return {
                    name: project.name,
                    project,
                    data: projectData.get(path) ?? {}
                  };
                })
                .filter((p): p is NonNullable<typeof p> => p !== null)}
              onRemove={(path) => toggleProject(path)}
              globalFilter={globalFilter}
              onGlobalFilterChange={setGlobalFilter}
              columnFilters={columnFilters}
              onColumnFiltersChange={setColumnFilters}
              sorting={sorting}
              onSortingChange={setSorting}
              columnVisibility={columnVisibility}
              onColumnVisibilityChange={setColumnVisibility}
              showFilters={showFilters}
              onShowFiltersChange={setShowFilters}
              showColumnPanel={showColumnPanel}
              onShowColumnPanelChange={setShowColumnPanel}
            />
          ) : (
            <div className="placeholder">Select projects to compare</div>
          )}
        </section>
      </main>
    </div>
  );
}