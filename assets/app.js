'use strict';
const $ = (id) => document.getElementById(id);
const translations = {
    fa: {
        skip: 'رفتن به مبدل',
        brandCaption: 'از Pages به امکانات بیشتر',
        checking: 'در حال بررسی…',
        connected: 'مبدل آماده است',
        missing: 'نیاز به LibreOffice',
        offline: 'ارتباط برقرار نیست',
        eyebrow: 'فایل‌های شما. روی کامپیوتر شما.',
        hero1: 'Pages را ورق بزنید.',
        hero2: 'با Word ادامه بدهید.',
        heroDescription:
            'یک پوشه انتخاب کنید. فایل‌های Pages را به Word تبدیل کنید و همه‌چیز را با همان نظم، در یک ZIP تحویل بگیرید.',
        local: 'پردازش محلی',
        structure: 'حفظ ساختار پوشه‌ها',
        noAccount: 'بدون حساب کاربری',
        missingTitle: 'LibreOffice پیدا نشد',
        missingDescription:
            'برای تبدیل Pages، LibreOffice را نصب کنید و وضعیت را دوباره بررسی کنید. کپی فایل‌های دیگر همچنان ممکن است.',
        install: 'دریافت LibreOffice',
        checkAgain: 'بررسی دوباره',
        workspaceLabel: 'میز کار شما',
        workspaceTitle: 'یک شروع مرتب',
        selectStep: 'انتخاب',
        convertStep: 'تبدیل',
        downloadStep: 'دریافت',
        dropTitle: 'فایل‌ها را اینجا رها کنید',
        dropDescription: 'یک فایل، چند فایل یا یک پوشهٔ کامل؛ انتخاب با شماست.',
        chooseFolder: 'انتخاب پوشه',
        chooseFiles: 'انتخاب فایل‌ها',
        limits: 'تا ۱ گیگابایت · حداکثر ۵۰۰ فایل',
        clear: 'پاک کردن همه',
        readyTitle: 'همه‌چیز آماده است',
        expiry: 'لینک تا یک ساعت، در همین اجرای برنامه فعال است.',
        downloadZip: 'دریافت ZIP',
        saveZip: 'ذخیره ZIP',
        saving: 'در حال ذخیره…',
        saved: 'ZIP در محل انتخاب‌شده ذخیره شد.',
        saveError:
            'ذخیره کامل نشد. فضای دیسک و دسترسی محل انتخاب‌شده را بررسی کنید یا از لینک دریافت ZIP استفاده کنید.',
        convert: 'تبدیل و آماده‌سازی ZIP',
        cancel: 'لغو پردازش',
        discard: 'حذف خروجی محلی',
        privateNote: 'فایل‌ها در همین دستگاه پردازش می‌شوند؛ بدون ارسال به فضای ابری.',
        guideLabel: 'ساده، از ابتدا تا انتها',
        guideTitle: 'نظم فایل‌ها حفظ می‌شود.',
        guideDescription: 'فقط Pages تغییر می‌کند. فایل‌های دیگر با محتوای اصلی خود در خروجی قرار می‌گیرند.',
        example: 'نمونه',
        feature1: 'نام‌های تکراری، بدون بازنویسی',
        feature2: 'نگهداری اصل فایل در صورت خطا',
        feature3: 'گزارش تبدیل در هر ZIP',
        tipTitle: 'یک نکتهٔ کوچک',
        tipDescription:
            'چیدمان‌های پیچیده و بعضی فونت‌ها ممکن است تغییر کنند. فایل Word خروجی را پیش از استفاده نهایی بررسی کنید.',
        faqTitle: 'چه فایل‌هایی پشتیبانی می‌شوند؟',
        faqAnswer:
            'فایل‌های تکیِ .pages که LibreOffice پشتیبانی کند، به .docx تبدیل می‌شوند. پوشه‌های بسته‌ای Pages را ابتدا در macOS به فایل تکی ذخیره کنید. پوشه‌های خالی در انتخاب مرورگر منتقل نمی‌شوند.',
        footer: 'ساخته‌شده برای فایل‌های شما، با احترام به حریم خصوصی.',
        openSource: 'متن‌باز، برای همه',
        selected: (n) => `${n} فایل انتخاب شده`,
        pages: (n) => `${n} فایل Pages`,
        copies: (n) => `${n} کپی مستقیم`,
        shown: (n) => `برای سرعت بیشتر، فقط ${n} فایل اول نمایش داده می‌شود. همه فایل‌ها پردازش می‌شوند.`,
        remove: 'حذف فایل',
        scanning: 'در حال خواندن پوشه…',
        uploading: 'انتقال محلی فایل‌ها…',
        processing: 'در حال تبدیل فایل‌ها…',
        packing: 'در حال ساخت ZIP…',
        queued: 'در انتظار پردازش…',
        done: 'پردازش کامل شد',
        cancelled: 'پردازش لغو شد و فایل‌های موقت حذف شدند.',
        converted: (n) => `تبدیل: ${n}`,
        copied: (n) => `کپی: ${n}`,
        failed: (n) => `خطا: ${n}`,
        results: (a, b) => `${a} تبدیل، ${b} کپی مستقیم؛ گزارش داخل ZIP است.`,
        partial: (n) =>
            `${n} فایل تبدیل نشد. اصل فایل‌ها در ZIP نگهداری شده‌اند؛ علت را در pages-converter-report.json ببینید.`,
        empty: 'فایلی در این انتخاب پیدا نشد.',
        duplicates: 'فایل‌های تکراری قبلاً انتخاب شده‌اند.',
        deleted: 'خروجی محلی حذف شد.',
        cancelling: 'در حال لغو…',
        network: 'ارتباط با برنامه قطع شد. وضعیت دوباره بررسی می‌شود…',
        chooseFirst: 'ابتدا فایل یا پوشه‌ای انتخاب کنید.',
        theme: 'تغییر پوسته',
        progress: 'پیشرفت پردازش',
        selectedLabel: 'فایل‌های انتخاب شده',
        stepsLabel: 'مراحل تبدیل',
        folderUnsupported:
            'این مرورگر انتخاب پوشه را پشتیبانی نمی‌کند. از Chrome یا Edge استفاده کنید یا فایل‌ها را انتخاب کنید.',
        errors: {
            too_large: 'حجم کل باید حداکثر ۱ گیگابایت باشد.',
            too_many: 'حداکثر ۵۰۰ فایل را در هر نوبت انتخاب کنید.',
            invalid_path:
                'یک مسیر نامعتبر یا نام ناسازگار با ویندوز وجود دارد. نام‌ها نباید CON، AUX و مانند آن باشند یا شامل < > : " | ? * باشند. مسیرهای بسیار طولانی را کوتاه کنید.',
            invalid_manifest: 'فهرست فایل‌ها معتبر نیست. فایل‌ها را دوباره انتخاب کنید.',
            invalid_request: 'درخواست کامل یا معتبر نبود. دوباره تلاش کنید.',
            busy: 'یک پردازش دیگر فعال است. تا پایان آن صبر کنید.',
            storage_full:
                'سه خروجی محلی نگهداری شده است. خروجی‌های قبلی را از تب‌های دیگر حذف کنید یا برنامه را دوباره اجرا کنید.',
            session_expired: 'نشست برنامه تغییر کرده است. این صفحه را دوباره بارگذاری کنید.',
            job_expired: 'این خروجی دیگر موجود نیست. فایل‌ها را دوباره انتخاب و پردازش کنید.',
            processing_failed: 'پردازش کامل نشد؛ فضای آزاد دیسک و دسترسی پوشه موقت را بررسی کنید.',
            server_error: 'خطای داخلی رخ داد. دوباره تلاش کنید و فضای آزاد دیسک را بررسی کنید.',
            download_busy: 'دانلود هنوز فعال است. پس از پایان آن دوباره تلاش کنید.',
            read_failed: 'خواندن یکی از پوشه‌ها ممکن نشد. پوشه را با دکمه انتخاب کنید.',
            network: 'ارتباط با برنامه ممکن نیست. باز بودن برنامه را بررسی کنید.',
        },
    },
    en: {
        skip: 'Skip to converter',
        brandCaption: 'A new chapter for your documents',
        checking: 'Checking converter…',
        connected: 'Converter ready',
        missing: 'LibreOffice required',
        offline: 'Connection unavailable',
        eyebrow: 'YOUR FILES. YOUR COMPUTER.',
        hero1: 'Turn the Pages.',
        hero2: 'Keep the possibilities.',
        heroDescription:
            'Choose a folder. Turn Apple Pages documents into Word files and get everything back in one neatly organized ZIP.',
        local: 'Local processing',
        structure: 'Folder structure intact',
        noAccount: 'No account needed',
        missingTitle: 'LibreOffice not found',
        missingDescription:
            'Install LibreOffice to convert Pages files, then check again. You can still copy other file types.',
        install: 'Get LibreOffice',
        checkAgain: 'Check again',
        workspaceLabel: 'YOUR WORKSPACE',
        workspaceTitle: 'Start with a clean slate',
        selectStep: 'Select',
        convertStep: 'Convert',
        downloadStep: 'Download',
        dropTitle: 'Drop your files right here',
        dropDescription: 'One document, a handful of files, or a whole folder. Your call.',
        chooseFolder: 'Choose folder',
        chooseFiles: 'Choose files',
        limits: 'Up to 1 GiB · 500 files per batch',
        clear: 'Clear all',
        readyTitle: 'All wrapped up',
        expiry: 'Available for one hour while this app stays open.',
        downloadZip: 'Download ZIP',
        saveZip: 'Save ZIP',
        saving: 'Saving…',
        saved: 'ZIP saved to your chosen location.',
        saveError:
            'Saving did not finish. Check disk space and folder permissions, or use the Download ZIP link.',
        convert: 'Convert & prepare ZIP',
        cancel: 'Cancel processing',
        discard: 'Delete local output',
        privateNote: 'Files are processed on this device, without a cloud upload.',
        guideLabel: 'A LITTLE ORDER GOES A LONG WAY',
        guideTitle: 'Same folders. A fresh format.',
        guideDescription: 'Only Pages files change. Everything else comes along with its original contents.',
        example: 'Example',
        feature1: 'Duplicate names, without overwrites',
        feature2: 'Originals kept if conversion fails',
        feature3: 'Conversion report in every ZIP',
        tipTitle: 'A little heads-up',
        tipDescription:
            'Complex layouts and some fonts may change. Give your converted Word documents a quick review before using them.',
        faqTitle: 'Which files are supported?',
        faqAnswer:
            'Single .pages files supported by LibreOffice convert to .docx. Save Pages package folders as single files on macOS first. Browser folder selection cannot include empty directories.',
        footer: 'Made for your documents. Mindful of your privacy.',
        openSource: 'Open source. Open to everyone.',
        selected: (n) => `${n} files selected`,
        pages: (n) => `${n} Pages files`,
        copies: (n) => `${n} copied as-is`,
        shown: (n) => `Showing the first ${n} files for performance. Every selected file will be processed.`,
        remove: 'Remove file',
        scanning: 'Reading folder…',
        uploading: 'Transferring files locally…',
        processing: 'Converting your documents…',
        packing: 'Putting your ZIP together…',
        queued: 'Waiting to start…',
        done: 'Processing complete',
        cancelled: 'Processing cancelled. Temporary files deleted.',
        converted: (n) => `Converted: ${n}`,
        copied: (n) => `Copied: ${n}`,
        failed: (n) => `Failed: ${n}`,
        results: (a, b) => `${a} converted, ${b} copied as-is. A report is included.`,
        partial: (n) =>
            `${n} files could not be converted. Their originals are included. See pages-converter-report.json in the ZIP for details.`,
        empty: 'No files found in this selection.',
        duplicates: 'These files are already selected.',
        deleted: 'Local output deleted.',
        cancelling: 'Cancelling…',
        network: 'Connection interrupted. Checking the job again…',
        chooseFirst: 'Choose some files or a folder first.',
        theme: 'Switch color theme',
        progress: 'Conversion progress',
        selectedLabel: 'Selected files',
        stepsLabel: 'Conversion steps',
        folderUnsupported:
            'Folder selection is unavailable in this browser. Use Chrome or Edge, or choose individual files.',
        errors: {
            too_large: 'The total size must be at most 1 GiB.',
            too_many: 'Choose at most 500 files per batch.',
            invalid_path:
                'A path is invalid or incompatible with Windows. Avoid reserved names such as CON or AUX, characters < > : " | ? *, and very long paths.',
            invalid_manifest: 'The file list is invalid. Select your files again.',
            invalid_request: 'The request was incomplete or invalid. Please try again.',
            busy: 'Another batch is running. Wait for it to finish.',
            storage_full:
                'Three local results are retained. Delete older results in other tabs, or restart the app.',
            session_expired: 'The app session changed. Reload this page.',
            job_expired: 'This output is no longer available. Select and process the files again.',
            processing_failed:
                'Processing did not finish. Check free disk space and temporary folder access.',
            server_error: 'An internal error occurred. Check free disk space and try again.',
            download_busy: 'A download is still active. Try again when it finishes.',
            read_failed: 'A folder could not be read. Use the folder selection button.',
            network: 'Could not reach the app. Check that it is still running.',
        },
    },
};
const storage = {
    get(key) {
        try {
            return sessionStorage.getItem(key);
        } catch {
            return null;
        }
    },
    set(key, value) {
        try {
            value === null ? sessionStorage.removeItem(key) : sessionStorage.setItem(key, value);
        } catch {
            /* Private browsing may block storage. */
        }
    },
};
const preferences = {
    get(key) {
        try {
            return localStorage.getItem(key);
        } catch {
            return null;
        }
    },
    set(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch {
            /* Preferences are optional. */
        }
    },
};
let lang = preferences.get('pages-language') === 'en' ? 'en' : 'fa';
let theme =
    preferences.get('pages-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
let entries = [],
    busy = false,
    scanning = false,
    saving = false,
    health = null,
    job = null,
    lastProgress = null,
    uploadPercent = 0,
    cancelling = false,
    pollGeneration = 0;
const token = document.querySelector('meta[name="pages-token"]').content;
const isPages = (name) => name.toLowerCase().endsWith('.pages');
const t = (key) => translations[lang][key];
const number = (value) => new Intl.NumberFormat(lang === 'fa' ? 'fa-IR' : 'en-US').format(value);
const size = (bytes) =>
    bytes < 1024
        ? `${bytes} B`
        : bytes < 1024 ** 2
          ? `${(bytes / 1024).toFixed(1)} KiB`
          : bytes < 1024 ** 3
            ? `${(bytes / 1024 ** 2).toFixed(1)} MiB`
            : `${(bytes / 1024 ** 3).toFixed(2)} GiB`;
const icon = (name) => {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('icon');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS(svg.namespaceURI, 'use');
    use.setAttribute('href', `/assets/icons.svg#${name}`);
    svg.append(use);
    return svg;
};
function show(message, kind = 'info') {
    $('status').textContent = message;
    $('status').className = `status ${kind}`;
    $('status').hidden = false;
}
function error(code) {
    return translations[lang].errors[code] || translations[lang].errors.server_error;
}
function hideStatus() {
    $('status').hidden = true;
}
function applyTheme() {
    document.documentElement.dataset.theme = theme;
    $('themeIcon').setAttribute('href', `/assets/icons.svg#${theme === 'dark' ? 'sun' : 'moon'}`);
    $('themeBtn').setAttribute('aria-label', t('theme'));
}
function setLanguage() {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'fa' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-i18n]').forEach((node) => (node.textContent = t(node.dataset.i18n)));
    $('languageBtn').textContent = lang === 'fa' ? 'EN' : 'فا';
    $('languageBtn').setAttribute('aria-label', lang === 'fa' ? 'Switch to English' : 'تغییر زبان به فارسی');
    $('progressTrack').setAttribute('aria-label', t('progress'));
    $('progressBox').setAttribute('aria-label', t('progress'));
    $('selection').setAttribute('aria-label', t('selectedLabel'));
    document.querySelector('.steps').setAttribute('aria-label', t('stepsLabel'));
    applyTheme();
    render();
    renderHealth();
    if (lastProgress) updateProgress(lastProgress);
    hideStatus();
}
function renderHealth() {
    const state = health ? (health.converterAvailable ? 'connected' : 'missing') : 'offline';
    $('connectionText').textContent = t(state);
    $('connection').className = `connection ${health?.converterAvailable ? 'ready' : 'offline'}`;
    $('dependencyNotice').hidden = !!health?.converterAvailable || !health;
}
function controls() {
    const locked = busy || scanning || saving;
    $('picker').disabled = locked;
    $('folderPicker').disabled = locked;
    $('filesBtn').disabled = locked;
    $('folderBtn').disabled = locked;
    $('clearBtn').disabled = locked;
    $('dropZone').classList.toggle('busy', locked);
    $('convertBtn').disabled =
        locked ||
        !entries.length ||
        !health ||
        (entries.some((e) => isPages(e.path)) && !health.converterAvailable);
    $('convertText').textContent = scanning
        ? t('scanning')
        : busy
          ? t(lastProgress?.status === 'uploading' ? 'uploading' : 'processing')
          : t('convert');
    $('cancelBtn').hidden = !busy || !job;
    $('cancelBtn').disabled = cancelling;
    $('cancelBtn').textContent = t(cancelling ? 'cancelling' : 'cancel');
    $('saveBtn').disabled = saving;
    $('saveText').textContent = t(saving ? 'saving' : 'saveZip');
    $('discardBtn').disabled = saving;
    $('downloadBtn').setAttribute('aria-disabled', String(saving));
    document.querySelectorAll('.remove-file').forEach((button) => (button.disabled = locked));
}
function render() {
    const pages = entries.filter((e) => isPages(e.path)).length;
    $('selection').hidden = !entries.length;
    $('selectionCount').textContent = t('selected')(number(entries.length));
    $('pagesCount').textContent = t('pages')(number(pages));
    $('copyCount').textContent = t('copies')(number(entries.length - pages));
    $('totalSize').textContent = size(entries.reduce((sum, e) => sum + e.file.size, 0));
    $('fileList').replaceChildren();
    entries.slice(0, 100).forEach((entry, index) => {
        const li = document.createElement('li'),
            symbol = document.createElement('span'),
            name = document.createElement('bdi'),
            bytes = document.createElement('span'),
            remove = document.createElement('button');
        symbol.className = `file-icon ${isPages(entry.path) ? 'pages' : ''}`;
        symbol.append(icon('file-text'));
        name.className = 'file-name';
        name.dir = 'ltr';
        name.textContent = entry.path;
        name.title = entry.path;
        bytes.className = 'file-size';
        bytes.dir = 'ltr';
        bytes.textContent = size(entry.file.size);
        remove.type = 'button';
        remove.className = 'remove-file';
        remove.setAttribute('aria-label', `${t('remove')}: ${entry.path}`);
        remove.append(icon('x'));
        remove.addEventListener('click', async () => {
            if (busy || scanning) return;
            if (!(await forgetResult())) return;
            entries.splice(index, 1);
            render();
            hideStatus();
        });
        li.append(symbol, name, bytes, remove);
        $('fileList').append(li);
    });
    $('listNote').hidden = entries.length <= 100;
    $('listNote').textContent = t('shown')(number(100));
    controls();
}
function clearResult() {
    job = null;
    lastProgress = null;
    storage.set('pages-job', null);
    $('result').hidden = true;
    $('discardBtn').hidden = true;
    $('progressBox').hidden = true;
    $('downloadBtn').removeAttribute('href');
    setStep(1);
}
async function forgetResult() {
    if (saving) return false;
    if (!job) return true;
    try {
        await api(`/api/jobs/${job}`, { method: 'DELETE' });
        clearResult();
        return true;
    } catch (exc) {
        show(error(exc.message), 'error');
        return false;
    }
}
function setStep(step) {
    [1, 2, 3].forEach((i) => {
        $(`step${i}`).className = i === step ? 'active' : i < step ? 'complete' : '';
        if (i === step) $(`step${i}`).setAttribute('aria-current', 'step');
        else $(`step${i}`).removeAttribute('aria-current');
    });
}
async function add(incoming) {
    if (busy) return;
    if (!incoming.length) {
        show(t('empty'));
        return;
    }
    const seen = new Set(entries.map((e) => `${e.path}\0${e.file.size}\0${e.file.lastModified}`));
    const next = [...entries];
    for (const entry of incoming) {
        const key = `${entry.path}\0${entry.file.size}\0${entry.file.lastModified}`;
        if (!seen.has(key)) {
            seen.add(key);
            next.push(entry);
        }
    }
    if (next.length > 500) {
        show(error('too_many'), 'error');
        return;
    }
    if (next.reduce((sum, e) => sum + e.file.size, 0) > 1024 ** 3) {
        show(error('too_large'), 'error');
        return;
    }
    if (next.length === entries.length) {
        show(t('duplicates'));
        return;
    }
    if (!(await forgetResult())) return;
    entries = next;
    render();
    hideStatus();
}
async function api(path, options = {}) {
    const controller = new AbortController(),
        timer = setTimeout(() => controller.abort(), 15000);
    try {
        const response = await fetch(path, {
            ...options,
            signal: controller.signal,
            cache: 'no-store',
            headers: { 'X-Pages-Token': token, ...options.headers },
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'server_error');
        return data;
    } catch (exc) {
        if (exc instanceof TypeError || exc.name === 'AbortError') throw new Error('network');
        throw exc;
    } finally {
        clearTimeout(timer);
    }
}
async function checkHealth() {
    try {
        health = await api('/api/health');
        renderHealth();
        controls();
    } catch (exc) {
        health = null;
        renderHealth();
        controls();
        show(error(exc.message), 'error');
    }
}
function updateProgress(p) {
    lastProgress = p;
    const percent =
        p.status === 'uploading' ? uploadPercent : p.total ? Math.floor((p.processed * 100) / p.total) : 0;
    $('progressBox').hidden = false;
    $('progressTitle').textContent = t(
        p.status === 'done'
            ? 'done'
            : ['packing', 'queued', 'uploading'].includes(p.status)
              ? p.status
              : 'processing'
    );
    $('percent').textContent = `${number(percent)}%`;
    $('progressBar').style.width = `${percent}%`;
    $('progressTrack').setAttribute('aria-valuenow', String(percent));
    $('currentFile').textContent = p.current || '';
    $('convertedStat').textContent = t('converted')(number(p.converted || 0));
    $('copiedStat').textContent = t('copied')(number(p.copied || 0));
    $('failedStat').textContent = t('failed')(number(p.failed || 0));
    controls();
    if (p.status === 'done') {
        $('result').hidden = false;
        $('resultDescription').textContent = t('results')(number(p.converted), number(p.copied));
        $('downloadBtn').href = `/api/jobs/${job}/download`;
        const canSave = typeof window.showSaveFilePicker === 'function';
        $('saveBtn').hidden = !canSave;
        $('downloadBtn').className = canSave ? 'text-button' : 'button yellow';
        $('discardBtn').hidden = false;
        setStep(3);
    }
}
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
// A native picker streams directly to the chosen file, without a ZIP-sized Blob.
$('saveBtn').addEventListener('click', async () => {
    if (!job || saving) return;
    let response, writable;
    try {
        const handle = await window.showSaveFilePicker({
            suggestedName: 'pages-converter-output.zip',
            types: [{ description: 'ZIP archive', accept: { 'application/zip': ['.zip'] } }],
        });
        saving = true;
        controls();
        hideStatus();
        response = await fetch(`/api/jobs/${job}/content`, { cache: 'no-store' });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'server_error');
        }
        writable = await handle.createWritable();
        const expected = Number(response.headers.get('Content-Length'));
        let received = 0;
        const counter = new TransformStream({
            transform(chunk, controller) {
                received += chunk.byteLength;
                controller.enqueue(chunk);
            },
        });
        await response.body.pipeThrough(counter).pipeTo(writable, { preventClose: true });
        if (!received || (expected && expected !== received)) throw new Error('incomplete_save');
        const writer = writable.getWriter();
        try {
            await writer.close();
        } finally {
            writer.releaseLock();
        }
        show(t('saved'), 'success');
    } catch (exc) {
        if (writable) await writable.abort().catch(() => {});
        if (response?.body && !response.body.locked) await response.body.cancel().catch(() => {});
        if (exc.name !== 'AbortError')
            show(translations[lang].errors[exc.message] || t('saveError'), 'error');
    } finally {
        saving = false;
        controls();
    }
});
$('downloadBtn').addEventListener('click', (event) => {
    if (saving) event.preventDefault();
});
async function poll(key) {
    const generation = ++pollGeneration;
    busy = true;
    setStep(2);
    controls();
    let failures = 0;
    try {
        while (generation === pollGeneration) {
            let p;
            try {
                p = await api(`/api/jobs/${key}`);
                if (failures) hideStatus();
                failures = 0;
            } catch (exc) {
                if (exc.message !== 'network') throw exc;
                failures++;
                show(t('network'), 'error');
                await wait(Math.min(5000, failures * 1000));
                continue;
            }
            if (generation !== pollGeneration) return;
            updateProgress(p);
            if (p.status === 'done') {
                if (p.failed) show(t('partial')(number(p.failed)), 'warning');
                break;
            }
            if (p.status === 'error') throw new Error(p.error || 'processing_failed');
            if (p.status === 'cancelled') {
                clearResult();
                show(t('cancelled'));
                break;
            }
            await wait(600);
        }
    } catch (exc) {
        show(error(exc.message), 'error');
        if (['job_expired', 'session_expired'].includes(exc.message)) clearResult();
        else $('discardBtn').hidden = false;
    } finally {
        if (generation === pollGeneration) {
            busy = false;
            cancelling = false;
            controls();
        }
    }
}
function upload(form) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/jobs');
        xhr.setRequestHeader('X-Pages-Token', token);
        xhr.timeout = 15 * 60 * 1000;
        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                uploadPercent = Math.floor((event.loaded * 100) / event.total);
                updateProgress({ status: 'uploading', total: entries.length, processed: 0 });
            }
        };
        xhr.onerror = () => reject(new Error('network'));
        xhr.ontimeout = () => reject(new Error('network'));
        xhr.onload = () => {
            try {
                const data = JSON.parse(xhr.responseText);
                xhr.status === 202 ? resolve(data) : reject(new Error(data.error || 'server_error'));
            } catch {
                reject(new Error('server_error'));
            }
        };
        xhr.send(form);
    });
}
$('convertBtn').addEventListener('click', async () => {
    if (busy || scanning || !entries.length) return;
    if (!(await forgetResult())) return;
    hideStatus();
    busy = true;
    uploadPercent = 0;
    setStep(2);
    updateProgress({ status: 'uploading', total: entries.length, processed: 0 });
    const form = new FormData();
    form.append('manifest', JSON.stringify(entries.map((e) => e.path)));
    entries.forEach((e) => form.append('files', e.file, e.file.name));
    try {
        const started = await upload(form);
        job = started.job;
        storage.set('pages-job', job);
        await poll(job);
    } catch (exc) {
        busy = false;
        show(error(exc.message), 'error');
        controls();
    }
});
$('cancelBtn').addEventListener('click', async () => {
    if (!job || cancelling) return;
    cancelling = true;
    controls();
    try {
        await api(`/api/jobs/${job}`, { method: 'DELETE' });
    } catch (exc) {
        cancelling = false;
        controls();
        show(error(exc.message), 'error');
    }
});
$('discardBtn').addEventListener('click', async () => {
    if (await forgetResult()) show(t('deleted'), 'success');
});
$('clearBtn').addEventListener('click', async () => {
    if (busy || scanning) return;
    if (!(await forgetResult())) return;
    entries = [];
    render();
    hideStatus();
});
$('filesBtn').addEventListener('click', () => $('picker').click());
$('folderBtn').addEventListener('click', () => {
    if ('webkitdirectory' in $('folderPicker')) $('folderPicker').click();
    else show(t('folderUnsupported'), 'error');
});
for (const [id, relative] of [
    ['picker', false],
    ['folderPicker', true],
])
    $(id).addEventListener('change', async (event) => {
        if (scanning || busy) return;
        scanning = true;
        controls();
        try {
            await add(
                [...event.target.files].map((file) => ({
                    file,
                    path: relative ? file.webkitRelativePath || file.name : file.name,
                }))
            );
        } finally {
            event.target.value = '';
            scanning = false;
            controls();
        }
    });
