document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileList = document.getElementById("fileList");
    const uploadBtn = document.getElementById("uploadBtn");
    const statusDot = document.getElementById("statusDot");
    const statusText = document.getElementById("statusText");
    const statusDetail = document.getElementById("statusDetail");
    const chatMessages = document.getElementById("chatMessages");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const clearChatBtn = document.getElementById("clearChatBtn");

    let selectedFiles = [];
    let isIndexed = false;

    // Trigger File Dialog
    dropZone.addEventListener("click", () => fileInput.click());

    // File Input Selection
    fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

    // Drag and Drop Events
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        for (let file of files) {
            if (file.type === "application/pdf" && !selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            }
        }
        updateFileList();
    }

    function updateFileList() {
        fileList.innerHTML = "";
        if (selectedFiles.length === 0) {
            fileList.innerHTML = `<li class="empty-msg">No files selected</li>`;
            uploadBtn.disabled = true;
            return;
        }

        selectedFiles.forEach((file, index) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span><i class="fa-regular fa-file-pdf"></i> ${file.name}</span>
                <i class="fa-solid fa-xmark remove-file" data-index="${index}" style="cursor:pointer; color:#ef4444;"></i>
            `;
            fileList.appendChild(li);
        });

        uploadBtn.disabled = false;

        // Remove File Handler
        document.querySelectorAll(".remove-file").forEach(icon => {
            icon.addEventListener("click", (e) => {
                const idx = parseInt(e.target.getAttribute("data-index"));
                selectedFiles.splice(idx, 1);
                updateFileList();
            });
        });
    }

    // Upload Files to FastAPI Backend
    uploadBtn.addEventListener("click", async () => {
        if (selectedFiles.length === 0) return;

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append("files", file));

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Indexing...`;

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                isIndexed = true;
                statusDot.className = "status-dot connected";
                statusText.innerText = "Documents Indexed";
                statusDetail.innerText = `${data.data.processed_files.length} paper(s) ready for context Q&A.`;
                sendBtn.disabled = false;
                appendSystemMessage("PDF papers successfully uploaded and indexed. You can now ask questions!");
            } else {
                alert(`Error: ${data.detail || 'Upload failed'}`);
            }
        } catch (err) {
            alert(`Error processing files: ${err.message}`);
        } finally {
            uploadBtn.innerHTML = `<i class="fa-solid fa-arrow-up-from-bracket"></i> Process & Index PDFs`;
            uploadBtn.disabled = false;
        }
    });

    // Auto-resize Textarea
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = userInput.scrollHeight + "px";
    });

    // Send Message on Enter Key (Shift+Enter for newline)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener("click", sendMessage);

    async function sendMessage() {
        const question = userInput.value.trim();
        if (!question || !isIndexed) return;

        appendUserMessage(question);
        userInput.value = "";
        userInput.style.height = "auto";
        sendBtn.disabled = true;

        const loadingMsgId = appendLoadingMessage();

        try {
            const response = await fetch("/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();
            removeMessage(loadingMsgId);

            if (response.ok) {
                appendAIMessage(data.answer, data.sources);
            } else {
                appendAIMessage(`Error: ${data.detail || 'Failed to retrieve answer.'}`, []);
            }
        } catch (err) {
            removeMessage(loadingMsgId);
            appendAIMessage(`Connection error: ${err.message}`, []);
        } finally {
            sendBtn.disabled = false;
        }
    }

    function appendUserMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message user";
        msgDiv.innerHTML = `<div class="msg-content">${escapeHtml(text)}</div>`;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendAIMessage(answer, sources) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message ai";
        
        let sourcesHtml = "";
        if (sources && sources.length > 0) {
            sourcesHtml = `<div class="sources-container">`;
            sources.forEach(src => {
                sourcesHtml += `<span class="source-badge"><i class="fa-solid fa-bookmark"></i> ${escapeHtml(src.source_file)} (Page ${src.page_number})</span>`;
            });
            sourcesHtml += `</div>`;
        }

        msgDiv.innerHTML = `
            <div class="msg-content">
                <p>${escapeHtml(answer)}</p>
                ${sourcesHtml}
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message system-message";
        msgDiv.innerHTML = `<i class="fa-solid fa-circle-check"></i> <div class="msg-content">${escapeHtml(text)}</div>`;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendLoadingMessage() {
        const id = "loading-" + Date.now();
        const msgDiv = document.createElement("div");
        msgDiv.className = "message ai";
        msgDiv.id = id;
        msgDiv.innerHTML = `<div class="msg-content"><i class="fa-solid fa-spinner fa-spin"></i> Searching uploaded papers...</div>`;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Expose prompt filler function globally
    window.fillPrompt = function(promptText) {
        userInput.value = promptText;
        userInput.dispatchEvent(new Event("input"));
        userInput.focus();
    };

    // Clear Chat
    clearChatBtn.addEventListener("click", () => {
        chatMessages.innerHTML = "";
        appendSystemMessage("Chat history cleared.");
    });
});