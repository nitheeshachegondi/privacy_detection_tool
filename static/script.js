document.addEventListener("DOMContentLoaded", () => {
  // Handle Text Analysis Form
  const textForm = document.getElementById("textForm");
  const textResult = document.getElementById("textResult");

  textForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent form from reloading the page
    textResult.innerHTML = "Analyzing text..."; // Show progress message

    // Get input values
    const url = document.getElementById("url").value;
    const keyword = document.getElementById("keyword").value;

    try {
      // Send POST request to Flask backend
      const response = await fetch("/detect-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, keyword }), // Send data as JSON
      });

      // Check if the response is not OK
      if (!response.ok) {
        const errorData = await response.json();
        textResult.innerHTML = `Error: ${errorData.error}`;
        return;
      }

      // Parse and display response from the server
      const result = await response.json();
      textResult.innerHTML = result.message || "No message returned.";
    } catch (error) {
      // Catch and display any network or runtime errors
      textResult.innerHTML = `Error analyzing text: ${error.message}`;
    }
  });

  // Handle Image Analysis Form
  const imageForm = document.getElementById("imageForm");
  const imageResult = document.getElementById("imageResult");

  imageForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent form from reloading the page
    imageResult.innerHTML = "Analyzing image..."; // Show progress message

    try {
      // Create a FormData object with the file data
      const formData = new FormData(imageForm);

      // Send POST request to Flask backend
      const response = await fetch("/detect-image", {
        method: "POST",
        body: formData, // Send FormData containing the file
      });

      // Check if the response is not OK
      if (!response.ok) {
        const errorData = await response.json();
        imageResult.innerHTML = `Error: ${errorData.error}`;
        return;
      }

      // Parse and display response from the server
      const result = await response.json();
      imageResult.innerHTML = result.message || "No message returned.";
    } catch (error) {
      // Catch and display any network or runtime errors
      imageResult.innerHTML = `Error analyzing image: ${error.message}`;
    }
  });
});