async function readEntry(entry, prefix, result, depth = 0) {
    if (depth > 40) throw new Error('invalid_path');
    if (result.length >= 500) throw new Error('too_many');
    if (entry.isFile) {
        const file = await new Promise((resolve, reject) => entry.file(resolve, reject));
        result.push({ file, path: prefix + file.name });
    } else if (entry.isDirectory) {
        const reader = entry.createReader();
        while (true) {
            const children = await new Promise((resolve, reject) => reader.readEntries(resolve, reject));
            if (!children.length) break;
            for (const child of children)
                await readEntry(child, `${prefix}${entry.name}/`, result, depth + 1);
        }
    }
}
const drop = $('dropZone');
['dragenter', 'dragover'].forEach((name) =>
    drop.addEventListener(name, (event) => {
        event.preventDefault();
        if (!busy && !scanning) drop.classList.add('drag');
    })
);
['dragleave', 'drop'].forEach((name) =>
    drop.addEventListener(name, (event) => {
        event.preventDefault();
        drop.classList.remove('drag');
    })
);
drop.addEventListener('drop', async (event) => {
    if (busy || scanning) return;
    const items = [...(event.dataTransfer.items || [])].filter((item) => item.kind === 'file'),
        roots = items.map((item) => item.webkitGetAsEntry?.());
    const flat = [...event.dataTransfer.files];
    scanning = true;
    controls();
    try {
        const found = [];
        if (roots.length && roots.every(Boolean)) {
            for (const root of roots) await readEntry(root, '', found);
        } else found.push(...flat.map((file) => ({ file, path: file.name })));
        await add(found);
    } catch (exc) {
        show(
            error(['too_many', 'invalid_path'].includes(exc.message) ? exc.message : 'read_failed'),
            'error'
        );
    } finally {
        scanning = false;
        controls();
    }
});
window.addEventListener('dragover', (event) => event.preventDefault());
window.addEventListener('drop', (event) => event.preventDefault());
$('languageBtn').addEventListener('click', () => {
    lang = lang === 'fa' ? 'en' : 'fa';
    preferences.set('pages-language', lang);
    setLanguage();
});
$('themeBtn').addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    preferences.set('pages-theme', theme);
    applyTheme();
});
$('retryHealth').addEventListener('click', () => {
    hideStatus();
    checkHealth();
});
window.addEventListener('beforeunload', (event) => {
    if ((busy && !job) || scanning || saving) {
        event.preventDefault();
        event.returnValue = '';
    }
});
setLanguage();
setStep(1);
checkHealth();
const restored = storage.get('pages-job');
if (restored && /^[a-f0-9]{32}$/.test(restored)) {
    job = restored;
    poll(restored);
}
