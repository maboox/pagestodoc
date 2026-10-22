const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const net = require('node:net');
const { spawn } = require('node:child_process');
const { chromium } = require('playwright');
const { default: AxeBuilder } = require('@axe-core/playwright');

async function main() {
    const root = path.resolve(__dirname, '..');
    const artifacts = path.join(root, 'test-results');
    await fs.mkdir(artifacts, { recursive: true });
    await fs.mkdir(path.join(artifacts, 'downloads'), { recursive: true });
    const port = await new Promise((resolve) => {
        const socket = net.createServer();
        socket.listen(0, '127.0.0.1', () => {
            const port = socket.address().port;
            socket.close(() => resolve(port));
        });
    });
    const origin = `http://127.0.0.1:${port}`;
    const python =
        process.env.PYTHON ||
        path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
    const server = spawn(python, ['app.py', '--port', String(port)], { cwd: root, windowsHide: true });
    let serverError = '';
    server.stderr.on('data', (chunk) => (serverError += chunk.toString()));
    server.on('error', (error) => (serverError += error.message));
    let browser;
    try {
        for (let attempt = 0; attempt < 100; attempt++) {
            try {
                if ((await fetch(origin)).ok) break;
            } catch {}
            if (attempt === 99) throw new Error(`Server did not start: ${serverError}`);
            await new Promise((resolve) => setTimeout(resolve, 100));
        }
        browser = await chromium.launch({
            headless: true,
            ...(process.env.PAGES_BROWSER_CHANNEL ? { channel: process.env.PAGES_BROWSER_CHANNEL } : {}),
            downloadsPath: path.join(artifacts, 'downloads'),
        });
        const context = await browser.newContext({
            viewport: { width: 1440, height: 1120 },
            acceptDownloads: true,
        });
        // The OS save dialog is outside Playwright's page surface. Exercise the
        // real fetch/stream path using a controlled writable destination.
        await context.addInitScript(() => {
            window.showSaveFilePicker = async () => ({
                createWritable: async () => {
                    window.savedZip = { bytes: 0, signature: '', closed: false, aborted: false };
                    return new WritableStream({
                        write(chunk) {
                            if (!window.savedZip.signature)
                                window.savedZip.signature = String.fromCharCode(...chunk.slice(0, 2));
                            window.savedZip.bytes += chunk.byteLength;
                        },
                        close() {
                            window.savedZip.closed = true;
                        },
                        abort() {
                            window.savedZip.aborted = true;
                        },
                    });
                },
            });
        });
        const page = await context.newPage();
        const errors = [],
            outbound = [];
        page.on('pageerror', (error) => errors.push(error.message));
        page.on('console', (message) => {
            if (message.type() === 'error') errors.push(message.text());
        });
        page.on('request', (request) => {
            if (!request.url().startsWith(origin + '/')) outbound.push(request.url());
        });
        const healthRequest = page.waitForResponse((response) => response.url().endsWith('/api/health'));
        await page.goto(origin);
        assert.equal((await healthRequest).status(), 200);
        await page.evaluate(() => document.fonts.ready);
        const capture = async (name) => {
            await page.evaluate(() => {
                document.activeElement?.blur();
                window.scrollTo(0, 0);
            });
            const destination = process.env.PAGES_SCREENSHOTS ? path.join(root, 'docs') : artifacts;
            await page.screenshot({ path: path.join(destination, `screenshot-${name}.png`), fullPage: true });
        };
        const accessibility = async (name) => {
            const result = await new AxeBuilder({ page })
                .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
                .analyze();
            await fs.writeFile(
                path.join(artifacts, `accessibility-${name}.json`),
                JSON.stringify(result.violations, null, 2)
            );
            assert.deepEqual(
                result.violations.map((item) => ({
                    id: item.id,
                    targets: item.nodes.map((node) => node.target),
                })),
                [],
                `${name}: accessibility violations`
            );
        };
        await capture('fa');
        await accessibility('fa');
        await page.locator('#languageBtn').click();
        assert.equal(await page.locator('html').getAttribute('dir'), 'ltr');
        await capture('en');
        await accessibility('en');
        await page.locator('#themeBtn').click();
        await capture('dark');
        await accessibility('dark');
        await page.locator('#themeBtn').click();
        await page.locator('#picker').setInputFiles([
            { name: 'Reference.pdf', mimeType: 'application/pdf', buffer: Buffer.from('Example PDF bytes') },
            { name: 'Notes.txt', mimeType: 'text/plain', buffer: Buffer.from('Example notes') },
        ]);
        await page.waitForFunction(() => !document.querySelector('#convertBtn').disabled);
        assert.equal(await page.locator('.file-list li').count(), 2);
        await page.locator('#convertBtn').click();
        await page.locator('#result').waitFor({ state: 'visible' });
        const archiveResponse = await page.request.get(
            new URL(await page.locator('#downloadBtn').getAttribute('href'), origin).href
        );
        assert.equal(archiveResponse.status(), 200);
        const archive = await archiveResponse.body();
        await fs.writeFile(path.join(artifacts, 'direct-output.zip'), archive);
        assert.equal(archive.subarray(0, 2).toString(), 'PK');
        await page.locator('#saveBtn').click();
        await page.waitForFunction(() => window.savedZip?.closed);
        assert.deepEqual(await page.evaluate(() => window.savedZip), {
            bytes: archive.length,
            signature: 'PK',
            closed: true,
            aborted: false,
        });
        if (process.env.PAGES_SKIP_NATIVE_DOWNLOAD === '1') {
            console.log(
                'Native attachment download explicitly skipped in this browser environment; direct stream verified.'
            );
        } else {
            const downloadRequest = page.waitForEvent('download');
            await page.locator('#downloadBtn').click();
            const download = await downloadRequest;
            assert.equal(await download.failure(), null, 'Browser download must complete');
            await download.saveAs(path.join(artifacts, 'browser-output.zip'));
            assert.equal(download.suggestedFilename(), 'pages-converter-output.zip');
        }
        await capture('result');
        await accessibility('result');
        // A filtered/truncated response must never be reported as a saved ZIP.
        await page.route('**/api/jobs/*/content', (route) =>
            route.fulfill({ status: 200, body: '', headers: { 'Content-Type': 'application/octet-stream' } })
        );
        await page.locator('#saveBtn').click();
        await page.waitForFunction(() => window.savedZip?.aborted);
        assert.equal(await page.evaluate(() => window.savedZip.closed), false);
        assert.equal(await page.locator('#status').getAttribute('class'), 'status error');
        await page.unroute('**/api/jobs/*/content');
        await page.reload();
        await page.locator('#result').waitFor({ state: 'visible' });
        await page.locator('#discardBtn').click();
        await page.locator('#result').waitFor({ state: 'hidden' });
        await page.setViewportSize({ width: 390, height: 844 });
        await page.locator('#languageBtn').click();
        await capture('mobile');
        await accessibility('mobile');
        for (const width of [320, 390, 760, 1024]) {
            await page.setViewportSize({ width, height: 844 });
            assert.equal(
                await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
                false,
                `Overflow at ${width}px`
            );
        }
        assert.deepEqual(errors, []);
        assert.deepEqual(outbound, [], 'No outbound requests while using the app');
        console.log(
            `UI passed: FA/EN, light/dark, accessibility, selection, ZIP stream, truncated-save rejection, reload recovery, deletion, responsive layout, no outbound requests. Native attachment: ${process.env.PAGES_SKIP_NATIVE_DOWNLOAD === '1' ? 'explicitly skipped' : 'verified'}.`
        );
    } finally {
        if (browser) await browser.close();
        server.kill();
    }
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
