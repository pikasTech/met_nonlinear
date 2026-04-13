import { useState, useMemo } from 'react';
import { Project, ProjectMetricsSummary } from '../types';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';

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
  // External state props for preset support
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: (filters: ColumnFiltersState) => void;
  globalFilter?: string;
  onGlobalFilterChange?: (filter: string) => void;
  columnVisibility?: Record<string, boolean>;
  onColumnVisibilityChange?: (visibility: Record<string, boolean>) => void;
  showFilters?: boolean;
  onShowFiltersChange?: (show: boolean) => void;
  showColumnPanel?: boolean;
  onShowColumnPanelChange?: (show: boolean) => void;
}

type RowData = {
  path: string;
  name: string;
  model: string;
  lossFunction: string | null;
  epochs: number | null;
  minValLoss: number | null;
  minLoss: number | null;
  trainMAE: number | null;
  trainAFMAE: number | null;
  valMAE: number | null;
  valAFMAE: number | null;
  totalParams: number | null;
  computeCost: number | null;
  computeHasUnsupportedLayers: boolean;
  computeUnsupportedLayerCount: number;
  computeCostWarning: string | null;
  freqDrift: number | null;
  sensDrift: number | null;
  linearity: number | null;
  lr: number | null;
  useCosineAnnealing: boolean | null;
};

function formatCell(val: number | null): string {
  if (val === null || val === undefined) return '(no data)';
  return val.toLocaleString();
}

function formatLoss(val: number | null): string {
  if (val === null || val === undefined) return '(no data)';
  return val.toFixed(6);
}

function formatPercent(val: number | null): string {
  if (val === null || val === undefined) return '(no data)';
  return val.toFixed(2) + '%';
}

function formatHz(val: number | null): string {
  if (val === null || val === undefined) return '(no data)';
  return val.toFixed(2) + ' Hz';
}

// Custom filter function for numeric columns - parses input as number (supports '1000' not just '1,000')
function numberFilter(row: any, columnId: string, filterValue: any) {
  if (filterValue === '' || filterValue === undefined || filterValue === null) return true;
  const cellValue = row.getValue(columnId);
  if (cellValue === null || cellValue === undefined) return false;
  const filterNum = parseFloat(String(filterValue).replace(/,/g, ''));
  if (isNaN(filterNum)) return true;
  return cellValue === filterNum;
}

const columnHelper = createColumnHelper<RowData>();

