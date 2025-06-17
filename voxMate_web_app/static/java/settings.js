const input = document.getElementById("silence_threshold_input");
const slider = document.getElementById("silence_threshold_slider");

let baseValue = parseInt(input.value) || 0;

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
        slider.value = 0;  // Reset slider to center
    }
});

function equalizeSectionHeights(sectionClass) {
    const elements = document.querySelectorAll(sectionClass);
    let maxHeight = 0;

    elements.forEach(el => {
        el.style.minHeight = ''; // reset
        const h = el.offsetHeight;
        if (h > maxHeight) maxHeight = h;
    });

    elements.forEach(el => {
        el.style.minHeight = maxHeight + 'px';
    });
    }

    // Run on DOM ready or window load:
    window.addEventListener('load', () => {
    equalizeSectionHeights('.section-title-desc');
    equalizeSectionHeights('.section-current-setting');
    equalizeSectionHeights('.section-input-controls');
    });