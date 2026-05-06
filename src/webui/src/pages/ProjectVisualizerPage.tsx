import { useState, useEffect, useMemo, useCallback } from 'react';
import { Project, ProjectMetricsSummary } from '../types';
import { fetchProjects, fetchProjectMetricsSummary, fetchState, saveState, fetchPresets, fetchPreset, savePreset, deletePreset, renamePreset, PresetState, PresetInfo, LossCurvesState, defaultLossCurvesState } from '../clientApi';
import ProjectList from '../components/ProjectList';
import ComparisonView from '../components/ComparisonView';
import { SortingState, ColumnFiltersState } from '@tanstack/react-table';
import '../App.css';

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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Preset management state
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [presetName, setPresetName] = useState('');
  const [showPresetPanel, setShowPresetPanel] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [initialized, setInitialized] = useState(false);
  const [renamingPreset, setRenamingPreset] = useState<string | null>(null);
  const [renameInput, setRenameInput] = useState('');

  // Loss curves state
  const [lossCurvesState, setLossCurvesState] = useState<LossCurvesState>(defaultLossCurvesState);

  const allFolderPaths = useMemo(() => {
    const folders = new Set<string>();
    for (const project of projects) {
      const parts = project.path.split('/');
      for (let i = 0; i < parts.length - 1; i++) {
        folders.add(parts.slice(0, i + 1).join('/'));
      }
    }
    return Array.from(folders).sort();
  }, [projects]);

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

  // Load saved state on startup (depends on projects loaded to validate selected projects)
  useEffect(() => {
    if (projects.length === 0) return; // Wait for projects to load
    const loadSavedState = async () => {
      try {
        const state = await fetchState();
        console.log('[State] Loaded state:', state);
        if (state) {
          // Filter to only valid project paths
          const validSelected = (state.selectedProjects ?? []).filter(
            (path: string) => projects.some((p) => p.path === path)
          );
          console.log('[State] Valid selected projects:', validSelected);
          setSelectedProjects(new Set(validSelected));
          setGlobalFilter(state.globalFilter ?? '');
          setColumnFilters(state.columnFilters ?? []);
          setSorting(state.sorting ?? []);
          setColumnVisibility(state.columnVisibility ?? {});
          setShowFilters(state.showFilters ?? false);
          setShowColumnPanel(state.showColumnPanel ?? false);
          setExpandedFolders(new Set(state.expandedFolders ?? []));
          setSidebarCollapsed(state.sidebarCollapsed ?? false);
          setLossCurvesState({ ...defaultLossCurvesState, ...state.lossCurves });
        }
        setInitialized(true);
      } catch (e) {
        console.error('[State] Failed to load saved state:', e);
        setInitialized(true);
      }
    };
    loadSavedState();
  }, [projects]);

  // Auto-save on state change (only after initialization is complete)
  useEffect(() => {
    if (!initialized) return; // Don't save until we've loaded the initial state
    const state: PresetState = {
      selectedProjects: Array.from(selectedProjects),
      globalFilter,
      columnFilters,
      sorting,
      columnVisibility,
      expandedFolders: Array.from(expandedFolders),
      showFilters,
      showColumnPanel,
      sidebarCollapsed,
      lossCurves: lossCurvesState,
    };
    console.log('[State] Auto-saving state, selectedProjects:', state.selectedProjects);
    saveState(state).catch((e) => {
      console.error('[State] Failed to auto-save state:', e);
    });
  }, [initialized, selectedProjects, globalFilter, columnFilters, sorting, columnVisibility, expandedFolders, showFilters, showColumnPanel, lossCurvesState]);

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

  const expandAllFolders = useCallback(() => {
    setExpandedFolders(new Set(allFolderPaths));
  }, [allFolderPaths]);

  const collapseAllFolders = useCallback(() => {
    setExpandedFolders(new Set());
  }, []);

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
        sidebarCollapsed,
        lossCurves: lossCurvesState,
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
        sidebarCollapsed,
        lossCurves: lossCurvesState,
      };
      await savePreset(name, state);
      const data = await fetchPresets();
      setPresets(data.presets);
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
        setSidebarCollapsed(state.sidebarCollapsed ?? false);
        setLossCurvesState({ ...defaultLossCurvesState, ...state.lossCurves });

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

  const handleRenamePreset = async (oldName: string) => {
    if (!renameInput.trim() || renameInput.trim() === oldName) {
      setRenamingPreset(null);
      setRenameInput('');
      return;
    }
    try {
      await renamePreset(oldName, renameInput.trim());
      const data = await fetchPresets();
      setPresets(data.presets);
      setRenamingPreset(null);
      setRenameInput('');
      showStatus(`Preset renamed to "${renameInput.trim()}"`);
    } catch (e) {
      showStatus('Failed to rename preset');
    }
  };

  const startRename = (name: string) => {
    setRenamingPreset(name);
    setRenameInput(name);
  };

  const selectedArray = useMemo(() => Array.from(selectedProjects), [selectedProjects]);

  if (loading) return <div className="loading">Loading projects...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="app">
      <header className="header">
        <button
          className="btn-sidebar-toggle"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={sidebarCollapsed ? 'Show sidebar' : 'Hide sidebar'}
        >
          {sidebarCollapsed ? '☰' : '◀'}
        </button>
        <h1>MET Nonlinear - Project Visualizer</h1>
        <div className="header-stats">
          {projects.length} projects | {selectedProjects.size} selected
        </div>
        <div className="header-actions">
          <button
            className="btn-header-action"
            onClick={expandAllFolders}
            title="Expand all project folders"
          >
            Expand All
          </button>
          <button
            className="btn-header-action"
            onClick={collapseAllFolders}
            title="Collapse all project folders"
          >
            Collapse All
          </button>
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
                {renamingPreset === p.name ? (
                  <>
                    <input
                      type="text"
                      className="preset-rename-input"
                      value={renameInput}
                      onChange={(e) => setRenameInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleRenamePreset(p.name)}
                      autoFocus
                    />
                    <button
                      className="btn-rename-confirm"
                      onClick={() => handleRenamePreset(p.name)}
                      title="Confirm rename"
                    >
                      ✓
                    </button>
                    <button
                      className="btn-rename-cancel"
                      onClick={() => { setRenamingPreset(null); setRenameInput(''); }}
                      title="Cancel rename"
                    >
                      ×
                    </button>
                  </>
                ) : (
                  <>
                    <span className="preset-item-name" onClick={() => handleLoadPreset(p.name)}>
                      {p.name}
                    </span>
                    <span className="preset-item-date">{new Date(p.createdAt).toLocaleString()}</span>
                    <button
                      className="btn-rename-preset"
                      onClick={() => startRename(p.name)}
                      title="Rename preset"
                    >
                      ✎
                    </button>
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
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {statusMsg && <div className="status-toast">{statusMsg}</div>}
      <main className="main">
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          {!sidebarCollapsed && (
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
          )}
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
              lossCurvesState={lossCurvesState}
              onLossCurvesStateChange={setLossCurvesState}
            />
          ) : (
            <div className="placeholder">Select projects to compare</div>
          )}
        </section>
      </main>
    </div>
  );
}
