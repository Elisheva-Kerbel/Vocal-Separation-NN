import { useEffect, useRef, useState } from 'react'

import { MIN_PASSWORD_LENGTH, currentUser, googleLogin, signIn, signOut, signUp } from './api/auth.js'
import {
  blockUser, changePassword, deleteAccount, deleteSong, getAdminSongs, getAdminStats, getAdminUsers,
  getDownloadUrl, getLibrary, getListenUrl,
  getPublicLibrary, getQuota, getSettings, getSong, getSongStatus, publishSong,
  rateSong, redeemCoupon, renameSong, reportSong, subscribe, toggleTier, unblockUser, unpublishSong, updateSettings, uploadSong,
} from './api/songs.js'

// --- i18n ---
const T = {
  he: {
    vocals: 'שירה', background: 'מוזיקה', original: 'מקור',
    queued: 'בתור', processing: 'בעיבוד', ready: 'מוכן', failed: 'נכשל', succeeded: 'מוכן',
    private: 'פרטי', public: 'ציבורי',
    free: 'חינם', pro: 'מקצועי',
    home: 'ראשי', upload: 'העלאת שיר', uploadShort: 'העלאה', myLibrary: 'הספרייה שלי', libraryShort: 'ספרייה', explore: 'גלה', settings: 'הגדרות',
    signOut: 'התנתק', signIn: 'התחבר', signUp: 'צור חשבון',
    proQuota: 'מקצועי', basicQuota: 'בסיסי', unlimited: 'ללא הגבלה',
    upgrade: 'שדרג',
    heroTagline: 'AI-Powered Audio Separation',
    heroTitle1: 'הפרדת שירים', heroTitle2: 'ברמה מקצועית',
    heroSub1: 'טכנולוגיית AI מתקדמת שמפרידה כל שיר ל', heroSub2: ' ו', heroSub3: ' באיכות סטודיו.',
    heroSub4: 'מעלים קובץ, מקבלים תוצאות. פשוט ככה.',
    startFree: 'התחל בחינם', haveAccount: 'יש לי חשבון', uploadSong: 'העלה שיר עכשיו',
    heroNote: 'ללא כרטיס אשראי · 3 הפרדות ביום · תוצאות תוך דקות',
    howTitle: 'איך זה עובד', howSub: 'שלושה צעדים פשוטים להפרדה מושלמת',
    step1: 'העלאת קובץ', step1d: 'MP3, WAV או M4A — עד 100MB. גוררים לתוך הדף או בוחרים מהמחשב.',
    step2: 'עיבוד AI', step2d: 'המודל מנתח את השיר ומפריד בין ערוץ השירה לערוץ המוזיקה באיכות גבוהה.',
    step3: 'הורדה והאזנה', step3d: 'מאזינים לתוצאות ומורידים בפורמט WAV. אפשר גם לשתף עם הקהילה.',
    whyTitle: 'למה VocalSplit', whySub: 'כל הכלים שצריך, במקום אחד',
    feat1: 'הפרדת שירה ומוזיקה', feat1d: 'חילוץ מדויק של שירה ומוזיקה מכל שיר באמצעות רשתות עצביות מתקדמות.',
    feat2: 'מודל Demucs של Meta', feat2d: 'גרסת Pro משתמשת במודל htdemucs_ft — state of the art בהפרדת שירים.',
    feat3: 'ספרייה אישית', feat3d: 'כל השירים שהפרדת נשמרים בספרייה שלך. האזנה והורדה בכל רגע.',
    feat4: 'קהילה ושיתוף', feat4d: 'שתפו הפרדות עם הקהילה וגלו שירים שאחרים הפרידו.',
    pricingTitle: 'תוכניות ומחירים', pricingSub: 'התחילו בחינם, שדרגו כשתרצו',
    tierBasic: 'בסיסי', tierPro: 'מקצועי', yourTier: 'הרמה שלך', mostPopular: 'הכי פופולרי',
    forever: '/ לתמיד', perMonth: '/ חודש', noCC: 'ללא כרטיס אשראי.',
    tierF1: 'שירה + מוזיקה', tierF2: '3 הפרדות ביום', tierF3: 'הורדה בפורמט WAV',
    tierP1: 'מודל Demucs (Meta) — איכות סטודיו', tierP2: '10 הפרדות מקצועיות ביום + בסיסי ללא הגבלה', tierP3: 'עדיפות בתור העיבוד', tierP4: 'תמיכה מועדפת',
    currentTier: 'הרמה הנוכחית שלך', upgradeNow: 'שדרג עכשיו', signUpUpgrade: 'הירשם ושדרג',
    readyStart: 'מוכנים להתחיל?', joinUsers: 'הצטרפו לאלפי משתמשים שכבר מפרידים שירים עם VocalSplit',
    createFreeAccount: 'צור חשבון בחינם',
    needAuth: 'צריך להתחבר', needAuthSub: 'כדי לגשת לעמוד זה, יש להתחבר או ליצור חשבון.',
    dropTitle: 'גרור לכאן קובץ שמע', dropSub: 'MP3, WAV, M4A · עד 100MB', orChoose: 'או בחר קובץ',
    chosenFile: 'נבחר:', modelLabel: 'מודל הפרדה:', modelBasic: 'בסיסי (מהיר)', modelPro: 'מקצועי — Demucs (Meta)',
    startSeparation: 'התחל הפרדה', uploading: 'מעלה...', separating: 'מפריד...',
    quotaBasic: 'הפרדות בסיסיות', quotaPro: 'הפרדות מקצועיות', of: 'מתוך', today: 'היום',
    listen: 'האזן', download: 'הורד', publish: 'פרסם', unpublish: 'הסר', delete: 'מחק',
    confirmDelete: 'בטוח שרוצה למחוק את השיר הזה?',
    songBy: 'הועלה ע"י', model: 'מודל', date: 'תאריך',
    libraryTitle: 'הספרייה שלי', libEmpty: 'עדיין אין שירים בספרייה.', uploadFirst: 'העלה שיר ראשון',
    exploreTitle: 'גלה שירים', exploreEmpty: 'עדיין אין שירים ציבוריים.',
    rate: 'דרג', report: 'דווח', reported: 'דווח', alreadyReported: 'כבר דווח',
    settingsTitle: 'הגדרות', email: 'אימייל', tier: 'רמה', changePw: 'שינוי סיסמה',
    currentPw: 'סיסמה נוכחית', newPw: 'סיסמה חדשה', updatePw: 'עדכן סיסמה', pwUpdated: 'הסיסמה עודכנה!',
    prefLang: 'שפה מועדפת', none: 'ללא', emailOptIn: 'קבלת עדכונים במייל',
    emailOptInDesc: 'קבלו התראות כששירים חדשים מתפרסמים בספרייה הציבורית, עדכוני תכונות חדשות וטיפים לשימוש טוב יותר בפלטפורמה.',
    profileVis: 'נראות פרופיל', switchTo: 'עבור ל',
    dangerZone: 'אזור מסוכן', deleteAccountBtn: 'מחק חשבון',
    deleteAccountConfirm: 'הקלד DELETE כדי למחוק את החשבון לצמיתות:',
    coupon: 'קוד קופון', redeemCoupon: 'ממש קופון', couponRedeemed: 'הקופון מומש בהצלחה!',
    authTitle: 'התחבר', authTitleNew: 'צור חשבון',
    continueGoogle: 'להמשיך עם Google', or: 'או',
    emailLabel: 'אימייל', passwordLabel: 'סיסמה',
    noAccount: 'אין חשבון?', hasAccount: 'יש חשבון?',
    upgradeTitle: 'שדרג לרמה מקצועית',
    upgradeSub: 'קבל גישה למודל Demucs של Meta עם הפרדות באיכות סטודיו.',
    subscribeMonthly: 'הרשמה חודשית — ₪29/חודש', subscribing: 'מפעיל...',
    footer: 'VocalSplit · פלטפורמת הפרדת שירים',
  },
  en: {
    vocals: 'Vocals', background: 'Music', original: 'Original',
    queued: 'Queued', processing: 'Processing', ready: 'Ready', failed: 'Failed', succeeded: 'Ready',
    private: 'Private', public: 'Public',
    free: 'Free', pro: 'Pro',
    home: 'Home', upload: 'Upload Song', uploadShort: 'Upload', myLibrary: 'My Library', libraryShort: 'Library', explore: 'Explore', settings: 'Settings',
    signOut: 'Sign Out', signIn: 'Sign In', signUp: 'Sign Up',
    proQuota: 'Pro', basicQuota: 'Basic', unlimited: 'Unlimited',
    upgrade: 'Upgrade',
    heroTagline: 'AI-Powered Audio Separation',
    heroTitle1: 'Vocal Separation', heroTitle2: 'Studio Quality',
    heroSub1: 'Advanced AI technology that separates any song into ', heroSub2: ' and ', heroSub3: ' in studio quality.',
    heroSub4: 'Upload a file, get results. Simple as that.',
    startFree: 'Start for Free', haveAccount: 'I have an account', uploadSong: 'Upload Song Now',
    heroNote: 'No credit card · 3 separations/day · Results in minutes',
    howTitle: 'How It Works', howSub: 'Three simple steps to perfect separation',
    step1: 'Upload File', step1d: 'MP3, WAV or M4A — up to 100MB. Drag & drop or choose from your computer.',
    step2: 'AI Processing', step2d: 'The model analyzes the song and separates vocals from music in high quality.',
    step3: 'Download & Listen', step3d: 'Listen to results and download in WAV format. You can also share with the community.',
    whyTitle: 'Why VocalSplit', whySub: 'All the tools you need, in one place',
    feat1: 'Vocal & Music Separation', feat1d: 'Precise extraction of vocals and music from any song using advanced neural networks.',
    feat2: 'Meta\'s Demucs Model', feat2d: 'Pro version uses the htdemucs_ft model — state of the art in audio separation.',
    feat3: 'Personal Library', feat3d: 'All your separated songs saved in your library. Listen and download anytime.',
    feat4: 'Community & Sharing', feat4d: 'Share separations with the community and discover songs others have separated.',
    pricingTitle: 'Plans & Pricing', pricingSub: 'Start free, upgrade when you want',
    tierBasic: 'Basic', tierPro: 'Professional', yourTier: 'Your plan', mostPopular: 'Most Popular',
    forever: '/ forever', perMonth: '/ month', noCC: 'No credit card required.',
    tierF1: 'Vocals + Music', tierF2: '3 separations/day', tierF3: 'WAV download',
    tierP1: 'Demucs (Meta) — Studio quality', tierP2: '10 pro separations/day + unlimited basic', tierP3: 'Priority processing', tierP4: 'Premium support',
    currentTier: 'Your current plan', upgradeNow: 'Upgrade Now', signUpUpgrade: 'Sign Up & Upgrade',
    readyStart: 'Ready to Start?', joinUsers: 'Join thousands of users already separating songs with VocalSplit',
    createFreeAccount: 'Create Free Account',
    needAuth: 'Login Required', needAuthSub: 'Please sign in or create an account to access this page.',
    dropTitle: 'Drag audio file here', dropSub: 'MP3, WAV, M4A · up to 100MB', orChoose: 'or choose a file',
    chosenFile: 'Selected:', modelLabel: 'Separation model:', modelBasic: 'Basic (fast)', modelPro: 'Professional — Demucs (Meta)',
    startSeparation: 'Start Separation', uploading: 'Uploading...', separating: 'Separating...',
    quotaBasic: 'Basic separations', quotaPro: 'Pro separations', of: 'of', today: 'today',
    listen: 'Listen', download: 'Download', publish: 'Publish', unpublish: 'Remove', delete: 'Delete',
    confirmDelete: 'Are you sure you want to delete this song?',
    songBy: 'Uploaded by', model: 'Model', date: 'Date',
    libraryTitle: 'My Library', libEmpty: 'No songs in your library yet.', uploadFirst: 'Upload First Song',
    exploreTitle: 'Explore Songs', exploreEmpty: 'No public songs yet.',
    rate: 'Rate', report: 'Report', reported: 'Reported', alreadyReported: 'Already reported',
    settingsTitle: 'Settings', email: 'Email', tier: 'Tier', changePw: 'Change Password',
    currentPw: 'Current Password', newPw: 'New Password', updatePw: 'Update Password', pwUpdated: 'Password updated!',
    prefLang: 'Preferred Language', none: 'None', emailOptIn: 'Email updates',
    emailOptInDesc: 'Get notified about new public songs, feature updates, and tips for using the platform.',
    profileVis: 'Profile Visibility', switchTo: 'Switch to',
    dangerZone: 'Danger Zone', deleteAccountBtn: 'Delete Account',
    deleteAccountConfirm: 'Type DELETE to permanently delete your account:',
    coupon: 'Coupon Code', redeemCoupon: 'Redeem Coupon', couponRedeemed: 'Coupon redeemed successfully!',
    authTitle: 'Sign In', authTitleNew: 'Create Account',
    continueGoogle: 'Continue with Google', or: 'or',
    emailLabel: 'Email', passwordLabel: 'Password',
    noAccount: 'No account?', hasAccount: 'Have an account?',
    upgradeTitle: 'Upgrade to Professional',
    upgradeSub: 'Get access to Meta\'s Demucs model with studio-quality separations.',
    subscribeMonthly: 'Subscribe Monthly — ₪29/mo', subscribing: 'Activating...',
    footer: 'VocalSplit · Audio Separation Platform',
  }
}

