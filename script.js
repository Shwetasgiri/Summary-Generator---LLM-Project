console.log("Script loaded - version 6");

const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const textInput = document.getElementById('text-input');
const summarizeBtn = document.getElementById('summarize-btn');
const resultSection = document.getElementById('result-section');
const similarityResultDiv = document.getElementById('similarity-result');

if (!uploadBtn || !summarizeBtn || !resultSection || !similarityResultDiv) {
    console.error("One or more required elements not found in the DOM");
} else {
    uploadBtn.addEventListener('click', handleFileUpload);
    summarizeBtn.addEventListener('click', handleTextSummarization);
}

async function handleFileUpload() {
    console.log("File upload started");
    const files = fileInput.files;
    if (files.length === 0) {
        console.log("No files selected");
        alert('Please select at least one file.');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
        console.log(`Appended file: ${files[i].name}`);
    }
    formData.append('summary_length', 150);

    try {
        console.log("Sending request to server");
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        console.log("Received response from server");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Server response:", data);
        displayResults(data);
    } catch (error) {
        console.error("Error during file upload:", error);
        alert('An error occurred during file upload. Please try again.');
    }
}

async function handleTextSummarization() {
    console.log("Text summarization started");
    const text = textInput.value.trim();
    if (!text) {
        console.log("No text entered");
        alert('Please enter some text to summarize.');
        return;
    }

    const formData = new FormData();
    formData.append('text', text);
    formData.append('summary_length', 150);

    try {
        const response = await fetch('/summarize-text', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Server response:", data);
        displayResults(data);
    } catch (error) {
        console.error("Error during text summarization:", error);
        alert('An error occurred during text summarization. Please try again.');
    }
}

function displayResults(data) {
    console.log("Displaying results:", data);
    
    resultSection.innerHTML = ''; // Clear previous results
    
    if (data.original_texts && data.summaries) {
        data.original_texts.forEach((text, index) => {
            const docBox = document.createElement('div');
            docBox.className = 'document-box';
            docBox.innerHTML = `
                <h3>Document ${index + 1}</h3>
                <div class="result-box">
                    <h4>Original Text:</h4>
                    <p>${text}</p>
                </div>
                <div class="result-box">
                    <h4>Summary:</h4>
                    <p>${data.summaries[index]}</p>
                </div>
            `;
            resultSection.appendChild(docBox);
        });
        
        console.log("Document boxes created for each text and summary");
        
        if (data.similarity_matrix) {
            displaySimilarityMatrix(data.similarity_matrix);
        } else {
            similarityResultDiv.textContent = 'Similarity information not available';
        }
    } else {
        console.error("Unexpected data format:", data);
        resultSection.innerHTML = "<p>Error: Unexpected data format</p>";
    }
}

function displaySimilarityMatrix(matrix) {
    let table = '<table><tr><th>Document</th>';
    for (let i = 0; i < matrix.length; i++) {
        table += `<th>Doc ${i+1}</th>`;
    }
    table += '</tr>';

    for (let i = 0; i < matrix.length; i++) {
        table += `<tr><th>Doc ${i+1}</th>`;
        for (let j = 0; j < matrix[i].length; j++) {
            if (i === j) {
                table += '<td>-</td>';
            } else {
                table += `<td>${matrix[i][j].toFixed(2)}</td>`;
            }
        }
        table += '</tr>';
    }
    table += '</table>';

    similarityResultDiv.innerHTML = table;
}