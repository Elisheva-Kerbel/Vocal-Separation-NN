export default function NeedAuth({ openAuth, t }) {
  return (
    <section className="hero">
      <div className="wrap" style={{ textAlign: 'center', padding: '4rem 0' }}>
        <h2>{t('needAuth')}</h2>
        <p className="hint" style={{ marginBottom: '1.5rem' }}>{t('needAuthSub')}</p>
        <button className="btn" style={{ maxWidth: '16rem', margin: '0 auto' }} onClick={() => openAuth(false)}>{t('signIn')}</button>
        <p className="hint" style={{ marginTop: '1rem' }}>
          {t('noAccount')} <button className="link" onClick={() => openAuth(true)}>{t('signUp')}</button>
        </p>
      </div>
    </section>
  )
}
