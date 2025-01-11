/*const toggleButton = document.getElementById('darkModeToggle');

toggleButton.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    // Optionally, store user preference in local storage
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

// Check if dark mode was previously enabled
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
} */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get form element
    const form = document.getElementById('uploadCaForm');
    // Add submit event listener to form
    form.addEventListener('submit', handleCaUpload);
});

async function handleCaUpload(event) {
// Prevent the default form submission
event.preventDefault();
alert('Upload started...');
    
// Get form values
const caName = document.getElementById('caName').value;
const cAction = document.getElementById('cAction').value;
const fileInput = document.getElementById('cafile');
const file = fileInput.files[0];

// Validate form
if (!caName || !cAction || !file) {
    alert('Please fill in all fields and select a file');
    return;
}

// Create FormData object to send file
const formData = new FormData();
formData.append('caName', caName);
formData.append('cAction', cAction);

// Here you would typically send the formData to a server
// For demonstration, we'll just log the data
//start
for (let i=0; i < fileInput.files.length; i++) {
    formData.append('cafile', fileInput.files[i]);
    console.log('cAction:', cAction, 'caName:', caName, 'File Name:', fileInput.files[i].name, 'File Size:', fileInput.files[i].size );
    const response = await fetch('/ca/upload', {
        method: 'POST',
        body: formData
        /*
         headers: {
                // Don't set Content-Type header when sending FormData
                // It will be automatically set with the correct boundary
                'Accept': 'application/json',
                // Add any authentication headers if needed
                // 'Authorization': 'Bearer your-token-here'
            }
        */
    }) //end of post
    .then(response => {
        if (!response.ok) {
           //check if teh response is json
           if (response.headers.get('content-type') && response.headers.get('content-type').includes('application/json')) {
               //get the json response
               return response.json().then(errorData => {
                //handle json error response
                console.error('Error:', errorData);
                showAlert('Upload filed with Error: ' + errorData.message, 'danger');
               });
            } else {
                //generic error response
                console.error('Error:', response);
                return response.text().then(responseText => {  // Read the text response
                    console.error('Server Response:', responseText); // Log the raw response for debugging
                    //alert('An error occurred during upload. Check the console for details.');
                    showAlert('An error occurred during upload.', 'danger');
                    });
            }
        }
        return response.json();
    }) //end of response
    .then(data => {
        console.log('File uploaded successfully:', data);
        //alert('Upload successful');
        showAlert('Upload successful', 'success');
    }) //end of data
    .catch((error) => {
        console.error('Network error during upload:', error);
        //alert('An error occurred during upload. Check the console for details.');
        showAlert('A network error occurred during upload.', 'danger');  // Red alert
    }); //end of catch
    formData.delete('cafile'); // Remove the file from formData for the next iteration
}//end of for loop for file input
//end


}
