import { Icons } from '../helpers.jsx'

export default function HomePage({ user, openAuth, t }) {
  return (
    <>
      <section className="landing-hero">
        <div className="landing-hero-glow" />
        <div className="wrap" style={{ position: 'relative', zIndex: 1 }}>
          <div className="landing-pill">{t('heroTagline')}</div>
          <h1 className="landing-h1">
            {t('heroTitle1')}<br />
            <span className="gradient-text">{t('heroTitle2')}</span>
          </h1>
          <p className="landing-sub">
            {t('heroSub1')}<em style={{ color: 'var(--vocal)', fontStyle: 'normal', fontWeight: 700 }}>{t('vocals')}</em>{t('heroSub2')}<em style={{ color: 'var(--instrumental)', fontStyle: 'normal', fontWeight: 700 }}>{t('background')}</em>{t('heroSub3')}
            <br />{t('heroSub4')}
          </p>
          <div className="landing-cta">
            {!user ? (
              <>
                <button className="btn btn-lg" onClick={() => openAuth(true)}>{t('startFree')}</button>
                <button className="btn secondary btn-lg" onClick={() => openAuth(false)}>{t('haveAccount')}</button>
              </>
            ) : (
              <a href="#/upload" className="btn btn-lg">{t('uploadSong')}</a>
            )}
          </div>
          <p className="landing-note">{t('heroNote')}</p>
        </div>
      </section>

      <section className="landing-section">
        <div className="wrap">
          <h2 className="landing-section-title">{t('howTitle')}</h2>
          <p className="landing-section-sub">{t('howSub')}</p>
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-num">01</div>
              <div className="step-icon">{Icons.upload}</div>
              <h3>{t('step1')}</h3>
              <p>{t('step1d')}</p>
            </div>
            <div className="step-card">
              <div className="step-num">02</div>
              <div className="step-icon">{Icons.headphones}</div>
              <h3>{t('step2')}</h3>
              <p>{t('step2d')}</p>
            </div>
            <div className="step-card">
              <div className="step-num">03</div>
              <div className="step-icon">{Icons.download}</div>
              <h3>{t('step3')}</h3>
              <p>{t('step3d')}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="wrap">
          <h2 className="landing-section-title">{t('whyTitle')}</h2>
          <p className="landing-section-sub">{t('whySub')}</p>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon" style={{ color: 'var(--vocal)' }}>{Icons.music}</div>
              <h3>{t('feat1')}</h3>
              <p>{t('feat1d')}</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ color: 'var(--accent)' }}>{Icons.globe}</div>
              <h3>{t('feat2')}</h3>
              <p>{t('feat2d')}</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ color: 'var(--instrumental)' }}>{Icons.library}</div>
              <h3>{t('feat3')}</h3>
              <p>{t('feat3d')}</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon" style={{ color: 'var(--primary)' }}>{Icons.explore}</div>
              <h3>{t('feat4')}</h3>
              <p>{t('feat4d')}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section" id="tiers">
        <div className="wrap">
          <h2 className="landing-section-title">{t('pricingTitle')}</h2>
          <p className="landing-section-sub">{t('pricingSub')}</p>
          <div className="pricing-grid">
            <article className={`tier ${!user || user.tier !== 'pro' ? 'live' : ''}`}>
              <div className="tier-head"><h3>{t('tierBasic')}</h3><span className="badge primary">{user && user.tier !== 'pro' ? t('yourTier') : t('free')}</span></div>
              <div className="tier-price">
                <span className="price-amount">₪0</span>
                <span className="price-period">{t('forever')}</span>
              </div>
              <ul><li>{t('tierF1')}</li><li>{t('tierF2')}</li><li>{t('tierF3')}</li></ul>
              <p style={{ margin: '1rem 0 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>{t('noCC')}</p>
            </article>
            <article className="tier pro">
              <div className="tier-popular">{t('mostPopular')}</div>
              <div className="tier-head"><h3>{t('tierPro')}</h3><span className="badge inst">Pro</span></div>
              <div className="tier-price">
                <span className="price-amount">₪29</span>
                <span className="price-period">{t('perMonth')}</span>
              </div>
              <ul>
                <li>{t('tierP1')}</li>
                <li>{t('tierP2')}</li>
                <li>{t('tierP3')}</li>
                <li>{t('tierP4')}</li>
              </ul>
              {user ? (
                user.tier === 'pro' ? (
                  <div style={{ marginTop: '1.25rem', textAlign: 'center' }}>
                    <span className="badge on" style={{ fontSize: '0.875rem', padding: '0.4rem 1rem' }}>{t('currentTier')}</span>
                  </div>
                ) : (
                  <a href="#/upgrade" className="btn pro-upgrade" style={{ marginTop: '1.25rem', display: 'block', textAlign: 'center' }}>{t('upgradeNow')}</a>
                )
              ) : (
                <button className="btn pro-upgrade" onClick={() => openAuth(true)} style={{ marginTop: '1.25rem' }}>{t('signUpUpgrade')}</button>
              )}
            </article>
          </div>
        </div>
      </section>

      {!user && (
        <section className="landing-bottom-cta">
          <div className="wrap" style={{ textAlign: 'center' }}>
            <h2 className="landing-section-title">{t('readyStart')}</h2>
            <p className="landing-section-sub" style={{ marginBottom: '2rem' }}>{t('joinUsers')}</p>
            <button className="btn btn-lg" onClick={() => openAuth(true)}>{t('createFreeAccount')}</button>
          </div>
        </section>
      )}
    </>
  )
}
