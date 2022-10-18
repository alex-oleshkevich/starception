Array.from(document.querySelectorAll('[id^="switch"]')).forEach(function (el) {
    el.addEventListener('click', function () {
        var traceIndex = el.dataset.traceTargetIndex;
        var traceElement = document.querySelector('#trace-target-' + traceIndex);
        var current = traceElement.querySelector('.snippet-wrapper.current');
        if (current) {
            current.classList.remove('current');
        }

        var frameIndex = el.dataset.frameIndex;
        var target = traceElement.querySelector('#snippet-' + frameIndex);
        if (target) {
            target.classList.add('current');
        }

        var currentSwitch = traceElement.querySelector('.frame.current');
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


document.querySelectorAll('.vendor-frames-toggle').forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
        var traceIndex = toggle.dataset.traceTargetIndex;
        var traceElement = document.querySelector('#trace-target-' + traceIndex);
        Array.from(traceElement.querySelectorAll('.frames .vendor')).forEach(function (frame) {
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
