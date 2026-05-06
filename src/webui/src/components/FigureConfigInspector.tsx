import { Fragment, useState, useRef, useCallback, useEffect, type ReactNode } from 'react';
import { PaperFigureConfigEntry } from '../clientApi';

export type PathToken = string | number;

const META_KEYS = new Set(['kind', 'title', 'description', 'output_name', 'renderable', 'subfigures', 'parent_montages']);
const LEGEND_LOC_OPTIONS = [
  'best',
  'upper right',
  'upper left',
  'lower left',
  'lower right',
  'right',
  'center left',
  'center right',
  'lower center',
  'upper center',
  'center',
];
const PANEL_ALIGN_X_OPTIONS = ['left', 'center', 'right'];
const PANEL_ALIGN_Y_OPTIONS = ['top', 'center', 'bottom'];
const FIT_MODE_OPTIONS = ['width', 'height', 'both'];
const LAYOUT_OPTIONS = ['horizontal', 'vertical', 'matrix', 'h', 'v', 'row', 'column'];
const LABEL_POSITION_OPTIONS = [
  'top-left',
  'top-right',
  'top-center',
  'bottom-left',
  'bottom-right',
  'bottom-center',
  'outside-top-left',
  'outside-top-right',
  'outside-top-center',
];
const MARGIN_KEYS = ['margin_left', 'margin_right', 'margin_top', 'margin_bottom'] as const;
type MarginKey = typeof MARGIN_KEYS[number];
const TRIM_BORDER_KEYS = ['trim_border_left', 'trim_border_right', 'trim_border_top', 'trim_border_bottom'] as const;
type TrimBorderKey = typeof TRIM_BORDER_KEYS[number];
const LEGEND_STRUCTURAL_KEYS = new Set([
  'legend_loc',
  'legend_bbox_to_anchor',
  'legend_ncol',
  'legend_frameon',
]);

type ChangeHandler = (path: PathToken[], value: unknown) => void;

function humanizeKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function isNumericArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'number');
}

function isObjectArray(value: unknown): value is Array<Record<string, unknown>> {
  return Array.isArray(value) && value.every((item) => isPlainObject(item));
}

const FIGSIZE_LABELS = ['Width', 'Height'];

function hasFlatLegend(record: Record<string, unknown>): boolean {
  return Object.keys(record).some((key) => LEGEND_STRUCTURAL_KEYS.has(key));
}

function getFlatLegendKeys(record: Record<string, unknown>): string[] {
  return Object.keys(record).filter((key) => key.startsWith('legend_'));
}

function isLegendConfigKey(key: string): boolean {
  return key === 'legend' || key.startsWith('legend_');
}

function isLegendLocField(key: string): boolean {
  const normalized = key.toLowerCase();
  return normalized === 'loc' || normalized === 'legend_loc' || normalized.endsWith('_legend_loc');
}

function fieldPath(basePath: PathToken[], key: string): PathToken[] {
  return [...basePath, key];
}

function pathTestId(path: PathToken[]): string {
  const suffix = path.map((token) => String(token)).join('-').replace(/[^a-zA-Z0-9_-]/g, '-');
  return suffix ? `studio-config-${suffix}` : 'studio-config-root';
}

function parseNumberInput(value: string): number | undefined {
  if (value.trim() === '') {
    return undefined;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section className="studio-adjuster-card">
      <div className="studio-adjuster-card__header">
        <strong>{title}</strong>
        {subtitle ? <span>{subtitle}</span> : null}
      </div>
      <div className="studio-adjuster-card__body">{children}</div>
    </section>
  );
}