export default function TableView({
  projects,
  onRemove,
  sorting: externalSorting,
  onSortingChange: externalOnSortingChange,
  columnFilters: externalColumnFilters,
  onColumnFiltersChange: externalOnColumnFiltersChange,
  globalFilter: externalGlobalFilter,
  onGlobalFilterChange: externalOnGlobalFilterChange,
  columnVisibility: externalColumnVisibility,
  onColumnVisibilityChange: externalOnColumnVisibilityChange,
  showFilters: externalShowFilters,
  onShowFiltersChange: externalOnShowFiltersChange,
  showColumnPanel: externalShowColumnPanel,
  onShowColumnPanelChange: externalOnShowColumnPanelChange,
}: Props) {
  // Internal state with external override capability
  const [internalSorting, setInternalSorting] = useState<SortingState>([]);
  const [internalColumnFilters, setInternalColumnFilters] = useState<ColumnFiltersState>([]);
  const [internalGlobalFilter, setInternalGlobalFilter] = useState('');
  const [internalColumnVisibility, setInternalColumnVisibility] = useState<Record<string, boolean>>({});
  const [internalShowColumnPanel, setInternalShowColumnPanel] = useState(false);
  const [internalShowFilters, setInternalShowFilters] = useState(false);

  // Use external state if provided, otherwise use internal
  const sorting = externalSorting ?? internalSorting;
  // Wrap external setters to handle TanStack Table's Updater pattern
  const setSorting = externalOnSortingChange
    ? (updaterOrValue: any) => {
        const value = typeof updaterOrValue === 'function' ? updaterOrValue(externalSorting) : updaterOrValue;
        externalOnSortingChange(value);
      }
    : setInternalSorting;
  const columnFilters = externalColumnFilters ?? internalColumnFilters;
  const setColumnFilters = externalOnColumnFiltersChange
    ? (updaterOrValue: any) => {
        const value = typeof updaterOrValue === 'function' ? updaterOrValue(externalColumnFilters) : updaterOrValue;
        externalOnColumnFiltersChange(value);
      }
    : setInternalColumnFilters;
  const globalFilter = externalGlobalFilter ?? internalGlobalFilter;
  const setGlobalFilter = externalOnGlobalFilterChange ?? setInternalGlobalFilter;
  const columnVisibility = externalColumnVisibility ?? internalColumnVisibility;
  const setColumnVisibility = externalOnColumnVisibilityChange
    ? (updaterOrValue: any) => {
        const value = typeof updaterOrValue === 'function' ? updaterOrValue(externalColumnVisibility) : updaterOrValue;
        externalOnColumnVisibilityChange(value);
      }
    : setInternalColumnVisibility;
  const showColumnPanel = externalShowColumnPanel ?? internalShowColumnPanel;
  const setShowColumnPanel = externalOnShowColumnPanelChange ?? setInternalShowColumnPanel;
  const showFilters = externalShowFilters ?? internalShowFilters;
  const setShowFilters = externalOnShowFiltersChange ?? setInternalShowFilters;

  const rowData: RowData[] = useMemo(() => {
    return projects.map((p) => ({
      path: p.project.path,
      name: p.name,
      model: p.project.config.use_model || 'unknown',
      lossFunction: p.data.summary?.loss_function ?? null,
      epochs: p.data.summary?.epochs ?? null,
      minValLoss: p.data.summary?.min_val_loss ?? null,
      minLoss: p.data.summary?.min_loss ?? null,
      trainMAE: p.data.summary?.train_mae ?? null,
      trainAFMAE: p.data.summary?.train_afmae ?? null,
      valMAE: p.data.summary?.val_mae ?? null,
      valAFMAE: p.data.summary?.val_afmae ?? null,
      totalParams: p.data.summary?.total_params ?? null,
      computeCost: p.data.summary?.compute_cost ?? null,
      computeHasUnsupportedLayers: p.data.summary?.compute_has_unsupported_layers ?? false,
      computeUnsupportedLayerCount: p.data.summary?.compute_unsupported_layer_count ?? 0,
      computeCostWarning: p.data.summary?.compute_cost_warning ?? null,
      freqDrift: p.data.summary?.freq_drift_hz ?? null,
      sensDrift: p.data.summary?.sens_drift_percent ?? null,
      linearity: p.data.summary?.linearity_percent ?? null,
      lr: p.data.summary?.lr ?? null,
      useCosineAnnealing: p.data.summary?.use_cosine_annealing ?? null,
    }));
  }, [projects]);

  const columns = useMemo(() => [
    columnHelper.accessor('name', {
      header: 'Project',
      cell: (info) => <span style={{ fontWeight: 500 }}>{info.getValue()}</span>,
    }),
    columnHelper.accessor('model', {
      header: 'Model',
      cell: (info) => <span style={{ color: '#666' }}>{info.getValue()}</span>,
    }),
    columnHelper.accessor('lossFunction', {
      header: 'Loss Function',
      cell: (info) => info.getValue() ?? '(no data)',
    }),
    columnHelper.accessor('epochs', {
      header: 'Epochs',
      cell: (info) => formatCell(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('minLoss', {
      header: 'Min Loss',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('minValLoss', {
      header: 'Min Val Loss',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('trainMAE', {
      header: 'Train MAE',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('trainAFMAE', {
      header: 'Train AFMAE',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('valMAE', {
      header: 'Val MAE',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('valAFMAE', {
      header: 'Val AFMAE',
      cell: (info) => formatLoss(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('totalParams', {
      header: 'Total Params',
      cell: (info) => formatCell(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('computeCost', {
      header: 'Compute Cost',
      cell: (info) => {
        const value = info.getValue();
        const row = info.row.original;
        if (value === null || value === undefined) {
          return '(no data)';
        }

        const warningSuffix = row.computeHasUnsupportedLayers
          ? ` (${row.computeUnsupportedLayerCount} unsupported)`
          : '';

        return (
          <span
            title={row.computeCostWarning ?? undefined}
            style={row.computeHasUnsupportedLayers ? { color: '#c62828', fontWeight: 700 } : undefined}
          >
            {formatCell(value)}
            {warningSuffix}
          </span>
        );
      },
      filterFn: numberFilter,
    }),
    columnHelper.accessor('freqDrift', {
      header: 'Freq Drift (Hz)',
      cell: (info) => formatHz(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('sensDrift', {
      header: 'Sens Drift (%)',
      cell: (info) => formatPercent(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('linearity', {
      header: 'Linearity (%)',
      cell: (info) => formatPercent(info.getValue()),
      filterFn: numberFilter,
    }),
    columnHelper.accessor('lr', {
      header: 'LR',
      cell: (info) => {
        const val = info.getValue();
        if (val === null || val === undefined) return '(no data)';
        return val.toExponential(2);
      },
      filterFn: numberFilter,
    }),
    columnHelper.accessor('useCosineAnnealing', {
      header: 'Cosine',
      cell: (info) => {
        const val = info.getValue();
        if (val === null || val === undefined) return '(no data)';
        return val ? 'Yes' : 'No';
      },
      filterFn: numberFilter,
    }),
    columnHelper.display({
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <button
          className="btn-remove"
          onClick={() => onRemove?.(row.original.path)}
          title="Deselect"
        >
          ×
        </button>
      ),
    }),
  ], []);

  const table = useReactTable({
    data: rowData,
    columns,
    state: { sorting, columnFilters, globalFilter, columnVisibility },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  if (projects.length === 0) {
    return <div className="no-data">No project data available</div>;
  }

  return (
    <div className="table-view">
      <div className="table-controls">
        <input
          type="text"
          placeholder="Search all columns..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="search-input"
        />
        <div className="filter-info">
          {table.getFilteredRowModel().rows.length} of {rowData.length} rows
        </div>
        <button
          className={`column-toggle-btn ${showFilters ? 'active' : ''}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>
        <button
          className={`column-toggle-btn ${showColumnPanel ? 'active' : ''}`}
          onClick={() => setShowColumnPanel(!showColumnPanel)}
        >
          {showColumnPanel ? 'Hide Columns' : 'Show Columns'}
        </button>
      </div>
      {showColumnPanel && (
        <div className="column-panel">
          <div className="column-panel-header">Toggle Columns</div>
          <div className="column-list">
            {table.getAllLeafColumns().filter(col => col.id !== 'name' && col.id !== 'actions').map((column) => (
              <label key={column.id} className="column-item">
                <input
                  type="checkbox"
                  checked={column.getIsVisible()}
                  onChange={column.getToggleVisibilityHandler()}
                />
                <span>{column.columnDef.header as string}</span>
              </label>
            ))}
          </div>
        </div>
      )}
      <div className="table-container">
        <table className="data-table">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    style={{ cursor: header.column.getCanSort() ? 'pointer' : 'default' }}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getIsSorted() && (
                      <span className="sort-indicator">
                        {header.column.getIsSorted() === 'asc' ? ' ↑' : ' ↓'}
                      </span>
                    )}
                  </th>
                ))}
              </tr>
            ))}
            {showFilters && (
              <tr className="filter-row">
                {table.getHeaderGroups()[0].headers.map((header) => {
                  const canFilter = header.id !== 'actions';
                  return (
                    <th key={header.id}>
                      {canFilter ? (
                        <input
                          type="text"
                          placeholder={`Filter ${header.column.columnDef.header as string}...`}
                          value={(header.column.getFilterValue() as string) ?? ''}
                          onChange={(e) => header.column.setFilterValue(e.target.value)}
                          className="filter-input"
                        />
                      ) : null}
                    </th>
                  );
                })}
              </tr>
            )}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <style>{`
        .table-view { display: flex; flex-direction: column; gap: 1rem; }
        .table-controls { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
        .search-input { flex: 1; padding: 0.5rem 1rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; }
        .filter-info { color: #666; font-size: 0.9rem; white-space: nowrap; }
        .column-toggle-btn { padding: 0.5rem 1rem; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
        .column-toggle-btn:hover { background: #f5f5f5; }
        .column-toggle-btn.active { background: #2c3e50; color: white; border-color: #2c3e50; }
        .column-panel { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .column-panel-header { font-weight: 600; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee; }
        .column-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .column-item { display: flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.6rem; background: #f8f8f8; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
        .column-item:hover { background: #eee; }
        .column-item input[type="checkbox"] { cursor: pointer; }
        .table-container { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        .data-table th { background: #f8f8f8; padding: 0.75rem; text-align: left; font-weight: 600; border-bottom: 2px solid #ddd; white-space: nowrap; position: sticky; top: 0; }
        .filter-row th { background: #f0f0f0; padding: 0.5rem; }
        .filter-input { width: 100%; padding: 0.35rem; border: 1px solid #ddd; border-radius: 3px; font-size: 0.8rem; box-sizing: border-box; }
        .data-table td { padding: 0.75rem; border-bottom: 1px solid #eee; }
        .data-table tr:hover td { background: #f8f8f8; }
        .sort-indicator { color: #2c3e50; margin-left: 0.25rem; }
        .no-data { text-align: center; color: #999; padding: 3rem; }
        .btn-remove { width: 22px; height: 22px; padding: 0; font-size: 14px; line-height: 1; border: none; background: #ff4444; color: white; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .btn-remove:hover { background: #cc0000; }
      `}</style>
    </div>
  );
}