function useLang(user) {
  const [lang, setLang] = useState(() => {
    if (user?.preferred_language) return user.preferred_language
    return localStorage.getItem('vocalsplit_lang') || 'he'
  })
  useEffect(() => {
    if (user?.preferred_language) setLang(user.preferred_language)
  }, [user?.preferred_language])
  useEffect(() => {
    localStorage.setItem('vocalsplit_lang', lang)
    document.documentElement.lang = lang
    document.documentElement.dir = lang === 'he' ? 'rtl' : 'ltr'
  }, [lang])
  const t = (key) => (T[lang] || T.he)[key] || (T.he)[key] || key
  return { lang, setLang, t }
}

const STEM_LABELS = { original: 'מקור', vocals: 'שירה', background: 'מוזיקה' }
const STATUS_LABELS = { queued: 'בתור', processing: 'בעיבוד', ready: 'מוכן', failed: 'נכשל', succeeded: 'מוכן' }
const VIS_LABELS = { private: 'פרטי', public: 'ציבורי' }
const TIER_LABELS = { free: 'חינם', pro: 'מקצועי' }

function statusBadgeClass(status) {
  if (status === 'ready' || status === 'succeeded') return 'badge ready'
  if (status === 'processing' || status === 'queued') return 'badge processing'
  if (status === 'failed') return 'badge failed'
  return 'badge neutral'
}

