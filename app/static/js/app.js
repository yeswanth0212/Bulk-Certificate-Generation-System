let activeJobPollInterval = null;
let currentJobId = null;

function loadSampleData() {
    const sample = 
`Alice Johnson, alice@example.com, High Distinction
Bob Smith, bob@example.com, First Class Honors
Charlie Davis, charlie@example.com, Certificate of Merit
Diana Prince, diana@example.com, Excellence Award`;
    document.getElementById("recipientsText").value = sample;
}

function loadSampleDataWithErrors() {
    const sampleWithErrors = 
`Elon Musk, elon@example.com, Starship Engineering
Invalid User No Email, invalid-email-format, Test Grade
   , blank-name@example.com, Empty Name Test
Grace Hopper, grace@example.com, Computer Science Pioneer`;
    document.getElementById("recipientsText").value = sampleWithErrors;
}

function parseRecipients(text) {
    const lines = text.trim().split("\n");
    const recipients = [];

    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        const parts = line.split(",").map(p => p.trim());
        recipients.push({
            name: parts[0] || "",
            email: parts[1] || "",
            custom_text: parts[2] || null
        });
    }
    return recipients;
}

async function handleJobSubmit(e) {
    e.preventDefault();
    const title = document.getElementById("title").value.trim();
    const issuer = document.getElementById("issuer").value.trim();
    const signatoryName = document.getElementById("signatory_name").value.trim() || null;
    const signatoryTitle = document.getElementById("signatory_title").value.trim() || null;
    const issueDate = document.getElementById("issue_date").value.trim() || null;
    const format = document.getElementById("format").value;
    const rawText = document.getElementById("recipientsText").value;

    const recipients = parseRecipients(rawText);

    if (recipients.length === 0) {
        alert("Please enter at least one recipient!");
        return;
    }

    const payload = {
        title: title,
        issuer: issuer,
        issue_date: issueDate,
        signatory_name: signatoryName,
        signatory_title: signatoryTitle,
        format: format,
        recipients: recipients
    };

    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");
    submitBtn.disabled = true;
    btnText.innerText = "Submitting Job...";

    try {
        const response = await fetch("/api/v1/jobs", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            let detailMsg = "Error submitting job.";
            try {
                const errData = await response.json();
                detailMsg = Array.isArray(errData.detail) 
                    ? errData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join("\n") 
                    : (errData.detail || detailMsg);
            } catch (jsonErr) {
                const rawText = await response.text();
                detailMsg = `Server Error (${response.status}): ${rawText.substring(0, 150)}`;
            }
            alert("Validation / Submission Error:\n" + detailMsg);
            return;
        }

        const jobData = await response.json();
        currentJobId = jobData.id;
        displayJob(jobData);
        startPolling(jobData.id);

    } catch (err) {
        alert("Failed to submit job: " + err.message);
    } finally {
        submitBtn.disabled = false;
        btnText.innerText = "🚀 Start Bulk Generation";
    }
}

async function fetchJobDetails(jobId) {
    try {
        const response = await fetch(`/api/v1/jobs/${jobId}`);
        if (!response.ok) return null;
        return await response.json();
    } catch (err) {
        console.error("Failed to fetch job", err);
        return null;
    }
}

function checkJobById() {
    const inputId = document.getElementById("searchJobId").value.trim();
    if (!inputId) return;
    currentJobId = inputId;
    fetchJobDetails(inputId).then(jobData => {
        if (!jobData) {
            alert("Job ID not found!");
            return;
        }
        displayJob(jobData);
        startPolling(inputId);
    });
}

function displayJob(job) {
    document.getElementById("noJobState").classList.add("hidden");
    document.getElementById("jobDetailsState").classList.remove("hidden");

    // Title & Badge
    document.getElementById("displayJobTitle").innerText = job.title;
    document.getElementById("displayJobMeta").innerText = `ID: ${job.id} | Issuer: ${job.issuer}`;
    
    const badge = document.getElementById("jobStatusBadge");
    badge.innerText = job.status;
    badge.className = `status-badge ${job.status}`;

    // ZIP Download Button
    const zipContainer = document.getElementById("zipDownloadContainer");
    if (job.zip_download_url && (job.status === "COMPLETED" || job.status === "PARTIAL_SUCCESS")) {
        zipContainer.innerHTML = `<a href="${job.zip_download_url}" target="_blank" class="btn-secondary">📦 Download All (ZIP)</a>`;
    } else {
        zipContainer.innerHTML = "";
    }

    // Progress Bar & Counts
    document.getElementById("progressBarFill").style.width = `${job.progress_percentage}%`;
    document.getElementById("progressText").innerText = `Progress: ${job.progress_percentage}%`;
    document.getElementById("countsText").innerText = `${job.processed_count} / ${job.total_recipients} Processed`;

    // Stats
    document.getElementById("statTotal").innerText = job.total_recipients;
    document.getElementById("statSuccess").innerText = job.success_count;
    document.getElementById("statFailed").innerText = job.failure_count;

    // Recipients Table
    const tbody = document.getElementById("recipientsTableBody");
    tbody.innerHTML = "";

    job.recipients.forEach(r => {
        const tr = document.createElement("tr");

        let statusPill = `<span class="status-badge ${r.status}">${r.status}</span>`;
        let dlAction = "-";
        let vrAction = "-";

        if (r.status === "SUCCESS" && r.download_url) {
            dlAction = `<a href="${r.download_url}" target="_blank" class="btn-dl">📥 Certificate</a>`;
            vrAction = `<a href="${r.verify_url}" target="_blank" class="btn-vr">🔍 Verify</a>`;
        } else if (r.status === "FAILED") {
            dlAction = `<span class="err-text" title="${r.error_message || 'Failed'}">⚠️ ${r.error_message || 'Failed'}</span>`;
        }

        tr.innerHTML = `
            <td>
                <div class="rec-name">${escapeHtml(r.recipient_name)}</div>
                <div class="rec-email">${escapeHtml(r.recipient_email)}</div>
            </td>
            <td>${statusPill}</td>
            <td>${dlAction}</td>
            <td>${vrAction}</td>
        `;
        tbody.appendChild(tr);
    });
}

function startPolling(jobId) {
    if (activeJobPollInterval) clearInterval(activeJobPollInterval);

    activeJobPollInterval = setInterval(async () => {
        const job = await fetchJobDetails(jobId);
        if (job) {
            displayJob(job);
            if (job.status === "COMPLETED" || job.status === "PARTIAL_SUCCESS" || job.status === "FAILED") {
                clearInterval(activeJobPollInterval);
            }
        }
    }, 1500);
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
