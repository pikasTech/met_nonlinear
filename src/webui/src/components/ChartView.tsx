import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Project, ProjectMetricsSummary } from '../types';

interface ProjectData {
  name: string;
  project: Project;
  data: {
    summary?: ProjectMetricsSummary;
  };
}

interface Props {
  projects: ProjectData[];
}

export default function ChartView({ projects }: Props) {
  const driftData = projects
    .filter((p) => p.data.summary)
    .map((p) => ({
      name: p.name,
      freq_drift_hz: p.data.summary!.freq_drift_hz ?? 0,
      sens_drift_percent: p.data.summary!.sens_drift_percent ?? 0,
      linearity_percent: p.data.summary!.linearity_percent ?? 0,
    }));

  const computeData = projects
    .filter((p) => p.data.summary?.compute_cost != null)
    .map((p) => ({
      name: p.name,
      total: p.data.summary!.compute_cost ?? 0,
      hasUnsupported: p.data.summary!.compute_has_unsupported_layers ?? false,
      warning: p.data.summary!.compute_cost_warning ?? null,
    }));

  const metricsData = projects
    .filter((p) => p.data.summary)
    .map((p) => ({
      name: p.name,
      val_mae: p.data.summary!.val_mae ?? 0,
      val_afmae: p.data.summary!.val_afmae ?? 0,
      val_loss: p.data.summary!.val_loss ?? 0,
    }));

  if (projects.length === 0) {
    return <div className="no-data">No project data available</div>;
  }

  return (
    <div className="chart-view">
      {driftData.length > 0 && (
        <div className="chart-section">
          <h3>Unified Drift Metrics</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={driftData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="freq_drift_hz" name="Freq Drift (Hz)" fill="#8884d8" isAnimationActive={false} />
              <Bar dataKey="sens_drift_percent" name="Sens Drift (%)" fill="#82ca9d" isAnimationActive={false} />
              <Bar dataKey="linearity_percent" name="Linearity (%)" fill="#ffc658" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {computeData.length > 0 && (
        <div className="chart-section">
          <h3>Compute Cost (Weighted Units)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total" name="Weighted Units" isAnimationActive={false}>
                {computeData.map((entry, index) => (
                  <Cell
                    key={`${entry.name}-${index}`}
                    fill={entry.hasUnsupported ? '#c62828' : '#8884d8'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {computeData.some((entry) => entry.hasUnsupported) && (
            <div className="chart-warning">
              Red bars indicate projects whose compute cost may be underestimated because unsupported layers remain in compute analysis.
            </div>
          )}
        </div>
      )}

      {metricsData.length > 0 && (
        <div className="chart-section">
          <h3>Evaluation Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="val_mae" name="Val MAE" fill="#8884d8" isAnimationActive={false} />
              <Bar dataKey="val_afmae" name="Val AFMAE" fill="#82ca9d" isAnimationActive={false} />
              <Bar dataKey="val_loss" name="Val Loss" fill="#ffc658" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <style>{`
        .chart-view { display: flex; flex-direction: column; gap: 2rem; }
        .chart-section { }
        .chart-section h3 { margin-bottom: 1rem; color: #2c3e50; font-size: 1.1rem; }
        .chart-warning { margin-top: 0.75rem; color: #c62828; font-size: 0.9rem; }
        .no-data { text-align: center; color: #999; padding: 3rem; }
      `}</style>
    </div>
  );
}