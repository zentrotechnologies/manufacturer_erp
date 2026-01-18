function IsValid(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    return false;
  }
}

function IsValidNumber(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    if (isNaN(value)) {
      return false;
    } else {
      return true;
    }
  }
}
function IsValidInteger(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^-?\d+$/; // Regular expression for integer
    return re.test(String(value).toLowerCase());
  }
}

function IsValidFloat(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^-?\d+(\.\d+)?$/; // Regular expression for float

    return re.test(String(value).toLowerCase());
  }
}

function IsValidAlpha(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^[a-zA-Z]+$/; // Regular expression for alphabetic characters
    return re.test(String(value).toLowerCase());
  }
}
function IsValidAlphaSpace(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^[a-zA-Z\s]+$/; // Regular expression for alphabetic characters with spaces
    return re.test(String(value).toLowerCase());
  }
}

function IsValidAlphaNumericSpace(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  }
  else {
    var re = /^[a-zA-Z0-9\s]+$/; // Regular expression for alphanumeric characters with spaces
    return re.test(String(value).toLowerCase());
  }
}




function IsValidAlphaNumeric(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  }
  else {
    var re = /^[a-zA-Z0-9]+$/; // Regular expression for alphanumeric characters
    return re.test(String(value).toLowerCase());
  }
}




function IsValidEmail(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(value).toLowerCase());
  }
}

function IsValidURL(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
    return re.test(String(value).toLowerCase());
  }
}

function IsValidPhone(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^\+?[1-9]\d{6,14}$/; // E.164 format
    return !re.test(String(value).toLowerCase());
  }
}

function IsValidDate(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$/; // DD-MM-YYYY format
    return re.test(String(value).toLowerCase());
  }
}


function IsValidTime(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/; // HH:MM format
    return re.test(String(value).toLowerCase());
  }
}

function IsValidDateTime(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4} (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/; // DD-MM-YYYY HH:MM format
    return re.test(String(value).toLowerCase());
  }
}
function IsValidTimeRange(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] - (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/; // HH:MM - HH:MM format
    return re.test(String(value).toLowerCase());
  }
}
function IsValidTimeRange24(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] - (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/; // HH:MM - HH:MM format
    return re.test(String(value).toLowerCase());
  }
}

function IsValidTimeRange12(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM) - (0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$/; // HH:MM AM/PM - HH:MM AM/PM format
    return re.test(String(value).toLowerCase());
  }
}
function IsValidTimeRange12AMPM(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM) - (0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$/; // HH:MM AM/PM - HH:MM AM/PM format
    return re.test(String(value).toLowerCase());
  }
}
function IsValidTimeRange24AMPM(value) {
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] - (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/; // HH:MM - HH:MM format
    return re.test(String(value).toLowerCase());
  }
}



function validateImageInput(inputElement) {

  if (inputElement.files && inputElement.files.length > 0) {
    const file = inputElement.files[0];
    const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
    const preview = document.getElementById('preview_' + inputElement.id);

    // Check if the file type is in our valid list
    if (!validImageTypes.includes(file.type)) {
      // Clear the invalid file
      inputElement.value = '';
      preview.style.display = 'none';
      preview.src = '';

      // Show error message
      swal({
        icon: "error",
        title: "",
        text: "Please upload only image files (JPEG, PNG, GIF, WEBP, SVG)",
      });
      return false;
    }

    // Optional: Check file size (e.g., 5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      inputElement.value = '';
      preview.style.display = 'none';
      preview.src = '';
      swal({
        icon: "error",
        title: "",
        text: "File size too large. Maximum allowed is 5MB.",
      });
      return false;
    }

    // Image preview logic
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);

    return true;
  }

  // No file selected - hide the preview
  const preview = document.getElementById('preview_' + inputElement.id);
  if (preview) {
    preview.style.display = 'none';
  }
  return false;
}

