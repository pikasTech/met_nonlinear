import { useState } from 'react';
import { Project, ProjectMetricsSummary } from '../types';
import ChartView from './ChartView';
import TableView from './TableView';
import { SortingState, ColumnFiltersState } from '@tanstack/react-table';

interface ProjectData {
  name: string;
  project: Project;
  data: {
    summary?: ProjectMetricsSummary;
  };
}

interface Props {
  projects: ProjectData[];
  onRemove?: (path: string) => void;
  // Table state props for preset support
  globalFilter?: string;
  onGlobalFilterChange?: (filter: string) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: (filters: ColumnFiltersState) => void;
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  columnVisibility?: Record<string, boolean>;
  onColumnVisibilityChange?: (visibility: Record<string, boolean>) => void;
  showFilters?: boolean;
  onShowFiltersChange?: (show: boolean) => void;
  showColumnPanel?: boolean;
  onShowColumnPanelChange?: (show: boolean) => void;
}

type ViewMode = 'chart' | 'table';

export default function ComparisonView({
  projects,
  onRemove,
  globalFilter,
  onGlobalFilterChange,
  columnFilters,
  onColumnFiltersChange,
  sorting,
  onSortingChange,
  columnVisibility,
  onColumnVisibilityChange,
  showFilters,
  onShowFiltersChange,
  showColumnPanel,
  onShowColumnPanelChange,
}: Props) {
  const [viewMode, setViewMode] = useState<ViewMode>('table');

  return (
    <div className="comparison">
      <div className="view-tabs">
        <button
          className={`tab ${viewMode === 'chart' ? 'active' : ''}`}
          onClick={() => setViewMode('chart')}
        >
          Charts
        </button>
        <button
          className={`tab ${viewMode === 'table' ? 'active' : ''}`}
          onClick={() => setViewMode('table')}
        >
          Table
        </button>
      </div>
      <div className="view-content">
        {viewMode === 'chart' ? (
          <ChartView projects={projects} />
        ) : (
          <TableView
            projects={projects}
            onRemove={onRemove}
            globalFilter={globalFilter}
            onGlobalFilterChange={onGlobalFilterChange}
            columnFilters={columnFilters}
            onColumnFiltersChange={onColumnFiltersChange}
            sorting={sorting}
            onSortingChange={onSortingChange}
            columnVisibility={columnVisibility}
            onColumnVisibilityChange={onColumnVisibilityChange}
            showFilters={showFilters}
            onShowFiltersChange={onShowFiltersChange}
            showColumnPanel={showColumnPanel}
            onShowColumnPanelChange={onShowColumnPanelChange}
          />
        )}
      </div>
      <style>{`
        .comparison { display: flex; flex-direction: column; gap: 1rem; position: relative; }
        .view-tabs { display: flex; gap: 0.5rem; border-bottom: 2px solid #eee; position: relative; z-index: 10; background: white; }
        .tab { padding: 0.75rem 1.5rem; border: none; background: none; cursor: pointer; font-size: 1rem; color: #666; border-bottom: 2px solid transparent; margin-bottom: -2px; }
        .tab:hover { color: #333; }
        .tab.active { color: #2c3e50; border-bottom-color: #2c3e50; font-weight: 600; }
        .view-content { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: auto; max-height: calc(100vh - 250px); }
      `}</style>
    </div>
  );
}