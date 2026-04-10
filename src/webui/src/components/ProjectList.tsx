import { useState, useMemo, useEffect } from 'react';
import { Project } from '../types';

interface Props {
  projects: Project[];
  selectedProjects: Set<string>;
  onToggle: (path: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  // External state props for preset support
  filter?: string;
  onFilterChange?: (filter: string) => void;
  expandedFolders?: Set<string>;
  onExpandedFoldersChange?: (folders: Set<string>) => void;
}

interface TreeNode {
  name: string;
  path: string;
  children: TreeNode[];
  project?: Project;
}

export default function ProjectList({
  projects,
  selectedProjects,
  onToggle,
  onSelectAll,
  onDeselectAll,
  filter: externalFilter,
  onFilterChange: externalOnFilterChange,
  expandedFolders: externalExpandedFolders,
  onExpandedFoldersChange: externalOnExpandedFoldersChange,
}: Props) {
  // Internal state with external override capability
  const [internalFilter, setInternalFilter] = useState('');
  const [modelFilter, setModelFilter] = useState<string>('all');
  const [internalExpandedFolders, setInternalExpandedFolders] = useState<Set<string>>(new Set());

  // Use external state if provided, otherwise use internal
  const filter = externalFilter ?? internalFilter;
  const setFilter = externalOnFilterChange ?? setInternalFilter;
  const expandedFolders = externalExpandedFolders ?? internalExpandedFolders;
  const setExpandedFolders = externalOnExpandedFoldersChange ?? setInternalExpandedFolders;

  const toggleFolder = (path: string) => {
    const current = expandedFolders;
    const next = new Set(current);
    if (next.has(path)) {
      next.delete(path);
    } else {
      next.add(path);
    }
    setExpandedFolders(next);
  };

  // Expand all folders
  const expandAll = () => {
    const allFolders = new Set<string>();
    for (const project of projects) {
      const parts = project.path.split('/');
      // Start from i=0 to include first-level folders (e.g., '01_LR_STUDY')
      // Stop at parts.length - 1 since the last part is the project name (leaf)
      for (let i = 0; i < parts.length - 1; i++) {
        allFolders.add(parts.slice(0, i + 1).join('/'));
      }
    }
    setExpandedFolders(allFolders);
  };

  // Collapse all folders
  const collapseAll = () => {
    setExpandedFolders(new Set());
  };

  const modelTypes = useMemo(() => {
    const types = new Set<string>();
    projects.forEach((p) => {
      if (p.config.use_model) types.add(p.config.use_model);
    });
    return ['all', ...Array.from(types).sort()];
  }, [projects]);

  const filtered = useMemo(() => {
    return projects.filter((p) => {
      const matchName = p.name.toLowerCase().includes(filter.toLowerCase());
      const matchModel = modelFilter === 'all' || p.config.use_model === modelFilter;
      return matchName && matchModel;
    });
  }, [projects, filter, modelFilter]);

  // Get selected projects
  const selectedProjectsList = useMemo(() => {
    return projects.filter((p) => selectedProjects.has(p.path));
  }, [projects, selectedProjects]);

  // Build tree from filtered projects
  const buildTree = (projectList: Project[]): TreeNode[] => {
    const root: TreeNode[] = [];
    const folderMap = new Map<string, TreeNode>();

    for (const project of projectList) {
      // Note: selected projects are NOT skipped here - they appear in both
      // the selected section AND their original tree position
      const parts = project.path.split('/');
      let currentLevel = root;

      for (let i = 0; i < parts.length; i++) {
        const partName = parts[i];
        const partPath = parts.slice(0, i + 1).join('/');
        const isLeaf = i === parts.length - 1;

        if (isLeaf) {
          currentLevel.push({
            name: partName,
            path: project.path,
            children: [],
            project,
          });
        } else {
          let folder = folderMap.get(partPath);
          if (!folder) {
            folder = {
              name: partName,
              path: partPath,
              children: [],
            };
            folderMap.set(partPath, folder);
            currentLevel.push(folder);
          }
          currentLevel = folder.children;
        }
      }
    }

    return root;
  };

  // Check if folder has visible children
  const isFolderExpanded = (path: string) => expandedFolders.has(path);

  // Update expanded state
  const tree = useMemo(() => buildTree(filtered), [filtered, selectedProjects]);

  // Flatten tree for rendering with depth
  const flattenTree = (nodes: TreeNode[], depth: number = 0): Array<{ node: TreeNode; depth: number }> => {
    const result: Array<{ node: TreeNode; depth: number }> = [];
    for (const node of nodes) {
      result.push({ node, depth });
      if (node.children.length > 0 && isFolderExpanded(node.path)) {
        result.push(...flattenTree(node.children, depth + 1));
      }
    }
    return result;
  };

  const flattenedNodes = useMemo(() => flattenTree(tree), [tree, expandedFolders]);

  // Selected project paths
  const selectedPaths = useMemo(() => new Set(selectedProjects), [selectedProjects]);

  // Auto-expand first level on initial load
  useEffect(() => {
    if (expandedFolders.size === 0 && filtered.length > 0) {
      const firstLevelFolders = new Set<string>();
      for (const project of filtered) {
        if (selectedProjects.has(project.path)) continue;
        const parts = project.path.split('/');
        if (parts.length > 1) {
          firstLevelFolders.add(parts[0]);
        }
      }
      setExpandedFolders(firstLevelFolders);
    }
  }, [filtered, selectedProjects]);

  return (
    <div className="project-list">
      <div className="filters">
        <input
          type="text"
          placeholder="Filter..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="filter-input"
        />
        <select value={modelFilter} onChange={(e) => setModelFilter(e.target.value)} className="filter-select">
          {modelTypes.map((t) => (
            <option key={t} value={t}>{t === 'all' ? 'All Models' : t}</option>
          ))}
        </select>
        <div className="batch-actions">
          <button onClick={onSelectAll} className="btn-small">Select All</button>
          <button onClick={onDeselectAll} className="btn-small">Deselect All</button>
          <button onClick={expandAll} className="btn-small">Expand All</button>
          <button onClick={collapseAll} className="btn-small">Collapse All</button>
        </div>
      </div>
      <div className="list-scroll">
        <div className="list">
          {/* Tree structure */}
          {flattenedNodes.map(({ node, depth }) => {
            const isFolder = node.children.length > 0;
            const isSelected = selectedPaths.has(node.path);

            const handleProjectClick = () => {
              if (!isFolder) {
                onToggle(node.path);
              }
            };

            const handleSelectAllInFolder = (e: React.MouseEvent) => {
              e.stopPropagation();
              // Select all projects under this folder
              const selectRecursive = (n: TreeNode) => {
                if (!n.children.length) {
                  // It's a project
                  if (!selectedPaths.has(n.path)) {
                    onToggle(n.path);
                  }
                } else {
                  n.children.forEach(selectRecursive);
                }
              };
              node.children.forEach(selectRecursive);
            };

            return (
              <div
                key={node.path}
                className={`tree-item ${isFolder ? 'folder' : 'project'} ${isSelected ? 'selected' : ''}`}
                style={{ paddingLeft: `${depth * 16 + 12}px` }}
                onClick={handleProjectClick}
              >
                {isFolder ? (
                  <>
                    <span className="folder-toggle" onClick={() => toggleFolder(node.path)}>
                      {isFolderExpanded(node.path) ? '▼' : '▶'}
                    </span>
                    <span className="folder-name">{node.name}</span>
                    <span className="folder-count">({node.children.length})</span>
                    <button
                      className="btn-select-folder"
                      onClick={handleSelectAllInFolder}
                      title="Select all in folder"
                    >
                      Select all
                    </button>
                  </>
                ) : (
                  <>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onToggle(node.path)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <span className="project-name">{node.name}</span>
                    <span className="project-model">{node.project?.config.use_model || 'unknown'}</span>
                  </>
                )}
              </div>
            );
          })}
          {flattenedNodes.length === 0 && selectedProjectsList.length === 0 && (
            <div className="no-results">No projects found</div>
          )}
        </div>
      </div>
      {/* Selected projects section - at bottom, independent scroll */}
      {selectedProjectsList.length > 0 && (
        <div className="selected-section">
          <div className="selected-header">
            Selected ({selectedProjectsList.length})
          </div>
          <div className="selected-list">
            {selectedProjectsList.map((project) => (
              <div key={project.path} className="tree-item project selected">
                <input
                  type="checkbox"
                  checked={true}
                  onChange={() => onToggle(project.path)}
                />
                <span className="project-name">{project.name}</span>
                <span className="project-model">{project.config.use_model || 'unknown'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <style>{`
        .project-list { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .filters { padding: 0.5rem; border-bottom: 1px solid #eee; flex-shrink: 0; }
        .filter-input, .filter-select { width: 100%; padding: 0.35rem; margin-bottom: 0.35rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.8rem; box-sizing: border-box; }
        .batch-actions { display: flex; gap: 0.5rem; margin-top: 0.35rem; flex-wrap: wrap; }
        .btn-small { padding: 0.25rem 0.5rem; font-size: 0.75rem; cursor: pointer; border: 1px solid #ddd; background: #f5f5f5; border-radius: 4px; }
        .btn-small:hover { background: #eee; }
        .list-scroll { flex: 1; overflow-y: auto; min-height: 0; }
        .list { padding: 0; }
        .selected-section { border-top: 2px solid #ddd; background: #f8f8f8; height: 150px; display: flex; flex-direction: column; flex-shrink: 0; }
        .selected-header { padding: 0.5rem 12px; font-weight: 600; font-size: 0.85rem; color: #2c3e50; background: #e3f2fd; border-bottom: 1px solid #ddd; flex-shrink: 0; }
        .selected-list { overflow-y: auto; flex: 1; }
        .tree-item { display: flex; align-items: center; padding: 4px 8px; cursor: pointer; border-bottom: 1px solid #f0f0f0; gap: 4px; white-space: nowrap; }
        .tree-item:hover { background: #f8f8f8; }
        .tree-item.selected { background: #e3f2fd; }
        .tree-item.folder { cursor: default; font-weight: 600; color: #333; }
        .tree-item.folder:hover { background: #f5f5f5; }
        .folder-toggle { cursor: pointer; font-size: 10px; color: #666; width: 16px; display: inline-block; text-align: center; flex-shrink: 0; }
        .folder-name { flex: 1; overflow: hidden; text-overflow: ellipsis; }
        .folder-count { font-size: 0.7rem; color: #999; margin-left: 4px; flex-shrink: 0; }
        .tree-item.project input[type="checkbox"] { width: 14px; height: 14px; cursor: pointer; flex-shrink: 0; }
        .project-name { flex: 1; font-weight: 500; overflow: hidden; text-overflow: ellipsis; font-size: 0.85rem; }
        .project-model { font-size: 0.65rem; color: #666; background: #eee; padding: 1px 4px; border-radius: 2px; flex-shrink: 0; }
        .no-results { padding: 2rem; text-align: center; color: #999; font-size: 0.9rem; }
        .btn-deselect { width: 16px; height: 16px; padding: 0; font-size: 11px; line-height: 1; border: none; background: #ff4444; color: white; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .btn-deselect:hover { background: #cc0000; }
        .btn-select-folder { padding: 2px 6px; font-size: 0.65rem; cursor: pointer; border: 1px solid #ddd; background: #f0f0f0; border-radius: 3px; opacity: 0; transition: opacity 0.2s; flex-shrink: 0; }
        .tree-item.folder:hover .btn-select-folder { opacity: 1; }
        .btn-select-folder:hover { background: #2c3e50; color: white; border-color: #2c3e50; }
      `}</style>
    </div>
  );
}
