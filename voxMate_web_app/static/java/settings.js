// const input = document.getElementById("silence_threshold_input");
// const slider = document.getElementById("silence_threshold_slider");

// let baseValue = parseInt(input.value) || 0;

// // Slider → Input (offset from base)
// slider.addEventListener("input", () => {
//     const offset = parseInt(slider.value);
//     input.value = baseValue + offset;
// });

// // Input → Slider (reset slider, store new base)
// input.addEventListener("input", () => {
//     const val = parseInt(input.value, 10);
//     if (!isNaN(val)) {
//         baseValue = val;
//         slider.value = 0;  // Reset slider to center
//     }
// });

// function equalizeSectionHeights(sectionClass) {
//     const elements = document.querySelectorAll(sectionClass);
//     let maxHeight = 0;

//     elements.forEach(el => {
//         el.style.minHeight = ''; // reset
//         const h = el.offsetHeight;
//         if (h > maxHeight) maxHeight = h;
//     });

//     elements.forEach(el => {
//         el.style.minHeight = maxHeight + 'px';
//     });
//     }

//     // Run on DOM ready or window load:
//     window.addEventListener('load', () => {
//     equalizeSectionHeights('.section-title-desc');
//     equalizeSectionHeights('.section-current-setting');
//     equalizeSectionHeights('.section-input-controls');
//     });

function setupInputSliderPair(inputId, sliderId, options = {}) {
    const input = document.getElementById(inputId);
    const slider = document.getElementById(sliderId);
    if (!input || !slider) return;

    const mode = options.mode || 'offset'; // Default to offset

    // Apply optional range and step settings
    if (options.min !== undefined) slider.min = options.min;
    if (options.max !== undefined) slider.max = options.max;
    if (options.step !== undefined) slider.step = options.step;

    let baseValue = parseInt(input.value) || 0;

    if (mode === 'offset') {
        // Slider → Input (offset from base)
        slider.addEventListener("input", () => {
            const offset = parseInt(slider.value);
            input.value = baseValue + offset;
        });

        // Input → Slider (reset slider, store new base)
        input.addEventListener("input", () => {
            const val = parseInt(input.value, 10);
            if (!isNaN(val)) {
                baseValue = val;
                slider.value = 0;
            }
        });
    } else if (mode === 'direct') {
        // Slider → Input (direct value)
        slider.value = baseValue; // Set slider to match input at start
        slider.addEventListener("input", () => {
            input.value = slider.value;
        });

        // Input → Slider (update slider to match new value)
        input.addEventListener("input", () => {
            const val = parseInt(input.value, 10);
            if (!isNaN(val) && val >= slider.min && val <= slider.max) {
                slider.value = val;
            }
        });
    }
}

function equalizeSectionHeights(sectionClass) {
    const elements = document.querySelectorAll(sectionClass);
    let maxHeight = 0;

    elements.forEach(el => {
        el.style.minHeight = ''; // Reset
        const h = el.offsetHeight;
        if (h > maxHeight) maxHeight = h;
    });

    elements.forEach(el => {
        el.style.minHeight = maxHeight + 'px';
    });
}

window.addEventListener('load', () => {
    setupInputSliderPair("silence_threshold_input", "silence_threshold_slider", {
        min: -500,
        max: 500,
        step: 50,
        mode: 'offset' // default, but explicit
    });

    setupInputSliderPair("default_volume_input", "default_volume_slider", {
        min: 0,
        max: 100,
        step: 1,
        mode: 'direct'
    });

    equalizeSectionHeights('.section-title-desc');
    equalizeSectionHeights('.section-current-setting');
    equalizeSectionHeights('.section-input-controls');
});