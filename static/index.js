document.addEventListener("DOMContentLoaded", function (event) {
  resetButton.addEventListener("click", function () {
    // Reset sliders value to default

    slider_bright.value = 1;
    slider_contrast.value = 1;
    slider_steps.value = 16;
    slider_dither.value = 0.25;

    updateSliderValue(slider_bright, output_bright);
    updateSliderValue(slider_contrast, contrast_output);
    updateSliderValue(slider_steps, steps_output);
    updateSliderValue(slider_dither, dither_output);
  });
  // Get the sliders and their associated value elements
  const slider_bright = document.getElementById("brightness");
  const slider_contrast = document.getElementById("contrast");
  const slider_steps = document.getElementById("steps");
  const slider_dither = document.getElementById("dither_op");

  const output_bright = document.getElementById("brightness_output");
  const contrast_output = document.getElementById("contrast_output");
  const steps_output = document.getElementById("steps_output");
  const dither_output = document.getElementById("dither_output");

  // Function to update the slider values
  function updateSliderValue(slider, valueElement) {
    valueElement.textContent = slider.value;
  }

  // Event listener for opacity slider
  slider_bright.addEventListener("input", function () {
    updateSliderValue(slider_bright, output_bright);
  });

  // Event listener for contrast slider
  slider_contrast.addEventListener("input", function () {
    updateSliderValue(slider_contrast, contrast_output);
  });

  // Event listener for opacity slider
  slider_steps.addEventListener("input", function () {
    updateSliderValue(slider_steps, steps_output);
  });

  // Event listener for contrast slider
  slider_dither.addEventListener("input", function () {
    updateSliderValue(slider_dither, dither_output);
  });

  // Update initial slider values
  updateSliderValue(slider_bright, output_bright);
  updateSliderValue(slider_contrast, contrast_output);
  updateSliderValue(slider_steps, steps_output);
  updateSliderValue(slider_dither, dither_output);

  const select = document.getElementById("options-box");
  const option1 = document.getElementById("grayscale");
  const option2 = document.getElementById("colors");

  // Initially hide the select element
  select.style.display = "none";

  // Add event listeners to radio buttons
  option1.addEventListener("change", function () {
    if (option1.checked) {
      select.style.display = "none";
    }
  });

  option2.addEventListener("change", function () {
    if (option2.checked) {
      select.style.display = "block";
    }
  });
});
// script.js

function handleRadioChange() {
  const select = document.getElementById("options-box");
  const option1 = document.getElementById("grayscale");

  // Initially hide the select element
  select.style.display = option1.checked ? "none" : "block";
}
