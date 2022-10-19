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

/**
 * Bind exception block features.
 * @param {HTMLElement} el
 */
function bindStackBlock(el) {
    bindVendorFramesToggle(el);
    bindExceptionBlocks(el);
    bindCodeSnippets(el);
    bindSecretsReveal();
}

function bindStackBlocks() {
    document.querySelectorAll('[data-stack-root]').forEach(bindStackBlock);
}

document.addEventListener('DOMContentLoaded', bindStackBlocks);