// --- Icons (inline SVG, Lucide-style) ---
const Icons = {
  home: <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  upload: <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  library: <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>,
  explore: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>,
  settings: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  logout: <svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  music: <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>,
  fileMusic: <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="10" cy="16" r="2"/><path d="M12 12v4"/><path d="M12 12l4-1"/></svg>,
  play: <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>,
  download: <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  headphones: <svg viewBox="0 0 24 24"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>,
  trash: <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>,
  globe: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>,
  eye: <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>,
  eyeOff: <svg viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>,
  arrowRight: <svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
  shield: <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
}

function useHash() {
  const [hash, setHash] = useState(window.location.hash || '#/')
  useEffect(() => {
    const onHash = () => setHash(window.location.hash || '#/')
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  return hash
}

export default function App() {
  const [user, setUser] = useState(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [newAccount, setNewAccount] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authBusy, setAuthBusy] = useState(false)
  const [quota, setQuota] = useState(null)
  const hash = useHash()
  const { lang, setLang, t } = useLang(user)

  function refreshQuota() {
    getQuota().then(setQuota).catch(() => {})
  }

  useEffect(() => {
    let live = true
    currentUser().then((account) => { if (live) { setUser(account); if (account) refreshQuota() } })
    return () => { live = false }
  }, [])

  useEffect(() => {
    if (!authOpen) return undefined
    const onKey = (e) => { if (e.key === 'Escape') setAuthOpen(false) }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [authOpen])

  function openAuth(creating) {
    setNewAccount(creating)
    setAuthError('')
    setAuthOpen(true)
  }

  async function onAuthSubmit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setAuthBusy(true)
    setAuthError('')
    try {
      const submit = newAccount ? signUp : signIn
      setUser(await submit(form.get('email'), form.get('password')))
      setAuthOpen(false)
    } catch (failure) {
      setAuthError(failure.message)
    } finally {
      setAuthBusy(false)
    }
  }

  async function onGoogleAuth(credential) {
    setAuthBusy(true)
    setAuthError('')
    try {
      setUser(await googleLogin(credential))
      setAuthOpen(false)
    } catch (failure) {
      setAuthError(failure.message)
    } finally {
      setAuthBusy(false)
    }
  }

  async function onSignOut() {
    await signOut().catch(() => {})
    setUser(null)
    window.location.hash = '#/'
  }

  const currentPage = hash.startsWith('#/song/') ? 'song'
    : hash === '#/library' ? 'library'
    : hash === '#/explore' ? 'explore'
    : hash === '#/settings' ? 'settings'
    : hash === '#/upload' ? 'upload'
    : hash === '#/upgrade' ? 'upgrade'
    : hash === '#/admin' ? 'admin'
    : 'home'

  let page
  if (hash.startsWith('#/song/')) {
    page = <SongPage songId={hash.replace('#/song/', '')} user={user} t={t} />
  } else if (hash === '#/library') {
    page = user ? <LibraryPage user={user} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/explore') {
    page = <ExplorePage user={user} t={t} />
  } else if (hash === '#/settings') {
    page = user ? <SettingsPage user={user} setUser={setUser} onSignOut={onSignOut} t={t} lang={lang} setLang={setLang} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/upload') {
    page = user ? <UploadPage user={user} quota={quota} onUploaded={refreshQuota} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/upgrade') {
    page = user ? <UpgradePage user={user} setUser={setUser} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/admin') {
    page = user && user.role === 'super_admin' ? <AdminPage user={user} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else {
    page = <HomePage user={user} openAuth={openAuth} t={t} />
  }

  return (
    <div className={`app-layout ${user ? '' : 'no-sidebar'}`}>
      {user && (
        <aside className="sidebar">
          <a href="#/" className="sidebar-brand">
            <span className="sidebar-brand-icon">{Icons.headphones}</span>
            <span className="sidebar-brand-name">VocalSplit</span>
          </a>
          <nav className="sidebar-nav">
            <a href="#/" className={`sidebar-link ${currentPage === 'home' ? 'active' : ''}`}>{Icons.home}<span>{t('home')}</span></a>
            <a href="#/upload" className={`sidebar-link ${currentPage === 'upload' ? 'active' : ''}`}>{Icons.upload}<span>{t('upload')}</span></a>
            <a href="#/library" className={`sidebar-link ${currentPage === 'library' ? 'active' : ''}`}>{Icons.library}<span>{t('myLibrary')}</span></a>
            <a href="#/explore" className={`sidebar-link ${currentPage === 'explore' ? 'active' : ''}`}>{Icons.explore}<span>{t('explore')}</span></a>
            <a href="#/settings" className={`sidebar-link ${currentPage === 'settings' ? 'active' : ''}`}>{Icons.settings}<span>{t('settings')}</span></a>
            {user.role === 'super_admin' && (
              <a href="#/admin" className={`sidebar-link ${currentPage === 'admin' ? 'active' : ''}`}>{Icons.shield}<span>ניהול</span></a>
            )}
          </nav>
          {user.tier !== 'pro' && (
            <a href="#/upgrade" className="sidebar-upgrade-btn">{t('upgrade')} →</a>
          )}
          <div className="sidebar-spacer" />
          <div className="sidebar-user">
            <div className="sidebar-user-email">{user.email}</div>
            <div className="sidebar-user-tier">{t(user.tier)}</div>
            {quota && (
              <div className="sidebar-quota">
                {user.tier === 'pro' ? (
                  <>
                    <span className="quota-line">{t('proQuota')}: {quota.professional_used}/{quota.professional_limit}</span>
                    <span className="quota-line">{t('basicQuota')}: {t('unlimited')}</span>
                  </>
                ) : (
                  <span className="quota-line">{t('basicQuota')}: {quota.basic_used}/{quota.basic_limit}</span>
                )}
              </div>
            )}
            <div className="sidebar-user-actions">
              <button className="ghost" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }} onClick={onSignOut}>{Icons.logout} {t('signOut')}</button>
            </div>
          </div>
        </aside>
      )}

      <header className="topbar">
        <div className="topbar-inner">
          <a href="#/" className="brand">VocalSplit</a>
          <nav className="nav">
            <a href="#/">{t('home')}</a>
            <a href="#/explore">{t('explore')}</a>
            <button className="topbar-signin" type="button" onClick={() => openAuth(false)}>{t('signIn')}</button>
          </nav>
        </div>
      </header>

      {user && (
        <nav className="mobile-nav">
          <a href="#/" className={currentPage === 'home' ? 'active' : ''}>{Icons.home}<span>{t('home')}</span></a>
          <a href="#/upload" className={currentPage === 'upload' ? 'active' : ''}>{Icons.upload}<span>{t('uploadShort')}</span></a>
          <a href="#/library" className={currentPage === 'library' ? 'active' : ''}>{Icons.library}<span>{t('libraryShort')}</span></a>
          <a href="#/explore" className={currentPage === 'explore' ? 'active' : ''}>{Icons.explore}<span>{t('explore')}</span></a>
          <a href="#/settings" className={currentPage === 'settings' ? 'active' : ''}>{Icons.settings}<span>{t('settings')}</span></a>
        </nav>
      )}

      <div className="content-area">
        <main>{page}</main>
        <footer><div className="wrap">{t('footer')}</div></footer>
      </div>

      {authOpen && <AuthModal
        newAccount={newAccount} setNewAccount={setNewAccount}
        authError={authError} setAuthError={setAuthError}
        authBusy={authBusy} onSubmit={onAuthSubmit}
        onGoogleAuth={onGoogleAuth}
        onClose={() => setAuthOpen(false)}
        t={t}
      />}
    </div>
  )
}

function NeedAuth({ openAuth, t }) {
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

function HomePage({ user, openAuth, t }) {
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

function UploadPage({ user, quota, onUploaded, t }) {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [modelChoice, setModelChoice] = useState(user.tier === 'pro' ? 'professional' : 'basic')
  const [visibility, setVisibility] = useState('private')

  const proQuotaLeft = quota && quota.professional_limit ? quota.professional_limit - quota.professional_used : 0
  const canPickPro = user.tier === 'pro' && proQuotaLeft > 0

  async function onUpload() {
    if (!file) return
    setBusy(true); setError(''); setProgress(0)
    try {
      const res = await uploadSong(file, setProgress, { modelChoice, visibility })
      setResult(res)
      if (onUploaded) onUploaded()
      window.location.hash = `#/song/${res.song_id}`
    } catch (f) { setError(f.message) }
    finally { setBusy(false) }
  }

  return (
    <section className="hero">
      <div className="wrap" style={{ maxWidth: '36rem' }}>
        <h2>{t('upload')}</h2>
        <p className="lede" style={{ margin: '0.5rem 0 1.5rem' }}>MP3, WAV או M4A · עד 100 MB · מקסימום 5.5 דקות</p>
        <div className="panel">
          {error && <p className="error" role="alert">{error}</p>}
          {result ? (
            <div style={{ textAlign: 'center' }}>
              <p className="success-msg" style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>ההעלאה הצליחה!</p>
              <p className="hint">העיבוד התחיל · {result.title || 'ללא שם'} · {result.model_tier === 'professional' ? 'מקצועי' : 'בסיסי'}</p>
              <a href={`#/song/${result.song_id}`} className="btn full" style={{ marginTop: '1.25rem' }}>צפה בשיר</a>
              <button className="btn secondary full" style={{ marginTop: '0.5rem' }} onClick={() => { setResult(null); setFile(null) }}>העלה שיר נוסף</button>
            </div>
          ) : (
            <>
              <label className="drop">
                <input type="file" accept="audio/mpeg,audio/wav,audio/mp4,.mp3,.wav,.m4a" onChange={e => setFile(e.target.files[0])} />
                <span className="drop-icon">{Icons.upload}</span>
                <b>{file ? file.name : 'בחר קובץ'}</b>
                {file && <span className="hint">{(file.size / 1024 / 1024).toFixed(1)} MB</span>}
              </label>

              <div className="upload-options">
                <div className="option-group">
                  <span className="option-label">רמת הפרדה</span>
                  <div className="segmented" role="radiogroup">
                    <button type="button" role="radio" aria-checked={modelChoice === 'basic'}
                      className={`seg ${modelChoice === 'basic' ? 'on' : ''}`}
                      onClick={() => setModelChoice('basic')}>בסיסי</button>
                    <button type="button" role="radio" aria-checked={modelChoice === 'professional'}
                      className={`seg ${modelChoice === 'professional' ? 'on' : ''} ${!canPickPro ? 'disabled' : ''}`}
                      disabled={!canPickPro}
                      onClick={() => canPickPro && setModelChoice('professional')}>
                      מקצועי {user.tier !== 'pro' && <span className="badge inst" style={{ fontSize: '0.65rem', marginRight: '0.25rem' }}>Pro</span>}
                    </button>
                  </div>
                  {user.tier === 'pro' && quota && (
                    <span className="hint" style={{ fontSize: '0.75rem' }}>נותרו {proQuotaLeft} הפרדות מקצועיות היום</span>
                  )}
                  {user.tier !== 'pro' && (
                    <span className="hint" style={{ fontSize: '0.75rem' }}>הפרדה מקצועית זמינה <a href="#/upgrade" className="link">למנויי Pro</a></span>
                  )}
                </div>

                <div className="option-group">
                  <span className="option-label">נראות</span>
                  <div className="segmented" role="radiogroup">
                    <button type="button" role="radio" aria-checked={visibility === 'private'}
                      className={`seg ${visibility === 'private' ? 'on' : ''}`}
                      onClick={() => setVisibility('private')}>פרטי</button>
                    <button type="button" role="radio" aria-checked={visibility === 'public'}
                      className={`seg ${visibility === 'public' ? 'on' : ''}`}
                      onClick={() => setVisibility('public')}>ציבורי</button>
                  </div>
                </div>
              </div>

              {busy && <div style={{ marginTop: '1rem' }}>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
                <p className="hint">{progress}% הועלה</p>
              </div>}
              <button className="btn full" type="button" disabled={!file || busy} onClick={onUpload} style={{ marginTop: '1rem' }}>
                {busy ? 'מעלה...' : 'העלה והפרד'}
              </button>
            </>
          )}
        </div>
      </div>
    </section>
  )
}

function SongPage({ songId, user, t }) {
  const [song, setSong] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [listenUrls, setListenUrls] = useState({})
  const [active, setActive] = useState('original')
  const [loaded, setLoaded] = useState({ original: true })
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')
  const [saved, setSaved] = useState(false)
  const [msg, setMsg] = useState('')
  const [elapsed, setElapsed] = useState(0)
  const titleRef = useRef(null)
  const players = useRef({})

  const isProcessing = song && (song.status === 'processing' || song.status === 'uploaded' || song.status === 'queued')

  useEffect(() => {
    let live = true
    loadSong()
    async function loadSong() {
      try {
        const s = await getSong(songId)
        if (live) { setSong(s); setLoading(false); setTitleDraft(s.title || '') }
        if (s.status === 'processing' || s.status === 'uploaded' || s.status === 'queued') {
          setTimeout(loadSong, 3000)
        }
        if (s.status === 'ready' && live) {
          const urls = {}
          for (const p of ['original', 'vocals', 'background']) {
            const hasStem = s.stems && s.stems.some(st => st.purpose === p)
            if (hasStem) {
              try {
                const r = await getListenUrl(songId, p)
                urls[p] = r.url
              } catch { urls[p] = `/songs/${songId}/stream/${p}` }
            }
          }
          if (live) setListenUrls(urls)
        }
      } catch (f) { if (live) { setError(f.message); setLoading(false) } }
    }
    return () => { live = false }
  }, [songId])

  useEffect(() => {
    if (!isProcessing) return undefined
    setElapsed(0)
    const tick = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(tick)
  }, [isProcessing])

  function switchTo(id) {
    setLoaded(prev => ({ ...prev, [id]: true }))
    const from = players.current[active]
    const to = players.current[id]
    if (from && to && to.readyState >= 1) {
      to.currentTime = from.currentTime
      if (!from.paused) { from.pause(); to.play() }
    } else if (from && !from.paused) {
      from.pause()
    }
    setActive(id)
  }

  async function onDownload(purpose) {
    try {
      const r = await getDownloadUrl(songId, purpose)
      window.location.href = r.url
    } catch {
      const a = document.createElement('a')
      a.href = `/songs/${songId}/stream/${purpose}`
      a.download = `${song.title || 'track'}_${purpose}.wav`
      a.click()
    }
  }

  async function onRename() {
    if (!titleDraft.trim()) return
    try {
      await renameSong(songId, titleDraft.trim())
      setSong(prev => ({ ...prev, title: titleDraft.trim() }))
      setEditingTitle(false)
      setMsg('השם עודכן')
      setTimeout(() => setMsg(''), 2000)
    } catch (f) { setError(f.message) }
  }

  async function onDelete() {
    try {
      await deleteSong(songId)
      window.location.hash = '#/upload'
    } catch (f) { setError(f.message) }
  }

  function onSave() {
    setSaved(true)
    setMsg('השיר נשמר בספרייה!')
    setTimeout(() => { window.location.hash = '#/library' }, 1200)
  }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>
  if (error && !song) return <section className="page-section"><div className="wrap"><p className="error">{error}</p></div></section>
  if (!song) return null

  const STEM_ORDER = ['original', 'vocals', 'background']
  const STEM_CSS = { original: '', vocals: 'vocal', background: 'inst' }
  const STEM_NAMES = { original: t('original') || 'מקור', vocals: t('vocals'), background: t('background') }
  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0')
  const ss = String(elapsed % 60).padStart(2, '0')

  return (
    <section className="page-section">
      <div className="wrap" style={{ maxWidth: '48rem' }}>
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          {!isProcessing && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              {editingTitle ? (
                <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
                  <input ref={titleRef} className="field-input" value={titleDraft} onChange={e => setTitleDraft(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') onRename(); if (e.key === 'Escape') setEditingTitle(false) }}
                    style={{ flex: 1, fontSize: '1.1rem' }} autoFocus />
                  <button className="btn" onClick={onRename} style={{ padding: '0.4rem 1rem' }}>שמור</button>
                  <button className="ghost" onClick={() => { setEditingTitle(false); setTitleDraft(song.title || '') }}>ביטול</button>
                </div>
              ) : (
                <h2 style={{ margin: 0, cursor: 'pointer' }} onClick={() => setEditingTitle(true)} title="לחץ לשינוי שם">
                  {song.title || 'ללא שם'} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>&#9998;</span>
                </h2>
              )}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span className={statusBadgeClass(song.status)}>{STATUS_LABELS[song.status] || song.status}</span>
                <span className="badge neutral">{VIS_LABELS[song.visibility] || song.visibility}</span>
              </div>
            </div>
          )}

          {msg && <p style={{ color: 'var(--ok)', fontWeight: 600, margin: '0 0 1rem' }}>{msg}</p>}
          {error && <p className="error">{error}</p>}

          {isProcessing && (
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div className="processing-anim">
                <span className="spinner" style={{ width: 48, height: 48 }} />
              </div>
              <h3 style={{ margin: '1.5rem 0 0.5rem', color: 'var(--text-primary)' }}>מפריד שירה ומוזיקה...</h3>
              <p className="hint">זה יכול לקחת כמה דקות. תוצאות איכותיות שוות את ההמתנה.</p>
              <p style={{ fontFamily: 'monospace', fontSize: '1.5rem', color: 'var(--primary)', margin: '1rem 0 0' }}>{mm}:{ss}</p>
            </div>
          )}

          {song.status === 'ready' && (
            <div style={{ marginTop: '0.5rem' }}>
              <div className="segmented" role="tablist" aria-label="בחר ערוץ">
                {STEM_ORDER.map(id => (
                  <button key={id} role="tab" type="button"
                    aria-selected={active === id}
                    className={`seg${active === id ? ' on' : ''}${active === id && STEM_CSS[id] ? ` ${STEM_CSS[id]}` : ''}`}
                    onClick={() => switchTo(id)}>
                    {STEM_NAMES[id]}
                  </button>
                ))}
              </div>

              {STEM_ORDER.map(id => (
                <audio key={id} ref={node => { players.current[id] = node }}
                  controls={active === id} src={loaded[id] ? (listenUrls[id] || '') : ''}
                  preload={active === id ? 'auto' : 'none'}
                  style={{ width: '100%', display: active === id ? 'block' : 'none', marginTop: '1rem' }} />
              ))}

              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                {STEM_ORDER.map(id => (
                  <button key={id} className="ghost" onClick={() => onDownload(id)} style={{ fontSize: '0.85rem' }}>
                    {Icons.download} {STEM_NAMES[id]}
                  </button>
                ))}
              </div>
            </div>
          )}

          {song.status === 'failed' && song.job && (
            <p className="error">{song.job.error_message || 'ההפרדה נכשלה.'}</p>
          )}
        </div>

        {song.status === 'ready' && !saved && (
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button className="btn" onClick={onSave}>שמור בספרייה</button>
            <button className="btn danger" onClick={onDelete}>מחק</button>
          </div>
        )}
        {song.status === 'ready' && saved && (
          <a href="#/library" className="btn secondary">לספרייה</a>
        )}
        {song.status === 'failed' && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <a href="#/upload" className="btn">העלה שיר חדש</a>
            <button className="btn danger" onClick={onDelete}>מחק</button>
          </div>
        )}
      </div>
    </section>
  )
}

function LibrarySongCard({ song, onPublish, onUnpublish, onDelete }) {
  const [listenUrls, setListenUrls] = useState({})
  const [error, setError] = useState('')

  async function loadListen(purpose) {
    try {
      const r = await getListenUrl(song.id, purpose)
      setListenUrls(prev => ({ ...prev, [purpose]: r.url }))
    } catch {
      setListenUrls(prev => ({ ...prev, [purpose]: `/songs/${song.id}/stream/${purpose}` }))
    }
  }

  async function onDownload(purpose) {
    try {
      const r = await getDownloadUrl(song.id, purpose)
      window.location.href = r.url
    } catch {
      const a = document.createElement('a')
      a.href = `/songs/${song.id}/stream/${purpose}`
      a.download = `${song.title || 'track'}_${purpose}.wav`
      a.click()
    }
  }

  return (
    <article className="song-card">
      <h3><a href={`#/song/${song.id}`}>{song.title || 'ללא שם'}</a></h3>
      <div style={{ display: 'flex', gap: '0.35rem', margin: '0.5rem 0', flexWrap: 'wrap' }}>
        <span className={statusBadgeClass(song.status)}>{STATUS_LABELS[song.status] || song.status}</span>
        <span className="badge neutral">{VIS_LABELS[song.visibility] || song.visibility}</span>
        {song.model_tier && <span className={`badge ${song.model_tier === 'professional' ? 'inst' : 'primary'} model-badge`}>
          {song.model_tier === 'professional' ? 'מקצועי' : 'בסיסי'}
        </span>}
      </div>
      <p className="hint">{new Date(song.created_at).toLocaleDateString('he-IL')}</p>

      {song.status === 'ready' && (
        <div className="song-card-stems">
          {['original', 'vocals', 'background'].map(purpose => (
            <div key={purpose} className="stem-row">
              <span className={`badge ${purpose === 'vocals' ? 'vocal' : purpose === 'background' ? 'inst' : 'neutral'}`} style={{ fontSize: '0.7rem', minWidth: '3rem', textAlign: 'center' }}>{STEM_LABELS[purpose] || 'מקור'}</span>
              {listenUrls[purpose] ? (
                <audio controls src={listenUrls[purpose]} style={{ flex: 1, height: 32 }} />
              ) : (
                <button className="ghost" style={{ fontSize: '0.75rem' }} onClick={() => loadListen(purpose)}>{Icons.headphones} האזן</button>
              )}
              <button className="ghost" style={{ fontSize: '0.75rem' }} onClick={() => onDownload(purpose)}>{Icons.download}</button>
            </div>
          ))}
        </div>
      )}

      {error && <p className="error" style={{ fontSize: '0.8rem' }}>{error}</p>}

      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        {song.status === 'ready' && song.visibility === 'private' && (
          <button className="ghost" onClick={() => onPublish(song.id)}>{Icons.globe} פרסם</button>
        )}
        {song.visibility === 'public' && (
          <button className="ghost" onClick={() => onUnpublish(song.id)}>{Icons.eyeOff} הסר</button>
        )}
        <button className="ghost" style={{ color: 'var(--danger)' }} onClick={() => onDelete(song.id)}>{Icons.trash} מחק</button>
      </div>
    </article>
  )
}

function LibraryPage({ user, t }) {
  const [songs, setSongs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => { loadLibrary() }, [])

  async function loadLibrary() {
    try {
      const res = await getLibrary()
      setSongs(res.songs); setTotal(res.total); setLoading(false)
    } catch (f) { setError(f.message); setLoading(false) }
  }

  async function onDelete(songId) {
    try { await deleteSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  async function onPublish(songId) {
    try { await publishSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  async function onUnpublish(songId) {
    try { await unpublishSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  return (
    <section className="page-section">
      <div className="wrap">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>{t('myLibrary')} ({total})</h2>
          <a href="#/upload" className="btn" style={{ margin: 0 }}>{Icons.upload} {t('upload')}</a>
        </div>

        {error && <p className="error">{error}</p>}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0' }}><span className="spinner" /></div>
        ) : songs.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>{t('libEmpty')}</p>
            <a href="#/upload" className="btn" style={{ maxWidth: '16rem', margin: '0 auto' }}>{t('uploadFirst')}</a>
          </div>
        ) : (
          <div className="grid">
            {songs.map(s => (
              <LibrarySongCard key={s.id} song={s} onPublish={onPublish} onUnpublish={onUnpublish} onDelete={onDelete} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

function PublicSongCard({ song: s, user, onRate }) {
  const [expanded, setExpanded] = useState(false)
  const [urls, setUrls] = useState({})

  async function loadPublicUrls() {
    if (expanded) { setExpanded(false); return }
    setExpanded(true)
    for (const p of ['original', 'vocals', 'background']) {
      if (urls[p]) continue
      try {
        const res = await fetch(`/public/songs/${s.id}/listen-url/${p}`)
        if (res.ok) {
          const data = await res.json()
          setUrls(prev => ({ ...prev, [p]: data.url }))
        }
      } catch { /* fallback to stream */ }
    }
  }

  return (
    <article className="song-card">
      <h3><a href={`#/song/${s.id}`}>{s.title || 'ללא שם'}</a></h3>
      {s.owner_name && <p className="hint">מאת {s.owner_name}</p>}
      <p className="hint">
        {s.avg_rating ? `${s.avg_rating}/5` : 'ללא דירוג'} ({s.rating_count})
      </p>
      <button className="ghost" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }} onClick={loadPublicUrls}>
        {expanded ? 'הסתר נגן' : <>{Icons.headphones} האזן</>}
      </button>
      {expanded && (
        <div style={{ marginTop: '0.5rem' }}>
          {['original', 'vocals', 'background'].map(purpose => (
            <div key={purpose} className="stem-row">
              <span className={`badge ${purpose === 'vocals' ? 'vocal' : purpose === 'background' ? 'inst' : 'neutral'}`} style={{ fontSize: '0.7rem', minWidth: '3rem', textAlign: 'center' }}>{STEM_LABELS[purpose] || 'מקור'}</span>
              <audio controls src={urls[purpose] || `/public/songs/${s.id}/stream/${purpose}`} style={{ flex: 1, height: 32 }} />
              <a href={urls[purpose] || `/public/songs/${s.id}/stream/${purpose}`} download={`${s.title || 'track'}_${purpose}.wav`} className="ghost" style={{ fontSize: '0.75rem' }}>{Icons.download}</a>
            </div>
          ))}
        </div>
      )}
      {user && (
        <div className="rating-bar" style={{ marginTop: '0.5rem' }}>
          {[1,2,3,4,5].map(n => (
            <button key={n} className="rating-btn" onClick={() => onRate(s.id, n)}>{n}</button>
          ))}
        </div>
      )}
    </article>
  )
}

function ExplorePage({ user, t }) {
  const [songs, setSongs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getPublicLibrary().then(res => { setSongs(res.songs); setTotal(res.total); setLoading(false) })
      .catch(f => { setError(f.message); setLoading(false) })
  }, [])

  async function onRate(songId, score) {
    try { await rateSong(songId, score) } catch (f) { setError(f.message) }
  }

  return (
    <section className="page-section">
      <div className="wrap">
        <h2>{t('exploreTitle')} ({total})</h2>
        {error && <p className="error">{error}</p>}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0' }}><span className="spinner" /></div>
        ) : songs.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>{t('exploreEmpty')}</p>
          </div>
        ) : (
          <div className="grid">
            {songs.map(s => (
              <PublicSongCard key={s.id} song={s} user={user} onRate={onRate} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

function UpgradePage({ user, setUser, t }) {
  const [selectedPlan, setSelectedPlan] = useState('monthly')
  const [couponCode, setCouponCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  if (user.tier === 'pro') {
    return (
      <section className="page-section">
        <div className="wrap upgrade-page" style={{ textAlign: 'center', padding: '3rem 0' }}>
          <h2>{t('upgradeTitle')}</h2>
          <p className="hint" style={{ marginBottom: '1.5rem' }}>{t('upgradeSub')}</p>
          <a href="#/upload" className="btn">{t('uploadSong')}</a>
        </div>
      </section>
    )
  }

  async function onSubscribe() {
    setBusy(true); setError(''); setMsg('')
    try {
      const res = await subscribe(selectedPlan, couponCode || undefined)
      setMsg(res.message)
      setUser(prev => ({ ...prev, tier: 'pro' }))
    } catch (f) { setError(f.message) }
    finally { setBusy(false) }
  }

  return (
    <section className="page-section">
      <div className="wrap upgrade-page">
        <h2>{t('upgradeTitle')}</h2>
        <p className="lede" style={{ margin: '0.5rem 0 2rem' }}>{t('upgradeSub')}</p>

        {msg && <div className="card" style={{ textAlign: 'center', marginBottom: '1.5rem', borderColor: 'var(--ok)' }}>
          <p style={{ color: 'var(--ok)', fontWeight: 600, margin: 0 }}>{msg}</p>
          <a href="#/upload" className="btn" style={{ marginTop: '1rem' }}>העלה שיר עכשיו</a>
        </div>}

        {!msg && (
          <>
            <div className="grid two" style={{ marginBottom: '2rem' }}>
              <article className="tier">
                <div className="tier-head"><h3>בסיסי</h3><span className="badge primary">הרמה שלך</span></div>
                <div className="tier-price"><span className="price-amount">₪0</span><span className="price-period">/ לתמיד</span></div>
                <ul><li>שירה + מוזיקה</li><li>3 הפרדות בסיסיות ביום</li><li>הורדה בפורמט WAV</li></ul>
              </article>
              <article className="tier pro live">
                <div className="tier-head"><h3>מקצועי</h3><span className="badge inst">Pro</span></div>
                <div className="tier-price"><span className="price-amount">₪29</span><span className="price-period">/ חודש</span></div>
                <ul>
                  <li>מודל Demucs (Meta) — איכות סטודיו</li>
                  <li>10 הפרדות מקצועיות + בסיסי ללא הגבלה</li>
                  <li>עדיפות בתור העיבוד</li>
                  <li>תמיכה מועדפת</li>
                </ul>
              </article>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>בחר תכנית</h3>
              <div className="plan-selector">
                <button className={`plan-option ${selectedPlan === 'monthly' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('monthly')}>
                  <span className="plan-name">חודשי</span>
                  <span className="plan-price">₪29<small>/חודש</small></span>
                </button>
                <button className={`plan-option ${selectedPlan === 'annual' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('annual')}>
                  <span className="plan-save">חסכון של ₪99!</span>
                  <span className="plan-name">שנתי</span>
                  <span className="plan-price">₪249<small>/שנה</small></span>
                  <span className="plan-monthly">₪20.75 לחודש</span>
                </button>
              </div>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>יש לך קופון?</h3>
              <div className="coupon-row">
                <input type="text" placeholder="הזן קוד קופון" value={couponCode}
                  onChange={e => setCouponCode(e.target.value)} />
              </div>
            </div>

            <div className="payment-placeholder">
              <p style={{ fontWeight: 600, margin: '0 0 0.5rem' }}>תשלום</p>
              <p style={{ margin: 0 }}>שער תשלום יתווסף בקרוב. כרגע ניתן לשדרג באמצעות קופון או לנסות את השירות.</p>
            </div>

            {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

            <button className="btn pro-upgrade full" onClick={onSubscribe} disabled={busy} style={{ marginTop: '1.5rem' }}>
              {busy ? 'מעבד...' : couponCode ? 'הפעל קופון ושדרג' : selectedPlan === 'monthly' ? 'שדרג — ₪29/חודש' : 'שדרג — ₪249/שנה'}
            </button>

            <a href="#/" className="link" style={{ display: 'block', textAlign: 'center', marginTop: '1rem' }}>חזרה לדף הראשי</a>
          </>
        )}
      </div>
    </section>
  )
}

const STATUS_COLORS = { ready: '#22c55e', processing: '#f59e0b', queued: '#3b82f6', uploaded: '#3b82f6', failed: '#ef4444' }

function AdminPage({ user }) {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [songs, setSongs] = useState([])
  const [tab, setTab] = useState('dashboard')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => { loadData() }, [])

  async function loadData() {
    try {
      const [s, u, sg] = await Promise.all([getAdminStats(), getAdminUsers(0, 100), getAdminSongs(0, 100)])
      setStats(s); setUsers(u); setSongs(sg); setLoading(false)
    } catch (e) { setError(e.message); setLoading(false) }
  }

  async function handleBlock(userId, blocked) {
    try {
      if (blocked) await unblockUser(userId); else await blockUser(userId)
      const u = await getAdminUsers(0, 100)
      setUsers(u)
    } catch (e) { setError(e.message) }
  }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>

  return (
    <section className="page-section">
      <div className="wrap">
        <h2>{Icons.shield} לוח ניהול</h2>
        {error && <p className="error">{error}</p>}

        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {['dashboard', 'users', 'songs'].map(t => (
            <button key={t} className={tab === t ? 'btn' : 'ghost'} onClick={() => setTab(t)}>
              {t === 'dashboard' ? 'סטטיסטיקות' : t === 'users' ? 'משתמשים' : 'שירים'}
            </button>
          ))}
        </div>

        {tab === 'dashboard' && stats && (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
            {[
              ['משתמשים', stats.total_users, '#7c3aed'],
              ['פעילים', stats.active_users, '#22c55e'],
              ['שירים', stats.total_songs, '#3b82f6'],
              ['ציבוריים', stats.public_songs, '#f59e0b'],
              ['מוכנים', stats.ready_songs, '#22c55e'],
              ['בעיבוד', stats.processing_songs, '#f59e0b'],
              ['נכשלו', stats.failed_songs, '#ef4444'],
            ].map(([label, val, color]) => (
              <div key={label} className="card" style={{ textAlign: 'center', padding: '1.25rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 700, color }}>{val}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{label}</div>
              </div>
            ))}
          </div>
        )}

        {tab === 'users' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>מייל</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>סטטוס</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תפקיד</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>רמה</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תאריך</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>פעולות</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.5rem' }}>{u.email}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span className={`badge ${u.status === 'active' ? 'primary' : 'danger'}`}>{u.status === 'active' ? 'פעיל' : 'חסום'}</span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{u.role === 'super_admin' ? 'מנהל' : 'משתמש'}</td>
                    <td style={{ padding: '0.5rem' }}>{u.tier === 'pro' ? 'מקצועי' : 'בסיסי'}</td>
                    <td style={{ padding: '0.5rem' }}>{new Date(u.created_at).toLocaleDateString('he-IL')}</td>
                    <td style={{ padding: '0.5rem' }}>
                      {u.email !== user.email && (
                        <button className="ghost" style={{ fontSize: '0.75rem', color: u.status === 'active' ? 'var(--danger)' : '#22c55e' }}
                          onClick={() => handleBlock(u.id, u.status === 'blocked')}>
                          {u.status === 'active' ? 'חסום' : 'שחרר'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'songs' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>שם</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>בעלים</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>סטטוס</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>נראות</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>מודל</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תאריך</th>
                </tr>
              </thead>
              <tbody>
                {songs.map(s => (
                  <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.5rem' }}><a href={`#/song/${s.id}`}>{s.title || 'ללא שם'}</a></td>
                    <td style={{ padding: '0.5rem' }}>{s.owner_email ? s.owner_email.split('@')[0] : '—'}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span style={{ color: STATUS_COLORS[s.status] || 'inherit' }}>{s.status === 'ready' ? 'מוכן' : s.status === 'failed' ? 'נכשל' : s.status === 'processing' ? 'בעיבוד' : s.status}</span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{s.visibility === 'public' ? 'ציבורי' : 'פרטי'}</td>
                    <td style={{ padding: '0.5rem' }}>{s.model_tier === 'professional' ? 'מקצועי' : 'בסיסי'}</td>
                    <td style={{ padding: '0.5rem' }}>{new Date(s.created_at).toLocaleDateString('he-IL')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}

function SettingsPage({ user, setUser, onSignOut, t, lang, setLang }) {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(false)
  const [pwBusy, setPwBusy] = useState(false)
  const [showCurPw, setShowCurPw] = useState(false)
  const [showNewPw, setShowNewPw] = useState(false)

  useEffect(() => {
    getSettings().then(s => { setSettings(s); setLoading(false) }).catch(f => { setError(f.message); setLoading(false) })
  }, [])

  async function onUpdate(field, value) {
    try {
      const updated = await updateSettings({ [field]: value })
      setSettings(updated)
      setMsg('ההגדרות נשמרו.')
      setTimeout(() => setMsg(''), 2000)
    } catch (f) { setError(f.message) }
  }

  async function onToggleTier() {
    try {
      const res = await toggleTier()
      setSettings(prev => ({ ...prev, tier: res.tier }))
      setUser(prev => ({ ...prev, tier: res.tier }))
      setMsg(`הרמה שונתה ל${res.tier === 'pro' ? 'מקצועי' : 'בסיסי'}`)
      setTimeout(() => setMsg(''), 3000)
    } catch (f) { setError(f.message) }
  }

  async function onChangePassword(e) {
    e.preventDefault()
    const form = e.target
    const cur = form.curPw.value
    const nw = form.newPw.value
    setPwBusy(true)
    setError('')
    try {
      const res = await changePassword(cur, nw)
      setMsg(res.message)
      form.reset()
      setShowCurPw(false)
      setShowNewPw(false)
      setTimeout(() => setMsg(''), 3000)
    } catch (f) { setError(f.message) }
    setPwBusy(false)
  }

  async function onDeleteAccount() {
    try {
      await deleteAccount()
      setUser(null)
      window.location.hash = '#/'
    } catch (f) { setError(f.message) }
  }

  const ROLE_LABELS = { free: 'משתמש', user: 'משתמש', content_moderator: 'מנהל תוכן', user_admin: 'מנהל משתמשים', coupon_admin: 'מנהל קופונים', super_admin: 'מנהל ראשי' }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>

  return (
    <section className="page-section">
      <div className="wrap" style={{ maxWidth: '36rem' }}>
        <h2>{t('settingsTitle')}</h2>
        {error && <p className="error">{error}</p>}
        {msg && <p style={{ color: 'var(--ok)', fontWeight: 600 }}>{msg}</p>}

        {settings && (
          <>
            <div className="card" style={{ marginBottom: '1rem' }}>
              <p style={{ margin: '0 0 0.35rem' }}><b>{t('email')}:</b> {settings.email}</p>
              <p style={{ margin: '0 0 0.35rem' }}><b>{t('tier')}:</b> <span className={`badge ${settings.tier === 'pro' ? 'inst' : 'primary'}`}>{t(settings.tier)}</span></p>
              <p style={{ margin: 0 }}><b>{lang === 'en' ? 'Role' : 'תפקיד'}:</b> {ROLE_LABELS[settings.role] || settings.role}</p>
              {settings.role === 'super_admin' && (
                <div style={{ marginTop: '1rem', padding: '0.85rem', background: 'var(--raised)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <p style={{ margin: 0, fontWeight: 600, fontSize: '0.875rem' }}>החלפת רמה (מנהל)</p>
                      <p className="hint" style={{ margin: '0.15rem 0 0', fontSize: '0.8125rem' }}>
                        {settings.tier === 'pro' ? 'מודל: Demucs htdemucs_ft (Meta)' : 'מודל: בסיסי (STFT masking)'}
                      </p>
                    </div>
                    <button className="ghost" onClick={onToggleTier} style={{ whiteSpace: 'nowrap' }}>
                      עבור ל{settings.tier === 'pro' ? 'בסיסי' : 'מקצועי'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="card" style={{ marginBottom: '1rem' }}>
              <label className="field">
                <span>{t('prefLang')}</span>
                <select value={lang} onChange={e => { const v = e.target.value; setLang(v); onUpdate('preferred_language', v) }}>
                  <option value="he">עברית</option>
                  <option value="en">English</option>
                </select>
              </label>

              <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'var(--raised)', borderRadius: 'var(--radius-sm)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={settings.email_opt_in} onChange={e => onUpdate('email_opt_in', e.target.checked)} />
                  <span style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{t('emailOptIn')}</span>
                </label>
                <p className="hint" style={{ margin: '0.35rem 0 0', fontSize: '0.8125rem' }}>
                  {t('emailOptInDesc')}
                </p>
              </div>

            </div>

            <form className="card" style={{ marginBottom: '1rem' }} onSubmit={onChangePassword}>
              <h3 style={{ marginTop: 0 }}>{t('changePw')}</h3>
              <label className="field"><span>{t('currentPw')}</span>
                <div className="password-field">
                  <input name="curPw" type={showCurPw ? 'text' : 'password'} autoComplete="current-password" required minLength={MIN_PASSWORD_LENGTH} />
                  <button type="button" className="password-toggle" onClick={() => setShowCurPw(!showCurPw)}
                    aria-label={showCurPw ? 'הסתר' : 'הצג'}>{showCurPw ? Icons.eyeOff : Icons.eye}</button>
                </div>
              </label>
              <label className="field"><span>{t('newPw')}</span>
                <div className="password-field">
                  <input name="newPw" type={showNewPw ? 'text' : 'password'} autoComplete="new-password" required minLength={MIN_PASSWORD_LENGTH} />
                  <button type="button" className="password-toggle" onClick={() => setShowNewPw(!showNewPw)}
                    aria-label={showNewPw ? 'הסתר' : 'הצג'}>{showNewPw ? Icons.eyeOff : Icons.eye}</button>
                </div>
              </label>
              <button className="btn" type="submit" disabled={pwBusy}>{pwBusy ? '...' : t('updatePw')}</button>
            </form>

            <div className="card danger-zone">
              <h3 style={{ marginTop: 0 }}>{t('dangerZone')}</h3>
              {!deleteConfirm ? (
                <button className="btn danger" onClick={() => setDeleteConfirm(true)}>{t('deleteAccountBtn')}</button>
              ) : (
                <>
                  <p style={{ color: 'var(--danger)', fontSize: '0.9375rem' }}>פעולה זו תמחק את החשבון שלך, כל השירים וכל הנתונים. לא ניתן לבטל.</p>
                  <div className="row">
                    <button className="btn danger" onClick={onDeleteAccount}>כן, מחק</button>
                    <button className="btn secondary" onClick={() => setDeleteConfirm(false)}>ביטול</button>
                  </div>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  )
}

function _getGoogleClientId() {
  const raw = document.querySelector('meta[name="google-client-id"]')?.content || ''
  if (!raw || raw.startsWith('%') || raw.length < 10) return null
  return raw
}

function AuthModal({ newAccount, setNewAccount, authError, setAuthError, authBusy, onSubmit, onGoogleAuth, onClose, t }) {
  const [showPw, setShowPw] = useState(false)
  const [googleReady, setGoogleReady] = useState(false)
  const googleBtnRef = useRef(null)
  const clientId = _getGoogleClientId()

  useEffect(() => {
    if (!clientId) return
    if (window.google?.accounts?.id && googleBtnRef.current) {
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', locale: 'he', width: '100%',
      })
      setGoogleReady(true)
      return
    }
    const existing = document.querySelector('script[src*="accounts.google.com/gsi/client"]')
    if (existing) return
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.onload = () => {
      if (!window.google?.accounts?.id) return
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp) => onGoogleAuth(resp.credential),
      })
      if (googleBtnRef.current) {
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', locale: 'he', width: '100%',
        })
        setGoogleReady(true)
      }
    }
    document.head.appendChild(script)
  }, [clientId, onGoogleAuth])

  return (
    <div className="modal" onClick={onClose}>
      <form className="auth" role="dialog" aria-modal="true"
        aria-label={newAccount ? t('authTitleNew') : t('authTitle')}
        onClick={e => e.stopPropagation()} onSubmit={onSubmit}>
        <h2>{newAccount ? t('authTitleNew') : t('authTitle')}</h2>
        {authError && <p className="error" role="alert">{authError}</p>}

        {clientId && <div ref={googleBtnRef} style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.75rem' }} />}

        {clientId && googleReady && <div className="auth-divider"><span>{t('or')}</span></div>}

        <label className="field"><span>{t('emailLabel')}</span><input name="email" type="email" autoComplete="username" required /></label>
        <label className="field"><span>{t('passwordLabel')}</span>
          <div className="password-field">
            <input name="password" type={showPw ? 'text' : 'password'}
              autoComplete={newAccount ? 'new-password' : 'current-password'} minLength={MIN_PASSWORD_LENGTH} required />
            <button type="button" className="password-toggle" onClick={() => setShowPw(!showPw)}
              aria-label={showPw ? 'hide' : 'show'}>{showPw ? Icons.eyeOff : Icons.eye}</button>
          </div>
        </label>
        <button className="btn full" type="submit" disabled={authBusy}>{authBusy ? '...' : newAccount ? t('signUp') : t('signIn')}</button>
        <p className="hint" style={{ textAlign: 'center' }}>
          {newAccount ? t('hasAccount') + ' ' : t('noAccount') + ' '}
          <button className="link" type="button" onClick={() => { setNewAccount(!newAccount); setAuthError('') }}>
            {newAccount ? t('signIn') : t('signUp')}
          </button>
        </p>
      </form>
    </div>
  )
}
