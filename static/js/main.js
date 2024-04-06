// static/js/main.js
document.getElementById('image-upload-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the default form submission

    const formData = new FormData();
    const imageFile = document.getElementById('image').files[0];
    if (!imageFile) {
        document.getElementById('upload-status').innerText = 'Please select a file.';
        return;
    }
    formData.append('image', imageFile);

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        document.getElementById('upload-status').innerText = data.message; // Display success message
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
        document.getElementById('upload-status').innerText = 'Upload failed.';
    });
});
