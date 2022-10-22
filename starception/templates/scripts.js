/**
 * Setup "Reveal secret" feature.
 */
function bindSecretsReveal() {
    document.querySelectorAll('[data-reveal]').forEach(function (el) {
        el.addEventListener('click', function () {
            el.innerText = el.dataset.reveal;
        });
    });
}

/**
 * Setup "Hide vendor frame" feature.
 * @param {HTMLElement} block
 */
function bindVendorFramesToggle(block) {
    block.querySelectorAll('[data-vendor-frame-toggle]').forEach(toggleEl => {
        toggleEl.addEventListener('click', function (e) {
            const parent = e.target.closest('.frames');
            parent.querySelectorAll('.vendor').forEach(function (frame) {
                if (e.target.checked) {
                    frame.classList.add('hidden');
                } else {
                    frame.classList.remove('hidden');
                }
            });
        });
    });
}

/**
 * Bind exception block (aka. "Caused by")
 * @param {HTMLElement} block
 */
function bindExceptionBlocks(block) {
    block.querySelectorAll('[data-trace-toggle]').forEach(el => {
        el.addEventListener('click', () => {
            const target = block.querySelector(`[data-trace-target]`);
            if (target.classList.contains('collapsed')) {
                target.classList.remove('collapsed');
            } else {
                target.classList.add('collapsed');
            }
        });
    });
}

/**
 * Handle code block switching on frame stack item click.
 * @param {HTMLElement} block
 */
function bindCodeSnippets(block) {
    block.querySelectorAll('[data-code-toggle]').forEach(el => {
        el.addEventListener('click', () => {
            let current = block.querySelector('.snippet-wrapper.current');
            if (current) {
                current.classList.remove('current');
            }

            let frameIndex = el.dataset.frameIndex;
            let target = block.querySelector(`[data-snippet="${frameIndex}"]`);
            if (target) {
                target.classList.add('current');
            }

            let currentSwitch = block.querySelector('.frame.current');
            if (currentSwitch) {
                currentSwitch.classList.remove('current');
            }
            el.classList.add('current');
        });
    });
}

function bindThemeToggle() {
    // auto -> dark -> light -> auto
    document.querySelector('[data-theme-toggle]').addEventListener('click', () => {
        if (document.documentElement.classList.contains('auto')) {
            // transition from auto to dark
            applyColorTheme('dark');
            rememberTheme('dark');
        } else if (document.documentElement.classList.contains('dark')) {
            // transition from dark to light
            applyColorTheme('light');
            rememberTheme('light');
        } else {
            // transition from light to auto
            applyColorTheme('auto');
            rememberTheme('auto');
        }
    });
}

function prefersDarkTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function themeFollower(e) {
    if (!document.documentElement.classList.contains('auto')) return;
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.remove('light');
    document.documentElement.classList.add(e.matches ? 'dark' : 'light');
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeFollower);

function applyColorTheme(theme) {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.remove('light');
    document.documentElement.classList.add(theme);

    if (theme == 'auto') {
        document.documentElement.classList.add('auto');
        document.documentElement.classList.add(prefersDarkTheme() ? 'dark' : 'light');
    } else {
        document.documentElement.classList.remove('auto');
    }
}

function rememberTheme(theme) {
    localStorage.setItem('theme', theme);
}

function getRememberedTheme() {
    return localStorage.getItem('theme') || 'auto';
}

function restoreColorTheme() {
    let colorTheme = getRememberedTheme();
    applyColorTheme(colorTheme);
}

/**
 * Bind exception block features.
 * @param {HTMLElement} el
 */
function bindStackBlock(el) {
    restoreColorTheme();
    bindThemeToggle();
    bindVendorFramesToggle(el);
    bindExceptionBlocks(el);
    bindCodeSnippets(el);
    bindSecretsReveal();
}

function bindStackBlocks() {
    document.querySelectorAll('[data-stack-root]').forEach(bindStackBlock);
}

document.addEventListener('DOMContentLoaded', bindStackBlocks);
