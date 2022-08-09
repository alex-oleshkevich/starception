Array.from(document.querySelectorAll('[id^="switch"]')).forEach(function (el) {
    el.addEventListener('click', function () {
        var current = document.querySelector('.snippet-wrapper.current');
        if (current) {
            current.classList.remove('current');
        }

        var frameIndex = el.dataset.frameIndex;
        var target = document.querySelector('#snippet-' + frameIndex);
        if (target) {
            target.classList.add('current');
        }

        var currentSwitch = document.querySelector('.frame.current');
        if (currentSwitch) {
            currentSwitch.classList.remove('current');
        }
        el.classList.add('current');
    });
});