function NumberField({
  label,
  path,
  value,
  onChange,
  step = 'any',
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  onChange: ChangeHandler;
  step?: string;
}) {
  const [draft, setDraft] = useState(typeof value === 'number' && Number.isFinite(value) ? String(value) : '');
  const committedRef = useRef(typeof value === 'number' && Number.isFinite(value) ? String(value) : '');

  useEffect(() => {
    const propStr = typeof value === 'number' && Number.isFinite(value) ? String(value) : '';
    setDraft(propStr);
    committedRef.current = propStr;
  }, [value]);

  const commit = useCallback((raw: string) => {
    const parsed = parseNumberInput(raw);
    if (parsed !== undefined) {
      onChange(path, parsed);
    }
    setDraft(raw || (typeof value === 'number' && Number.isFinite(value) ? String(value) : ''));
    committedRef.current = raw || (typeof value === 'number' && Number.isFinite(value) ? String(value) : '');
  }, [onChange, path, value]);

  return (
    <label className="studio-adjuster-field">
      <span className="studio-adjuster-field__label">{label}</span>
      <input
        className="studio-adjuster-field__input"
        data-testid={pathTestId(path)}
        type="number"
        step={step}
        value={draft}
        onChange={(event) => {
          setDraft(event.target.value);
          committedRef.current = event.target.value;
        }}
        onBlur={() => commit(committedRef.current)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            commit(event.currentTarget.value);
          }
        }}
      />
    </label>
  );
}

function TextField({
  label,
  path,
  value,
  onChange,
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  onChange: ChangeHandler;
}) {
  return (
    <label className="studio-adjuster-field">
      <span className="studio-adjuster-field__label">{label}</span>
      <input
        className="studio-adjuster-field__input"
        data-testid={pathTestId(path)}
        type="text"
        value={typeof value === 'string' ? value : ''}
        onChange={(event) => onChange(path, event.target.value)}
      />
    </label>
  );
}

function ToggleField({
  label,
  path,
  value,
  onChange,
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  onChange: ChangeHandler;
}) {
  return (
    <label className="studio-adjuster-toggle">
      <span className="studio-adjuster-field__label">{label}</span>
      <input
        className="studio-adjuster-toggle__input"
        data-testid={pathTestId(path)}
        type="checkbox"
        checked={Boolean(value)}
        onChange={(event) => onChange(path, event.target.checked)}
      />
    </label>
  );
}

function SelectField({
  label,
  path,
  value,
  options,
  onChange,
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  options: string[];
  onChange: ChangeHandler;
}) {
  const current = typeof value === 'string' ? value : '';
  const resolvedOptions = current && !options.includes(current) ? [current, ...options] : options;
  return (
    <label className="studio-adjuster-field">
      <span className="studio-adjuster-field__label">{label}</span>
      <select
        className="studio-adjuster-field__input"
        data-testid={pathTestId(path)}
        value={current}
        onChange={(event) => onChange(path, event.target.value)}
      >
        <option value="">Unset</option>
        {resolvedOptions.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberTupleField({
  label,
  path,
  value,
  onChange,
  itemLabels,
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  onChange: ChangeHandler;
  itemLabels: string[];
}) {
  const tuple = Array.isArray(value) ? value : [];
  const [drafts, setDrafts] = useState<string[]>(() =>
    tuple.map((v) => (typeof v === 'number' && Number.isFinite(v) ? String(v) : '')),
  );
  const committedRef = useRef<string[]>(tuple.map((v) => (typeof v === 'number' && Number.isFinite(v) ? String(v) : '')));

  const commit = useCallback(
    (index: number, raw: string) => {
      const next = Array.from({ length: itemLabels.length }, (_, i) => {
        if (i === index) {
          const parsed = parseNumberInput(raw);
          return parsed !== undefined ? parsed : (typeof tuple[i] === 'number' && Number.isFinite(tuple[i]) ? tuple[i] : 0);
        }
        return typeof tuple[i] === 'number' && Number.isFinite(tuple[i]) ? tuple[i] : 0;
      });
      onChange(path, next);
    },
    [itemLabels.length, onChange, path, tuple],
  );

  return (
    <div className="studio-adjuster-field studio-adjuster-field--tuple">
      <span className="studio-adjuster-field__label">{label}</span>
      <div className="studio-adjuster-tuple">
        {itemLabels.map((itemLabel, index) => (
          <label key={`${label}-${itemLabel}-${index}`} className="studio-adjuster-tuple__item">
            <span>{itemLabel}</span>
            <input
              className="studio-adjuster-field__input"
              data-testid={`${pathTestId(path)}-${index}`}
              type="number"
              step="any"
              value={drafts[index] ?? ''}
              onChange={(event) => {
                const nextDrafts = [...drafts];
                nextDrafts[index] = event.target.value;
                setDrafts(nextDrafts);
                committedRef.current = nextDrafts;
              }}
              onBlur={() => commit(index, committedRef.current[index] ?? '')}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  commit(index, event.currentTarget.value);
                }
              }}
            />
          </label>
        ))}
      </div>
    </div>
  );
}

