interface HomePageProps {
  onNavigate: (path: string) => void;
}

export default function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="home-page">
      <div className="home-page__glow home-page__glow--left" />
      <div className="home-page__glow home-page__glow--right" />
      <section className="home-hero">
        <p className="home-hero__eyebrow">MET Nonlinear / Paper Workshop</p>
        <h1 className="home-hero__title">Choose the room you want to work in.</h1>
        <p className="home-hero__body">
          One space stays focused on project-level comparison. The new studio is tuned for paper figures, config-driven redraws
          and previewing the exact bitmap that `main.tex` consumes.
        </p>
      </section>

      <section className="home-grid">
        <article className="home-card home-card--visualizer">
          <div className="home-card__badge">Existing</div>
          <h2 className="home-card__title">Project Visualizer</h2>
          <p className="home-card__copy">
            Browse `projects/`, compare metrics, inspect loss curves and reuse presets from the existing workflow.
          </p>
          <ul className="home-card__list">
            <li>Recursive project tree</li>
            <li>Loss Curves + Table views</li>
            <li>Preset persistence</li>
          </ul>
          <button className="home-card__cta" data-testid="open-project-visualizer" onClick={() => onNavigate('/projects')}>
            Open visualizer
          </button>
        </article>

        <article className="home-card home-card--editor">
          <div className="home-card__badge">New</div>
          <h2 className="home-card__title">Paper Editor</h2>
          <p className="home-card__copy">
            Edit docs/paper/latex/main.tex in source mode, keep the preview synchronized, inspect macros and profile the
            live pipeline with a built-in performance panel.
          </p>
          <ul className="home-card__list">
            <li>Split source / preview workspace</li>
            <li>Math, macro and imported tex preview</li>
            <li>Outline navigator + runtime telemetry</li>
          </ul>
          <button className="home-card__cta home-card__cta--editor" data-testid="open-paper-editor" onClick={() => onNavigate('/paper-editor')}>
            Open paper editor
          </button>
        </article>

        <article className="home-card home-card--studio">
          <div className="home-card__badge">New</div>
          <h2 className="home-card__title">Figure Studio</h2>
          <p className="home-card__copy">
            Edit `docs/paper/config.json`, preview the real generated figure, and trigger single-figure redraws from one panel.
          </p>
          <ul className="home-card__list">
            <li>Single / montage figure library</li>
            <li>Auto or manual redraw</li>
            <li>Live config-backed bitmap preview</li>
          </ul>
          <button
            className="home-card__cta home-card__cta--studio"
            data-testid="open-figure-studio"
            onClick={() => onNavigate('/paper-figures')}
          >
            Open figure studio
          </button>
        </article>
      </section>
    </div>
  );
}
