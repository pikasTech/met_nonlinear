import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Project, LinearityByFrequency, ProjectMetricsSummary } from '../types';

interface ProjectData {
  name: string;
  project: Project;
  data: {
    linearity?: LinearityByFrequency;
    summary?: ProjectMetricsSummary;
  };
}

interface Props {
  projects: ProjectData[];
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00C49F', '#FFBB28', '#FF6F61', '#6B8E23'];

export default function ChartView({ projects }: Props) {
  const linearityData = projects
    .filter((p) => p.data.linearity?.linearity_by_frequency)
    .map((p) => ({
      name: p.name,
      data: p.data.linearity!.linearity_by_frequency.map((lf: { frequency_hz: number; r_squared_origin: number; r_squared_comped: number; improvement: number }) => ({
        freq: lf.frequency_hz,
        r2_origin: lf.r_squared_origin,
        r2_comped: lf.r_squared_comped,
        improvement: lf.improvement,
      })),
    }));

  const improvementData = projects
    .filter((p) => p.data.linearity?.linearity_by_frequency)
    .map((p) => ({
      name: p.name,
      improvement: p.data.linearity!.linearity_by_frequency.reduce((sum, lf) => sum + lf.improvement, 0) / p.data.linearity!.linearity_by_frequency.length,
    }));

  const computeData = projects
    .filter((p) => p.data.summary?.compute_cost != null)
    .map((p) => ({
      name: p.name,
      total: p.data.summary!.compute_cost ?? 0,
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
      {linearityData.length > 0 && (
        <div className="chart-section">
          <h3>R² by Frequency (Origin vs Compensated)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="freq" />
              <YAxis domain={[0.9, 1]} />
              <Tooltip />
              <Legend />
              {linearityData.map((series, i) => (
                <Line key={series.name} type="monotone" data={series.data} dataKey="r2_origin" name={`${series.name} Origin`} stroke={COLORS[i % COLORS.length]} isAnimationActive={false} />
              ))}
              {linearityData.map((series, i) => (
                <Line key={`${series.name}-comp`} type="monotone" data={series.data} dataKey="r2_comped" name={`${series.name} Comped`} stroke={COLORS[i % COLORS.length]} strokeDasharray="5 5" isAnimationActive={false} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {improvementData.length > 0 && (
        <div className="chart-section">
          <h3>R² Improvement</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              {improvementData.map((item, i) => (
                <Bar key={item.name} data={[item]} dataKey="improvement" name={item.name} fill={COLORS[i % COLORS.length]} isAnimationActive={false} />
              ))}
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
              <Bar dataKey="total" name="Weighted Units" fill="#8884d8" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
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
        .no-data { text-align: center; color: #999; padding: 3rem; }
      `}</style>
    </div>
  );
}