function validateMultipleImageInput(inputElement) {
  let currentFiles = [];

  const previewContainer = document.getElementById('preview_' + inputElement.id);
  previewContainer.innerHTML = ''; // Clear previous previews

  if (inputElement.files && inputElement.files.length > 0) {
    currentFiles = [...currentFiles, ...Array.from(inputElement.files)];

    const files = inputElement.files;
    const validTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
      'video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo',
      'video/x-flv', 'video/x-matroska'
    ];
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes (larger for videos)

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // Validate file type
      if (!validTypes.includes(file.type)) {
        inputElement.value = '';
        previewContainer.innerHTML = '';
        swal({
          icon: "error",
          title: "Invalid File Type",
          text: "Please upload only image or video files in supported formats.",
        });
        return false;
      }

      // Validate file size
      if (file.size > maxSize) {
        inputElement.value = '';
        previewContainer.innerHTML = '';
        swal({
          icon: "error",
          title: "File Too Large",
          text: "Maximum file size allowed is 50MB.",
        });
        return false;
      }

      // Create preview
      const previewElement = document.createElement(file.type.includes('video') ? 'video' : 'img');
      previewElement.style.maxWidth = '150px';
      previewElement.style.maxHeight = '150px';
      previewElement.style.objectFit = 'cover';

      if (file.type.includes('video')) {
        previewElement.controls = true;
      }

      const reader = new FileReader();
      reader.onload = function (e) {
        previewElement.src = e.target.result;
      };
      reader.readAsDataURL(file);

      const previewWrapper = document.createElement('div');
      previewWrapper.style.position = 'relative';
      previewWrapper.style.display = 'inline-block';

      // Add remove button
      const removeBtn = document.createElement('button');
      removeBtn.innerHTML = '×';
      removeBtn.style.position = 'absolute';
      removeBtn.style.top = '0';
      removeBtn.style.right = '0';
      removeBtn.style.background = 'red';
      removeBtn.style.color = 'white';
      removeBtn.style.border = 'none';
      removeBtn.style.borderRadius = '50%';
      removeBtn.style.width = '20px';
      removeBtn.style.height = '20px';
      removeBtn.style.cursor = 'pointer';
      removeBtn.onclick = function () {
        // Remove this file from input (this requires more complex handling)
        previewWrapper.remove();
      };

      previewWrapper.appendChild(previewElement);
      previewWrapper.appendChild(removeBtn);
      previewContainer.appendChild(previewWrapper);

      // Modify the remove button handler:
      removeBtn.onclick = function () {
        // Remove file from currentFiles array
        currentFiles = currentFiles.filter((f) => f.name !== file.name);

        // Update the input element
        const dataTransfer = new DataTransfer();
        currentFiles.forEach(file => dataTransfer.items.add(file));
        inputElement.files = dataTransfer.files;

        // Remove preview
        previewWrapper.remove();
      };

    }
    return true;
  }
  return false;
}





function IsValidAlphaSpaceInput(inoutElement) {

  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  }
  else {
    var re = /^[a-zA-Z\s]+$/; // Regular expression for alphabetic characters with spaces
    // Check if the input value matches the regular expression
    // else remove  exclude alphabetic characters and spaces
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-alphabetic characters and spaces
      inoutElement.value = value.replace(/[^a-zA-Z\s]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input


  }
}
function IsValidAlphaNumericSpaceInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  }
  else {
    var re = /^[a-zA-Z0-9\s]+$/; // Regular expression for alphanumeric characters with spaces
    // Check if the input value matches the regular expression
    // else remove  exclude alphanumeric characters and spaces
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-alphanumeric characters and spaces
      inoutElement.value = value.replace(/[^a-zA-Z0-9\s]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidAlphaNumericInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  }
  else {
    var re = /^[a-zA-Z0-9]+$/; // Regular expression for alphanumeric characters
    // Check if the input value matches the regular expression
    // else remove  exclude alphanumeric characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-alphanumeric characters
      inoutElement.value = value.replace(/[^a-zA-Z0-9]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidEmailInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    // Check if the input value matches the regular expression
    // else remove  exclude email characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-email characters
      inoutElement.value = value.replace(/[^a-zA-Z0-9@._-]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidNumberInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    // Check if the input value is a valid number
    if (isNaN(value)) {
      // If it's not a valid number, remove non-numeric characters
      inoutElement.value = value.replace(/[^0-9.-]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidPhoneInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^\+?[1-9]\d{1,14}$/; // E.164 format
    // Check if the input value matches the regular expression
    // else remove  exclude phone characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-phone characters
      inoutElement.value = value.replace(/[^0-9+]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}

function IsValidURLInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
    // Check if the input value matches the regular expression
    // else remove  exclude URL characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-URL characters
      inoutElement.value = value.replace(/[^a-zA-Z0-9:\/?&=._-]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidLattitudeInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^-?([1-8]?\d(\.\d+)?|90(\.0+)?)$/; // Latitude range -90 to 90
    // Check if the input value matches the regular expression
    // else remove  exclude latitude characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-latitude characters
      inoutElement.value = value.replace(/[^0-9.-]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}
function IsValidLongitudeInput(inoutElement) {
  var value = inoutElement.value;
  if (value == "" || value == null || value == undefined) {
    return true;
  } else {
    var re = /^-?((1[0-7]\d(\.\d+)?)|([1-9]?\d(\.\d+)?|180(\.0+)?))$/; // Longitude range -180 to 180
    // Check if the input value matches the regular expression
    // else remove  exclude longitude characters
    if (!re.test(String(value).toLowerCase())) {
      // If it doesn't match, remove non-longitude characters
      inoutElement.value = value.replace(/[^0-9.-]/g, '');
      return false; // Invalid input
    }
    return true; // Valid input
  }
}

/**
 * Initialize password visibility togglers
 */


function ddmmyyyytoyyyymmdd(datestr) {
  // Use regex to split by either - or /
  const parts = datestr.split(/[-\/]/);
  
  if (parts.length !== 3) {
    throw new Error('Invalid date format. Expected dd-mm-yyyy or dd/mm/yyyy');
  }
  
  const day = parts[0].padStart(2, '0');
  const month = parts[1].padStart(2, '0');
  const year = parts[2];
  
  return `${year}-${month}-${day}`;
}