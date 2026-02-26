document.addEventListener("DOMContentLoaded", function (event) {
  // Get the sliders and their associated value elements
  const slider_bright = document.getElementById("brightness");
  const slider_contrast = document.getElementById("contrast");
  const slider_steps = document.getElementById("steps");
  const slider_dither = document.getElementById("dither_op");
  const slider_size = document.getElementById("pixel_size");

  const output_bright = document.getElementById("brightness_output");
  const contrast_output = document.getElementById("contrast_output");
  const steps_output = document.getElementById("steps_output");
  const dither_output = document.getElementById("dither_output");
  const size_output = document.getElementById("pixel_output");


  // Function to update the slider values
  function updateSliderValue(slider, valueElement) {
    valueElement.textContent = slider.value;
  }

  function updateSliderPercentage(slider,valueElement) {
      valueElement.textContent = (slider.value * 100) -100 + "%"
  }

  function updateDitherSlider(slider, valueElement) {
    valueElement.textContent = slider.value * 100 + "%";
  }

  // Event listener for opacity slider
  slider_bright.addEventListener("input", function () {
    updateSliderPercentage(slider_bright, output_bright);
  });

  // Event listener for contrast slider
  slider_contrast.addEventListener("input", function () {
    updateSliderPercentage(slider_contrast, contrast_output);
  });

  // Event listener for steps slider
  slider_steps.addEventListener("input", function () {
    updateSliderValue(slider_steps, steps_output);
  });

  // Event listener for ditter slider
  slider_dither.addEventListener("input", function () {
    updateDitherSlider(slider_dither, dither_output);
  });

  // Event listener for size slider
  slider_size.addEventListener("input", function () {
    updateSliderValue(slider_size, size_output);
  });

  // Update initial slider values
  updateSliderPercentage(slider_bright, output_bright);
  updateSliderPercentage(slider_contrast, contrast_output);
  updateSliderValue(slider_steps, steps_output);
  updateDitherSlider(slider_dither, dither_output);
  updateSliderValue(slider_size, size_output);

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


let PALETTES = null;
let fileInput = null;
let resultInput = null;
let previewToggle = true; // true shows the original , false shows the result
let disabledPreview = true // this is for when theres no results

function handleRadioChange() {
  const select = document.getElementById("options-box");
  const option1 = document.getElementById("grayscale");

  // Initially hide the select element
  select.style.display = option1.checked ? "none" : "block";
}

function displayFileName(input) {
    fileInput = input.files[0];
    const fileName = fileInput.name;
    if (!fileInput) return;

    document.getElementById("file-name").textContent = fileName;
    const preview = document.getElementById("uploaded-preview");

    previewToggle = true;
    resultInput = null;

    // Create temporary local URL
    preview.src = URL.createObjectURL(fileInput);
    preview.style.display = "block";


    //for the results switch (probably turn this into a function
    const resultImg = document.getElementById("result-preview");
    const noResultText = document.getElementById("no-result-text");
    const resultActions = document.getElementById("result-actions");

    resultImg.style.display = "none";
    noResultText.style.display = "none";
    resultActions.style.display = "none";


}

function togglePreviewBtn() {
    //checker , if its true then will switch false and show the result
    if( previewToggle) {
        previewToggle = !previewToggle;
        const preview = document.getElementById("uploaded-preview");
        preview.style.display = "block";
        const resultImg = document.getElementById("result-preview");
        resultImg.style.display= "none";
        const btnPreview = document.getElementById("previewBtn");
        btnPreview.textContent = "Show Result"
    }
    else {
        previewToggle = !previewToggle;
        const preview = document.getElementById("uploaded-preview");
        preview.style.display = "none";
        const resultImg = document.getElementById("result-preview");
        resultImg.style.display= "block";
        const btnPreview = document.getElementById("previewBtn");
        btnPreview.textContent = "Show Original"
    }
}

async function updatePalettePreview(name) {
    const preview = document.getElementById("palettePreview");
    preview.innerHTML = "";

    if (!name) return;

    // Load once if not loaded
    if (!PALETTES) {
        const response = await fetch("./static/assets/pallets.JSON");
        PALETTES = await response.json();
    }

    if (!PALETTES[name]) return;

    PALETTES[name].forEach(color => {
        const block = document.createElement("div");
        block.className = "color-block";
        block.style.backgroundColor = color;
        block.style.border= "1px solid white"
        block.title = color;
        preview.appendChild(block);
    });
}

  async function sendToBackend() {

   const fileInput = document.getElementById("file");
   console.log(fileInput)

    if (!fileInput.files[0]) {
      alert("Please upload an image first.");
      return;
    }


    const formData = new FormData();

    // File
    formData.append("file", fileInput.files[0]);

    // Sliders (example — adapt IDs to yours)
    formData.append("brightness", document.getElementById("brightness").value);
    formData.append("contrast", document.getElementById("contrast").value);
    formData.append("steps", document.getElementById("steps").value);
    formData.append("dither", document.getElementById("dither_op").value);
    formData.append("pixel_size", document.getElementById("pixel_size").value)

    //Radio Button selction choise
    const greyscaleOption = document.getElementById("grayscale");
    const colorOption = document.getElementById("colors");

    if (greyscaleOption.checked) {
      formData.append("grayscale" , "grayscale")
    }
    if (colorOption.checked) {
      formData.append("grayscale", "colors")
      formData.append("colors", document.getElementById("select-option").value);
    }


    try {
          const response = await fetch("/pixelfy", {
              method: "POST",
              body: formData
          });

          const data = await response.json();
          console.log(data);
          resultInput = "data:image/jpeg;base64," + data.image_data;

          const resultImg = document.getElementById("result-preview");
          const noResultText = document.getElementById("no-result-text");
          const resultActions = document.getElementById("result-actions");

          resultImg.src = resultInput
          resultImg.style.display = "block";
          noResultText.style.display = "none";
          resultActions.style.display = "block";
          //turn off the preview file
          const preview = document.getElementById("uploaded-preview");
          preview.style.display = "none"


      } catch (error) {
        console.error("Error:", error);
    }
}

function saveImage() {
    const img = document.getElementById("result-preview");
    if (!img.src) return;

    const link = document.createElement("a");
    link.href = img.src;
    link.download = "pixely-" + Date.now() + ".jpg"; // change if PNG

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

