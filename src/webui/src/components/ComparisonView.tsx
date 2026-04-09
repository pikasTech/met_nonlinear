import { useState } from 'react';
import { Project, ProjectMetricsSummary } from '../types';
import ChartView from './ChartView';
import TableView from './TableView';

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
}

type ViewMode = 'chart' | 'table';

export default function ComparisonView({ projects, onRemove }: Props) {
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
          <TableView projects={projects} onRemove={onRemove} />
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
