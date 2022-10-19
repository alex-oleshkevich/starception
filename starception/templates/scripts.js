Array.from(document.querySelectorAll('[id^="switch"]')).forEach(function (el) {
    el.addEventListener('click', function () {
        let traceIndex = el.dataset.traceTargetIndex;
        let traceElement = document.querySelector('#trace-target-' + traceIndex);
        let current = traceElement.querySelector('.snippet-wrapper.current');
        if (current) {
            current.classList.remove('current');
        }

        let frameIndex = el.dataset.frameIndex;
        let target = traceElement.querySelector('#snippet-' + frameIndex);
        if (target) {
            target.classList.add('current');
        }

        let currentSwitch = traceElement.querySelector('.frame.current');
        if (currentSwitch) {
            currentSwitch.classList.remove('current');
        }
        el.classList.add('current');
    });
});


Array.from(document.querySelectorAll('[data-reveal]')).forEach(function (el) {
    el.addEventListener('click', function () {
        el.innerText = el.dataset.reveal;
    });
});


document.querySelectorAll('[data-vendor-frame-toggle]').forEach(el => {
    el.addEventListener('click', function (e) {
        const parent = e.target.closest('.frames');
        Array.from(parent.querySelectorAll('.vendor')).forEach(function (frame) {
            if (e.target.checked) {
                frame.classList.add('hidden');
            } else {
                frame.classList.remove('hidden');
            }
        });
    });
});

document.querySelectorAll('[data-toggle-trace]').forEach(el => {
    el.addEventListener('click', () => {
        const index = el.dataset.traceIndex;
        const target = document.querySelector(`[data-trace-target="${index}"]`);
        if (target.classList.contains('collapsed')) {
            target.classList.remove('collapsed');
        } else {
            target.classList.add('collapsed');
        }
    });
})