function PaletteAdjuster({
  title,
  value,
  basePath,
  onChange,
}: {
  title: string;
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const entries = Object.entries(value);
  if (entries.length === 0) {
    return null;
  }
  return (
    <SectionCard title={title} subtitle={`${entries.length} color slots`}>
      <div className="studio-adjuster-grid">
        {entries.map(([key, color]) => (
          <Fragment key={`${title}-${key}`}>
            <TextField label={humanizeKey(key)} path={fieldPath(basePath, key)} value={color} onChange={onChange} />
          </Fragment>
        ))}
      </div>
    </SectionCard>
  );
}

function MarginsAdjuster({
  value,
  basePath,
  onChange,
}: {
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const keys = ['left', 'right', 'bottom', 'top'].filter((key) => key in value);
  if (keys.length === 0) {
    return null;
  }
  return (
    <SectionCard title="Margins" subtitle="Common plot window padding">
      <div className="studio-adjuster-grid studio-adjuster-grid--two">
        {keys.map((key) => (
          <NumberField key={key} label={humanizeKey(key)} path={fieldPath(basePath, key)} value={value[key]} onChange={onChange} />
        ))}
      </div>
    </SectionCard>
  );
}

function MarginsPanelAdjuster({
  value,
  basePath,
  onChange,
}: {
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const presentKeys = MARGIN_KEYS.filter((key) => key in value);
  if (presentKeys.length === 0) {
    return null;
  }
  return (
    <SectionCard title="Panel Margins" subtitle="Individual white-edge padding per panel">
      <div className="studio-adjuster-grid studio-adjuster-grid--four">
        {presentKeys.map((key) => {
          const shortLabels: Record<MarginKey, string> = {
            margin_left: 'Left',
            margin_right: 'Right',
            margin_top: 'Top',
            margin_bottom: 'Bottom',
          };
          return (
            <NumberField
              key={key}
              label={shortLabels[key]}
              path={fieldPath(basePath, key)}
              value={value[key]}
              onChange={onChange}
            />
          );
        })}
      </div>
    </SectionCard>
  );
}

function TrimBorderPanelAdjuster({
  value,
  basePath,
  onChange,
}: {
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const presentKeys = TRIM_BORDER_KEYS.filter((key) => key in value);
  if (presentKeys.length === 0) {
    return null;
  }
  return (
    <SectionCard title="Trim Border" subtitle="Per-edge background padding after auto-crop">
      <div className="studio-adjuster-grid studio-adjuster-grid--four">
        {presentKeys.map((key) => {
          const shortLabels: Record<TrimBorderKey, string> = {
            trim_border_left: 'Left',
            trim_border_right: 'Right',
            trim_border_top: 'Top',
            trim_border_bottom: 'Bottom',
          };
          return (
            <NumberField
              key={key}
              label={shortLabels[key]}
              path={fieldPath(basePath, key)}
              value={value[key]}
              onChange={onChange}
            />
          );
        })}
      </div>
    </SectionCard>
  );
}

function LegendAdjuster({
  title,
  basePath,
  value,
  onChange,
  flat,
}: {
  title: string;
  basePath: PathToken[];
  value: Record<string, unknown>;
  onChange: ChangeHandler;
  flat?: boolean;
}) {
  const resolveKey = (key: string) => (flat ? `legend_${key}` : key);
  const legendLoc = value[resolveKey('loc')];
  const legendNcol = value[resolveKey('ncol')];
  const legendFrameon = value[resolveKey('frameon')];
  const legendFontsize = value[resolveKey('fontsize')];
  const legendBbox = value[resolveKey('bbox_to_anchor')];

  return (
    <SectionCard title={title} subtitle="Reusable legend controls">
      <div className="studio-adjuster-grid studio-adjuster-grid--two">
        <SelectField label="Position" path={fieldPath(basePath, resolveKey('loc'))} value={legendLoc} options={LEGEND_LOC_OPTIONS} onChange={onChange} />
        <NumberField label="Columns" path={fieldPath(basePath, resolveKey('ncol'))} value={legendNcol} onChange={onChange} step="1" />
        <NumberField label="Font Size" path={fieldPath(basePath, resolveKey('fontsize'))} value={legendFontsize} onChange={onChange} />
        <ToggleField label="Frame Border" path={fieldPath(basePath, resolveKey('frameon'))} value={legendFrameon} onChange={onChange} />
      </div>
      <NumberTupleField
        label="BBox Anchor"
        path={fieldPath(basePath, resolveKey('bbox_to_anchor'))}
        value={legendBbox}
        onChange={onChange}
        itemLabels={['x', 'y']}
      />
    </SectionCard>
  );
}

function XYPlotAdjuster({
  value,
  basePath,
  onChange,
}: {
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const rangeFields: Array<[string, string]> = [
    ['xlim', 'X Axis Range'],
    ['ylim', 'Y Axis Range'],
    ['left_ylim', 'Left Y Range'],
    ['right_ylim', 'Right Y Range'],
    ['y1_ylim', 'Y1 Axis Range'],
    ['y2_ylim', 'Y2 Axis Range'],
  ];
  const visibleRanges = rangeFields.filter(([key]) => key in value);

  return (
    <SectionCard title="X-Y Plot" subtitle="Reusable axis range and typography controls">
      <div className="studio-adjuster-grid">
        {visibleRanges.map(([key, label]) => (
          <NumberTupleField
            key={key}
            label={label}
            path={fieldPath(basePath, key)}
            value={value[key]}
            onChange={onChange}
            itemLabels={['min', 'max']}
          />
        ))}
      </div>
      <div className="studio-adjuster-grid studio-adjuster-grid--two">
        <NumberField label="Axis Label Font Size" path={fieldPath(basePath, 'label_fontsize')} value={value.label_fontsize} onChange={onChange} />
        <NumberField label="Tick Font Size" path={fieldPath(basePath, 'tick_fontsize')} value={value.tick_fontsize} onChange={onChange} />
        <NumberField label="Label To Axis Distance" path={fieldPath(basePath, 'labelpad')} value={value.labelpad} onChange={onChange} />
        <NumberField label="Tick To Axis Distance" path={fieldPath(basePath, 'tick_pad')} value={value.tick_pad} onChange={onChange} />
      </div>
    </SectionCard>
  );
}

function MontageLayoutAdjuster({
  value,
  basePath,
  onChange,
}: {
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
}) {
  const layoutValue = value.layout;
  const labelPositionValue = value.label_position;
  const paddingValue = value.padding;
  const gutterValue = value.gutter;

  return (
    <SectionCard title="Montage Layout" subtitle="Grid arrangement and spacing">
      <div className="studio-adjuster-grid studio-adjuster-grid--two">
        <SelectField label="Layout" path={fieldPath(basePath, 'layout')} value={layoutValue} options={LAYOUT_OPTIONS} onChange={onChange} />
        <SelectField label="Label Position" path={fieldPath(basePath, 'label_position')} value={labelPositionValue} options={LABEL_POSITION_OPTIONS} onChange={onChange} />
      </div>
      {Array.isArray(paddingValue) && paddingValue.length === 4 && (
        <NumberTupleField
          label="Padding"
          path={fieldPath(basePath, 'padding')}
          value={paddingValue}
          onChange={onChange}
          itemLabels={['Left', 'Top', 'Right', 'Bottom']}
        />
      )}
      {Array.isArray(gutterValue) && gutterValue.length === 2 && (
        <NumberTupleField
          label="Gutter"
          path={fieldPath(basePath, 'gutter')}
          value={gutterValue}
          onChange={onChange}
          itemLabels={['Horizontal', 'Vertical']}
        />
      )}
    </SectionCard>
  );
}

function PrimitiveField({
  label,
  path,
  value,
  onChange,
}: {
  label: string;
  path: PathToken[];
  value: unknown;
  onChange: ChangeHandler;
}) {
  const key = String(path[path.length - 1] ?? '');
  if (isLegendLocField(key)) {
    return <SelectField label={label} path={path} value={value} options={LEGEND_LOC_OPTIONS} onChange={onChange} />;
  }
  if (key === 'align_x') {
    return <SelectField label={label} path={path} value={value} options={PANEL_ALIGN_X_OPTIONS} onChange={onChange} />;
  }
  if (key === 'align_y') {
    return <SelectField label={label} path={path} value={value} options={PANEL_ALIGN_Y_OPTIONS} onChange={onChange} />;
  }
  if (key === 'fit_mode') {
    return <SelectField label={label} path={path} value={value} options={FIT_MODE_OPTIONS} onChange={onChange} />;
  }
  if (key === 'layout') {
    return <SelectField label={label} path={path} value={value} options={LAYOUT_OPTIONS} onChange={onChange} />;
  }
  if (key === 'label_position') {
    return <SelectField label={label} path={path} value={value} options={LABEL_POSITION_OPTIONS} onChange={onChange} />;
  }
  if (typeof value === 'boolean') {
    return <ToggleField label={label} path={path} value={value} onChange={onChange} />;
  }
  if (typeof value === 'number' || typeof value === 'undefined') {
    return <NumberField label={label} path={path} value={value} onChange={onChange} />;
  }
  return <TextField label={label} path={path} value={value} onChange={onChange} />;
}

function PanelsArrayAdjuster({
  title,
  value,
  basePath,
  onChange,
  suppressLegend,
}: {
  title: string;
  value: Array<Record<string, unknown>>;
  basePath: PathToken[];
  onChange: ChangeHandler;
  suppressLegend?: boolean;
}) {
  return (
    <SectionCard title={title} subtitle={`${value.length} reusable panel overrides`}>
      <div className="studio-adjuster-stack">
        {value.map((item, index) => {
          const entries = Object.entries(item).filter(([key]) => !(suppressLegend && isLegendConfigKey(key)));
          const hasMargins = MARGIN_KEYS.some((k) => k in item);
          const marginEntry = hasMargins ? MARGIN_KEYS.filter((k) => k in item).reduce((acc, k) => ({ ...acc, [k]: item[k] }), {} as Record<string, unknown>) : null;
          const hasTrimBorders = TRIM_BORDER_KEYS.some((k) => k in item);
          const trimBorderEntry = hasTrimBorders ? TRIM_BORDER_KEYS.filter((k) => k in item).reduce((acc, k) => ({ ...acc, [k]: item[k] }), {} as Record<string, unknown>) : null;

          return (
            <section key={`${title}-${index}`} className="studio-adjuster-subcard">
              <div className="studio-adjuster-subcard__title">Panel {index + 1}</div>
              {marginEntry && (
                <MarginsPanelAdjuster
                  value={marginEntry}
                  basePath={[...basePath, index]}
                  onChange={onChange}
                />
              )}
              {trimBorderEntry && (
                <TrimBorderPanelAdjuster
                  value={trimBorderEntry}
                  basePath={[...basePath, index]}
                  onChange={onChange}
                />
              )}
              {entries.filter(([key]) => !MARGIN_KEYS.includes(key as MarginKey) && !TRIM_BORDER_KEYS.includes(key as TrimBorderKey)).length > 0 ? (
                <div className="studio-adjuster-grid studio-adjuster-grid--two">
                  {entries
                    .filter(([key]) => !MARGIN_KEYS.includes(key as MarginKey) && !TRIM_BORDER_KEYS.includes(key as TrimBorderKey))
                    .map(([key, childValue]) => {
                      if (isNumericArray(childValue)) {
                        return (
                          <NumberTupleField
                            key={`${index}-${key}`}
                            label={humanizeKey(key)}
                            path={[...basePath, index, key]}
                            value={childValue}
                            onChange={onChange}
                            itemLabels={childValue.map((_, childIndex) => String(childIndex + 1))}
                          />
                        );
                      }
                      return (
                        <PrimitiveField
                          key={`${index}-${key}`}
                          label={humanizeKey(key)}
                          path={[...basePath, index, key]}
                          value={childValue}
                          onChange={onChange}
                        />
                      );
                    })}
                </div>
              ) : (
                <div className="studio-adjuster-subcard__empty">No overrides in this slot.</div>
              )}
            </section>
          );
        })}
      </div>
    </SectionCard>
  );
}

function ObjectAdjuster({
  title,
  value,
  basePath,
  onChange,
  suppressLegend,
}: {
  title: string;
  value: Record<string, unknown>;
  basePath: PathToken[];
  onChange: ChangeHandler;
  suppressLegend?: boolean;
}) {
  const consumed = new Set<string>();
  const blocks: ReactNode[] = [];

  if (suppressLegend) {
    for (const key of Object.keys(value)) {
      if (isLegendConfigKey(key)) {
        consumed.add(key);
      }
    }
  }

  if (!suppressLegend && isPlainObject(value.legend)) {
    consumed.add('legend');
    blocks.push(
      <LegendAdjuster
        key={`${title}-legend`}
        title="Legend"
        basePath={fieldPath(basePath, 'legend')}
        value={value.legend as Record<string, unknown>}
        onChange={onChange}
      />,
    );
  } else if (!suppressLegend && hasFlatLegend(value)) {
    for (const key of getFlatLegendKeys(value)) {
      consumed.add(key);
    }
    blocks.push(
      <LegendAdjuster
        key={`${title}-legend-flat`}
        title="Legend"
        basePath={basePath}
        value={value}
        onChange={onChange}
        flat
      />,
    );
  }

  if (isPlainObject(value.palette)) {
    consumed.add('palette');
    blocks.push(
      <PaletteAdjuster
        key={`${title}-palette`}
        title="Palette"
        value={value.palette as Record<string, unknown>}
        basePath={fieldPath(basePath, 'palette')}
        onChange={onChange}
      />,
    );
  }

  if (isPlainObject(value.xy_plot)) {
    consumed.add('xy_plot');
    blocks.push(
      <XYPlotAdjuster
        key={`${title}-xy-plot`}
        value={value.xy_plot as Record<string, unknown>}
        basePath={fieldPath(basePath, 'xy_plot')}
        onChange={onChange}
      />,
    );
  }

  if (isPlainObject(value.margins)) {
    consumed.add('margins');
    blocks.push(
      <MarginsAdjuster
        key={`${title}-margins`}
        value={value.margins as Record<string, unknown>}
        basePath={fieldPath(basePath, 'margins')}
        onChange={onChange}
      />,
    );
  }

  if (suppressLegend && (value.layout || value.label_position || value.padding || value.gutter)) {
    consumed.add('layout');
    consumed.add('label_position');
    consumed.add('padding');
    consumed.add('gutter');
    blocks.push(
      <MontageLayoutAdjuster
        key={`${title}-montage-layout`}
        value={value}
        basePath={basePath}
        onChange={onChange}
      />,
    );
  }

  const tupleEntries = Object.entries(value).filter(([key, childValue]) => !consumed.has(key) && isNumericArray(childValue));
  const figsizeEntry = tupleEntries.find(([key]) => key === 'figsize');
  const genericTupleEntries = tupleEntries.filter(([key]) => key !== 'figsize');
  const primitiveEntries = Object.entries(value).filter(
    ([key, childValue]) =>
      !consumed.has(key) &&
      (typeof childValue === 'number' || typeof childValue === 'string' || typeof childValue === 'boolean' || typeof childValue === 'undefined'),
  );
  const objectEntries = Object.entries(value).filter(([key, childValue]) => !consumed.has(key) && isPlainObject(childValue));
  const objectArrayEntries = Object.entries(value).filter(([key, childValue]) => !consumed.has(key) && isObjectArray(childValue));

  if (primitiveEntries.length > 0 || genericTupleEntries.length > 0 || figsizeEntry) {
    blocks.push(
      <SectionCard key={`${title}-common`} title={title} subtitle="Reusable scalar and tuple adjusters">
        <div className="studio-adjuster-grid studio-adjuster-grid--two">
          {primitiveEntries.map(([key, childValue]) => (
            <PrimitiveField key={`${title}-${key}`} label={humanizeKey(key)} path={fieldPath(basePath, key)} value={childValue} onChange={onChange} />
          ))}
          {figsizeEntry && (
            <NumberTupleField
              key={`${title}-figsize`}
              label="Figure Size"
              path={fieldPath(basePath, figsizeEntry[0])}
              value={figsizeEntry[1]}
              onChange={onChange}
              itemLabels={FIGSIZE_LABELS}
            />
          )}
          {genericTupleEntries.map(([key, childValue]) => (
            <NumberTupleField
              key={`${title}-${key}`}
              label={humanizeKey(key)}
              path={fieldPath(basePath, key)}
              value={childValue}
              onChange={onChange}
              itemLabels={(childValue as number[]).map((_, index) => String(index + 1))}
            />
          ))}
        </div>
      </SectionCard>,
    );
  }

  for (const [key, childValue] of objectEntries) {
    blocks.push(
      <ObjectAdjuster
        key={`${title}-${key}`}
        title={humanizeKey(key)}
        value={childValue as Record<string, unknown>}
        basePath={fieldPath(basePath, key)}
        onChange={onChange}
        suppressLegend={suppressLegend}
      />,
    );
  }

  for (const [key, childValue] of objectArrayEntries) {
    blocks.push(
      <PanelsArrayAdjuster
        key={`${title}-${key}`}
        title={humanizeKey(key)}
        value={childValue as Array<Record<string, unknown>>}
        basePath={fieldPath(basePath, key)}
        onChange={onChange}
        suppressLegend={suppressLegend}
      />,
    );
  }

  return <>{blocks}</>;
}

export default function FigureConfigInspector({
  config,
  onChange,
}: {
  config: PaperFigureConfigEntry;
  onChange: ChangeHandler;
}) {
  const suppressLegend = config.kind === 'montage';
  const entries = Object.entries(config).filter(([key]) => !META_KEYS.has(key) && !(suppressLegend && isLegendConfigKey(key)));
  const rootRecord: Record<string, unknown> = {};
  const nestedBlocks: Array<[string, Record<string, unknown> | Array<Record<string, unknown>>]> = [];

  for (const [key, value] of entries) {
    if (isPlainObject(value) || isObjectArray(value)) {
      nestedBlocks.push([key, value as Record<string, unknown> | Array<Record<string, unknown>>]);
    } else {
      rootRecord[key] = value;
    }
  }

  return (
    <div className="studio-adjuster-stack">
      {Object.keys(rootRecord).length > 0 ? (
        <ObjectAdjuster title="General" value={rootRecord} basePath={[]} onChange={onChange} suppressLegend={suppressLegend} />
      ) : null}
      {nestedBlocks.map(([key, value]) =>
        isPlainObject(value) ? (
          <ObjectAdjuster key={key} title={humanizeKey(key)} value={value} basePath={[key]} onChange={onChange} suppressLegend={suppressLegend} />
        ) : (
          <PanelsArrayAdjuster key={key} title={humanizeKey(key)} value={value} basePath={[key]} onChange={onChange} suppressLegend={suppressLegend} />
        ),
      )}
    </div>
  );
}
